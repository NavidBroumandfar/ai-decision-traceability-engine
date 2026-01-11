"""
SQLite-backed persistence for trace events.

This module provides durable storage for decision traces using SQLite,
ensuring that trace data survives process restarts.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .trace_models import TraceEvent


# Database file path
DB_PATH = Path("audit_log.db")


def safe_json_loads(value: str | None) -> dict[str, Any]:
    """
    Safely parse JSON string, handling empty or null values.
    
    Args:
        value: JSON string to parse, or None
        
    Returns:
        Parsed dictionary, or empty dict if value is None/empty/invalid
    """
    if value is None:
        return {}
    if isinstance(value, str) and not value.strip():
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}


def _get_connection() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: Connection to the database
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    """
    Initialize the SQLite database if it does not exist.
    
    Creates the trace_events table with the following schema:
    - run_id: TEXT (identifier of the decision run)
    - timestamp: TEXT (ISO format datetime string)
    - agent_name: TEXT (source component that generated the event)
    - input_snapshot: TEXT (JSON string for input events)
    - output_snapshot: TEXT (JSON string for output events)
    - status: TEXT (event type, e.g., 'input_received', 'agent_output', etc.)
    """
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trace_events (
                run_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                input_snapshot TEXT,
                output_snapshot TEXT,
                status TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_run_id ON trace_events(run_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON trace_events(timestamp)
        """)
        conn.commit()
    finally:
        conn.close()


def store_trace_event(event: TraceEvent) -> None:
    """
    Store a trace event in the SQLite database.
    
    Maps TraceEvent fields to database columns:
    - run_id -> run_id
    - timestamp -> timestamp (stored as ISO string)
    - source -> agent_name
    - event_type -> status
    - payload -> input_snapshot or output_snapshot based on event type
    
    Args:
        event: The trace event to store
        
    Raises:
        sqlite3.Error: If database operation fails
        ValueError: If event cannot be serialized
    """
    # Ensure database is initialized
    initialize_database()
    
    # Determine which snapshot field to use based on event type
    input_snapshot = None
    output_snapshot = None
    
    if event.event_type == "input_received":
        input_snapshot = json.dumps(event.payload, ensure_ascii=False)
    else:
        # For agent_output, rule_evaluation, final_decision, store in output_snapshot
        output_snapshot = json.dumps(event.payload, ensure_ascii=False)
    
    conn = _get_connection()
    try:
        conn.execute("""
            INSERT INTO trace_events 
            (run_id, timestamp, agent_name, input_snapshot, output_snapshot, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event.run_id,
            event.timestamp.isoformat(),
            event.source,
            input_snapshot,
            output_snapshot,
            event.event_type
        ))
        conn.commit()
    finally:
        conn.close()


def get_trace_events_by_run_id(run_id: str) -> list[TraceEvent]:
    """
    Retrieve all trace events for a given run_id from the database.
    
    Args:
        run_id: The run_id to retrieve traces for
        
    Returns:
        List of TraceEvent objects, sorted by timestamp
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    if not DB_PATH.exists():
        return []
    
    conn = _get_connection()
    try:
        cursor = conn.execute("""
            SELECT run_id, timestamp, agent_name, input_snapshot, 
                   output_snapshot, status
            FROM trace_events
            WHERE run_id = ?
            ORDER BY timestamp ASC
        """, (run_id,))
        
        events = []
        for idx, row in enumerate(cursor.fetchall()):
            # Reconstruct payload from input_snapshot or output_snapshot
            payload_json = row["input_snapshot"] or row["output_snapshot"]
            payload = safe_json_loads(payload_json)
            
            # Reconstruct TraceEvent
            # Generate unique event_id from run_id, timestamp, and index
            event_id = f"{run_id}_{row['timestamp']}_{idx}"
            event = TraceEvent(
                event_id=event_id,
                run_id=row["run_id"],
                event_type=row["status"],
                source=row["agent_name"],
                payload=payload,
                timestamp=datetime.fromisoformat(row["timestamp"])
            )
            events.append(event)
        
        return events
    finally:
        conn.close()

