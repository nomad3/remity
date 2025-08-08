from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, recipients, transactions

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(recipients.router, prefix="/recipients", tags=["recipients"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
