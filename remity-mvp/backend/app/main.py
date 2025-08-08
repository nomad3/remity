from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db import base  # noqa: F401
from sqlalchemy import text
import os
from app import models, crud
from app.core.security import get_password_hash
from sqlalchemy.orm import Session
from decimal import Decimal

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Create tables if not exist
base.Base.metadata.create_all(bind=engine)

# Safe migration for new columns
with engine.begin() as conn:
    try:
        conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS proof_of_payment_url VARCHAR(255)"))
    except Exception:
        pass

# Optional seed data for demos
def seed_data(db: Session) -> None:
    # Users
    def ensure_user(email: str, full_name: str, is_superuser: bool) -> models.User:
        u = db.query(models.User).filter(models.User.email == email).first()
        if u:
            return u
        u = models.User(
            email=email,
            full_name=full_name,
            is_superuser=is_superuser,
            hashed_password=get_password_hash("Test12345!"),
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        return u

    admin = ensure_user("admin@remity.io", "Admin User", True)
    operator = ensure_user("operator@remity.io", "Operator User", True)
    user = ensure_user("user@remity.io", "Demo User", False)

    # Recipients for demo user
    def ensure_recipient(owner: models.User, name: str, email: str) -> models.Recipient:
        rcpt = (
            db.query(models.Recipient)
            .filter(models.Recipient.user_id == owner.id, models.Recipient.full_name == name)
            .first()
        )
        if rcpt:
            return rcpt
        rcpt = models.Recipient(
            user_id=owner.id,
            full_name=name,
            email=email,
            country="US",
            bank_name="Demo Bank",
            account_number="1234567890",
        )
        db.add(rcpt)
        db.commit()
        db.refresh(rcpt)
        return rcpt

    r1 = ensure_recipient(user, "Alice Receiver", "alice@example.com")
    r2 = ensure_recipient(user, "Bob Recipient", "bob@example.com")

    # Transactions
    def ensure_tx(u: models.User, rcpt: models.Recipient, amount: Decimal, status: str):
        # create a tx if not exists with same amount/status
        existing = (
            db.query(models.Transaction)
            .filter(
                models.Transaction.user_id == u.id,
                models.Transaction.recipient_id == rcpt.id,
                models.Transaction.amount == amount,
                models.Transaction.status == status,
            )
            .first()
        )
        if existing:
            return existing
        tx = models.Transaction(
            user_id=u.id,
            recipient_id=rcpt.id,
            amount=amount,
            currency_from="USD",
            currency_to="EUR",
            exchange_rate=Decimal("0.90"),
            fee_amount=Decimal("2.50"),
            total_amount=amount + Decimal("2.50"),
            status=status,
            payment_method="bank_transfer",
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx

    ensure_tx(user, r1, Decimal("100.00"), "pending")
    ensure_tx(user, r2, Decimal("250.00"), "in_progress")
    ensure_tx(user, r1, Decimal("500.00"), "completed")

if os.getenv("ENABLE_SEED", "false").lower() == "true":
    try:
        db = SessionLocal()
        seed_data(db)
    finally:
        db.close()

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origin_regex=r".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
