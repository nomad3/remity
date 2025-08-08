from typing import Optional
from datetime import datetime
from pydantic import BaseModel, AnyUrl, ConfigDict
from .user import User as UserSchema
from .recipient import Recipient as RecipientSchema

class TransactionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recipient_id: int
    amount: float
    currency_from: str
    currency_to: str
    exchange_rate: float
    fee_amount: float
    total_amount: float
    payment_method: str
    purpose: Optional[str] = None
    source_of_funds: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: Optional[str] = None
    compliance_notes: Optional[str] = None
    proof_of_payment_url: Optional[AnyUrl] = None

class TransactionInDBBase(TransactionBase):
    id: int
    user_id: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Transaction(TransactionInDBBase):
    pass

class TransactionWithRelations(TransactionInDBBase):
    user: Optional[UserSchema] = None
    recipient: Optional[RecipientSchema] = None
