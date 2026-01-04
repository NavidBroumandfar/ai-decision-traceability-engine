"""
UI component rendering helpers for the Streamlit audit interface.

This module provides small helper functions for formatting and displaying
decision results and trace events. No business logic here - formatting only.
"""

import json
from datetime import datetime
from typing import Any

import streamlit as st

from src.core.decision_models import DecisionResult
from src.tracing.trace_models import TraceEvent


def render_decision_result(result: DecisionResult) -> None:
    """
    Render a decision result in the UI.
    
    Args:
        result: The DecisionResult to display
    """
    st.subheader("Decision Output")
    
    # Final decision
    st.write("**Final Decision:**")
    st.code(result.final_decision, language=None)
    
    # Confidence score
    st.write("**Confidence Score:**")
    st.write(f"{result.confidence_score:.3f}")
    
    # Reason codes
    st.write("**Reason Codes:**")
    if result.reason_codes:
        for code in result.reason_codes:
            st.write(f"- {code}")
    else:
        st.write("_No reason codes_")
    
    # Metadata
    st.write("**Metadata:**")
    st.write(f"- Run ID: `{result.run_id}`")
    st.write(f"- Created At: {result.created_at.isoformat()}")


def render_trace_event(event: TraceEvent) -> None:
    """
    Render a single trace event in the timeline.
    
    Args:
        event: The TraceEvent to display
    """
    # Event header
    st.write(f"**{event.event_type}** (from `{event.source}`)")
    
    # Timestamp
    st.write(f"*{event.timestamp.isoformat()}*")
    
    # Payload summary
    st.write("**Payload:**")
    
    # Format payload as JSON for readability
    payload_str = json.dumps(event.payload, indent=2, default=str)
    st.code(payload_str, language="json")
    
    st.divider()

