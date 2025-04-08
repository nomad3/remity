from typing import Any, Dict, Optional, Union, List # Import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
# Import security utils - ensure this path is correct later
# Assuming it will be in app/core/security.py
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """ CRUD operations for User model. """

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """ Get a user by email address. """
        statement = select(self.model).where(self.model.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """ Create a new user, hashing the password. """
        # Convert Pydantic schema to dict
        create_data = obj_in.model_dump()
        # Hash the password before saving
        create_data["hashed_password"] = get_password_hash(create_data.pop("password"))
        # Create the DB object
        db_obj = self.model(**create_data)

        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(f"Created User with ID: {db_obj.id}, Email: {db_obj.email}")
            return db_obj
        except Exception as e: # Catch potential integrity errors (e.g., duplicate email)
            await db.rollback()
            logger.error(f"Error creating user with email {obj_in.email}: {e}", exc_info=True)
            # Consider raising specific exceptions for duplicate email etc.
            raise

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """ Update a user, handling password hashing if provided. """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # If password is being updated, hash it before saving
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"] # Remove plain password
            update_data["hashed_password"] = hashed_password # Add hashed password

        # Use the base class update method for the actual update
        return await super().update(db=db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """ Authenticate a user by email and password. """
        user = await self.get_by_email(db, email=email)
        logger.debug(f"Attempting authentication for email: {email}")
        user = await self.get_by_email(db, email=email)
        if not user:
            logger.warning(f"Authentication failed: User not found for email {email}")
            return None
        logger.debug(f"User found: {user.email} (Active: {user.is_active})")
        if not user.is_active:
            logger.warning(f"Authentication failed: User {email} is inactive.")
            return None

        # Log password verification attempt
        logger.debug(f"Verifying password for user {email}. Provided password length: {len(password)}, Stored hash: {user.hashed_password}")
        password_verified = verify_password(password, user.hashed_password)
        logger.debug(f"Password verification result for {email}: {password_verified}")

        if not password_verified:
            logger.warning(f"Authentication failed: Invalid password for user {email}")
            return None

        logger.info(f"Authentication successful for user {email}")
        return user

    def is_active(self, user: User) -> bool:
        """ Check if a user is active. """
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """ Check if a user is a superuser. """
        return user.is_superuser

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """ Get multiple users (admin function). """
        # Use the base class method directly
        return await super().get_multi(db=db, skip=skip, limit=limit)

    # Note: Deleting users might be better handled by setting is_active=False (soft delete)
    # rather than using the base remove method which does a hard delete.
    # Implement soft delete logic here if required.


# Instantiate the CRUD object for users
user = CRUDUser(User)
