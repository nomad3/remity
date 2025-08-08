from typing import Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.recipient import Recipient
from app.schemas.recipient import RecipientCreate, RecipientUpdate

class CRUDRecipient(CRUDBase[Recipient, RecipientCreate, RecipientUpdate]):
    def get_user_recipient(self, db: Session, *, user_id: int, recipient_id: int) -> Optional[Recipient]:
        return db.query(Recipient).filter(Recipient.id == recipient_id, Recipient.user_id == user_id).first()

    def create_with_owner(self, db: Session, *, user_id: int, obj_in: RecipientCreate) -> Recipient:
        db_obj = Recipient(user_id=user_id, **obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Recipient, obj_in: Union[RecipientUpdate, Dict[str, Any]]):
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

recipient = CRUDRecipient(Recipient)
