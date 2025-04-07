import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app import crud, schemas, models
from app.core.security import verify_password
from tests.utils.user import random_email, random_lower_string

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

async def test_create_user(db: AsyncSession) -> None:
    """ Test creating a new user. """
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(email=email, password=password)
    user = await crud.user.create(db=db, obj_in=user_in)

    assert user.email == email
    assert hasattr(user, "hashed_password")
    assert verify_password(password, user.hashed_password)
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.kyc_status == models.KYCStatus.PENDING # Check default KYC status

async def test_get_user_by_email(db: AsyncSession) -> None:
    """ Test retrieving a user by email. """
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(email=email, password=password)
    await crud.user.create(db=db, obj_in=user_in)

    user = await crud.user.get_by_email(db=db, email=email)
    assert user
    assert user.email == email

async def test_get_user_by_email_not_found(db: AsyncSession) -> None:
    """ Test retrieving a non-existent user by email. """
    email = random_email()
    user = await crud.user.get_by_email(db=db, email=email)
    assert user is None

async def test_authenticate_user(db: AsyncSession) -> None:
    """ Test authenticating a user. """
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(email=email, password=password)
    await crud.user.create(db=db, obj_in=user_in)

    authenticated_user = await crud.user.authenticate(db=db, email=email, password=password)
    assert authenticated_user
    assert authenticated_user.email == email

async def test_authenticate_user_wrong_password(db: AsyncSession) -> None:
    """ Test authentication with wrong password. """
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(email=email, password=password)
    await crud.user.create(db=db, obj_in=user_in)

    authenticated_user = await crud.user.authenticate(db=db, email=email, password="wrongpassword")
    assert authenticated_user is None

async def test_authenticate_user_not_found(db: AsyncSession) -> None:
    """ Test authentication for a non-existent user. """
    email = random_email()
    password = random_lower_string()

    authenticated_user = await crud.user.authenticate(db=db, email=email, password=password)
    assert authenticated_user is None

async def test_update_user(db: AsyncSession) -> None:
    """ Test updating a user's information (excluding password). """
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(email=email, password=password, full_name="Initial Name")
    user = await crud.user.create(db=db, obj_in=user_in)

    new_full_name = "Updated Name"
    user_update = schemas.UserUpdate(full_name=new_full_name)
    updated_user = await crud.user.update(db=db, db_obj=user, obj_in=user_update)

    assert updated_user.id == user.id
    assert updated_user.email == email # Email not changed
    assert updated_user.full_name == new_full_name
    assert verify_password(password, updated_user.hashed_password) # Password unchanged

async def test_update_user_password(db: AsyncSession) -> None:
    """ Test updating a user's password. """
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(email=email, password=password)
    user = await crud.user.create(db=db, obj_in=user_in)

    new_password = random_lower_string(length=16)
    user_update = schemas.UserUpdate(password=new_password)
    updated_user = await crud.user.update(db=db, db_obj=user, obj_in=user_update)

    assert updated_user.id == user.id
    assert updated_user.email == email
    assert verify_password(new_password, updated_user.hashed_password)
    assert not verify_password(password, updated_user.hashed_password) # Old password should fail

async def test_check_if_user_is_active(db: AsyncSession) -> None:
    """ Test the is_active check. """
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(email=email, password=password)
    user = await crud.user.create(db=db, obj_in=user_in)
    assert crud.user.is_active(user) is True

    # Manually set is_active to False (simulate deactivation)
    user.is_active = False
    db.add(user)
    await db.commit()
    await db.refresh(user)
    assert crud.user.is_active(user) is False

async def test_check_if_user_is_superuser(db: AsyncSession) -> None:
    """ Test the is_superuser check. """
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(email=email, password=password)
    user = await crud.user.create(db=db, obj_in=user_in)
    assert crud.user.is_superuser(user) is False

    # Manually set is_superuser to True
    user.is_superuser = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    assert crud.user.is_superuser(user) is True
