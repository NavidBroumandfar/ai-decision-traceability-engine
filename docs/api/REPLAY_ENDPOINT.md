# Replay API Endpoint

## Overview

The replay endpoint re-runs a previously persisted decision input and returns a
structured comparison report. It is intended for reference/debugging use, not as
a forensic guarantee.

Replay requires:

- `data/decisions/{run_id}.json`
- `data/traces/{run_id}.jsonl`

API and Streamlit decisions are persisted to both locations.

## Endpoint

`POST /decision/{run_id}/replay`

- Path parameter: `run_id`
- Request body: none
- Response: `ReplayReport`

Example:

```bash
curl -X POST http://127.0.0.1:8000/decision/<RUN_ID>/replay
```

## Success Response

```json
{
  "run_id": "original-run-id",
  "replay_run_id": "new-replay-run-id",
  "same_final_decision": true,
  "same_reason_codes": true,
  "confidence_delta": 0.0,
  "agent_diffs": {
    "context_agent": {
      "original": {},
      "replay": {},
      "changed_keys": []
    },
    "policy_agent": {
      "original": {},
      "replay": {},
      "changed_keys": []
    },
    "recommendation_agent": {
      "original": {},
      "replay": {},
      "changed_keys": []
    }
  },
  "notes": []
}
```

Fields:

| Field | Meaning |
| --- | --- |
| `run_id` | Original run ID. |
| `replay_run_id` | New run ID created for the replay. |
| `same_final_decision` | Whether the deterministic final decision matched. |
| `same_reason_codes` | Whether reason codes matched, order-independent. |
| `confidence_delta` | Replay confidence minus original confidence. |
| `agent_diffs` | Per-agent original/replay payload comparison. |
| `notes` | Human-readable differences and caveats. |

## Error Responses

| Status | Condition |
| --- | --- |
| 404 | Original decision result or trace file is missing. |
| 400 | Trace exists but is malformed or missing `input_received`. |
| 502 | Replay execution failed, usually due to LLM config or connection. |
| 500 | Unexpected server error; details are logged server-side. |

## Determinism Caveat

Final decision rules are deterministic for identical agent outputs. Replay calls
the LLM agents again, so agent outputs can differ even with the same request,
same policy text, and `temperature=0`.

Use replay to inspect drift and traceability, not to prove global LLM
determinism.
