"""
Core decision models for AI decision traceability.

This module defines the data models for decision requests and results,
providing a structured foundation for traceable AI decisions.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    """Represents an incoming decision request."""
    
    request_id: str = Field(..., description="Unique identifier for the request")
    timestamp: datetime = Field(..., description="When the request was received")
    input_payload: dict[str, Any] = Field(..., description="Input data for the decision")
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata associated with the request"
    )


class DecisionResult(BaseModel):
    """Represents the result of a decision process."""
    
    run_id: str = Field(..., description="Unique identifier for the decision run")
    final_decision: str = Field(..., description="The final decision output")
    confidence_score: float = Field(..., description="Confidence score for the decision")
    reason_codes: list[str] = Field(..., description="List of reason codes explaining the decision")
    created_at: datetime = Field(..., description="When the decision was created")

