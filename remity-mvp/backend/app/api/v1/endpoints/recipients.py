from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import uuid
from typing import List

from app import crud, models, schemas # Import from top-level __init__ files
from app.api import dependencies # Import dependencies

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=schemas.Recipient, status_code=status.HTTP_201_CREATED)
async def create_recipient(
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    recipient_in: schemas.RecipientCreate,
    current_user: models.User = Depends(dependencies.get_current_active_user), # Any active user can add recipients
) -> models.Recipient:
    """
    Create a new recipient for the current logged-in user.
    """
    logger.info(f"User {current_user.email} attempting to create recipient: {recipient_in.full_name} ({recipient_in.country_code})")
    try:
        # Use the CRUD method that links the recipient to the current user
        recipient = await crud.recipient.create_with_owner(
            db=db, obj_in=recipient_in, user_id=current_user.id
        )
        logger.info(f"Recipient created successfully (ID: {recipient.id}) for user {current_user.email}")
        return recipient
    except ValueError as ve: # Catch validation errors from schema
         logger.warning(f"Recipient creation validation failed for user {current_user.email}: {ve}")
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        # CRUD create already logs DB errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the recipient.",
        )


@router.get("/", response_model=List[schemas.Recipient])
async def read_recipients(
    db: AsyncSession = Depends(dependencies.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> List[models.Recipient]:
    """
    Retrieve recipients for the current logged-in user.
    """
    logger.info(f"User {current_user.email} fetching recipients (skip={skip}, limit={limit})")
    recipients = await crud.recipient.get_multi_by_owner(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return recipients


@router.get("/{recipient_id}", response_model=schemas.Recipient)
async def read_recipient(
    recipient_id: uuid.UUID,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> models.Recipient:
    """
    Get a specific recipient by ID, ensuring it belongs to the current user.
    """
    logger.info(f"User {current_user.email} fetching recipient ID: {recipient_id}")
    recipient = await crud.recipient.get_by_owner(
        db=db, recipient_id=recipient_id, user_id=current_user.id
    )
    if not recipient:
        logger.warning(f"Recipient {recipient_id} not found or not owned by user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found",
        )
    return recipient


@router.put("/{recipient_id}", response_model=schemas.Recipient)
async def update_recipient(
    recipient_id: uuid.UUID,
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    recipient_in: schemas.RecipientUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> models.Recipient:
    """
    Update a recipient owned by the current user.
    Note: Updating payout details might be restricted or require re-validation.
    """
    logger.info(f"User {current_user.email} attempting to update recipient ID: {recipient_id}")
    db_recipient = await crud.recipient.get_by_owner(
        db=db, recipient_id=recipient_id, user_id=current_user.id
    )
    if not db_recipient:
        logger.warning(f"Update failed: Recipient {recipient_id} not found or not owned by user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found",
        )

    # Prevent updating certain fields if necessary (e.g., payout_details)
    update_data = recipient_in.model_dump(exclude_unset=True)
    if "payout_details" in update_data or "payout_method" in update_data or "country_code" in update_data:
         logger.warning(f"User {current_user.email} attempted to update restricted recipient fields for ID: {recipient_id}")
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Updating payout method, country, or details is not allowed via this endpoint.",
         )

    try:
        updated_recipient = await crud.recipient.update(
            db=db, db_obj=db_recipient, obj_in=update_data
        )
        logger.info(f"Recipient {recipient_id} updated successfully for user {current_user.email}")
        return updated_recipient
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the recipient.",
        )


@router.delete("/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipient(
    recipient_id: uuid.UUID,
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> None:
    """
    Delete a recipient owned by the current user.
    """
    logger.info(f"User {current_user.email} attempting to delete recipient ID: {recipient_id}")
    db_recipient = await crud.recipient.get_by_owner(
        db=db, recipient_id=recipient_id, user_id=current_user.id
    )
    if not db_recipient:
        logger.warning(f"Delete failed: Recipient {recipient_id} not found or not owned by user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found",
        )

    try:
        await crud.recipient.remove(db=db, id=recipient_id)
        logger.info(f"Recipient {recipient_id} deleted successfully by user {current_user.email}")
        # Return No Content
    except Exception as e:
        # CRUD remove already logs DB errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the recipient.",
        )
