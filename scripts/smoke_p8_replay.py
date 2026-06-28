"""
Smoke test for P8-1 Decision Replay Engine.

This script:
1. Runs a decision (using local provider recommended)
2. Confirms decision + trace persisted
3. Replays the same run_id
4. Prints replay report summary
5. Exits non-zero if replay fails or report is missing required fields

Run (from project root):
  python scripts/smoke_p8_replay.py
If "python" is not in PATH on Windows, use:
  .\\scripts\\run_smoke_p8_replay.ps1
  or:  .venv\\Scripts\\python.exe scripts/smoke_p8_replay.py
"""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ASCII-only status for Windows console (avoid UnicodeEncodeError on cp1252)
OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[WARN]"

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config.policy import load_policy_text
from src.core.decision_models import DecisionRequest
from src.orchestration.orchestrator import DecisionOrchestrator
from src.persistence.decision_store import FileDecisionStore
from src.replay.replay_engine import ReplayReport, replay_decision


def main():
    """Run smoke test for replay engine."""
    print("=" * 60)
    print("P8-1 Replay Engine Smoke Test")
    print("=" * 60)

    # Initialize orchestrator with the public-safe sample policy.
    orchestrator = DecisionOrchestrator(policy_text=load_policy_text())
    decision_store = FileDecisionStore()

    # Step 1: Run a decision
    print("\n[Step 1] Running initial decision...")
    test_request = DecisionRequest(
        request_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        input_payload={"test_field": "test_value", "number": 42},
        metadata={"smoke_test": True},
    )

    try:
        original_result = orchestrator.run_decision(test_request)
        decision_store.save(
            original_result
        )  # Persist so replay can load it (same as API)
        print(f"{OK} Decision executed: run_id={original_result.run_id}")
        print(f"  Final decision: {original_result.final_decision}")
        print(f"  Confidence: {original_result.confidence_score:.3f}")
        print(f"  Reason codes: {original_result.reason_codes}")
    except Exception as e:
        print(f"{FAIL} Failed to run decision: {e}")
        sys.exit(1)

    # Step 2: Confirm decision + trace persisted
    print("\n[Step 2] Verifying persistence...")

    # Check decision store
    if not decision_store.exists(original_result.run_id):
        print(f"{FAIL} Decision result not found in store: {original_result.run_id}")
        sys.exit(1)
    print(
        f"{OK} Decision result persisted: data/decisions/{original_result.run_id}.json"
    )

    # Check trace file
    trace_file = Path("data/traces") / f"{original_result.run_id}.jsonl"
    if not trace_file.exists():
        print(f"{FAIL} Trace file not found: {trace_file}")
        sys.exit(1)
    print(f"{OK} Trace file persisted: {trace_file}")

    # Step 3: Replay the same run_id
    print("\n[Step 3] Replaying decision...")
    try:
        replay_report = replay_decision(orchestrator, original_result.run_id)
        print(f"{OK} Replay completed: replay_run_id={replay_report.replay_run_id}")
    except Exception as e:
        print(f"{FAIL} Replay failed: {e}")
        sys.exit(1)

    # Step 4: Print replay report summary
    print("\n[Step 4] Replay Report Summary:")
    print("-" * 60)
    print(f"Original run_id:     {replay_report.run_id}")
    print(f"Replay run_id:       {replay_report.replay_run_id}")
    print(f"Same final decision: {replay_report.same_final_decision}")
    print(f"Same reason codes:   {replay_report.same_reason_codes}")
    print(f"Confidence delta:    {replay_report.confidence_delta:+.3f}")
    print("\nAgent output changes:")
    for agent_name, agent_diff in replay_report.agent_diffs.items():
        changed_count = len(agent_diff.changed_keys)
        status = OK if changed_count == 0 else FAIL
        print(f"  {status} {agent_name}: {changed_count} changed key(s)")
        if changed_count > 0:
            print(f"    Changed keys: {', '.join(agent_diff.changed_keys[:5])}")
            if len(agent_diff.changed_keys) > 5:
                print(f"    ... and {len(agent_diff.changed_keys) - 5} more")

    if replay_report.notes:
        print("\nNotes:")
        for note in replay_report.notes:
            print(f"  - {note}")

    # Step 5: Validate report has required fields
    print("\n[Step 5] Validating report structure...")
    required_fields = [
        "run_id",
        "replay_run_id",
        "same_final_decision",
        "same_reason_codes",
        "confidence_delta",
        "agent_diffs",
        "notes",
    ]

    missing_fields = []
    for field in required_fields:
        if not hasattr(replay_report, field):
            missing_fields.append(field)

    if missing_fields:
        print(f"{FAIL} Report missing required fields: {', '.join(missing_fields)}")
        sys.exit(1)

    # Validate agent_diffs structure
    required_agents = ["context_agent", "policy_agent", "recommendation_agent"]
    missing_agents = []
    for agent in required_agents:
        if agent not in replay_report.agent_diffs:
            missing_agents.append(agent)

    if missing_agents:
        print(f"{FAIL} Report missing agent diffs: {', '.join(missing_agents)}")
        sys.exit(1)

    # Validate agent diff structure
    for agent_name, agent_diff in replay_report.agent_diffs.items():
        if not hasattr(agent_diff, "original") or not hasattr(agent_diff, "replay"):
            print(f"{FAIL} Agent diff for {agent_name} missing original or replay")
            sys.exit(1)
        if not hasattr(agent_diff, "changed_keys"):
            print(f"{FAIL} Agent diff for {agent_name} missing changed_keys")
            sys.exit(1)

    print(f"{OK} Report structure valid")

    # Final summary
    print("\n" + "=" * 60)
    if replay_report.same_final_decision and replay_report.same_reason_codes:
        print(f"{OK} Smoke test PASSED: Decision replay successful and deterministic")
    else:
        print(f"{WARN} Smoke test PASSED with differences:")
        if not replay_report.same_final_decision:
            print("  - Final decision differs (may indicate LLM non-determinism)")
        if not replay_report.same_reason_codes:
            print("  - Reason codes differ (may indicate LLM non-determinism)")
    print("=" * 60)

    # Exit successfully (differences are expected with LLM non-determinism)
    sys.exit(0)


if __name__ == "__main__":
    main()
