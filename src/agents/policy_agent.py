"""
Policy Interpretation Agent implementation.

This agent interprets policy text in the context of extracted facts.
It identifies applicable rules, explains their relevance, and highlights ambiguities.
It does NOT enforce rules or make approval/denial decisions.
"""

import json

from openai import OpenAI

from src.agents.agent_models import ContextAgentOutput, PolicyAgentOutput
from src.config.settings import settings


def run_policy_agent(
    context_output: ContextAgentOutput,
    policy_text: str
) -> PolicyAgentOutput:
    """
    Run the Policy Interpretation Agent.
    
    Args:
        context_output: Output from the Context Agent
        policy_text: Plain text policy document or rules
        
    Returns:
        PolicyAgentOutput with applicable rules, explanations, and ambiguities
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
    
    prompt = f"""You are a Policy Interpretation Agent. Your role is to interpret policy rules in the context of extracted facts.

CRITICAL CONSTRAINTS:
- You MUST NOT enforce rules
- You MUST NOT make approval/denial decisions
- You MUST NOT evaluate compliance
- You MUST only identify applicable rules and explain their relevance

Context from previous agent:
Facts: {json.dumps(context_output.facts, indent=2)}
Assumptions: {json.dumps(context_output.assumptions, indent=2)}
Missing Fields: {json.dumps(context_output.missing_fields, indent=2)}

Policy text:
{policy_text}

Your task:
1. Identify which policy rules are applicable given the context
2. Explain why each rule is relevant
3. Highlight any ambiguities or unclear aspects

Return a JSON object with the following structure:
{{
    "applicable_rules": ["rule1", "rule2", ...],
    "rule_explanations": {{
        "rule1": "explanation of relevance",
        "rule2": "explanation of relevance"
    }},
    "ambiguities": ["ambiguity1", "ambiguity2", ...]
}}

Return ONLY valid JSON, no additional text."""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You are a Policy Interpretation Agent. Identify applicable rules and explain relevance. Never enforce rules or make decisions."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    
    result_text = response.choices[0].message.content
    result_dict = json.loads(result_text)
    
    return PolicyAgentOutput(**result_dict)

