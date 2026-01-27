"""
Policy Interpretation Agent implementation.

This agent interprets policy text in the context of extracted facts.
It identifies applicable rules, explains their relevance, and highlights ambiguities.
It does NOT enforce rules or make approval/denial decisions.
"""

import json

from openai import APIConnectionError

from src.agents.agent_models import ContextAgentOutput, PolicyAgentOutput
from src.config.settings import settings
from src.lib.llm_client import get_llm_client_and_model


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
    # Get the appropriate LLM client and model based on provider configuration
    client, model = get_llm_client_and_model(settings)
    
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

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a Policy Interpretation Agent. Identify applicable rules and explain relevance. Never enforce rules or make decisions."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
    except APIConnectionError as e:
        base_url = settings.get_effective_base_url() or "OpenAI API"
        error_msg = (
            f"Connection error: Cannot connect to {base_url}.\n"
        )
        if settings.llm_provider.value in ("ollama", "lmstudio"):
            error_msg += (
                f"  - Make sure your local model server is running.\n"
                f"  - For Ollama: Run 'ollama serve' in a terminal.\n"
                f"  - For LM Studio: Start the local server in the application.\n"
                f"  - Verify the server is accessible at: {base_url}\n"
            )
        else:
            error_msg += (
                f"  - Check your internet connection.\n"
                f"  - Verify your OPENAI_API_KEY is correct in the .env file.\n"
            )
        raise ConnectionError(error_msg) from e
    
    result_text = response.choices[0].message.content
    result_dict = json.loads(result_text)
    
    return PolicyAgentOutput(**result_dict)

