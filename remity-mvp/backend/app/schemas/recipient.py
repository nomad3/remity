from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class RecipientBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    routing_number: Optional[str] = None
    swift_code: Optional[str] = None
    iban: Optional[str] = None
    account_type: Optional[str] = None
    bank_branch: Optional[str] = None
    notes: Optional[str] = None

class RecipientCreate(RecipientBase):
    pass

class RecipientUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    routing_number: Optional[str] = None
    swift_code: Optional[str] = None
    iban: Optional[str] = None
    account_type: Optional[str] = None
    bank_branch: Optional[str] = None
    notes: Optional[str] = None

class RecipientInDBBase(RecipientBase):
    id: int
    user_id: int

class Recipient(RecipientInDBBase):
    pass
