from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
import logging

from app.core.config import settings
from app.schemas.user import TokenPayload # Import the schema for token data

logger = logging.getLogger(__name__)

# Configure password hashing context (using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.JWT_ALGORITHM
JWT_SECRET_KEY = settings.JWT_SECRET_KEY # Should be loaded from environment

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """ Creates a JWT access token. """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    try:
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error encoding access token: {e}", exc_info=True)
        raise # Re-raise or handle appropriately

def create_refresh_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """ Creates a JWT refresh token (can also be an opaque token stored in DB/Redis). """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    # Add a claim to distinguish refresh tokens if needed, e.g., 'type': 'refresh'
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    try:
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM) # Use the same secret for simplicity, consider separate key for refresh tokens
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error encoding refresh token: {e}", exc_info=True)
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ Verifies a plain password against a hashed password. """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}", exc_info=True)
        return False

def get_password_hash(password: str) -> str:
    """ Hashes a plain password. """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}", exc_info=True)
        raise # Cannot proceed without hashing

def decode_token(token: str) -> Optional[TokenPayload]:
    """ Decodes a JWT token and returns the payload. Returns None if invalid. """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        # Validate standard claims if needed (e.g., 'exp' is handled by jwt.decode)
        # You might add 'aud' (audience) or 'iss' (issuer) validation here

        # Use Pydantic model for structure and basic validation
        token_data = TokenPayload(sub=payload.get("sub"), exp=payload.get("exp"))
        return token_data
    except JWTError as e:
        logger.warning(f"JWT Error decoding token: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}", exc_info=True)
        return None

# Optional: Function to verify if a token is specifically a refresh token
def verify_refresh_token(token: str) -> Optional[TokenPayload]:
    """ Decodes a token and verifies it's intended as a refresh token. """
    payload_data = decode_token(token)
    if not payload_data:
        return None

    # Check for the specific claim added during refresh token creation
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            logger.warning("Token verification failed: Not a refresh token type.")
            return None
    except JWTError: # Already handled by decode_token, but good practice
        return None

    return payload_data
