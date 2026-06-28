# Reference Implementation Contract

This file documents what the repository does and does not guarantee. The file
name is retained for continuity, but the project is positioned as a reference
implementation and single-node prototype.

## Scope

The implementation demonstrates:

- Structured LLM agent outputs.
- Deterministic final rule evaluation.
- Local trace and decision persistence.
- Replay diffs for a stored decision input.
- A configurable public-safe policy text path.

It does not provide production-grade security, reliability, governance, or
compliance controls.

## Determinism Contract

Deterministic for identical inputs:

- `evaluate_decision_rules`
- `calculate_confidence_score`
- JSON serialization of a given trace or decision object
- Decision-store path validation and atomic decision JSON replacement

Not deterministic across full LLM runs:

- Context agent output
- Policy agent output
- Recommendation agent output
- Replay agent outputs
- Final decisions when agent outputs differ
- Generated UUIDs and timestamps

The important boundary is: LLMs do not make the final decision. They produce
structured inputs to deterministic rules.

## Persistence Contract

Decision results:

- Stored at `data/decisions/{run_id}.json`
- Written through a temp file and `os.replace`
- Loaded by `FileDecisionStore`

Trace events:

- Stored at `data/traces/{run_id}.jsonl`
- Appended one JSON event per line
- Flushed after each event

Replay:

- Loads the original decision result and trace.
- Extracts the original request input from the trace.
- Runs a new decision under a new `replay_run_id`.
- Saves the replay decision result and trace.
- Returns a `ReplayReport` comparing original and replay outputs.

Local artifact paths constrain `run_id` to safe filename tokens before reading or
writing files.

## Configuration Contract

Provider selection:

- `LLM_PROVIDER=openai` uses `OPENAI_API_KEY`, `OPENAI_MODEL`, and optional
  `OPENAI_BASE_URL`.
- `LLM_PROVIDER=ollama` or `LLM_PROVIDER=lmstudio` uses `LLM_MODEL` and
  `LLM_BASE_URL`.
- For older local-provider configs, `OPENAI_MODEL` and `OPENAI_BASE_URL` are
  still accepted as fallbacks.

Policy text:

- `POLICY_PATH` defaults to `config/reference_policy.md`.
- The file must exist and contain non-empty text.
- Policy versions are not persisted with decisions.

## Operational Assumptions

- Single process or externally coordinated access.
- Writable local `data/` directory.
- Configured LLM endpoint is available when agents run.
- No automatic cleanup, backup, or artifact retention policy.
- No sensitive data is submitted because traces are not redacted.

## Not Provided

- Authentication or authorization.
- Tenant isolation.
- Encryption at rest.
- Redaction.
- Distributed locking.
- High availability.
- Monitoring, alerting, or SLAs.
- Compliance evidence.

This contract is deliberately modest. It should make the reference project easy
to review without implying readiness for real operational use.
