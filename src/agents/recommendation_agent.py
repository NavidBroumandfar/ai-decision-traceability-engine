"""
Recommendation Agent implementation.

This agent proposes a recommendation based on context and policy interpretation.
It cites facts and rules by reference, states uncertainty explicitly,
and does NOT make final decisions.
"""

import json

from openai import APIConnectionError

from src.agents.agent_models import ContextAgentOutput, PolicyAgentOutput, RecommendationAgentOutput
from src.config.settings import settings
from src.lib.llm_client import get_llm_client_and_model


def run_recommendation_agent(
    context_output: ContextAgentOutput,
    policy_output: PolicyAgentOutput
) -> RecommendationAgentOutput:
    """
    Run the Recommendation Agent.
    
    Args:
        context_output: Output from the Context Agent
        policy_output: Output from the Policy Agent
        
    Returns:
        RecommendationAgentOutput with recommendation, justification, confidence, and risks
    """
    # Get the appropriate LLM client and model based on provider configuration
    client, model = get_llm_client_and_model(settings)
    
    prompt = f"""You are a Recommendation Agent. Your role is to propose a recommendation based on context and policy interpretation.

CRITICAL CONSTRAINTS:
- You MUST NOT make final decisions
- You MUST NOT enforce rules
- You MUST only propose a recommendation
- You MUST cite facts and rules by reference
- You MUST explicitly state uncertainty and risks

Context from Context Agent:
Facts: {json.dumps(context_output.facts, indent=2)}
Assumptions: {json.dumps(context_output.assumptions, indent=2)}
Missing Fields: {json.dumps(context_output.missing_fields, indent=2)}

Policy interpretation from Policy Agent:
Applicable Rules: {json.dumps(policy_output.applicable_rules, indent=2)}
Rule Explanations: {json.dumps(policy_output.rule_explanations, indent=2)}
Ambiguities: {json.dumps(policy_output.ambiguities, indent=2)}

Your task:
1. Propose a recommendation based on the context and policy interpretation
2. Justify your recommendation by citing specific facts (by index) and rules (by identifier)
3. Self-report your confidence level (0.0 to 1.0)
4. List all known risks and uncertainties

Justification format: Each entry should be a dict with:
- "type": "fact" or "rule"
- "reference": index/identifier
- "reason": explanation

Return a JSON object with the following structure:
{{
    "recommendation": "your proposed recommendation text",
    "justification": [
        {{"type": "fact", "reference": 0, "reason": "explanation"}},
        {{"type": "rule", "reference": "rule1", "reason": "explanation"}}
    ],
    "confidence_self_report": 0.75,
    "known_risks": ["risk1", "risk2", ...]
}}

Return ONLY valid JSON, no additional text."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a Recommendation Agent. Propose recommendations with justification. Never make final decisions or enforce rules."},
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
    
    return RecommendationAgentOutput(**result_dict)

