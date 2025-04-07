from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create the async engine
try:
    # Ensure the DATABASE_URL is correctly formatted (already handled in config.py)
    db_url = str(settings.DATABASE_URL)
    logger.info(f"Connecting to database: {db_url.replace(settings.POSTGRES_PASSWORD, '****')}") # Log URL without password
    engine = create_async_engine(
        db_url,
        pool_pre_ping=True, # Check connection before using from pool
        pool_recycle=3600, # Recycle connections every hour
        echo=settings.DEBUG, # Log SQL queries in debug mode
    )
except Exception as e:
    logger.error(f"Failed to create database engine: {e}", exc_info=True)
    raise

# Create a configured "AsyncSession" class
AsyncSessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # Keep objects accessible after commit
    autoflush=False, # Manual flush control
    autocommit=False # Manual commit control
)

async def get_db() -> AsyncSession:
    """
    FastAPI dependency that provides an async database session.
    Ensures the session is closed even if errors occur.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            # Optional: commit here if you want auto-commit behavior per request
            # await session.commit()
        except Exception:
            await session.rollback() # Rollback on error
            raise
        finally:
            await session.close() # Ensure session is closed

# Optional: Function to initialize DB (create tables) - Often handled by Alembic
# async def init_db():
#     async with engine.begin() as conn:
#         # Import Base here if needed
#         # from app.db.base_class import Base
#         # await conn.run_sync(Base.metadata.drop_all) # Use with caution
#         # await conn.run_sync(Base.metadata.create_all)
#     logger.info("Database tables initialized (if create_all was run).")
