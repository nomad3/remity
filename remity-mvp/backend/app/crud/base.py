from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import select, update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.db.base_class import Base

# Define TypeVars for generic CRUD operations
ModelType = TypeVar("ModelType", bound=Base) # The SQLAlchemy model type
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel) # Pydantic schema for creation
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel) # Pydantic schema for update

logger = logging.getLogger(__name__)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD base class with default methods to Create, Read, Update, Delete (CRUD).

    **Parameters**

    * `model`: A SQLAlchemy model class
    * `schema`: A Pydantic model (schema) class - Not directly used here but good for context
    """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """ Get a single record by ID. """
        try:
            statement = select(self.model).where(self.model.id == id)
            result = await db.execute(statement)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting {self.model.__name__} by id {id}: {e}", exc_info=True)
            # Depending on policy, you might raise a custom DB error or return None
            return None

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """ Get multiple records with pagination. """
        try:
            statement = select(self.model).offset(skip).limit(limit).order_by(self.model.id) # Default order by ID
            result = await db.execute(statement)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting multiple {self.model.__name__}: {e}", exc_info=True)
            return []

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """ Create a new record. """
        try:
            # Convert Pydantic schema to dict, excluding unset fields
            obj_in_data = obj_in.model_dump(exclude_unset=True)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with ID: {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error creating {self.model.__name__}: {e}", exc_info=True)
            # Raise a custom exception or return None/handle appropriately
            raise # Re-raise the error after logging and rollback

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """ Update an existing record. """
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                # Convert Pydantic schema to dict, excluding unset fields to avoid overwriting with None
                update_data = obj_in.model_dump(exclude_unset=True)

            if not update_data:
                # No fields to update
                return db_obj

            # Update the model object directly
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
                else:
                     logger.warning(f"Attempted to update non-existent field '{field}' on {self.model.__name__}")


            db.add(db_obj) # Add the modified object to the session
            await db.commit()
            await db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with ID: {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error updating {self.model.__name__} with ID {db_obj.id}: {e}", exc_info=True)
            raise

    async def remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """ Delete a record by ID. """
        try:
            obj = await self.get(db, id=id)
            if obj:
                await db.delete(obj)
                await db.commit()
                logger.info(f"Deleted {self.model.__name__} with ID: {id}")
                return obj
            else:
                logger.warning(f"Attempted to delete non-existent {self.model.__name__} with ID: {id}")
                return None
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error deleting {self.model.__name__} with ID {id}: {e}", exc_info=True)
            raise

    # Alternative remove using delete statement (potentially more efficient for bulk)
    # async def remove_by_id(self, db: AsyncSession, *, id: Any) -> int:
    #     """ Delete a record by ID using a delete statement. Returns number of rows deleted. """
    #     try:
    #         statement = sqlalchemy_delete(self.model).where(self.model.id == id)
    #         result = await db.execute(statement)
    #         await db.commit()
    #         deleted_count = result.rowcount
    #         if deleted_count > 0:
    #              logger.info(f"Deleted {deleted_count} {self.model.__name__}(s) with ID: {id}")
    #         else:
    #              logger.warning(f"Attempted to delete non-existent {self.model.__name__} with ID: {id}")
    #         return deleted_count
    #     except SQLAlchemyError as e:
    #         await db.rollback()
    #         logger.error(f"Database error deleting {self.model.__name__} with ID {id}: {e}", exc_info=True)
    #         raise
