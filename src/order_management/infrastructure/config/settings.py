"""
Application settings via pydantic-settings.
Loads from .env and environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Order Management System"
    debug: bool = False
    environment: str = "development"
    database_url: str = "sqlite:///./order_management.db"
