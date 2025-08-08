import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Remity"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "remity")
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

    # CORS
    # Allow override via env var BACKEND_CORS_ORIGINS (comma-separated)
    _cors_env = os.getenv("BACKEND_CORS_ORIGINS")
    if _cors_env:
        BACKEND_CORS_ORIGINS: List[str] = [o.strip() for o in _cors_env.split(",") if o.strip()]
    else:
        BACKEND_CORS_ORIGINS: List[str] = [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8080",
            "https://remity.io",
            "https://www.remity.io",
        ]

    class Config:
        case_sensitive = True

settings = Settings()
