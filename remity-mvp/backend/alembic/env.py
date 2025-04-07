import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine # Import async engine

from alembic import context

# Add project root to sys.path to allow importing app modules
# Adjust the path ('..') if your alembic directory is nested differently
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Base from your models and settings
from app.db.base_class import Base
from app.core.config import settings # Import your application settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the database URL from settings
# This overrides the sqlalchemy.url from alembic.ini if DATABASE_URL is set in the environment
if settings.DATABASE_URL:
    # Ensure the URL is a string for Alembic
    config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
else:
    # Handle case where DATABASE_URL might not be set (optional, depends on requirements)
    print("Warning: DATABASE_URL environment variable not set. Alembic might use value from alembic.ini if available.")

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata # Use Base.metadata from your models

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Get URL from config (already set from settings above)
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise ValueError("Database URL not configured. Set DATABASE_URL environment variable or sqlalchemy.url in alembic.ini.")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# --- Async Support ---
import asyncio

async def run_migrations_online() -> None: # Make the function async
    """Run migrations in 'online' mode using an async engine."""

    # Get URL from config (already set from settings above)
    db_url = config.get_main_option("sqlalchemy.url")
    if not db_url:
        raise ValueError("Database URL not configured. Set DATABASE_URL environment variable or sqlalchemy.url in alembic.ini.")

    # Create async engine
    connectable = create_async_engine(
        db_url,
        poolclass=pool.NullPool, # Use NullPool for migration script
        # echo=True # Uncomment for debugging SQL
    )

    # Use async connection
    async with connectable.connect() as connection:
        # Pass the synchronous function to run_sync
        await connection.run_sync(do_run_migrations)

    # Dispose the engine after use
    await connectable.dispose()

def do_run_migrations(connection):
    """Helper function to run migrations within the async context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True, # Enable type comparison for better autogenerate
        # include_schemas=True, # Include schemas if using them
        # Render ENUM types correctly in migrations
        render_as_batch=True, # Recommended for SQLite, might be useful elsewhere
    )

    with context.begin_transaction():
        context.run_migrations()

# --- Main Execution Logic ---

if context.is_offline_mode():
    run_migrations_offline()
else:
    # Run the async online migration function
    asyncio.run(run_migrations_online())
