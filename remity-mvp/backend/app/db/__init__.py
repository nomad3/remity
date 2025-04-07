# Import Base class
from .base_class import Base

# Import all models from app.models to ensure they are registered with Base.metadata
# This is crucial for Alembic auto-generation and Base.metadata.create_all
from app.models.user import User
from app.models.recipient import Recipient
from app.models.transaction import Transaction
from app.models.internal_ledger import InternalLedgerEntry
from app.models.audit_log import AuditLog

# Make session utilities available
from .session import engine, AsyncSessionFactory, get_db
