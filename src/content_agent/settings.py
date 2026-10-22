"""Application configuration module using Pydantic Settings."""

from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration class for the content-agent application.

    Reads configuration from environment variables and an optional local .env file.
    Environment variables take precedence over values defined in the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Content Agent"
    app_env: Literal["development", "testing", "production"] = "development"
    debug: bool = False
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    database_url: SecretStr | None = None


def get_settings() -> Settings:
    """Return a new instance of application settings."""
    return Settings()
