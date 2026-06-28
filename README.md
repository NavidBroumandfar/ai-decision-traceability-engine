# AI Decision Traceability Engine

A public reference implementation for LLM-assisted decision traceability.

This repository demonstrates a small governed decision flow where LLM agents
produce structured intermediate outputs, deterministic Python rules make the
final decision, and local trace artifacts make the run inspectable and replayable.

It is intentionally scoped as a single-node prototype, not a standalone serious
product or enterprise platform.

## What It Shows

- Three-agent LLM workflow: context extraction, policy interpretation, and
  recommendation.
- Deterministic final decision rules that operate on agent outputs.
- Local JSON/JSONL persistence for decision results and trace events.
- Replay support that re-runs a stored decision input and reports output diffs.
- A public-safe sample policy at `config/reference_policy.md`.
- Focused tests for deterministic logic and local persistence without live LLM
  calls.

## What It Does Not Claim

- It does not guarantee globally deterministic decisions across LLM runs.
- It does not provide authentication, authorization, tenant isolation, PII
  redaction, encryption at rest, backups, queues, or high availability.
- It does not provide an audit search API, dashboard, or commercial workflow.
- It is not a compliance-certified system.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

### Local Provider Example

```env
ENV=local
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_BASE_URL=http://localhost:11434/v1
POLICY_PATH=config/reference_policy.md
LOG_LEVEL=INFO
```

For LM Studio, use:

```env
LLM_PROVIDER=lmstudio
LLM_MODEL=<local-model-name>
LLM_BASE_URL=http://localhost:1234/v1
```

### OpenAI Example

```env
ENV=local
LLM_PROVIDER=openai
OPENAI_API_KEY=<OPENAI_API_KEY>
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=
POLICY_PATH=config/reference_policy.md
```

For local providers, `LLM_MODEL` and `LLM_BASE_URL` are preferred. The code still
falls back to `OPENAI_MODEL` and `OPENAI_BASE_URL` for older local-provider
configs, but new examples should use `LLM_*`.

## Run

FastAPI:

```bash
source .venv/bin/activate
uvicorn src.api.app:app
```

Streamlit:

```bash
source .venv/bin/activate
python -m streamlit run src/ui/app.py
```

## Replay

Replay requires both:

- `data/decisions/{run_id}.json`
- `data/traces/{run_id}.jsonl`

API and Streamlit-created decisions are persisted to both stores. Replay creates
a new trace and decision result under a new `replay_run_id`, then returns a diff
report:

```bash
curl -X POST http://127.0.0.1:8000/decision/<RUN_ID>/replay
```

The deterministic rules are stable for identical agent outputs. The LLM agent
outputs themselves may vary between original and replay runs.

## Tests

Default tests do not call a live LLM:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Syntax/import check:

```bash
.venv/bin/python -m compileall -q src scripts tests
```

Optional live replay smoke test:

```bash
.venv/bin/python scripts/smoke_p8_replay.py
```

The smoke test requires a configured provider and running LLM endpoint.

## Local Artifacts And Privacy

Decision results, trace files, SQLite databases, `.env`, and virtual
environments are ignored by git. The trace writer stores full request and agent
payloads without redaction, so do not submit secrets, private customer data, or
regulated data to this reference implementation.

## Project Status

The useful reference ideas are the decision trace model, deterministic final
authority boundary, replay diff helpers, and small policy-loading path. Future
serious product work should happen in a product/evaluation repo rather than
expanding this repository into a SaaS surface.
