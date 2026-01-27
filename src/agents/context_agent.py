"""
Context Agent implementation.

This agent normalizes raw input payloads into explicit facts, assumptions,
and missing fields. It does NOT make decisions or recommendations.
"""

import json
from typing import Any

from openai import APIConnectionError, OpenAI

from src.agents.agent_models import ContextAgentOutput
from src.config.settings import settings


def run_context_agent(input_payload: dict[str, Any]) -> ContextAgentOutput:
    """
    Run the Context Agent to normalize input payload.
    
    Args:
        input_payload: Raw input data dictionary
        
    Returns:
        ContextAgentOutput with facts, assumptions, and missing fields
    """
    if not settings.openai_model:
        raise ValueError(
            "Model is not configured. Please set OPENAI_MODEL in your .env file."
        )
    
    # For local models, API key is often optional but OpenAI client requires it
    # If base_url is set (local model), use a dummy key
    # Otherwise, require API key for OpenAI API
    api_key = settings.openai_api_key.strip() if settings.openai_api_key else ""
    if not api_key and not settings.openai_base_url:
        raise ValueError(
            "API key is required when using OpenAI API. Please set OPENAI_API_KEY in your .env file, "
            "or set OPENAI_BASE_URL to use a local model server (e.g., http://localhost:11434/v1 for Ollama)."
        )
    
    # For local models, use a dummy key (OpenAI client requires api_key parameter)
    # For OpenAI API, use the actual API key
    final_api_key = api_key if api_key else "ollama"  # Dummy key for local models
    
    client = OpenAI(
        base_url=settings.openai_base_url.strip() if settings.openai_base_url else None,
        api_key=final_api_key
    )
    
    prompt = f"""You are a Context Agent. Your role is to analyze input data and extract structured information.

CRITICAL CONSTRAINTS:
- You MUST NOT make any decisions
- You MUST NOT provide recommendations
- You MUST NOT evaluate or judge the input
- You MUST only extract and normalize information

Your task:
1. Extract explicit facts from the input payload
2. Identify any assumptions that must be made
3. List any missing or unclear fields

Input payload:
{json.dumps(input_payload, indent=2)}

Return a JSON object with the following structure:
{{
    "facts": ["fact1", "fact2", ...],
    "assumptions": ["assumption1", "assumption2", ...],
    "missing_fields": ["field1", "field2", ...]
}}

Return ONLY valid JSON, no additional text."""

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a Context Agent. Extract facts, assumptions, and missing fields. Never make decisions or recommendations."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
    except APIConnectionError as e:
        base_url = settings.openai_base_url or "OpenAI API"
        error_msg = (
            f"Connection error: Cannot connect to {base_url}.\n"
        )
        if settings.openai_base_url:
            error_msg += (
                f"  - Make sure your local model server is running.\n"
                f"  - For Ollama: Run 'ollama serve' in a terminal.\n"
                f"  - For LM Studio: Start the local server in the application.\n"
                f"  - Verify the server is accessible at: {settings.openai_base_url}\n"
            )
        else:
            error_msg += (
                f"  - Check your internet connection.\n"
                f"  - Verify your OPENAI_API_KEY is correct in the .env file.\n"
            )
        raise ConnectionError(error_msg) from e
    
    result_text = response.choices[0].message.content
    result_dict = json.loads(result_text)
    
    return ContextAgentOutput(**result_dict)

