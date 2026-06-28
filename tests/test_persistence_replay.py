import os
import tempfile
import unittest
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from src.core.decision_models import DecisionRequest, DecisionResult
from src.persistence.artifact_paths import artifact_path
from src.persistence.decision_store import FileDecisionStore
from src.replay.replay_engine import (
    diff_dicts,
    extract_agent_outputs,
    extract_input_event,
    load_trace_events,
    replay_decision,
)
from src.tracing.trace_models import TraceEvent
from src.tracing.trace_writer import write_trace_event


@contextmanager
def temporary_cwd():
    original = Path.cwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        try:
            yield Path(temp_dir)
        finally:
            os.chdir(original)


def make_result(run_id: str) -> DecisionResult:
    return DecisionResult(
        run_id=run_id,
        final_decision="accept",
        confidence_score=0.5,
        reason_codes=["ACCEPT_RECOMMENDATION"],
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def make_event(
    run_id: str,
    event_type: str,
    source: str,
    payload: dict,
    second: int,
) -> TraceEvent:
    return TraceEvent(
        event_id=f"{run_id}-{event_type}-{second}",
        run_id=run_id,
        event_type=event_type,
        source=source,
        payload=payload,
        timestamp=datetime(2026, 1, 1, 12, 0, second, tzinfo=timezone.utc),
    )


class ArtifactPathTests(unittest.TestCase):
    def test_artifact_path_accepts_safe_run_id(self):
        self.assertEqual(
            artifact_path("data/traces", "run-123_ABC", ".jsonl"),
            Path("data/traces/run-123_ABC.jsonl"),
        )

    def test_artifact_path_rejects_path_traversal(self):
        with self.assertRaises(ValueError):
            artifact_path("data/traces", "../secret", ".jsonl")


class DecisionStoreTests(unittest.TestCase):
    def test_save_load_exists_with_temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileDecisionStore(base_dir=temp_dir)
            result = make_result("run-123")

            store.save(result)
            loaded = store.load(result.run_id)

            self.assertTrue(store.exists(result.run_id))
            self.assertEqual(loaded, result)

    def test_load_invalid_run_id_returns_none(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FileDecisionStore(base_dir=temp_dir)

            self.assertIsNone(store.load("../secret"))
            self.assertFalse(store.exists("../secret"))


class TraceSerializationTests(unittest.TestCase):
    def test_write_and_load_trace_events_sorted(self):
        with temporary_cwd():
            later = make_event("run-123", "final_decision", "orchestrator", {"final_decision": "accept"}, 2)
            earlier = make_event("run-123", "input_received", "orchestrator", {"input_payload": {"x": 1}}, 1)

            write_trace_event(later)
            write_trace_event(earlier)

            loaded = load_trace_events("run-123")

            self.assertEqual([event.event_type for event in loaded], ["input_received", "final_decision"])

    def test_malformed_trace_event_raises_value_error(self):
        with temporary_cwd():
            trace_dir = Path("data/traces")
            trace_dir.mkdir(parents=True)
            (trace_dir / "run-123.jsonl").write_text("{not-json}\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_trace_events("run-123")


class ReplayHelperTests(unittest.TestCase):
    def test_extract_input_event_and_agent_outputs(self):
        events = [
            make_event("run-123", "input_received", "orchestrator", {"input_payload": {"x": 1}}, 1),
            make_event("run-123", "agent_output", "context_agent", {"facts": ["x"]}, 2),
            make_event("run-123", "agent_output", "policy_agent", {"applicable_rules": ["r1"]}, 3),
        ]

        self.assertEqual(extract_input_event(events).payload["input_payload"], {"x": 1})
        self.assertEqual(
            extract_agent_outputs(events),
            {
                "context_agent": {"facts": ["x"]},
                "policy_agent": {"applicable_rules": ["r1"]},
            },
        )

    def test_diff_dicts_reports_changed_added_and_removed_keys(self):
        self.assertEqual(
            diff_dicts({"a": 1, "b": 2}, {"b": 3, "c": 4}),
            ["a", "b", "c"],
        )


class FakeOrchestrator:
    def run_decision(self, request: DecisionRequest, run_id_override: str | None = None) -> DecisionResult:
        run_id = run_id_override or "fake-replay-run"
        write_trace_event(
            make_event(
                run_id,
                "agent_output",
                "context_agent",
                {"facts": ["x"], "assumptions": [], "missing_fields": []},
                2,
            )
        )
        write_trace_event(
            make_event(
                run_id,
                "agent_output",
                "policy_agent",
                {"applicable_rules": ["rule-1"], "rule_explanations": {}, "ambiguities": []},
                3,
            )
        )
        write_trace_event(
            make_event(
                run_id,
                "agent_output",
                "recommendation_agent",
                {"recommendation": "approve", "confidence_self_report": 0.8},
                4,
            )
        )
        return make_result(run_id)


class ReplayDecisionTests(unittest.TestCase):
    def test_replay_decision_uses_persisted_input_and_saves_replay_result(self):
        with temporary_cwd():
            original_run_id = "run-123"
            store = FileDecisionStore()
            store.save(make_result(original_run_id))
            write_trace_event(
                make_event(
                    original_run_id,
                    "input_received",
                    "orchestrator",
                    {
                        "request_id": "request-123",
                        "input_payload": {"x": 1},
                        "metadata": {"case": "test"},
                    },
                    1,
                )
            )
            for event in [
                make_event(original_run_id, "agent_output", "context_agent", {"facts": ["x"]}, 2),
                make_event(original_run_id, "agent_output", "policy_agent", {"applicable_rules": ["rule-1"]}, 3),
                make_event(original_run_id, "agent_output", "recommendation_agent", {"recommendation": "approve"}, 4),
            ]:
                write_trace_event(event)

            report = replay_decision(FakeOrchestrator(), original_run_id)

            self.assertTrue(report.same_final_decision)
            self.assertTrue(report.same_reason_codes)
            self.assertTrue(FileDecisionStore().exists(report.replay_run_id))
            self.assertEqual(set(report.agent_diffs), {"context_agent", "policy_agent", "recommendation_agent"})


if __name__ == "__main__":
    unittest.main()
