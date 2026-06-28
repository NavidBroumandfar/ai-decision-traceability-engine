"""
Append-only trace writer for audit logging.

This module provides functionality to write trace events to JSONL files
in an append-only manner, ensuring full auditability.
"""

import json
from pathlib import Path

from src.persistence.artifact_paths import artifact_path

from .trace_models import TraceEvent


def write_trace_event(event: TraceEvent) -> None:
    """
    Write a trace event to a JSONL file.
    
    Events are written to: data/traces/{run_id}.jsonl
    One event per line in JSON format.
    
    Args:
        event: The trace event to write
        
    Raises:
        OSError: If the file cannot be written
        ValueError: If the event cannot be serialized
    """
    # Construct the file path
    traces_dir = Path("data/traces")
    traces_dir.mkdir(parents=True, exist_ok=True)
    
    trace_file = artifact_path(traces_dir, event.run_id, ".jsonl")
    
    # Serialize the event to JSON (Pydantic handles datetime conversion)
    event_dict = event.model_dump(mode="json")
    
    # Write the event as a single line
    with open(trace_file, "a", encoding="utf-8") as f:
        json_line = json.dumps(event_dict, ensure_ascii=False)
        f.write(json_line + "\n")
        f.flush()  # Ensure immediate write to disk
