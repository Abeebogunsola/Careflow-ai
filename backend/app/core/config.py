"""
Centralized Configuration Module for CareFlow AI Backend.

Uses Pydantic Settings to load and validate environment variables.
Follows the security guidelines in docs/safety-privacy.md.
"""

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Metadata
    PROJECT_NAME: str = "CareFlow AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "CareFlow AI — HIV Care Retention & Support Platform API"
    API_V1_STR: str = "/api/v1"

    # Runtime Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security Configuration
    # Placeholder for development; must be overridden by environment variable in production.
    SECRET_KEY: str = "insecure-dev-secret-key-change-in-production"

    # Allowed CORS Origins
    # Development defaults to standard local frontend development ports.
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Database Configuration (PostgreSQL)
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/careflow_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # AI Agent and LLM Configuration (Phase 7)
    # Supported providers: "mock", "openai", "groq", "custom"
    LLM_PROVIDER: str = "mock"
    LLM_API_KEY: Union[str, None] = None
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_BASE_URL: Union[str, None] = None
    LLM_TEMPERATURE: float = 0.0
    LLM_TIMEOUT_SECONDS: int = 15
    EMERGENCY_CONTACT_INSTRUCTIONS: str = (
        "If you are experiencing a medical emergency, please call your local emergency "
        "services (911/112) or go to the nearest emergency center immediately. "
        "Our clinic staff has also been notified."
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError("Invalid format for CORS_ORIGINS")

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_production(cls, v: List[str], info) -> List[str]:
        # Enforce docs/safety-privacy.md: never allow wildcard CORS in production
        env = info.data.get("ENVIRONMENT", "development")
        if env == "production" and "*" in v:
            raise ValueError(
                "Wildcard CORS '*' is prohibited in production per docs/safety-privacy.md"
            )
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Global settings singleton
settings = Settings()
