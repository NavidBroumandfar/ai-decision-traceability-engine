"""
Application settings and configuration management.

This module provides strongly-validated configuration using Pydantic Settings.
Configuration is loaded from environment variables with strict validation
based on the deployment environment (local vs production).
"""

from enum import Enum
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM provider types."""

    OPENAI = "openai"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Settings are validated based on the deployment environment:
    - Local: Allows missing API keys with warnings
    - Production: Requires all mandatory settings, fails fast on misconfiguration
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_ignore_empty=True,
    )

    # Environment configuration
    env: Literal["local", "prod"] = Field(
        default="local",
        description="Deployment environment: 'local' for development, 'prod' for production"
    )

    # LLM configuration
    llm_provider: LLMProvider = Field(
        default=LLMProvider.OLLAMA,
        description="LLM provider: 'openai', 'ollama', or 'lmstudio'"
    )
    openai_base_url: str = Field(
        default="",
        description="Base URL for LLM API (empty for OpenAI, set for local models)"
    )
    openai_api_key: str = Field(
        default="",
        description="API key for LLM provider (required in prod for OpenAI)"
    )
    openai_model: str = Field(
        default="",
        description="Model name/identifier (e.g., 'llama3.2', 'gpt-4o-mini')"
    )

    # Application configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    max_request_size: int = Field(
        default=1024 * 1024,  # 1MB
        description="Maximum request body size in bytes"
    )

    @field_validator("llm_provider", mode="before")
    @classmethod
    def validate_llm_provider(cls, v):
        """Validate LLM provider value. Fails fast on invalid values."""
        # If already an LLMProvider enum, return as-is
        if isinstance(v, LLMProvider):
            return v
        
        # Handle string values from environment variables
        if isinstance(v, str):
            v = v.lower().strip()
            try:
                return LLMProvider(v)
            except ValueError:
                valid_values = ", ".join([p.value for p in LLMProvider])
                raise ValueError(
                    f"Invalid LLM_PROVIDER: '{v}'. Must be one of: {valid_values}"
                )
        
        # For any other type, let Pydantic handle it (will fail with type error)
        return v

    def validate_production_config(self) -> list[str]:
        """
        Validate configuration for production environment.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if self.env == "prod":
            # In production, OPENAI_API_KEY is required for OpenAI provider
            if self.llm_provider == LLMProvider.OPENAI:
                if not self.openai_api_key or not self.openai_api_key.strip():
                    errors.append(
                        "OPENAI_API_KEY is required in production when LLM_PROVIDER=openai"
                    )

            # Model name is always required
            if not self.openai_model or not self.openai_model.strip():
                errors.append("OPENAI_MODEL is required")

        return errors

    def get_effective_base_url(self) -> str | None:
        """
        Get the effective base URL based on provider.
        
        Returns:
            Base URL string or None for OpenAI API
        """
        if self.llm_provider == LLMProvider.OPENAI:
            return None  # OpenAI uses default base URL
        elif self.llm_provider == LLMProvider.OLLAMA:
            return self.openai_base_url.strip() if self.openai_base_url else "http://localhost:11434/v1"
        elif self.llm_provider == LLMProvider.LMSTUDIO:
            return self.openai_base_url.strip() if self.openai_base_url else "http://localhost:1234/v1"
        return None


# Global settings instance
settings = Settings()

