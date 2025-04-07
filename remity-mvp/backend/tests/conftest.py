import pytest
import pytest_asyncio # Use pytest_asyncio for async fixtures
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
import logging
import asyncio # Needed for event loop management

# Import Base from your models to create/drop tables
from app.db.base_class import Base
# Import your FastAPI app instance
from app.main import app
# Import session getter override
from app.api.dependencies import get_db
from app.core.config import settings

# Ensure test environment uses a separate database if possible
# Modify DATABASE_URL for testing (e.g., append '_test')
# IMPORTANT: This assumes DATABASE_URL is correctly set in the test environment
# You might need to load a specific .env.test file or set env vars
TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"
logger = logging.getLogger(__name__)
logger.info(f"Using test database: {TEST_DATABASE_URL}")

# Create async engine for tests
engine = create_async_engine(TEST_DATABASE_URL, echo=False) # echo=False for cleaner test output

# Create async session factory for tests
TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """ Create an instance of the default event loop for the session. """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def _engine():
    """ Yield the test engine. """
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(_engine):
    """ Setup the test database: create tables before tests, drop after. """
    async with _engine.begin() as conn:
        logger.info("Dropping all tables in test database...")
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Creating all tables in test database...")
        await conn.run_sync(Base.metadata.create_all)
    yield # Run tests
    # Teardown is handled by engine disposal in _engine fixture

@pytest_asyncio.fixture(scope="function")
async def db(_engine) -> AsyncSession:
    """
    Provides a database session for each test function.
    Rolls back transactions after each test.
    """
    connection = await _engine.connect()
    transaction = await connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session # Provide the session to the test

    # Rollback transaction and close session/connection
    await session.close()
    if transaction.is_active:
        await transaction.rollback()
    await connection.close()


# Fixture for overriding the get_db dependency in API tests
async def override_get_db():
    """ Dependency override for yielding test DB session. """
    async with TestingSessionLocal() as session:
        yield session

# Apply the override for the duration of tests that use the client
# app.dependency_overrides[get_db] = override_get_db # Apply globally if needed, or per test module/function

@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncClient:
    """
    Provides an HTTPX AsyncClient for making requests to the test app.
    Overrides the database dependency.
    """
    # Override the dependency for this client instance
    app.dependency_overrides[get_db] = lambda: db

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()
