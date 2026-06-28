# Limitations And Non-Goals

This repository is a public reference implementation for LLM decision
traceability. It is useful for studying the mechanics of traces, deterministic
rule authority, and replay diffs. It is not a hardened product.

## Current Capabilities

- Runs a three-agent LLM workflow.
- Applies deterministic final decision rules to structured agent outputs.
- Persists decision results to `data/decisions/{run_id}.json`.
- Persists trace events to `data/traces/{run_id}.jsonl`.
- Replays a stored decision input and returns a structured diff report.
- Loads public-safe policy text from `POLICY_PATH`, defaulting to
  `config/reference_policy.md`.

## Replay Limitations

Replay is implemented, but it is not a forensic guarantee.

- Replay requires both the original decision JSON and trace JSONL files.
- Replay calls the configured LLM provider again, so agent outputs can differ.
- The final decision is deterministic only for identical agent outputs.
- Policy text is loaded from the current configured policy file; policy versions
  are not stored with each decision.
- There is no schema migration layer for old trace or decision artifacts.

## Trace Privacy Limitations

Trace files store full payloads.

- No PII redaction.
- No sensitive-field filtering.
- No encryption at rest.
- No access control around local artifact files.
- No retention policy or cleanup automation.

Do not use private customer data, secrets, credentials, regulated data, or
production payloads in this repository.

## API And UI Limitations

- No authentication or authorization.
- No tenant isolation.
- No rate limiting or cost controls.
- No queueing, retries, circuit breakers, or fallback providers.
- No audit search/query API beyond basic run metadata and replay.
- Streamlit is a local inspection interface, not an admin product.

## Persistence Limitations

- File-based storage only.
- Single-node assumption.
- No cross-process locking.
- No indexing or aggregation.
- No backups or replication.
- Generated artifacts are intentionally ignored by git.

## Decision Quality Limitations

- The system does not guarantee decision correctness.
- The confidence score is a deterministic heuristic, not calibrated against
  ground truth.
- Rules are hardcoded and generic.
- Input payloads are not domain-schema validated.
- LLM outputs can be incomplete, wrong, or inconsistent.

## Non-Goals

- Enterprise deployment platform.
- Compliance-certified audit system.
- Multi-tenant SaaS application.
- Commercial dashboard or workflow layer.
- Broad provider abstraction beyond simple OpenAI-compatible local/OpenAI
  configuration.

## Best Use

Use this repo as a polished, sanitized example of traceability mechanics. Carry
the durable ideas into evaluation/product repositories only after validating a
real product need.
