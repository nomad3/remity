import asyncio
import logging
import argparse # For command-line arguments

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Need to import DB session, CRUD, schemas etc.
# Ensure pythonpath allows finding 'app'
try:
    from app.db.session import AsyncSessionFactory
    from app import crud, schemas, models
    from app.core.config import settings # Needed for DB connection setup implicitly
except ImportError as e:
     logger.error(f"Import error: {e}. Ensure script is run with correct PYTHONPATH.")
     logger.error("Try running from the 'backend' directory using: python -m app.initial_data ...")
     exit(1)


async def create_superuser(email: str, password: str):
    """ Creates or updates a user to be a superuser. """
    logger.info(f"Attempting to create/update superuser: {email}")

    # Use the session factory directly for a single operation
    async with AsyncSessionFactory() as db:
        try:
            user = await crud.user.get_by_email(db=db, email=email)

            if user:
                if not user.is_superuser:
                    logger.info(f"User {email} already exists. Updating to superuser.")
                    user.is_superuser = True
                    db.add(user)
                    await db.commit()
                    logger.info(f"User {email} successfully updated to superuser.")
                else:
                    logger.info(f"User {email} already exists and is already a superuser.")
            else:
                logger.info(f"User {email} not found. Creating new superuser.")
                user_in = schemas.UserCreate(email=email, password=password)
                # Create user first (hashes password)
                new_user = await crud.user.create(db=db, obj_in=user_in) # create handles commit/refresh
                # Now update the newly created user to be superuser
                # Need a separate commit for the update after creation
                logger.info(f"Setting is_superuser=True for new user {email}")
                new_user.is_superuser = True
                db.add(new_user)
                await db.commit()
                logger.info(f"Superuser {email} created successfully.")

        except Exception as e:
            await db.rollback() # Ensure rollback on error
            logger.error(f"Error creating/updating superuser {email}: {e}", exc_info=True)
            raise # Re-raise after logging


async def main():
    parser = argparse.ArgumentParser(description="Create initial superuser for Remity.")
    parser.add_argument("--email", type=str, required=True, help="Email address for the superuser.")
    parser.add_argument("--password", type=str, required=True, help="Password for the superuser.")
    args = parser.parse_args()

    # Basic password validation (optional, enhance as needed)
    if len(args.password) < 8:
        logger.error("Password must be at least 8 characters long.")
        return

    await create_superuser(email=args.email, password=args.password)


if __name__ == "__main__":
    logger.info("Starting initial data script...")
    # Ensure DB is ready (optional, entrypoint should handle this usually)
    # Add a small delay maybe? time.sleep(5)
    asyncio.run(main())
    logger.info("Initial data script finished.")
