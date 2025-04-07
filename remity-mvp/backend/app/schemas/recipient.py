from pydantic import BaseModel, Field, UUID4, field_validator, model_validator
from typing import Optional, Dict, Any
from datetime import datetime

# --- Base Schemas ---

class RecipientBase(BaseModel):
    """ Base schema for recipient attributes """
    full_name: str = Field(..., max_length=255, description="Recipient's full name")
    country_code: str = Field(..., min_length=2, max_length=2, description="Recipient's country code (ISO 3166-1 alpha-2)")
    payout_method: str = Field(..., description="Payout method (e.g., 'spei_clabe', 'gcash_mobile')")
    # Payout details structure depends heavily on the payout_method and country
    payout_details: Dict[str, Any] = Field(..., description="Dictionary containing payout details specific to the method")

    @field_validator('country_code')
    def validate_country_code(cls, v):
        # Basic validation, expand with supported countries
        supported_countries = {"MX", "PH"} # Example for MVP
        if v.upper() not in supported_countries:
            raise ValueError(f"Country code '{v}' is not supported.")
        return v.upper()

    # Add more complex validation based on country and payout method
    @model_validator(mode='after')
    def check_payout_details(self) -> 'RecipientBase':
        method = self.payout_method
        details = self.payout_details
        country = self.country_code

        if country == "MX" and method == "spei_clabe":
            if not details.get("clabe") or not isinstance(details["clabe"], str) or len(details["clabe"]) != 18:
                 raise ValueError("Valid 18-digit 'clabe' is required for SPEI payout in MX.")
            # Optional: Add bank name validation if needed
        elif country == "PH" and method == "gcash_mobile":
            if not details.get("mobile_number") or not isinstance(details["mobile_number"], str):
                 raise ValueError("Valid 'mobile_number' is required for GCash payout in PH.")
            # Add specific mobile number format validation for PH if needed
        else:
            # Add validation for other supported methods/countries
            raise ValueError(f"Payout method '{method}' for country '{country}' is not supported or details are invalid.")

        return self

    class Config:
        orm_mode = True


# --- Schemas for API Requests ---

class RecipientCreate(RecipientBase):
    """ Schema for creating a new recipient """
    # Inherits all fields from RecipientBase
    pass


class RecipientUpdate(BaseModel):
    """ Schema for updating recipient information (all fields optional) """
    # Note: Updating payout details might require careful handling or re-verification
    full_name: Optional[str] = Field(None, max_length=255)
    # Potentially allow updating payout_details, but requires re-validation
    # payout_details: Optional[Dict[str, Any]] = None


# --- Schemas for Database Interaction (Internal) ---

class RecipientInDBBase(RecipientBase):
    """ Base schema for recipient data as stored in the database """
    id: UUID4
    user_id: UUID4 # The user this recipient belongs to
    created_at: datetime
    updated_at: datetime


# --- Schemas for API Responses ---

class Recipient(RecipientInDBBase):
    """ Schema for returning recipient data via the API """
    # Inherits all fields from RecipientInDBBase
    pass
