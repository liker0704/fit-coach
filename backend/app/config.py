"""Application configuration."""

import secrets
from typing import List, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FitCoach"
    VERSION: str = "0.1.0"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production-please-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:1420",  # Tauri dev server
        "tauri://localhost",
        "http://tauri.localhost",
        "https://tauri.localhost",
    ]

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "fitcoach"
    POSTGRES_PASSWORD: str = "fitcoachpass"
    POSTGRES_DB: str = "fitcoach"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        """Assemble database URL from components."""
        if isinstance(v, str):
            return v
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=info.data.get("POSTGRES_USER"),
                password=info.data.get("POSTGRES_PASSWORD"),
                host=info.data.get("POSTGRES_SERVER"),
                port=info.data.get("POSTGRES_PORT"),
                path=f"{info.data.get('POSTGRES_DB') or ''}",
            )
        )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # LLM Configuration
    LLM_PROVIDER: str = "gemini"
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "gemini-2.0-flash-exp"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 500

    @field_validator("LLM_MODEL_NAME", mode="before")
    @classmethod
    def set_default_model_name(cls, v: Optional[str], info) -> str:
        """Set default model name based on provider if not specified."""
        if v:
            return v
        provider = info.data.get("LLM_PROVIDER", "openai").lower()
        if provider == "openai":
            return "gpt-3.5-turbo"
        elif provider == "gemini":
            return "gemini-2.0-flash-exp"
        return "gpt-3.5-turbo"

    # Vision Agent Settings (for meal photo recognition)
    VISION_PROVIDER: str = "gemini"  # "openai" or "gemini"
    VISION_MODEL: str = "gpt-4-turbo"  # For OpenAI: gpt-4-turbo, gpt-4o
    GEMINI_VISION_MODEL: str = "gemini-2.0-flash-exp"  # For Gemini: gemini-2.0-flash-exp, gemini-1.5-flash, gemini-1.5-pro
    VISION_MAX_TOKENS: int = 500

    # Web Search Settings (for nutrition data lookup)
    TAVILY_API_KEY: Optional[str] = None
    ENABLE_WEB_SEARCH: bool = True

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Meal Photos Storage
    MEAL_PHOTOS_DIR: str = "uploads/meal_photos"
    MAX_PHOTO_SIZE_MB: int = 10


settings = Settings()
