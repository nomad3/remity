import uuid
from sqlalchemy import String, func, ForeignKey, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, INET
from datetime import datetime
# Import Optional for type hinting
from typing import TYPE_CHECKING, Optional

from app.db.base_class import Base
if TYPE_CHECKING:
    from .user import User


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True) # Can be NULL for system actions

    action: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # Examples: LOGIN_SUCCESS, LOGIN_FAILURE, PASSWORD_RESET_REQUEST, TRANSACTION_CREATED,
    #           KYC_STATUS_UPDATED, USER_PROFILE_UPDATED, ADMIN_ACTION

    ip_address: Mapped[str | None] = mapped_column(INET) # Store IP address if available
    user_agent: Mapped[str | None] = mapped_column(Text) # Store User-Agent string
    details: Mapped[dict | None] = mapped_column(JSONB) # Store additional context (e.g., changed fields)

    timestamp: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, index=True
    )

    # Relationship
    # Correct type hint using Optional for the forward reference string
    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")

    def __repr__(self):
        user_info = f"user_id={self.user_id}" if self.user_id else "system"
        return f"<AuditLog(id={self.id}, {user_info}, action='{self.action}')>"
