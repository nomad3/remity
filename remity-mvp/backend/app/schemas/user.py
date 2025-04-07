from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional
from datetime import datetime

# Import the Enum from the model to reuse it
from app.models.user import KYCStatus

# --- Base Schemas ---

class UserBase(BaseModel):
    """ Base schema with common user attributes """
    email: EmailStr = Field(..., description="User's unique email address")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    phone_number: Optional[str] = Field(None, max_length=50, description="User's phone number")
    # address: Optional[str] = Field(None, description="User's address") # Keep simple for now

    class Config:
        # Allows using model attributes like user.email instead of user['email']
        # Deprecated in Pydantic v2, use model_config instead if migrating
        orm_mode = True
        # Pydantic v2 equivalent:
        # model_config = {
        #     "from_attributes": True
        # }


# --- Schemas for API Requests ---

class UserCreate(UserBase):
    """ Schema for creating a new user (registration) """
    password: str = Field(..., min_length=8, description="User's password (will be hashed)")


class UserUpdate(BaseModel):
    """ Schema for updating user profile information (all fields optional) """
    email: Optional[EmailStr] = Field(None, description="New email address")
    full_name: Optional[str] = Field(None, max_length=255, description="Updated full name")
    phone_number: Optional[str] = Field(None, max_length=50, description="Updated phone number")
    password: Optional[str] = Field(None, min_length=8, description="New password (if changing)")


# --- Schemas for Database Interaction (Internal) ---

class UserInDBBase(UserBase):
    """ Base schema for user data as stored in the database """
    id: UUID4
    kyc_status: KYCStatus
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class UserInDB(UserInDBBase):
    """ Schema representing a full user object in the database, including hashed password """
    hashed_password: str


# --- Schemas for API Responses ---

class User(UserInDBBase):
    """ Schema for returning user data via the API (excludes sensitive info) """
    # Inherits id, email, full_name, phone_number, kyc_status, is_active, is_superuser, created_at, updated_at
    # Excludes hashed_password by default
    pass


# --- Schemas for Authentication ---

class Token(BaseModel):
    """ Schema for JWT access and refresh tokens """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """ Schema for the data encoded within the JWT """
    sub: Optional[str] = None # Subject (usually user ID or email)
    exp: Optional[datetime] = None # Expiry timestamp


class RefreshTokenRequest(BaseModel):
    """ Schema for requesting a new access token using a refresh token """
    refresh_token: str
