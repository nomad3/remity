from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import uuid
from typing import List

from app import crud, models, schemas # Import from top-level __init__ files
from app.api import dependencies # Import dependencies
from app.models.transaction import TransactionStatus, Transaction # Import status enum and model
from app.models.user import User # Import User model

logger = logging.getLogger(__name__)

router = APIRouter()

# --- User Management Endpoints (Admin Only) ---

@router.get("/users/", response_model=List[schemas.User])
async def read_users(
    db: AsyncSession = Depends(dependencies.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> List[models.User]:
    """
    Retrieve all users. Requires superuser privileges.
    """
    logger.info(f"Admin {current_user.email} fetching all users.")
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> models.User:
    """
    Get a specific user by ID. Requires superuser privileges.
    """
    logger.info(f"Admin {current_user.email} fetching user ID: {user_id}")
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user_admin(
    user_id: uuid.UUID,
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    user_in: schemas.UserUpdate, # Use the same update schema for now
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> models.User:
    """
    Update a user's details (e.g., activate/deactivate, change roles).
    Requires superuser privileges.
    Password changes should ideally go through a separate flow or user action.
    """
    logger.info(f"Admin {current_user.email} attempting to update user ID: {user_id}")
    db_user = await crud.user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Prevent admin from changing password directly via this endpoint for security
    if user_in.password:
        logger.warning(f"Admin {current_user.email} attempted to change password for user {user_id} via admin endpoint.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be updated via this admin endpoint.")

    # Check for email conflict if email is being changed
    if user_in.email and user_in.email != db_user.email:
        existing_user = await crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            logger.warning(f"Admin update failed for {user_id}: New email '{user_in.email}' already registered.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists.",
            )

    # TODO: Add logic here to update roles or is_active status if needed via specific fields in UserUpdate or a dedicated AdminUserUpdate schema

    try:
        updated_user = await crud.user.update(db=db, db_obj=db_user, obj_in=user_in)
        logger.info(f"User {user_id} updated successfully by admin {current_user.email}")
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user.",
        )

# Note: Deleting users via API might be risky; consider soft delete (setting is_active=False) instead.
# @router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT) ...

# --- Transaction Management Endpoints (Admin Only) ---

@router.get("/transactions/", response_model=List[schemas.Transaction])
async def list_all_transactions(
    db: AsyncSession = Depends(dependencies.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    # Add filtering options? e.g., by status, user_id, date range
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> List[models.Transaction]:
    """
    Retrieve all transactions (paginated). Requires superuser privileges.
    """
    logger.info(f"Admin {current_user.email} fetching all transactions.")
    transactions = await crud.transaction.get_multi(db, skip=skip, limit=limit)
    return transactions


@router.get("/transactions/pending", response_model=List[schemas.Transaction])
async def list_transactions_pending_approval( # Keep this specific endpoint
    db: AsyncSession = Depends(dependencies.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(dependencies.get_current_active_superuser), # Requires admin/superuser
) -> List[models.Transaction]:
    """
    Retrieve transactions that are awaiting manual approval.
    Requires superuser privileges.
    """
    logger.info(f"Admin {current_user.email} fetching transactions pending approval.")
    # TODO: Add specific CRUD method for this query for efficiency if needed
    statement = (
        select(models.Transaction)
        .where(models.Transaction.status == TransactionStatus.PENDING_APPROVAL)
        .offset(skip)
        .limit(limit)
        .order_by(models.Transaction.created_at.asc()) # Order by oldest first
    )
    result = await db.execute(statement)
    transactions = result.scalars().all()
    return transactions


@router.post("/transactions/{transaction_id}/approve", response_model=schemas.Transaction)
async def approve_transaction(
    transaction_id: uuid.UUID,
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    # Optional: Add reason/notes from schema if needed: approve_in: schemas.TransactionApprove,
    current_user: models.User = Depends(dependencies.get_current_active_superuser), # Requires admin/superuser
) -> models.Transaction:
    """
    Manually approve a transaction that is pending approval.
    Requires superuser privileges.
    """
    logger.info(f"Admin {current_user.email} attempting to approve transaction {transaction_id}")
    db_transaction = await crud.transaction.get(db, id=transaction_id)

    if not db_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if db_transaction.status != TransactionStatus.PENDING_APPROVAL:
        logger.warning(f"Admin {current_user.email} tried to approve transaction {transaction_id} with invalid status: {db_transaction.status}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction is not pending approval (current status: {db_transaction.status})."
        )

    try:
        approved_transaction = await crud.transaction.approve(
            db=db, db_obj=db_transaction, reviewer_id=current_user.id
        )
        logger.info(f"Transaction {transaction_id} approved by admin {current_user.email}")
        # TODO: Trigger the next step in the process (e.g., internal processing, crypto swap/transfer simulation)
        # This might involve calling a service or publishing an event.
        return approved_transaction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while approving the transaction.",
        )


@router.post("/transactions/{transaction_id}/reject", response_model=schemas.Transaction)
async def reject_transaction(
    transaction_id: uuid.UUID,
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    reject_in: schemas.TransactionReject, # Requires reason
    current_user: models.User = Depends(dependencies.get_current_active_superuser), # Requires admin/superuser
) -> models.Transaction:
    """
    Manually reject a transaction that is pending approval.
    Requires superuser privileges and a reason for rejection.
    """
    logger.info(f"Admin {current_user.email} attempting to reject transaction {transaction_id} with reason: {reject_in.reason}")
    db_transaction = await crud.transaction.get(db, id=transaction_id)

    if not db_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if db_transaction.status != TransactionStatus.PENDING_APPROVAL:
        logger.warning(f"Admin {current_user.email} tried to reject transaction {transaction_id} with invalid status: {db_transaction.status}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction is not pending approval (current status: {db_transaction.status})."
        )

    try:
        rejected_transaction = await crud.transaction.reject(
            db=db, db_obj=db_transaction, reviewer_id=current_user.id, reason=reject_in.reason
        )
        logger.info(f"Transaction {transaction_id} rejected by admin {current_user.email}")
        # TODO: Trigger refund process or notification to user.
        return rejected_transaction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while rejecting the transaction.",
        )

# Add other admin endpoints as needed (e.g., view all transactions, manage users)
