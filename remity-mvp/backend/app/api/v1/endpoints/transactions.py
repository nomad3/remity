from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app import crud, models, schemas
from app.api import dependencies

router = APIRouter()

@router.get("/", response_model=List[schemas.Transaction])
def list_transactions(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == current_user.id)
        .order_by(models.Transaction.id.desc())
        .all()
    )

@router.get("/admin", response_model=List[schemas.TransactionWithRelations])
def list_transactions_admin(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
):
    return (
        db.query(models.Transaction)
        .options(joinedload(models.Transaction.user), joinedload(models.Transaction.recipient))
        .order_by(models.Transaction.id.desc())
        .all()
    )

@router.post("/", response_model=schemas.Transaction)
def create_transaction(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    tx_in: schemas.TransactionCreate,
):
    # Validate recipient ownership
    rcpt = db.query(models.Recipient).filter(models.Recipient.id == tx_in.recipient_id, models.Recipient.user_id == current_user.id).first()
    if not rcpt:
        raise HTTPException(status_code=400, detail="Invalid recipient")
    return crud.transaction.create_with_owner(db, user_id=current_user.id, obj_in=tx_in)

@router.patch("/{tx_id}", response_model=schemas.Transaction)
def update_transaction(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    tx_id: int,
    tx_in: schemas.TransactionUpdate,
):
    q = db.query(models.Transaction).filter(models.Transaction.id == tx_id)
    if not current_user.is_superuser:
        q = q.filter(models.Transaction.user_id == current_user.id)
    tx = q.first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    updated = crud.transaction.update(db, db_obj=tx, obj_in=tx_in)
    # Set completed timestamp if status becomes completed
    if tx_in.status and tx_in.status.lower() == "completed" and not updated.completed_at:
        updated.completed_at = datetime.now(timezone.utc)
        db.add(updated)
        db.commit()
        db.refresh(updated)
    return updated

@router.patch("/{tx_id}/admin", response_model=schemas.Transaction)
def update_transaction_admin(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
    tx_id: int,
    tx_in: schemas.TransactionUpdate,
):
    tx = db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    updated = crud.transaction.update(db, db_obj=tx, obj_in=tx_in)
    if tx_in.status and tx_in.status.lower() == "completed" and not updated.completed_at:
        updated.completed_at = datetime.now(timezone.utc)
        db.add(updated)
        db.commit()
        db.refresh(updated)
    return updated
