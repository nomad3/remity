from typing import Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate

class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    def create_with_owner(self, db: Session, *, user_id: int, obj_in: TransactionCreate) -> Transaction:
        db_obj = Transaction(user_id=user_id, **obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Transaction, obj_in: Union[TransactionUpdate, Dict[str, Any]]):
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

transaction = CRUDTransaction(Transaction)
