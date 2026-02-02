"""
Decision replay engine for audit and debugging.

This module provides functionality to re-run past decisions using persisted
inputs and produce structured diff reports comparing original vs replayed results.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.core.decision_models import DecisionRequest, DecisionResult
from src.orchestration.orchestrator import DecisionOrchestrator
from src.persistence.decision_store import FileDecisionStore
from src.tracing.trace_models import TraceEvent


class AgentDiff(BaseModel):
    """Diff information for a single agent output."""
    
    original: dict[str, Any] = Field(..., description="Original agent output payload")
    replay: dict[str, Any] = Field(..., description="Replayed agent output payload")
    changed_keys: list[str] = Field(..., description="Keys that differ between original and replay")


class ReplayReport(BaseModel):
    """Report comparing original vs replayed decision execution."""
    
    run_id: str = Field(..., description="Original decision run ID")
    replay_run_id: str = Field(..., description="Replay decision run ID")
    same_final_decision: bool = Field(..., description="Whether final decision matches")
    same_reason_codes: bool = Field(..., description="Whether reason codes match")
    confidence_delta: float = Field(..., description="Difference in confidence scores (replay - original)")
    agent_diffs: dict[str, AgentDiff] = Field(
        ...,
        description="Per-agent diff information (keys: context_agent, policy_agent, recommendation_agent)"
    )
    notes: list[str] = Field(default_factory=list, description="Additional notes about the replay")


def load_trace_events(run_id: str) -> list[TraceEvent]:
    """
    Load all trace events for a given run_id.
    
    Args:
        run_id: The unique identifier for the decision run
        
    Returns:
        List of TraceEvent objects in chronological order
        
    Raises:
        FileNotFoundError: If trace file does not exist
        ValueError: If trace file is malformed
    """
    trace_file = Path("data/traces") / f"{run_id}.jsonl"
    
    if not trace_file.exists():
        raise FileNotFoundError(
            f"Trace file not found: {trace_file}. "
            f"Action: Ensure the decision run {run_id} was executed and trace was written."
        )
    
    events = []
    try:
        with open(trace_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    event = TraceEvent.model_validate(data)
                    events.append(event)
                except (json.JSONDecodeError, ValueError) as e:
                    raise ValueError(
                        f"Malformed trace event at line {line_num} in {trace_file}: {e}. "
                        f"Action: Check trace file integrity or re-run the decision."
                    ) from e
    except OSError as e:
        raise OSError(
            f"Failed to read trace file {trace_file}: {e}. "
            f"Action: Check file permissions and disk space."
        ) from e
    
    return events


def extract_input_event(events: list[TraceEvent]) -> TraceEvent:
    """
    Extract the input_received event from trace events.
    
    Args:
        events: List of trace events
        
    Returns:
        The input_received TraceEvent
        
    Raises:
        ValueError: If input_received event is missing
    """
    for event in events:
        if event.event_type == "input_received":
            return event
    
    raise ValueError(
        "Missing input_received event in trace. "
        "Action: Ensure the decision run was executed with proper tracing enabled."
    )


def extract_agent_outputs(events: list[TraceEvent]) -> dict[str, dict[str, Any]]:
    """
    Extract agent output payloads from trace events.
    
    Args:
        events: List of trace events
        
    Returns:
        Dictionary mapping agent source names to their output payloads
        Keys: "context_agent", "policy_agent", "recommendation_agent"
    """
    agent_outputs = {}
    
    for event in events:
        if event.event_type == "agent_output":
            if event.source in ("context_agent", "policy_agent", "recommendation_agent"):
                agent_outputs[event.source] = event.payload
    
    return agent_outputs


def diff_dicts(original: dict[str, Any], replay: dict[str, Any]) -> list[str]:
    """
    Compute deterministic diff between two dictionaries.
    
    Args:
        original: Original dictionary
        replay: Replayed dictionary
        
    Returns:
        List of keys that differ between the two dictionaries
    """
    changed_keys = []
    
    # Check all keys in original
    for key in original:
        if key not in replay:
            changed_keys.append(key)
        elif original[key] != replay[key]:
            changed_keys.append(key)
    
    # Check keys in replay that aren't in original
    for key in replay:
        if key not in original:
            changed_keys.append(key)
    
    return sorted(set(changed_keys))


def replay_decision(orchestrator: DecisionOrchestrator, run_id: str) -> ReplayReport:
    """
    Re-run a past decision using persisted inputs and produce a diff report.
    
    This function:
    1. Loads original DecisionResult from FileDecisionStore
    2. Loads original trace events from JSONL
    3. Extracts input_payload + metadata from input_received event
    4. Re-runs orchestrator with same input but new replay_run_id
    5. Compares final_decision, reason_codes, confidence_score, and agent outputs
    6. Produces structured ReplayReport
    
    Args:
        orchestrator: The DecisionOrchestrator instance to use for replay
        run_id: The original decision run ID to replay
        
    Returns:
        ReplayReport with comparison results
        
    Raises:
        FileNotFoundError: If decision result or trace file is missing
        ValueError: If trace is malformed or missing required events
        RuntimeError: If replay execution fails
    """
    # Load original decision result
    decision_store = FileDecisionStore()
    original_result = decision_store.load(run_id)
    
    if original_result is None:
        raise FileNotFoundError(
            f"Decision result not found for run_id: {run_id}. "
            f"Action: Ensure the decision was executed and persisted to data/decisions/{run_id}.json"
        )
    
    # Load original trace events
    original_events = load_trace_events(run_id)
    
    # Extract input from trace
    input_event = extract_input_event(original_events)
    input_payload = input_event.payload.get("input_payload", {})
    metadata = input_event.payload.get("metadata")
    request_id = input_event.payload.get("request_id", str(uuid.uuid4()))
    
    # Extract original agent outputs
    original_agent_outputs = extract_agent_outputs(original_events)
    
    # Generate new run_id for replay
    replay_run_id = str(uuid.uuid4())
    
    # Create DecisionRequest from extracted input
    replay_request = DecisionRequest(
        request_id=request_id,
        timestamp=datetime.utcnow(),
        input_payload=input_payload,
        metadata=metadata
    )
    
    # Re-run orchestrator with run_id override
    try:
        replay_result = orchestrator.run_decision(replay_request, run_id_override=replay_run_id)
    except Exception as e:
        raise RuntimeError(
            f"Replay execution failed for run_id {run_id}: {e}. "
            f"Action: Check orchestrator configuration and LLM provider availability."
        ) from e
    
    # Load replay trace events
    replay_events = load_trace_events(replay_run_id)
    replay_agent_outputs = extract_agent_outputs(replay_events)
    
    # Compare final decision
    same_final_decision = original_result.final_decision == replay_result.final_decision
    
    # Compare reason codes (order-independent)
    same_reason_codes = set(original_result.reason_codes) == set(replay_result.reason_codes)
    
    # Calculate confidence delta
    confidence_delta = replay_result.confidence_score - original_result.confidence_score
    
    # Compare agent outputs
    agent_diffs = {}
    for agent_name in ("context_agent", "policy_agent", "recommendation_agent"):
        original_output = original_agent_outputs.get(agent_name, {})
        replay_output = replay_agent_outputs.get(agent_name, {})
        
        changed_keys = diff_dicts(original_output, replay_output)
        
        agent_diffs[agent_name] = AgentDiff(
            original=original_output,
            replay=replay_output,
            changed_keys=changed_keys
        )
    
    # Generate notes
    notes = []
    if not same_final_decision:
        notes.append("Final decision differs between original and replay")
    if not same_reason_codes:
        notes.append("Reason codes differ between original and replay")
    if abs(confidence_delta) > 0.01:  # Significant confidence change
        notes.append(f"Confidence score changed by {confidence_delta:.3f}")
    
    # Check for agent output differences
    any_agent_changes = any(
        len(diff.changed_keys) > 0 for diff in agent_diffs.values()
    )
    if any_agent_changes:
        notes.append("Agent outputs differ - LLM non-determinism likely")
    
    return ReplayReport(
        run_id=run_id,
        replay_run_id=replay_run_id,
        same_final_decision=same_final_decision,
        same_reason_codes=same_reason_codes,
        confidence_delta=confidence_delta,
        agent_diffs=agent_diffs,
        notes=notes
    )
