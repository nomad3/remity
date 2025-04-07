from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker # Requires 'pip install Faker' in test environment
import logging

# Import models using absolute path from root for consistency in tests
from app import crud, models, schemas
from app.core.config import settings

fake = Faker()
logger = logging.getLogger(__name__)

async def create_random_user(db: AsyncSession) -> models.User:
    """ Creates a random user in the database for testing. """
    email = fake.email()
    password = fake.password(length=12)
    user_in = schemas.UserCreate(email=email, password=password, full_name=fake.name())
    logger.debug(f"Creating test user with email: {email}")
    # Ensure crud.user is correctly imported and refers to the instantiated CRUDUser object
    user = await crud.user.create(db=db, obj_in=user_in)
    return user

def random_email() -> str:
    return fake.email()

def random_lower_string(length: int = 12) -> str:
    return fake.password(length=length)
