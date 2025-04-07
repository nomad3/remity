from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.session import get_db # Import async session getter
from app.core.config import settings
from app.core import security # Import security utilities
from app.models.user import User, KYCStatus
from app.schemas.user import TokenPayload
from app.crud import user as crud_user # Import user CRUD operations

logger = logging.getLogger(__name__)

# OAuth2 scheme using the login endpoint URL
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current user from the JWT token.
    Raises HTTPException if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload_data = security.decode_token(token)
        if payload_data is None or payload_data.sub is None:
            logger.warning("Token decoding failed or subject missing.")
            raise credentials_exception
        # Assuming subject 'sub' is the user's email for lookup
        user_email: str = payload_data.sub
    except JWTError:
        logger.warning("JWTError during token decoding.", exc_info=True)
        raise credentials_exception
    except Exception as e: # Catch unexpected errors during decoding
        logger.error(f"Unexpected error decoding token: {e}", exc_info=True)
        raise credentials_exception

    user = await crud_user.user.get_by_email(db, email=user_email)
    if user is None:
        logger.warning(f"User not found for email '{user_email}' from token.")
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current user and ensure they are active.
    """
    if not crud_user.user.is_active(current_user):
        logger.warning(f"Inactive user attempted access: {current_user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency to get the current active user and ensure they are a superuser.
    """
    if not crud_user.user.is_superuser(current_user):
        logger.warning(f"Non-superuser attempted admin access: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency to get the current active user and ensure their KYC is verified.
    """
    if current_user.kyc_status != KYCStatus.VERIFIED:
         logger.warning(f"User {current_user.email} attempted action requiring verified KYC, but status is {current_user.kyc_status}")
         raise HTTPException(
             status_code=status.HTTP_403_FORBIDDEN,
             detail="KYC verification required for this action.",
         )
    return current_user

# You can add more dependencies here as needed, e.g., for specific permissions
