"""
LLM client factory for provider-agnostic OpenAI-compatible client creation.

This module provides a unified interface for creating LLM clients regardless of
the provider (OpenAI, Ollama, or LM Studio). It ensures correct API key handling
and prevents the common error of using fake keys with local providers.
"""

from openai import OpenAI

from src.config.settings import LLMProvider, Settings


def get_llm_client_and_model(settings: Settings) -> tuple[OpenAI, str]:
    """
    Get the appropriate OpenAI-compatible client and model name based on provider.
    
    This function handles provider-specific configuration:
    - For OpenAI: Uses OPENAI_API_KEY, OPENAI_MODEL, and OPENAI_BASE_URL
    - For Ollama/LM Studio: Uses LLM_MODEL and LLM_BASE_URL, with empty API key
    
    Args:
        settings: Application settings instance
        
    Returns:
        Tuple of (OpenAI client, model_name)
        
    Raises:
        ValueError: If required configuration is missing for the selected provider
    """
    if settings.llm_provider == LLMProvider.OPENAI:
        # OpenAI provider requires API key and model
        if not settings.openai_api_key or not settings.openai_api_key.strip():
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
                "Please set OPENAI_API_KEY in your .env file."
            )
        
        model = settings.get_effective_model()
        if not model:
            raise ValueError(
                "OPENAI_MODEL is required when LLM_PROVIDER=openai. "
                "Please set OPENAI_MODEL in your .env file."
            )
        
        base_url = settings.get_effective_base_url()
        client = OpenAI(
            api_key=settings.openai_api_key.strip(),
            base_url=base_url
        )
        
        return client, model
    
    elif settings.llm_provider in (LLMProvider.OLLAMA, LLMProvider.LMSTUDIO):
        # Local providers: use empty string for API key (not "not-needed" or "ollama")
        # The base_url points to local server, so no API key validation occurs
        model = settings.get_effective_model()
        if not model:
            provider_name = settings.llm_provider.value
            raise ValueError(
                f"LLM_MODEL is required when LLM_PROVIDER={provider_name}. "
                f"Please set LLM_MODEL in your .env file."
            )
        
        base_url = settings.get_effective_base_url()
        if not base_url:
            provider_name = settings.llm_provider.value
            raise ValueError(
                f"LLM_BASE_URL is required when LLM_PROVIDER={provider_name}. "
                f"Please set LLM_BASE_URL in your .env file."
            )
        
        # Use empty string for API key - local servers don't validate it
        # This prevents confusion and ensures we never hit OpenAI endpoints
        client = OpenAI(
            api_key="",  # Empty string, not "not-needed" or "ollama"
            base_url=base_url
        )
        
        return client, model
    
    else:
        raise ValueError(
            f"Unsupported LLM provider: {settings.llm_provider}. "
            f"Must be one of: openai, ollama, lmstudio"
        )
