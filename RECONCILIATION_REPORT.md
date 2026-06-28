# Reconciliation Report

**Date:** 2026-06-28
**Positioning:** Public reference implementation
**Recommended direction:** Keep polished and modest; do not expand into a
standalone product.

## Executive Summary

The repository now represents a small, reviewable implementation of LLM decision
traceability:

- LLM agents produce structured context, policy, and recommendation outputs.
- Deterministic rules retain final decision authority.
- Decision results and traces are stored as local files.
- Replay re-runs a stored input and reports differences.
- The default policy is public-safe sample text.

The code is useful as reference material for later evaluation/product work. It
should not duplicate Agent Behavior Evals Lab or Agent Evals Pro.

## Implemented Phases

| Phase | Status | Notes |
| --- | --- | --- |
| P0 Repo & Scaffolding | Complete | Python package, source layout, docs |
| P1 Decision & Trace Model | Complete | Pydantic request/result/trace models |
| P2 Agent Graph | Complete | Sequential LangGraph agent flow |
| P3 Orchestration & Guards | Complete | Deterministic rule authority |
| P4 FastAPI API | Complete | Run, metadata, replay endpoints |
| P5 Streamlit UI | Complete | Local run and trace inspection |
| P6 Docs & Limits | Complete | Reconciled for reference positioning |
| P7 Persistent Audit Log | Complete | JSON decisions and JSONL traces |
| P8 Replay Engine | Complete | Replay endpoint and diff helpers |
| P9 Audit Query API | Deferred | Out of scope for reference repo |
| P10 Governance Diagrams | Deferred | Not needed unless kept lightweight |
| P11 Hardening & Evaluation Hooks | Deferred | Belongs in eval/product repos |

## Current Source Of Truth

- `README.md`: public overview and setup.
- `LIMITATIONS.md`: explicit non-goals and privacy boundaries.
- `SYSTEM_OVERVIEW.md`: runtime flow.
- `PRODUCTION_CONTRACT.md`: modest reference contract.
- `docs/api/REPLAY_ENDPOINT.md`: replay API behavior.
- `src/vision/ProjectVision.ts`: phase status.
- `config/reference_policy.md`: sample policy text.

## Persistence And Replay Status

API and Streamlit flows persist decisions through `FileDecisionStore`.

Replay requires both:

- `data/decisions/{run_id}.json`
- `data/traces/{run_id}.jsonl`

Replay saves a new decision result and trace under `replay_run_id`, then returns
a `ReplayReport`. It does not guarantee identical outputs because the LLM agents
are called again.

## Public Hygiene Status

- Local generated traces, decisions, SQLite databases, `.env`, virtual
  environments, pycache, and egg-info are ignored.
- Docs and examples use placeholders rather than real secrets.
- The public sample policy contains no private business data.
- `run_id` file artifacts are constrained to safe filename tokens.

## PR #1 Position

PR #1 (`phase-7-sqlite-persistence`) should be superseded or closed, not merged
blindly. It is old, conflicts with `main`, removes newer replay/config/docs work,
and hardcodes LM Studio behavior. The only idea worth preserving was local trace
persistence, and `main` already has a simpler public-reference file path.

## Recommendation

Keep this repository active only for small reference-quality maintenance:

- tests for deterministic helpers,
- clearer docs,
- sanitized examples,
- small trace/replay improvements.

Do not add dashboards, SaaS workflows, broad provider integrations, or
commercial governance layers here. If no further reference improvements are
needed, archive it as a polished public reference.
