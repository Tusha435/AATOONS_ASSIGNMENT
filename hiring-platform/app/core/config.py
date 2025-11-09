"""
Core configuration settings for the Proof-of-Work Hiring Platform.

This module centralizes all configuration management using Pydantic settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via .env file or environment variables.
    """

    # ========================================================================
    # DATABASE
    # ========================================================================
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/hiring_platform",
        description="PostgreSQL database URL"
    )

    # ========================================================================
    # REDIS
    # ========================================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for caching and background jobs"
    )

    # ========================================================================
    # API KEYS
    # ========================================================================
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key for AI code analysis"
    )

    GITHUB_TOKEN: Optional[str] = Field(
        default=None,
        description="GitHub personal access token for repo analysis"
    )

    # ========================================================================
    # SECURITY
    # ========================================================================
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )

    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT token expiry in minutes"
    )

    # ========================================================================
    # APPLICATION
    # ========================================================================
    APP_NAME: str = Field(
        default="Proof-of-Work Hiring Platform",
        description="Application name"
    )

    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )

    ENVIRONMENT: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )

    SQL_ECHO: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )

    API_URL: str = Field(
        default="http://localhost:8000",
        description="API base URL"
    )

    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for CORS"
    )

    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================
    ENABLE_AI_INTERVIEW: bool = Field(
        default=True,
        description="Enable AI interview bot feature"
    )

    ENABLE_COMMIT_ANALYSIS: bool = Field(
        default=True,
        description="Enable Git commit analysis"
    )

    ENABLE_AUTO_SCORING: bool = Field(
        default=True,
        description="Enable automated evaluation scoring"
    )

    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    MAX_EVALUATIONS_PER_DAY: int = Field(
        default=10,
        description="Max evaluations per HR manager per day"
    )

    MAX_SUBMISSIONS_PER_MONTH: int = Field(
        default=5,
        description="Max submissions per candidate per month"
    )

    # ========================================================================
    # BACKGROUND JOBS
    # ========================================================================
    CELERY_BROKER_URL: Optional[str] = Field(
        default=None,
        description="Celery broker URL (defaults to REDIS_URL)"
    )

    CELERY_RESULT_BACKEND: Optional[str] = Field(
        default=None,
        description="Celery result backend (defaults to REDIS_URL)"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def celery_broker(self) -> str:
        """Get Celery broker URL (defaults to REDIS_URL)"""
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def celery_backend(self) -> str:
        """Get Celery result backend (defaults to REDIS_URL)"""
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency for FastAPI to inject settings.

    Example:
        @app.get("/config")
        def get_config(settings: Settings = Depends(get_settings)):
            return {"environment": settings.ENVIRONMENT}
    """
    return settings
