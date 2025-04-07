from fastapi import APIRouter

# Import endpoint routers here as they are created
from .endpoints import auth
from .endpoints import users
from .endpoints import recipients
from .endpoints import transactions
from .endpoints import admin # Import the admin router
# from .endpoints import kyc, webhooks

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(recipients.router, prefix="/recipients", tags=["Recipients"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"]) # Add admin routes
# api_router.include_router(kyc.router, prefix="/kyc", tags=["KYC"])
# api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

# Add more routers as needed
