# System Overview

This document describes the reference implementation flow and separates LLM
reasoning from deterministic decision authority.

## Layers

1. API/UI layer: FastAPI and Streamlit entry points.
2. Policy configuration: `POLICY_PATH`, defaulting to
   `config/reference_policy.md`.
3. LLM reasoning layer: context, policy, and recommendation agents.
4. Deterministic orchestration layer: final rules and confidence calculation.
5. Trace and persistence layer: JSON decision files and JSONL trace files.
6. Replay layer: stored-input re-execution and diff reporting.

## Decision Flow

1. A request is submitted through `POST /decision/run` or the Streamlit UI.
2. The orchestrator assigns a `run_id` and writes an `input_received` trace
   event.
3. The context agent extracts facts, assumptions, and missing fields.
4. The policy agent interprets the configured policy text against those facts.
5. The recommendation agent proposes a non-authoritative recommendation.
6. `evaluate_decision_rules` makes the final decision from agent outputs.
7. `calculate_confidence_score` computes a deterministic heuristic confidence
   value.
8. The trace writer appends events to `data/traces/{run_id}.jsonl`.
9. API and UI flows save the result to `data/decisions/{run_id}.json`.

## Decision Authority

The LLM agents never make the final decision. The final decision comes from
deterministic Python rules operating on structured agent outputs.

This means:

- Same agent outputs produce the same final decision and confidence score.
- Same raw request does not guarantee the same agent outputs across LLM runs.
- Replay is a comparison tool, not proof of global LLM determinism.

## Replay Flow

`POST /decision/{run_id}/replay`:

1. Loads the original decision JSON.
2. Loads the original trace JSONL.
3. Extracts the original input payload and metadata from `input_received`.
4. Runs the orchestrator again under a new `replay_run_id`.
5. Saves the replay decision and trace.
6. Compares final decisions, reason codes, confidence, and per-agent outputs.

Replay requires a configured live LLM provider. Default tests avoid live
provider calls by using deterministic helpers and fake orchestrators.

## Persistence

- Decisions: `data/decisions/{run_id}.json`
- Traces: `data/traces/{run_id}.jsonl`
- Local SQLite files such as `audit_log.db` are ignored artifacts, not the
  active persistence path on `main`.

All generated artifacts are local and ignored by git.

## Privacy Boundary

Trace events include full input and agent payloads. There is no redaction,
encryption, access control, or retention policy. Do not use sensitive or private
payloads in this reference implementation.

## Current Status

The repository is coherent as a polished public reference implementation. Future
work should favor tests, docs, and small traceability examples rather than
turning this repo into a product surface.
