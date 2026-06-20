"""Application configuration.

The backend keeps configuration intentionally small so the prototype can
run locally with minimal setup while still allowing deployment-specific
overrides later.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = "Alcohol Label Verification API"
    app_version: str = "0.1.0"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    model_config = SettingsConfigDict(env_prefix="ALCOHOL_LABEL_", extra="ignore")


settings = Settings()
