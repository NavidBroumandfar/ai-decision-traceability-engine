"""
Streamlit audit interface for AI Decision Traceability Engine.

This is an INTERNAL AUDIT TOOL that provides a transparent view of
decision processes, allowing humans to inspect decisions and their traces.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import uuid
from datetime import datetime
from typing import Any

import streamlit as st

from src.core.decision_models import DecisionRequest, DecisionResult
from src.orchestration.orchestrator import DecisionOrchestrator
from src.tracing.persistence import get_trace_events_by_run_id
from src.tracing.trace_models import TraceEvent
from src.ui.components import render_decision_result, render_trace_event


def load_trace_events(run_id: str) -> list[TraceEvent]:
    """
    Load trace events for a given run_id from JSONL file or SQLite database.
    
    First attempts to load from JSONL file (for backward compatibility).
    If JSONL file doesn't exist, loads from SQLite database.
    
    Args:
        run_id: The run_id to load traces for
        
    Returns:
        List of TraceEvent objects, sorted by timestamp
    """
    # First try to load from JSONL file (if it exists)
    trace_file = Path("data/traces") / f"{run_id}.jsonl"
    
    if trace_file.exists():
        events = []
        with open(trace_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event_dict = json.loads(line)
                    # Convert timestamp string back to datetime
                    event_dict["timestamp"] = datetime.fromisoformat(event_dict["timestamp"])
                    event = TraceEvent(**event_dict)
                    events.append(event)
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    # Skip malformed lines but continue processing
                    st.warning(f"Skipping malformed trace event: {e}")
                    continue
        
        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)
        return events
    
    # If JSONL doesn't exist, try loading from SQLite
    try:
        events = get_trace_events_by_run_id(run_id)
        return events
    except Exception as e:
        st.warning(f"Failed to load traces from database: {e}")
        return []


# Initialize orchestrator with empty policy text
# In production, this would come from configuration
_orchestrator = DecisionOrchestrator(policy_text="")


# ============================================================================
# HEADER
# ============================================================================

st.title("AI Decision Traceability & Audit Engine")
st.caption("Governed AI decision audit interface")


# ============================================================================
# DECISION INPUT SECTION
# ============================================================================

st.header("Decision Input")

# Input payload (JSON or text)
input_mode = st.radio(
    "Input Mode",
    ["JSON", "Text"],
    horizontal=True
)

input_payload = None

if input_mode == "JSON":
    input_json = st.text_area(
        "Input Payload (JSON)",
        height=150,
        placeholder='{"key": "value"}'
    )
    if input_json:
        try:
            input_payload = json.loads(input_json)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
else:
    input_text = st.text_area(
        "Input Payload (Text)",
        height=150,
        placeholder="Enter input text here..."
    )
    if input_text:
        input_payload = {"text": input_text}

# Optional metadata
metadata_json = st.text_area(
    "Metadata (Optional JSON)",
    height=100,
    placeholder='{"key": "value"}'
)

metadata = None
if metadata_json:
    try:
        metadata = json.loads(metadata_json)
    except json.JSONDecodeError as e:
        st.error(f"Invalid metadata JSON: {e}")

# Run decision button
run_button = st.button("Run Decision", type="primary")


# ============================================================================
# DECISION OUTPUT SECTION
# ============================================================================

if run_button:
    if input_payload is None:
        st.error("Please provide an input payload")
    else:
        try:
            # Create decision request
            request = DecisionRequest(
                request_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                input_payload=input_payload,
                metadata=metadata
            )
            
            # Run decision
            with st.spinner("Processing decision..."):
                result: DecisionResult = _orchestrator.run_decision(request)
            
            # Display result
            render_decision_result(result)
            
            # Store run_id in session state for trace display
            st.session_state["last_run_id"] = result.run_id
            
        except Exception as e:
            st.error(f"Decision execution failed: {str(e)}")
            st.exception(e)


# ============================================================================
# TRACE TIMELINE SECTION
# ============================================================================

st.header("Trace Timeline")

# Get run_id from session state or allow manual input
run_id_input = st.text_input(
    "Run ID",
    value=st.session_state.get("last_run_id", ""),
    placeholder="Enter run_id to view traces"
)

if run_id_input:
    trace_events = load_trace_events(run_id_input)
    
    if trace_events:
        st.write(f"Found {len(trace_events)} trace event(s) for run_id: `{run_id_input}`")
        st.divider()
        
        # Display events in chronological order
        for event in trace_events:
            render_trace_event(event)
    else:
        st.info(f"No trace events found for run_id: `{run_id_input}`")
        st.write("Trace events are written to: `data/traces/{run_id}.jsonl`")
else:
    st.info("Enter a run_id above to view trace events, or run a decision to automatically load traces.")

