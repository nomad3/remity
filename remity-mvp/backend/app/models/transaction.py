import uuid
import enum
from sqlalchemy import String, func, ForeignKey, Text, Numeric, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
from decimal import Decimal
# Import Optional for type hinting
from typing import TYPE_CHECKING, Optional

from app.db.base_class import Base
if TYPE_CHECKING:
    from .user import User
    from .recipient import Recipient
    from .internal_ledger import InternalLedgerEntry


class TransactionStatus(str, enum.Enum):
    QUOTE_CREATED = "quote_created"
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_RECEIVED = "payment_received"
    PENDING_APPROVAL = "pending_approval" # New: Waiting for operator approval
    PROCESSING = "processing" # Renamed: Approved, starting internal/crypto leg
    PAYOUT_INITIATED = "payout_initiated"
    PAYOUT_COMPLETED = "payout_completed" # Confirmed by provider, might not be final delivery
    DELIVERED = "delivered" # Final confirmation if available
    FAILED = "failed"
    CANCELLED = "cancelled" # User cancelled before payment/approval
    MANUALLY_REJECTED = "manually_rejected" # New: Operator rejected
    REFUNDED = "refunded"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    recipient_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("recipients.id"), index=True, nullable=False)

    status: Mapped[TransactionStatus] = mapped_column(
        SQLAlchemyEnum(TransactionStatus, name="transaction_status_enum", create_type=True),
        nullable=False,
        default=TransactionStatus.QUOTE_CREATED,
        index=True
    )

    source_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True) # e.g., USD
    target_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True) # e.g., MXN

    # Use Numeric for precise monetary values
    source_amount: Mapped[Decimal] = mapped_column(Numeric(19, 8), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(19, 8), nullable=False)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(19, 8), nullable=False) # Source Fiat / Target Fiat
    remity_fee: Mapped[Decimal] = mapped_column(Numeric(19, 8), nullable=False, default=0)
    payment_provider_fee: Mapped[Decimal] = mapped_column(Numeric(19, 8), nullable=False, default=0) # On-ramp fee

    estimated_delivery_time: Mapped[str | None] = mapped_column(String(100)) # e.g., "1-2 hours"

    # References to external systems
    onramp_payment_intent_id: Mapped[str | None] = mapped_column(String(255), index=True) # Stripe Payment Intent ID
    onramp_payment_status: Mapped[str | None] = mapped_column(String(50)) # Status from Stripe webhook
    offramp_payout_reference: Mapped[str | None] = mapped_column(String(255), index=True) # ID from Off-ramp provider
    offramp_payout_status: Mapped[str | None] = mapped_column(String(50)) # Status from Off-ramp webhook

    failure_reason: Mapped[str | None] = mapped_column(Text) # Details if status is FAILED or MANUALLY_REJECTED

    # Fields for manual approval/rejection
    reviewed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True) # FK to the admin user who reviewed
    reviewed_at: Mapped[datetime | None] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    # Explicitly define foreign_keys for relationships back to User
    user: Mapped["User"] = relationship(
        back_populates="transactions",
        foreign_keys=[user_id] # Keep using column object here for back_populates side
    )
    recipient: Mapped["Recipient"] = relationship(back_populates="transactions")
    ledger_entries: Mapped[list["InternalLedgerEntry"]] = relationship(back_populates="transaction")
    reviewer: Mapped[Optional["User"]] = relationship(
        back_populates="reviewed_transactions", # Add back_populates
        foreign_keys=[reviewed_by_user_id] # Keep using column object here for back_populates side
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, status='{self.status}', {self.source_currency}->{self.target_currency})>"
