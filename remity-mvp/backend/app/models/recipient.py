import uuid
from sqlalchemy import String, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from datetime import datetime

from app.db.base_class import Base
# Import User relationship type hint safely
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
    from .transaction import Transaction


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), index=True, nullable=False) # ISO 3166-1 alpha-2
    payout_method: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., "spei_clabe", "gcash_mobile"
    # Store sensitive payout details securely, consider encryption at application level if needed
    # JSONB is flexible but requires careful validation in the application layer
    payout_details: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Example payout_details:
    # {"clabe": "...", "bank_name": "..."}
    # {"mobile_number": "..."}

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="recipients")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="recipient")

    def __repr__(self):
        return f"<Recipient(id={self.id}, user_id={self.user_id}, country='{self.country_code}')>"
