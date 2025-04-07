from typing import List, Optional, Dict, Any
from sqlalchemy import select, update as sqlalchemy_update
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import uuid
from decimal import Decimal

from app.crud.base import CRUDBase
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.transaction import TransactionCreate, TransactionBase # Using TransactionBase for update for now

logger = logging.getLogger(__name__)

class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionBase]): # Using TransactionBase for UpdateSchema for now
    """ CRUD operations for Transaction model. """

    async def create_with_owner_and_recipient(
        self,
        db: AsyncSession,
        *,
        obj_in: TransactionCreate,
        user_id: uuid.UUID,
        # recipient_id is already in obj_in
    ) -> Transaction:
        """ Create a new transaction linked to a user and recipient. """
        try:
            # Convert Pydantic schema to dict
            obj_in_data = obj_in.model_dump()
            # Create the DB object, explicitly setting the user_id and initial status
            # NOTE: The status will be set to PENDING_APPROVAL by the payment webhook handler later.
            # Here, we just create the record based on the input schema.
            # The initial status from the model default ('quote_created') might apply briefly.
            db_obj = self.model(
                **obj_in_data,
                user_id=user_id
                # Status will be updated by API endpoint or webhook
            )
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(f"Created Transaction with ID: {db_obj.id} for User ID: {user_id}")
            return db_obj
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating transaction for user {user_id}: {e}", exc_info=True)
            raise

    async def get_multi_by_owner(
        self, db: AsyncSession, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """ Get multiple transactions belonging to a specific user. """
        try:
            statement = (
                select(self.model)
                .where(self.model.user_id == user_id)
                .offset(skip)
                .limit(limit)
                .order_by(self.model.created_at.desc()) # Order by creation date
            )
            result = await db.execute(statement)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting transactions for user {user_id}: {e}", exc_info=True)
            return []

    async def get_by_owner(
        self, db: AsyncSession, *, transaction_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Transaction]:
        """ Get a specific transaction by its ID and owner's ID. """
        try:
            statement = select(self.model).where(
                self.model.id == transaction_id,
                self.model.user_id == user_id
            )
            result = await db.execute(statement)
            return result.scalar_one_or_none()
        except Exception as e:
             logger.error(f"Error getting transaction {transaction_id} for user {user_id}: {e}", exc_info=True)
             return None

    async def update_status(
        self, db: AsyncSession, *, transaction_id: uuid.UUID, status: TransactionStatus, details: Optional[Dict[str, Any]] = None
    ) -> Optional[Transaction]:
        """ Update the status and potentially other details of a transaction. """
        db_obj = await self.get(db, id=transaction_id) # Use base get as status update might come from system/webhook
        if not db_obj:
            logger.warning(f"Attempted to update status for non-existent transaction ID: {transaction_id}")
            return None

        update_data = {"status": status}
        if details:
            update_data.update(details) # Add fields like failure_reason, payout_reference etc.

        try:
            # Use the base update method
            updated_obj = await super().update(db=db, db_obj=db_obj, obj_in=update_data)
            logger.info(f"Updated status for transaction {transaction_id} to {status}")
            return updated_obj
        except Exception as e:
            # Base update handles rollback and logging
            logger.error(f"Failed to update status for transaction {transaction_id}", exc_info=True)
            logger.error(f"Failed to update status/details for transaction {transaction_id}", exc_info=True)
            raise # Re-raise after logging

    async def approve(
        self, db: AsyncSession, *, db_obj: Transaction, reviewer_id: uuid.UUID
    ) -> Transaction:
        """ Mark a transaction as approved by an admin. """
        update_data = {
            "status": TransactionStatus.PROCESSING, # Move to processing state
            "reviewed_by_user_id": reviewer_id,
            "reviewed_at": datetime.now(timezone.utc) # Use timezone aware datetime
        }
        # Use base class update method
        return await super().update(db=db, db_obj=db_obj, obj_in=update_data)

    async def reject(
        self, db: AsyncSession, *, db_obj: Transaction, reviewer_id: uuid.UUID, reason: str
    ) -> Transaction:
        """ Mark a transaction as manually rejected by an admin. """
        update_data = {
            "status": TransactionStatus.MANUALLY_REJECTED,
            "reviewed_by_user_id": reviewer_id,
            "reviewed_at": datetime.now(timezone.utc), # Use timezone aware datetime
            "failure_reason": reason # Store the rejection reason
        }
        # Use base class update method
        return await super().update(db=db, db_obj=db_obj, obj_in=update_data)

    async def get_by_payment_intent_id(
        self, db: AsyncSession, *, payment_intent_id: str
    ) -> Optional[Transaction]:
        """ Get a transaction by its Stripe Payment Intent ID. """
        try:
            statement = select(self.model).where(self.model.onramp_payment_intent_id == payment_intent_id)
            result = await db.execute(statement)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting transaction by payment intent ID {payment_intent_id}: {e}", exc_info=True)
            return None


# Instantiate the CRUD object for transactions
transaction = CRUDTransaction(Transaction)
