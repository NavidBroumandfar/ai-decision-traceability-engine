"""
Pydantic models for agent outputs.

This module defines structured output schemas for all agents in the system.
Agents produce these structured outputs to ensure traceability and auditability.
"""

from pydantic import BaseModel, Field


class ContextAgentOutput(BaseModel):
    """Output from the Context Agent.
    
    Represents normalized facts, assumptions, and missing information
    extracted from raw input payloads.
    """
    
    facts: list[str] = Field(
        ...,
        description="Explicit facts extracted from the input payload"
    )
    assumptions: list[str] = Field(
        ...,
        description="Assumptions made during context extraction"
    )
    missing_fields: list[str] = Field(
        ...,
        description="Fields that are missing or unclear in the input"
    )


class PolicyAgentOutput(BaseModel):
    """Output from the Policy Interpretation Agent.
    
    Represents applicable rules, their explanations, and identified ambiguities
    from policy interpretation.
    """
    
    applicable_rules: list[str] = Field(
        ...,
        description="List of applicable policy rules identified"
    )
    rule_explanations: dict[str, str] = Field(
        ...,
        description="Mapping of rule identifiers to explanations of their relevance"
    )
    ambiguities: list[str] = Field(
        ...,
        description="Ambiguities or unclear aspects in policy interpretation"
    )


class RecommendationAgentOutput(BaseModel):
    """Output from the Recommendation Agent.
    
    Represents a recommendation proposal with justification, confidence,
    and known risks. This is NOT a final decision.
    """
    
    recommendation: str = Field(
        ...,
        description="The proposed recommendation (not a final decision)"
    )
    justification: list[dict] = Field(
        ...,
        description="List of justification entries, each referencing facts and rules"
    )
    confidence_self_report: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Self-reported confidence level (0.0 to 1.0)"
    )
    known_risks: list[str] = Field(
        ...,
        description="Known risks or uncertainties associated with the recommendation"
    )

