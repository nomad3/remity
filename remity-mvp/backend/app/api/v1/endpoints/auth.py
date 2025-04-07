from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app import crud, models, schemas # Import from top-level __init__ files
from app.api import dependencies # Import dependencies like get_db
from app.core import security # Import security utilities like token creation/verification
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    user_in: schemas.UserCreate,
) -> models.User:
    """
    Register a new user.
    """
    logger.info(f"Attempting registration for email: {user_in.email}")
    existing_user = await crud.user.get_by_email(db, email=user_in.email)
    if existing_user:
        logger.warning(f"Registration failed: Email already registered - {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )
    try:
        user = await crud.user.create(db=db, obj_in=user_in)
        logger.info(f"User registered successfully: {user.email} (ID: {user.id})")
        # Optional: Send verification email here
        return user
    except Exception as e:
        # CRUD create already logs the error and rolls back
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration.",
        )


@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    db: AsyncSession = Depends(dependencies.get_db),
    form_data: OAuth2PasswordRequestForm = Depends() # Standard form data for username/password
) -> schemas.Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Username is the user's email.
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        # crud.user.authenticate already logs details
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create access and refresh tokens
    access_token = security.create_access_token(subject=user.email)
    refresh_token = security.create_refresh_token(subject=user.email)
    logger.info(f"Login successful, tokens generated for user: {user.email}")

    # Optional: Log successful login in AuditLog here

    return schemas.Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=schemas.Token)
async def refresh_access_token(
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    refresh_token_request: schemas.RefreshTokenRequest = Body(...)
) -> schemas.Token:
    """
    Refresh the access token using a valid refresh token.
    """
    refresh_token_str = refresh_token_request.refresh_token
    logger.info("Attempting token refresh.")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials (invalid refresh token)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the refresh token itself (check type claim, expiry, signature)
    token_payload = security.verify_refresh_token(refresh_token_str)
    if not token_payload or not token_payload.sub:
        logger.warning("Refresh token validation failed.")
        raise credentials_exception

    user_email = token_payload.sub
    user = await crud.user.get_by_email(db, email=user_email)

    if not user:
        logger.warning(f"User '{user_email}' from refresh token not found.")
        raise credentials_exception
    if not user.is_active:
         logger.warning(f"User '{user_email}' from refresh token is inactive.")
         raise credentials_exception

    # Generate new tokens
    new_access_token = security.create_access_token(subject=user.email)
    # Optional: Rotate refresh token (generate new one, potentially invalidate old one)
    new_refresh_token = security.create_refresh_token(subject=user.email)
    logger.info(f"Token refresh successful for user: {user.email}")

    return schemas.Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token, # Return the new refresh token
        token_type="bearer",
    )

# Optional: Add /logout endpoint if using server-side refresh token revocation (e.g., storing in Redis/DB)

# Optional: Add /verify-email endpoint
