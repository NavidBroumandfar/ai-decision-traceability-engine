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
    
    # Configuration for local providers (ollama/lmstudio)
    llm_model: str | None = Field(
        default=None,
        description="Model name for local providers (e.g., 'qwen2.5-coder:7b-instruct', 'llama3.2')"
    )
    llm_base_url: str | None = Field(
        default=None,
        description="Base URL for local LLM server (e.g., 'http://localhost:11434/v1' for Ollama)"
    )
    
    # Configuration for OpenAI provider
    openai_api_key: str | None = Field(
        default=None,
        description="API key for OpenAI API (required when LLM_PROVIDER=openai)"
    )
    openai_model: str | None = Field(
        default=None,
        description="Model name for OpenAI API (e.g., 'gpt-4o-mini')"
    )
    openai_base_url: str | None = Field(
        default=None,
        description="Base URL for OpenAI API (default: https://api.openai.com/v1)"
    )

    # Application configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    max_request_size: int = Field(
        default=1048576,  # 1MB
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
            if self.llm_provider == LLMProvider.OPENAI:
                # OpenAI provider requires API key and model
                if not self.openai_api_key or not self.openai_api_key.strip():
                    errors.append(
                        "OPENAI_API_KEY is required when LLM_PROVIDER=openai"
                    )
                if not self.openai_model or not self.openai_model.strip():
                    errors.append(
                        "OPENAI_MODEL is required when LLM_PROVIDER=openai"
                    )
            elif self.llm_provider in (LLMProvider.OLLAMA, LLMProvider.LMSTUDIO):
                # Local providers require model and base_url
                if not self.llm_model or not self.llm_model.strip():
                    errors.append(
                        f"LLM_MODEL is required when LLM_PROVIDER={self.llm_provider.value}"
                    )
                if not self.llm_base_url or not self.llm_base_url.strip():
                    errors.append(
                        f"LLM_BASE_URL is required when LLM_PROVIDER={self.llm_provider.value}"
                    )

        return errors
    
    def validate_local_config(self) -> list[str]:
        """
        Validate configuration for local environment.
        
        Returns:
            List of validation warning messages (empty if valid)
        """
        warnings = []

        if self.env == "local":
            if self.llm_provider == LLMProvider.OPENAI:
                # In local, still require API key for OpenAI to avoid confusion
                if not self.openai_api_key or not self.openai_api_key.strip():
                    warnings.append(
                        "OPENAI_API_KEY is required when LLM_PROVIDER=openai (even in local mode)"
                    )
                if not self.openai_model or not self.openai_model.strip():
                    warnings.append(
                        "OPENAI_MODEL is recommended when LLM_PROVIDER=openai"
                    )
            elif self.llm_provider in (LLMProvider.OLLAMA, LLMProvider.LMSTUDIO):
                # Warn if model or base_url missing, but don't fail
                if not self.llm_model or not self.llm_model.strip():
                    warnings.append(
                        f"LLM_MODEL is recommended when LLM_PROVIDER={self.llm_provider.value}"
                    )
                if not self.llm_base_url or not self.llm_base_url.strip():
                    warnings.append(
                        f"LLM_BASE_URL is recommended when LLM_PROVIDER={self.llm_provider.value} "
                        f"(will use default: {self.get_effective_base_url()})"
                    )

        return warnings

    def get_effective_base_url(self) -> str | None:
        """
        Get the effective base URL based on provider.
        
        Supports backward compatibility: if LLM_BASE_URL is not set for local providers,
        falls back to OPENAI_BASE_URL for migration purposes.
        
        Returns:
            Base URL string or None for OpenAI API
        """
        if self.llm_provider == LLMProvider.OPENAI:
            return self.openai_base_url.strip() if self.openai_base_url and self.openai_base_url.strip() else "https://api.openai.com/v1"
        elif self.llm_provider == LLMProvider.OLLAMA:
            # Try LLM_BASE_URL first, fall back to OPENAI_BASE_URL for backward compatibility
            if self.llm_base_url and self.llm_base_url.strip():
                return self.llm_base_url.strip()
            elif self.openai_base_url and self.openai_base_url.strip():
                return self.openai_base_url.strip()
            return "http://localhost:11434/v1"
        elif self.llm_provider == LLMProvider.LMSTUDIO:
            # Try LLM_BASE_URL first, fall back to OPENAI_BASE_URL for backward compatibility
            if self.llm_base_url and self.llm_base_url.strip():
                return self.llm_base_url.strip()
            elif self.openai_base_url and self.openai_base_url.strip():
                return self.openai_base_url.strip()
            return "http://localhost:1234/v1"
        return None
    
    def get_effective_model(self) -> str | None:
        """
        Get the effective model name based on provider.
        
        Supports backward compatibility: if LLM_MODEL is not set for local providers,
        falls back to OPENAI_MODEL for migration purposes.
        
        Returns:
            Model name string or None if not configured
        """
        if self.llm_provider == LLMProvider.OPENAI:
            return self.openai_model.strip() if self.openai_model and self.openai_model.strip() else None
        elif self.llm_provider in (LLMProvider.OLLAMA, LLMProvider.LMSTUDIO):
            # Try LLM_MODEL first, fall back to OPENAI_MODEL for backward compatibility
            if self.llm_model and self.llm_model.strip():
                return self.llm_model.strip()
            elif self.openai_model and self.openai_model.strip():
                return self.openai_model.strip()
            return None
        return None


# Global settings instance
settings = Settings()

