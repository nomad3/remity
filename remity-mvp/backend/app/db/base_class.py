from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from typing import Any

# Recommended naming convention for constraints for Alembic compatibility
# See: https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

class Base(DeclarativeBase):
    """ Base class for SQLAlchemy models. """
    metadata = metadata
    # You can define common columns or methods here if needed
    # e.g., id: Any
    #       created_at: Any
    #       updated_at: Any
    pass
