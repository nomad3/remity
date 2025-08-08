from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import dependencies

router = APIRouter()

@router.get("/", response_model=List[schemas.Recipient])
def list_recipients(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    return db.query(models.Recipient).filter(models.Recipient.user_id == current_user.id).all()

@router.post("/", response_model=schemas.Recipient)
def create_recipient(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    recipient_in: schemas.RecipientCreate,
):
    return crud.recipient.create_with_owner(db, user_id=current_user.id, obj_in=recipient_in)

@router.patch("/{recipient_id}", response_model=schemas.Recipient)
def update_recipient(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    recipient_id: int,
    recipient_in: schemas.RecipientUpdate,
):
    db_obj = crud.recipient.get_user_recipient(db, user_id=current_user.id, recipient_id=recipient_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return crud.recipient.update(db, db_obj=db_obj, obj_in=recipient_in)

@router.delete("/{recipient_id}")
def delete_recipient(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    recipient_id: int,
):
    db_obj = crud.recipient.get_user_recipient(db, user_id=current_user.id, recipient_id=recipient_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Recipient not found")
    db.delete(db_obj)
    db.commit()
    return {"ok": True}
