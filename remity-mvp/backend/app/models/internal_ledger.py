import uuid # Import the uuid module
from sqlalchemy import String, func, ForeignKey, Text, Numeric, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
from decimal import Decimal
# Import Optional for type hinting
from typing import TYPE_CHECKING, Optional

from app.db.base_class import Base
if TYPE_CHECKING:
    from .transaction import Transaction


class InternalLedgerEntry(Base):
    __tablename__ = "internal_ledger"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True) # Use BigInteger for potentially large number of entries
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("transactions.id"), index=True) # Can be NULL for non-transaction events

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Examples: FIAT_DEPOSIT_CONFIRMED, CRYPTO_PURCHASE_SIMULATED, CRYPTO_TRANSFER_SIMULATED,
    #           FIAT_PAYOUT_INITIATED, FEE_COLLECTED, REFUND_PROCESSED

    currency: Mapped[str] = mapped_column(String(10), nullable=False) # e.g., USD, EUR, USDC, MXN, PHP
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 8), nullable=False) # Positive for credit, negative for debit (relative to Remity's internal view)
    description: Mapped[str | None] = mapped_column(Text)

    timestamp: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, index=True
    )

    # Relationship
    # Correct type hint using Optional for the forward reference string
    transaction: Mapped[Optional["Transaction"]] = relationship(back_populates="ledger_entries")

    def __repr__(self):
        return f"<InternalLedgerEntry(id={self.id}, event='{self.event_type}', amount={self.amount} {self.currency})>"
