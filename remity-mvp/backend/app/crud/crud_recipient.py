from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import uuid

from app.crud.base import CRUDBase
from app.models.recipient import Recipient
from app.schemas.recipient import RecipientCreate, RecipientUpdate

logger = logging.getLogger(__name__)

class CRUDRecipient(CRUDBase[Recipient, RecipientCreate, RecipientUpdate]):
    """ CRUD operations for Recipient model. """

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: RecipientCreate, user_id: uuid.UUID
    ) -> Recipient:
        """ Create a new recipient linked to a specific user. """
        try:
            # Convert Pydantic schema to dict
            obj_in_data = obj_in.model_dump()
            # Create the DB object, explicitly setting the user_id
            db_obj = self.model(**obj_in_data, user_id=user_id)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(f"Created Recipient with ID: {db_obj.id} for User ID: {user_id}")
            return db_obj
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating recipient for user {user_id}: {e}", exc_info=True)
            raise

    async def get_multi_by_owner(
        self, db: AsyncSession, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Recipient]:
        """ Get multiple recipients belonging to a specific user. """
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
            logger.error(f"Error getting recipients for user {user_id}: {e}", exc_info=True)
            return []

    async def get_by_owner(
        self, db: AsyncSession, *, recipient_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Recipient]:
        """ Get a specific recipient by its ID and owner's ID. """
        try:
            statement = select(self.model).where(
                self.model.id == recipient_id,
                self.model.user_id == user_id
            )
            result = await db.execute(statement)
            return result.scalar_one_or_none()
        except Exception as e:
             logger.error(f"Error getting recipient {recipient_id} for user {user_id}: {e}", exc_info=True)
             return None


# Instantiate the CRUD object for recipients
recipient = CRUDRecipient(Recipient)
