"""
Application Configuration Module
===============================
This module handles all environment configuration using Pydantic Settings.
It automatically loads variables from .env file and provides typed access.
This pattern ensures type safety and validation for all configuration values.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings class.
    All values are loaded from environment variables or .env file.
    Pydantic validates types automatically (e.g., PORT must be int).
    """
    
    # MongoDB Configuration
    mongodb_url: str  # Full MongoDB Atlas connection string
    database_name: str = "fastapi_crud"  # Default database name
    
    # Application Metadata
    app_title: str = "FastAPI MongoDB CRUD API"
    app_version: str = "1.0.0"
    environment: str = "development"  # development, staging, production
    
    # Server Configuration
    host: str = "0.0.0.0"  # 0.0.0.0 allows external connections
    port: int = 8000  # Default FastAPI port
    
    # Logging Configuration
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file
        env_file_encoding="utf-8",  # Handle special characters
        case_sensitive=False  # Allow MONGODB_URL or mongodb_url
    )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Using lru_cache ensures we only create one Settings object
    per application lifecycle, improving performance.
    """
    return Settings()


# Export for easy importing
settings = get_settings()