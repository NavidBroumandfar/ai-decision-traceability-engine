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
    client = OpenAI(
        base_url=settings.openai_base_url or None,
        api_key=settings.openai_api_key or "not-needed"
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

