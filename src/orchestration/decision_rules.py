"""
Deterministic decision rule evaluation.

This module implements explicit, interpretable, and deterministic rules
that operate on agent outputs to produce final decisions and reason codes.

Rules do NOT embed policy text logic. They operate on agent outputs only.
"""

from typing import Any

from src.agents.agent_models import (
    ContextAgentOutput,
    PolicyAgentOutput,
    RecommendationAgentOutput
)


def evaluate_decision_rules(
    context_output: ContextAgentOutput,
    policy_output: PolicyAgentOutput,
    recommendation_output: RecommendationAgentOutput
) -> dict[str, Any]:
    """
    Evaluate deterministic rules against agent outputs.
    
    Rules are evaluated in order of priority:
    1. Reject if missing_fields is non-empty
    2. Flag for review if policy ambiguities exist
    3. Escalate if agent recommendation confidence < threshold
    4. Otherwise, accept the recommendation
    
    Args:
        context_output: Output from Context Agent
        policy_output: Output from Policy Agent
        recommendation_output: Output from Recommendation Agent
        
    Returns:
        Dictionary with:
            - decision: str - The final decision ("accept", "reject", "review", "escalate")
            - reason_codes: list[str] - List of reason codes explaining the decision
    """
    reason_codes: list[str] = []
    decision: str = "accept"
    
    # Rule 1: Reject if missing_fields is non-empty
    if len(context_output.missing_fields) > 0:
        decision = "reject"
        reason_codes.append(f"REJECT_MISSING_FIELDS: {len(context_output.missing_fields)} missing field(s): {', '.join(context_output.missing_fields)}")
        return {
            "decision": decision,
            "reason_codes": reason_codes
        }
    
    # Rule 2: Flag for review if policy ambiguities exist
    if len(policy_output.ambiguities) > 0:
        decision = "review"
        reason_codes.append(f"REVIEW_POLICY_AMBIGUITIES: {len(policy_output.ambiguities)} ambiguity(ies) identified")
        # Continue evaluation (don't return early) to check other rules
    
    # Rule 3: Escalate if agent recommendation confidence < threshold
    CONFIDENCE_THRESHOLD = 0.5
    if recommendation_output.confidence_self_report < CONFIDENCE_THRESHOLD:
        if decision == "review":
            # If already flagged for review, escalate instead
            decision = "escalate"
            reason_codes.append(f"ESCALATE_LOW_CONFIDENCE: Agent confidence {recommendation_output.confidence_self_report:.2f} below threshold {CONFIDENCE_THRESHOLD}")
        else:
            decision = "escalate"
            reason_codes.append(f"ESCALATE_LOW_CONFIDENCE: Agent confidence {recommendation_output.confidence_self_report:.2f} below threshold {CONFIDENCE_THRESHOLD}")
    
    # Rule 4: Check if recommendation is empty or invalid
    if not recommendation_output.recommendation or not recommendation_output.recommendation.strip():
        decision = "reject"
        reason_codes.append("REJECT_EMPTY_RECOMMENDATION: Recommendation agent produced empty output")
        return {
            "decision": decision,
            "reason_codes": reason_codes
        }
    
    # Rule 5: Check if known_risks are severe (heuristic: more than 3 risks)
    if len(recommendation_output.known_risks) > 3:
        if decision == "accept":
            decision = "review"
            reason_codes.append(f"REVIEW_HIGH_RISK_COUNT: {len(recommendation_output.known_risks)} known risks identified")
    
    # If no rules triggered, accept the recommendation
    if decision == "accept":
        reason_codes.append("ACCEPT_RECOMMENDATION: All rules passed, accepting agent recommendation")
    
    return {
        "decision": decision,
        "reason_codes": reason_codes
    }

