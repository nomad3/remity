from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

# Assuming you will create these modules later
# from app.api.v1 import api_router # Import the main API router
# from app.core.logging_config import setup_logging # Import custom logging setup
from app.core.config import settings
# from app.db.session import engine, init_db # For DB initialization if needed
# from app.core.security import get_current_active_user # Example dependency

# --- Basic Logging Setup (Replace/Enhance with setup_logging later) ---
log_level = logging.DEBUG if settings.DEBUG else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
# --- End Basic Logging Setup ---

# --- Lifespan Management (for startup/shutdown events) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info(f"Starting Remity API - Environment: {settings.ENVIRONMENT}")
    logger.info(f"CORS Origins: {settings.BACKEND_CORS_ORIGINS}")
    # Example: Initialize DB if needed
    # await init_db()
    # Example: Connect to Redis pool
    # app.state.redis = await create_redis_pool(settings.REDIS_URL)
    # Example: Initialize Stripe client
    # import stripe
    # stripe.api_key = settings.STRIPE_SECRET_KEY
    # logger.info("Stripe client initialized.")

    yield # Application runs here

    # Shutdown logic
    logger.info("Shutting down Remity API...")
    # Example: Close Redis pool
    # if hasattr(app.state, 'redis') and app.state.redis:
    #     await app.state.redis.close()
    # Example: Dispose DB engine
    # await engine.dispose()
# --- End Lifespan Management ---


# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.ENVIRONMENT != "production" else None,
    version="0.1.0",
    lifespan=lifespan # Use the lifespan context manager
)

# --- Middlewares ---

# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip('/') for origin in settings.BACKEND_CORS_ORIGINS], # Ensure no trailing slash
        allow_credentials=True,
        allow_methods=["*"], # Allow all standard methods
        allow_headers=["*"], # Allow all standard headers (customize if needed for security)
    )
else:
    # Allow all origins in development if not specified (use with caution)
    if settings.ENVIRONMENT == "development":
        logger.warning("No CORS origins specified, allowing all origins in development mode.")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

# Basic Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Request: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.2f}ms"
    )
    # Add security headers (can be moved to a dedicated middleware or handled by proxy/LB)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    # response.headers["Content-Security-Policy"] = "default-src 'self'" # Basic CSP
    if settings.ENVIRONMENT == "production":
         response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# --- Exception Handlers ---

# Handle Pydantic Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log the detailed error for debugging
    logger.warning(f"Validation error for {request.method} {request.url.path}: {exc.errors()}")
    # Return a user-friendly error response
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": exc.errors()}, # Provide structured errors
    )

# Generic Exception Handler (Catch-all)
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )

# --- API Routers ---
from app.api.v1 import api_router # Import the main API router

app.include_router(api_router, prefix=settings.API_V1_STR)

# --- Root Endpoint ---
@app.get("/", tags=["Default"])
async def read_root():
    """ Basic health check endpoint """
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}!"}

# Example Protected Endpoint (Uncomment when auth is ready)
# @app.get("/users/me", tags=["Users"])
# async def read_users_me(current_user: dict = Depends(get_current_active_user)):
#     """ Example of a protected route """
#     return current_user

# --- Main execution (for running directly with uvicorn, useful for debugging) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
