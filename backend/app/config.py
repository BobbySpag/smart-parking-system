"""Application configuration using Pydantic BaseSettings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/smart_parking"
    SECRET_KEY: str = "changeme-use-a-real-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = False
    APP_NAME: str = "Smart Parking System"
    APP_VERSION: str = "1.0.0"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
