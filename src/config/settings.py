"""
Application settings and configuration management.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    openai_base_url: str = ""
    openai_api_key: str = ""
    openai_model: str = ""
    log_level: str = "INFO"


# Global settings instance
settings = Settings()

