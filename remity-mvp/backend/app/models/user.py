import uuid
from sqlalchemy import String, Text, func, Enum as SQLAlchemyEnum
# Import foreign from sqlalchemy.orm
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import expression
from datetime import datetime
import enum
# Import TYPE_CHECKING and List
from typing import TYPE_CHECKING, List

from app.db.base_class import Base

# Import Transaction model only for type checking to avoid circular imports
if TYPE_CHECKING:
    from .transaction import Transaction
    from .recipient import Recipient
    from .audit_log import AuditLog


class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    phone_number: Mapped[str | None] = mapped_column(String(50), index=True)
    address: Mapped[str | None] = mapped_column(Text) # Consider structuring this (e.g., JSONB) if needed

    kyc_status: Mapped[KYCStatus] = mapped_column(
        SQLAlchemyEnum(KYCStatus, name="kyc_status_enum", create_type=True), # Use native PG Enum
        nullable=False,
        default=KYCStatus.PENDING,
        index=True
    )
    kyc_provider_reference: Mapped[str | None] = mapped_column(String(255)) # ID from Onfido/Veriff etc.

    is_active: Mapped[bool] = mapped_column(server_default=expression.true(), nullable=False) # For soft deletes or disabling accounts
    is_superuser: Mapped[bool] = mapped_column(server_default=expression.false(), nullable=False) # Admin flag

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    recipients: Mapped[list["Recipient"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    # Explicitly define foreign_keys to resolve ambiguity
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        foreign_keys="[Transaction.user_id]"  # Explicitly define the FK
    )
    # Add relationship for transactions reviewed by this user (if they are an admin)
    reviewed_transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="reviewer",
        foreign_keys="[Transaction.reviewed_by_user_id]"  # Explicitly define the FK
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', kyc_status='{self.kyc_status}')>"
