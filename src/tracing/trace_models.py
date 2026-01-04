"""
Trace event models for audit logging.

This module defines the structure of trace events that capture
the execution flow of AI decision-making processes.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TraceEvent(BaseModel):
    """Represents a single trace event in the decision process."""
    
    event_id: str = Field(..., description="Unique identifier for the event")
    run_id: str = Field(..., description="Identifier of the decision run this event belongs to")
    event_type: str = Field(..., description="Type of event (e.g., 'input_received', 'agent_output', 'rule_evaluation', 'final_decision')")
    source: str = Field(..., description="Source component that generated the event")
    payload: dict[str, Any] = Field(..., description="Event-specific data payload")
    timestamp: datetime = Field(..., description="When the event occurred")

