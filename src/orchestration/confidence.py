"""
Confidence score calculator.

This module implements a deterministic confidence proxy calculator that
combines agent self-reported confidence with other factors to produce
a final confidence score between 0 and 1.
"""


def calculate_confidence_score(
    agent_confidence: float,
    missing_fields_count: int,
    ambiguities_count: int,
    triggered_rules_count: int
) -> float:
    """
    Calculate a deterministic confidence score from agent outputs.
    
    The confidence score is computed using weighted factors:
    - Base: Agent self-reported confidence (weight: 0.6)
    - Penalty: Missing fields (weight: 0.2, -0.1 per field)
    - Penalty: Policy ambiguities (weight: 0.15, -0.05 per ambiguity)
    - Penalty: Triggered rules (weight: 0.05, -0.02 per rule)
    
    Args:
        agent_confidence: Self-reported confidence from recommendation agent (0.0 to 1.0)
        missing_fields_count: Number of missing fields from context agent
        ambiguities_count: Number of ambiguities from policy agent
        triggered_rules_count: Number of rules that triggered (from decision_rules)
        
    Returns:
        Confidence score between 0.0 and 1.0
        
    Raises:
        ValueError: If agent_confidence is outside [0.0, 1.0]
    """
    if agent_confidence < 0.0 or agent_confidence > 1.0:
        raise ValueError(f"agent_confidence must be between 0.0 and 1.0, got {agent_confidence}")
    
    # Base confidence from agent
    base_score = agent_confidence * 0.6
    
    # Penalty for missing fields (max -0.2, capped at 0.0)
    missing_penalty = min(missing_fields_count * 0.1, 0.2)
    
    # Penalty for ambiguities (max -0.15, capped at 0.0)
    ambiguity_penalty = min(ambiguities_count * 0.05, 0.15)
    
    # Penalty for triggered rules (max -0.05, capped at 0.0)
    # Note: We subtract 1 because "ACCEPT_RECOMMENDATION" is a reason code but not a penalty
    rule_penalty = min(max(triggered_rules_count - 1, 0) * 0.02, 0.05)
    
    # Calculate final score
    confidence_score = base_score - missing_penalty - ambiguity_penalty - rule_penalty
    
    # Clamp to [0.0, 1.0]
    confidence_score = max(0.0, min(1.0, confidence_score))
    
    return confidence_score

