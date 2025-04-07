import os
from typing import List, Union, Optional
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

class Settings(BaseSettings):
    # Core Application Settings
    PROJECT_NAME: str = "Remity.io Backend"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development" # development, staging, production
    DEBUG: bool = False

    # Database (PostgreSQL)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            port=str(values.data.get("POSTGRES_PORT")),
            path=f"/{values.data.get('POSTGRES_DB') or ''}",
        )

    # Redis Cache
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[RedisDsn] = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: Optional[str], values) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme="redis",
            host=values.data.get("REDIS_HOST"),
            port=str(values.data.get("REDIS_PORT")),
            path=f"/{values.data.get('REDIS_DB') or 0}",
        )

    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [] # e.g., ["http://localhost:3000", "https://remity.io"]

    # External API Keys & Secrets (Load from environment)
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    KYC_PROVIDER_API_KEY: Optional[str] = None
    KYC_PROVIDER_WEBHOOK_SECRET: Optional[str] = None
    OFFRAMP_PROVIDER_API_KEY: Optional[str] = None
    OFFRAMP_PROVIDER_WEBHOOK_SECRET: Optional[str] = None

    # Email Settings (Optional, for verification/notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # GCP Settings (for production secrets)
    GCP_PROJECT_ID: Optional[str] = None

    # Define model config to use .env file
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()

# Example usage: print(settings.DATABASE_URL)
