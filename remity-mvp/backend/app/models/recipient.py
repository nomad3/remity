from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Personal information
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    # Address information
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=False)

    # Bank information
    bank_name = Column(String(200), nullable=True)
    account_number = Column(String(100), nullable=True)
    routing_number = Column(String(50), nullable=True)  # For US banks
    swift_code = Column(String(50), nullable=True)  # For international transfers
    iban = Column(String(50), nullable=True)  # For European banks

    # Additional bank details
    account_type = Column(String(50), nullable=True)  # savings, checking, etc.
    bank_branch = Column(String(200), nullable=True)

    # Status and preferences
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    preferred_payment_method = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="recipients")
    transactions = relationship("Transaction", back_populates="recipient")

    # Additional fields
    notes = Column(Text, nullable=True)
    verification_document = Column(String(255), nullable=True)
