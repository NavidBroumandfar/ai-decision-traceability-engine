"""
Append-only trace writer for audit logging.

This module provides functionality to write trace events to JSONL files
in an append-only manner, ensuring full auditability.
Also persists events to SQLite for durable storage.
"""

import json
from pathlib import Path

from .persistence import store_trace_event
from .trace_models import TraceEvent


def write_trace_event(event: TraceEvent) -> None:
    """
    Write a trace event to a JSONL file and SQLite database.
    
    Events are written to:
    - JSONL: data/traces/{run_id}.jsonl (one event per line in JSON format)
    - SQLite: audit_log.db (durable persistence)
    
    Args:
        event: The trace event to write
        
    Raises:
        OSError: If the file cannot be written
        ValueError: If the event cannot be serialized
        sqlite3.Error: If database operation fails
    """
    # Construct the file path
    traces_dir = Path("data/traces")
    traces_dir.mkdir(parents=True, exist_ok=True)
    
    trace_file = traces_dir / f"{event.run_id}.jsonl"
    
    # Serialize the event to JSON (Pydantic handles datetime conversion)
    event_dict = event.model_dump(mode="json")
    
    # Write the event as a single line to JSONL
    with open(trace_file, "a", encoding="utf-8") as f:
        json_line = json.dumps(event_dict, ensure_ascii=False)
        f.write(json_line + "\n")
        f.flush()  # Ensure immediate write to disk
    
    # Also persist to SQLite for durable storage
    store_trace_event(event)

