# Replay API Endpoint

## Overview

The replay endpoint re-executes a past decision using persisted decision and trace data, then returns a structured report comparing the original run with the replayed run. It does **not** mutate or overwrite the original `run_id` files; replay results are stored under a new `replay_run_id`.

## Endpoint

**POST** `/decision/{run_id}/replay`

- **Path parameter:** `run_id` (string) — The unique identifier of the decision run to replay.
- **Request body:** None. Input is loaded from the persisted trace for `run_id`.
- **Content-Type:** `application/json` (optional; no body is sent).

### Example request (PowerShell)

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/decision/<RUN_ID>/replay" -ContentType "application/json"
```

Replace `<RUN_ID>` with the `run_id` returned by `POST /decision/run`.

---

## Success response (200 OK)

Response body is a **ReplayReport** JSON:

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | Original decision run ID. |
| `replay_run_id` | string | New run ID created for this replay. |
| `same_final_decision` | boolean | Whether the replayed final decision matches the original. |
| `same_reason_codes` | boolean | Whether the replayed reason codes match the original (order-independent). |
| `confidence_delta` | number | Difference in confidence scores: `replay - original`. |
| `agent_diffs` | object | Per-agent diff. Keys: `context_agent`, `policy_agent`, `recommendation_agent`. Each value has `original`, `replay`, and `changed_keys`. |
| `notes` | array of string | Optional notes (e.g. differences, LLM non-determinism). |

### Example success response

```json
{
  "run_id": "abc-123-original",
  "replay_run_id": "def-456-replay",
  "same_final_decision": true,
  "same_reason_codes": true,
  "confidence_delta": 0.02,
  "agent_diffs": {
    "context_agent": {
      "original": { "summary": "..." },
      "replay": { "summary": "..." },
      "changed_keys": []
    },
    "policy_agent": { "original": {}, "replay": {}, "changed_keys": [] },
    "recommendation_agent": { "original": {}, "replay": {}, "changed_keys": [] }
  },
  "notes": []
}
```

---

## Error responses

All error responses use a consistent JSON shape where applicable: `{ "error": "...", "detail": "..." }`.

| Status | Condition | Response |
|--------|-----------|----------|
| **404** | Decision file missing for `run_id`, or trace file missing. | `{ "error": "Decision or trace not found", "detail": "<message>" }` |
| **400** | Trace exists but does not contain an `input_received` event (malformed or incomplete trace). | `{ "error": "Invalid or incomplete trace", "detail": "<message>" }` |
| **502** | Replay execution failed (e.g. LLM connection or configuration issue). No stacktrace in response. | `{ "error": "Replay execution failed", "detail": "<message>" }` |
| **500** | Unexpected server error. Exception is logged server-side; response is generic. | `{ "error": "Internal server error", "detail": "An unexpected error occurred during replay." }` |

---

## LLM nondeterminism

Agent outputs (context, policy, recommendation) can differ between original and replay runs because LLM responses are not strictly deterministic. The **deterministic rules** (e.g. final decision rules) should remain stable when inputs and policy are unchanged. The `agent_diffs` and `notes` fields in the ReplayReport indicate where outputs differed; `same_final_decision` and `same_reason_codes` indicate whether the governed outcome was stable.

---

## Compatibility

- Works with local providers (e.g. Ollama, LM Studio); OpenAI keys are not required unless configured.
- Does not alter existing behaviour of `/health` or `/decision/run`.
- Uses the same orchestrator instance as `POST /decision/run`.
