from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app import crud, models, schemas # Import from top-level __init__ files
from app.api import dependencies # Import dependencies

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> models.User:
    """
    Get current logged-in user's profile information.
    """
    # The dependency already fetches the user object.
    # The response_model (schemas.User) automatically filters out sensitive fields like hashed_password.
    logger.info(f"Fetching profile for user: {current_user.email}")
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> models.User:
    """
    Update current logged-in user's profile information.
    """
    logger.info(f"Attempting profile update for user: {current_user.email}")

    # Check if email is being updated and if it's already taken
    if user_in.email and user_in.email != current_user.email:
        existing_user = await crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            logger.warning(f"Update failed for {current_user.email}: New email '{user_in.email}' already registered.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists.",
            )

    try:
        updated_user = await crud.user.update(db=db, db_obj=current_user, obj_in=user_in)
        logger.info(f"Profile updated successfully for user: {updated_user.email}")
        # Optional: Log profile update in AuditLog here
        return updated_user
    except Exception as e:
        # CRUD update already logs the error and rolls back
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the profile.",
        )

# Consider adding endpoints for admin users to manage other users if needed
# Example:
# @router.get("/", response_model=List[schemas.User])
# async def read_users(
#     db: AsyncSession = Depends(dependencies.get_db),
#     skip: int = 0,
#     limit: int = 100,
#     current_user: models.User = Depends(dependencies.get_current_active_superuser),
# ):
#     """ Retrieve users (admin only). """
#     users = await crud.user.get_multi(db, skip=skip, limit=limit)
#     return users
