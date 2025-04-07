from pydantic import BaseModel, Field, UUID4, field_validator, model_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

# Import the Enum from the model
from app.models.transaction import TransactionStatus

# --- Schemas for API Requests ---

class TransactionQuoteRequest(BaseModel):
    """ Schema for requesting a transaction quote """
    source_currency: str = Field(..., min_length=3, max_length=3, description="Currency code of the amount being sent (e.g., USD)")
    target_currency: str = Field(..., min_length=3, max_length=3, description="Currency code of the amount to be received (e.g., MXN)")
    # User must provide EITHER source_amount OR target_amount
    source_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=8, description="Amount to send in source currency")
    target_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=8, description="Amount to receive in target currency")

    @field_validator('source_currency', 'target_currency')
    def validate_currency_codes(cls, v):
        # Basic validation, expand with supported currencies from config/service
        supported_currencies = {"USD", "EUR", "MXN", "PHP", "USDC"} # Include internal stablecoin if needed
        if v.upper() not in supported_currencies:
            raise ValueError(f"Currency code '{v}' is not supported.")
        return v.upper()

    @model_validator(mode='after')
    def check_amounts_exclusive(self) -> 'TransactionQuoteRequest':
        if self.source_amount is None and self.target_amount is None:
            raise ValueError("Either 'source_amount' or 'target_amount' must be provided.")
        if self.source_amount is not None and self.target_amount is not None:
            raise ValueError("Provide either 'source_amount' or 'target_amount', not both.")
        return self


class TransactionCreate(BaseModel):
    """ Schema for creating a new transaction after getting a quote """
    quote_id: Optional[str] = Field(None, description="Identifier for the quote used (if applicable, e.g., from cache)") # Optional: Use if quotes are cached/stored
    recipient_id: UUID4 = Field(..., description="ID of the recipient for this transaction")
    source_currency: str = Field(..., min_length=3, max_length=3)
    target_currency: str = Field(..., min_length=3, max_length=3)
    source_amount: Decimal = Field(..., gt=0, decimal_places=8)
    target_amount: Decimal = Field(..., gt=0, decimal_places=8)
    exchange_rate: Decimal = Field(..., gt=0, decimal_places=8)
    remity_fee: Decimal = Field(..., ge=0, decimal_places=8)
    payment_provider_fee: Decimal = Field(..., ge=0, decimal_places=8) # Fee from quote

    # Ensure consistency with quote request validation
    @field_validator('source_currency', 'target_currency')
    def validate_currency_codes(cls, v):
        supported_currencies = {"USD", "EUR", "MXN", "PHP", "USDC"}
        if v.upper() not in supported_currencies:
            raise ValueError(f"Currency code '{v}' is not supported.")
        return v.upper()


# --- Base Schema for DB/API Response ---

class TransactionBase(BaseModel):
    """ Base schema containing common transaction fields """
    id: UUID4
    user_id: UUID4
    recipient_id: UUID4
    status: TransactionStatus
    source_currency: str
    target_currency: str
    source_amount: Decimal
    target_amount: Decimal
    exchange_rate: Decimal
    remity_fee: Decimal
    payment_provider_fee: Decimal
    estimated_delivery_time: Optional[str] = None
    onramp_payment_intent_id: Optional[str] = None
    offramp_payout_reference: Optional[str] = None
    failure_reason: Optional[str] = None # Can be set on FAILED or MANUALLY_REJECTED
    reviewed_by_user_id: Optional[UUID4] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# --- Schemas for API Responses ---

class TransactionQuoteResponse(BaseModel):
    """ Schema for responding to a quote request """
    quote_id: Optional[str] = Field(None, description="Identifier for this quote (e.g., cache key)")
    source_currency: str
    target_currency: str
    source_amount: Decimal # The calculated/confirmed source amount
    target_amount: Decimal # The calculated/confirmed target amount
    exchange_rate: Decimal # The rate used (Fiat Source / Fiat Target)
    remity_fee: Decimal
    payment_provider_fee: Decimal # Estimated on-ramp fee
    total_cost: Decimal = Field(..., description="Total amount user will pay (source_amount + remity_fee + payment_provider_fee)")
    estimated_delivery_time: str
    expires_at: Optional[datetime] = None # Optional: Indicate when the quote expires


class TransactionCreateResponse(BaseModel):
    """ Schema for responding after initiating transaction creation """
    transaction_id: UUID4
    status: TransactionStatus # Should be 'pending_payment'
    # Include Stripe Payment Intent client secret for frontend payment processing
    onramp_payment_intent_client_secret: str


class Transaction(TransactionBase):
    """ Schema for returning transaction details via the API """
    # Inherits all fields from TransactionBase
    # Consider adding recipient/reviewer details if needed
    # recipient: Optional[Recipient] = None
    # reviewer_email: Optional[EmailStr] = None # Example if joining reviewer info
    pass


# --- Schemas for Admin Actions ---

class TransactionManualReviewAction(BaseModel):
    """ Base schema for manual review actions """
    reason: Optional[str] = Field(None, description="Reason for rejection (required if rejecting)")

class TransactionApprove(TransactionManualReviewAction):
    """ Schema for approving a transaction """
    pass # No extra fields needed, maybe optional notes

class TransactionReject(TransactionManualReviewAction):
    """ Schema for rejecting a transaction """
    reason: str = Field(..., description="Reason for rejection is mandatory")
