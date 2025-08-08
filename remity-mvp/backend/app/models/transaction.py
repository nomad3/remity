from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("recipients.id"), nullable=False)

    # Transaction details
    amount = Column(Numeric(10, 2), nullable=False)
    currency_from = Column(String(3), nullable=False)  # USD, EUR, etc.
    currency_to = Column(String(3), nullable=False)
    exchange_rate = Column(Numeric(10, 6), nullable=False)
    fee_amount = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)

    # Status and tracking
    status = Column(String(20), default="pending")  # pending, approved, completed, cancelled
    tracking_number = Column(String(50), unique=True, index=True)

    # Payment method
    payment_method = Column(String(50), nullable=False)  # bank_transfer, credit_card, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    recipient = relationship("Recipient", back_populates="transactions")

    # Additional fields for compliance
    purpose = Column(String(200), nullable=True)
    source_of_funds = Column(String(100), nullable=True)
    compliance_notes = Column(Text, nullable=True)
    proof_of_payment_url = Column(String(255), nullable=True)
