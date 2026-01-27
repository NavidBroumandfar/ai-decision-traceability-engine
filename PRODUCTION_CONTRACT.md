# Production Contract

## Purpose & Non-Goals

This document defines the production guarantees, assumptions, and limitations of the AI Decision Traceability Engine. It explicitly states what is deterministic vs non-deterministic, what is guaranteed, persistence guarantees, and operational assumptions.

**Non-Goals:**
- This is not an enterprise-grade system with distributed coordination, high availability, or automatic failover
- This is not a multi-tenant system with isolation guarantees
- This does not provide real-time replication or backup automation
- This does not guarantee sub-second response times or SLA commitments

## Determinism Contract

### Deterministic Components

The following components produce identical outputs for identical inputs:

- **Rule Evaluation** (`evaluate_decision_rules`): Explicit Python logic that evaluates agent outputs against fixed rules. Same agent outputs → same decision and reason codes.
- **Confidence Calculation** (`calculate_confidence_score`): Fixed weighted formula combining agent confidence, missing fields, ambiguities, and triggered rules. Same inputs → same confidence score.
- **Persistence Write Semantics**: Atomic file writes using temp file + `os.replace()`. Either the file is fully written or not written at all (no partial writes).
- **UUID Generation**: Standard UUID4 generation for `run_id` (deterministic algorithm, non-deterministic values).
- **Trace Event Emission**: Fixed event structure and serialization. Same execution → same trace events.

### Non-Deterministic Components

The following components may produce different outputs for identical inputs:

- **LLM Agent Outputs**: Context Agent, Policy Agent, and Recommendation Agent outputs are non-deterministic. Even with `temperature=0`, LLM outputs may vary due to:
  - Model implementation differences
  - External API non-determinism
  - Model updates on provider side
- **External LLM Availability**: LLM endpoint availability, rate limits, and response times are not guaranteed.
- **File System Timing**: While writes are atomic, the exact timing of when files appear on disk depends on OS buffering and disk I/O.

**Implication**: Given the same `input_payload`, the final decision may differ if agent outputs differ. The deterministic layer (rules + confidence) ensures that if agent outputs are identical, the final decision is identical.

## Persistence Contract

### What Gets Persisted

- **Decision Results**: JSON files at `data/decisions/{run_id}.json`
  - Contains: `run_id`, `final_decision`, `confidence_score`, `reason_codes`, `created_at`
  - Format: Pretty-printed JSON (indent=2)
- **Trace Events**: JSONL files at `data/traces/{run_id}.jsonl`
  - Contains: All execution events (input_received, agent_output, rule_evaluation, final_decision)
  - Format: One JSON object per line (append-only)

### Write Semantics

- **Decision Results**: Atomic write using temp file + `os.replace()`. Either the file exists with complete data or does not exist.
- **Trace Events**: Append-only writes. Each event is flushed immediately after write (`f.flush()`). No atomicity guarantee across multiple events in the same file.
- **Directory Creation**: Directories are created automatically if missing (`mkdir(parents=True, exist_ok=True)`).

### File Locations

All persistent data is stored under the `data/` directory:
- `data/decisions/` - Decision result JSON files
- `data/traces/` - Trace event JSONL files

### Single-Node Assumption

This system assumes a single-node deployment:
- No distributed coordination or locking
- No concurrent write protection across processes
- File system is the source of truth (no database)
- If multiple processes write to the same `run_id`, behavior is undefined (last write wins)

**Recommendation**: Run one orchestrator instance per deployment, or implement external coordination if multiple instances are required.

## Compatibility & Schema Versioning

### Current State

- Decision result JSON files do not include a `schema_version` field
- Trace event JSONL files do not include a `schema_version` field
- No migration path for schema changes

### Future Recommendation

When adding new fields or changing existing fields:
- Add a `schema_version` field to `DecisionResult` model and persisted JSON
- Add a `schema_version` field to `TraceEvent` model and persisted JSONL
- Implement version-aware deserialization in loaders
- Document migration paths for each schema version

**Note**: This is a recommendation for future work. It is not implemented in the current codebase.

## Operational Assumptions

### Required Environment Variables

- `OPENAI_BASE_URL`: Base URL for LLM API (e.g., `http://localhost:11434/v1` for Ollama, or empty for OpenAI)
- `OPENAI_API_KEY`: API key for LLM provider (can be empty for local models)
- `OPENAI_MODEL`: Model name/identifier (e.g., `llama3.2`, `gpt-4o-mini`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

These are loaded from `.env` file in the project root via `pydantic_settings`.

### LLM Endpoint Availability

- The system assumes the LLM endpoint is available when agents are invoked
- No retry logic or circuit breakers are implemented
- If the LLM endpoint is unavailable, agent execution will fail and the decision request will fail
- No fallback to alternative endpoints

### Key Rotation

To rotate API keys:
1. Update the `OPENAI_API_KEY` value in `.env`
2. Restart the application process
3. No in-flight requests are affected (each request uses the current key)

### Policy Text

- Policy text is provided at orchestrator initialization (`DecisionOrchestrator(policy_text=...)`)
- Policy text changes require orchestrator reinitialization
- No runtime policy updates

## If You Deploy This

**Pre-Deployment Checklist:**

- [ ] Set required environment variables in `.env` or deployment environment
- [ ] Ensure `data/decisions/` and `data/traces/` directories are writable
- [ ] Verify LLM endpoint is accessible and credentials are valid
- [ ] Configure log level appropriate for production (`INFO` or `WARNING`)
- [ ] Ensure sufficient disk space for decision and trace files
- [ ] Set up backup strategy for `data/` directory (this system does not provide automated backups)
- [ ] Configure process management (systemd, supervisor, etc.) to ensure single instance
- [ ] Review and set appropriate file permissions for `data/` directory
- [ ] Test decision flow end-to-end with sample inputs
- [ ] Monitor disk usage (trace files grow over time)

**Post-Deployment Monitoring:**

- Monitor disk usage in `data/` directory
- Monitor LLM API rate limits and costs
- Review trace files for errors or anomalies
- Ensure decision results are being persisted correctly

**Limitations to Accept:**

- Single-node deployment only
- No automatic backups or replication
- No query API for historical decisions (planned for P9)
- No replay capability (planned for P8)
- LLM outputs are non-deterministic
- No retry logic for LLM failures
