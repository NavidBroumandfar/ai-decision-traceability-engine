"""
Context Agent implementation.

This agent normalizes raw input payloads into explicit facts, assumptions,
and missing fields. It does NOT make decisions or recommendations.
"""

import json
from typing import Any

from openai import OpenAI

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
    client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="local-only"
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

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You are a Context Agent. Extract facts, assumptions, and missing fields. Never make decisions or recommendations."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    
    result_text = response.choices[0].message.content
    result_dict = json.loads(result_text)
    
    return ContextAgentOutput(**result_dict)

