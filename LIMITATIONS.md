# System Limitations and Non-Goals

This document explicitly states what the system does NOT do, known limitations, and what the system intentionally does NOT guarantee.

## Explicit Non-Goals

### 1. Persistent Decision Storage
**✅ COMPLETED in Phase 7**

- Decision results are now stored persistently in `data/decisions/{run_id}.json`
- Results survive server restarts
- File-based storage with atomic writes
- Trace events stored in `data/traces/{run_id}.jsonl`

**Note**: While storage is persistent, query capabilities are still limited (see Audit Query API below).

### 2. Decision Replay
**The system does NOT support replaying past decisions.**

- Cannot re-execute a decision using stored inputs
- Cannot verify decision consistency over time
- No versioning of decision logic

**Rationale**: Decision replay is planned for Phase 8 (Decision Replay Engine).

### 3. Audit Query API
**The system does NOT provide read-only API endpoints for querying decisions.**

- No endpoints to search decisions by criteria
- No endpoints to retrieve decision history
- No endpoints to aggregate decision statistics
- Trace files exist but are not queryable via API

**Rationale**: Audit query API is planned for Phase 9 (Audit Query API Surface).

### 4. Real-Time Monitoring
**The system does NOT provide real-time monitoring or alerting.**

- No metrics collection
- No performance monitoring
- No alerting for decision anomalies
- No dashboards for system health

**Rationale**: Monitoring and evaluation hooks are planned for Phase 11 (Hardening & Evaluation Hooks).

### 5. Multi-Tenancy or Access Control
**The system does NOT provide multi-tenancy or access control.**

- No user authentication
- No authorization checks
- No tenant isolation
- No role-based access control

**Rationale**: This is outside the current project scope.

### 6. Policy Versioning
**The system does NOT track policy versions or changes.**

- Policy text is configured at orchestrator initialization
- No history of policy changes
- No ability to associate decisions with specific policy versions
- No policy rollback capability

**Rationale**: Policy versioning is not in the current project scope.

### 7. LLM Output Determinism
**The system does NOT guarantee deterministic LLM outputs.**

- Agent outputs may vary between runs with identical inputs
- LLM non-determinism is inherent to the model
- No seed or temperature control in current implementation
- Rule evaluation is deterministic, but agent outputs are not

**Rationale**: This is a known limitation of LLM-based systems.

## Known System Limitations

### 1. File-Based Result Storage
**Current State**: Decision results are stored in JSON files at `data/decisions/{run_id}.json`.

**Limitations**:
- No indexing or querying capabilities (files must be read individually)
- No automatic cleanup or archival
- No compression
- Not suitable for high-volume production workloads without additional infrastructure

**Impact**: Results persist across restarts, but querying requires reading individual files.

### 2. Trace File Management
**Current State**: Trace events are written to `data/traces/{run_id}.jsonl` files.

**Limitations**:
- No indexing or querying capabilities
- No automatic cleanup or archival
- No compression
- No ability to search across traces
- Files must be read manually to retrieve trace data

**Impact**: Trace data exists but is not easily accessible programmatically.

### 3. Single Policy Configuration
**Current State**: Policy text is set at orchestrator initialization.

**Limitations**:
- Cannot change policy without restarting the server
- All decisions use the same policy
- No per-request policy selection
- No policy testing or validation

**Impact**: Policy changes require server restart.

### 4. No Input Validation
**Current State**: Input payloads are accepted as `dict[str, Any]` with minimal validation.

**Limitations**:
- No schema validation for input payloads
- No type checking beyond Pydantic model validation
- Invalid inputs may cause agent failures
- No input sanitization

**Impact**: Invalid inputs may cause unexpected errors or produce incorrect results.

### 5. No Rate Limiting
**Current State**: API endpoints accept requests without rate limiting.

**Limitations**:
- No protection against request flooding
- No per-client rate limits
- No cost controls for LLM API calls
- No queue management for concurrent requests

**Impact**: System may be overwhelmed by high request volumes.

### 6. No Error Recovery
**Current State**: Errors in agent execution or rule evaluation cause request failures.

**Limitations**:
- No retry logic for transient failures
- No fallback mechanisms
- No partial result handling
- Errors propagate to the client immediately

**Impact**: Transient failures cause request failures with no automatic recovery.

### 7. No Confidence Calibration
**Current State**: Confidence scores are calculated using a fixed formula.

**Limitations**:
- Formula weights are not calibrated against ground truth
- No validation that confidence scores correlate with decision accuracy
- No confidence threshold tuning
- Formula is heuristic-based, not data-driven

**Impact**: Confidence scores may not accurately reflect decision reliability.

### 8. Limited Rule Coverage
**Current State**: Decision rules cover basic cases (missing fields, ambiguities, low confidence, etc.).

**Limitations**:
- Rules are hardcoded and not configurable
- No domain-specific rule customization
- Rules may not cover all edge cases
- Rule priority is fixed

**Impact**: Some decision scenarios may not be handled by existing rules.

### 9. No Agent Output Caching
**Current State**: Agent outputs are computed fresh for every request.

**Limitations**:
- No caching of agent outputs for identical inputs
- No memoization of policy interpretations
- Every request incurs full LLM API costs
- No optimization for repeated queries

**Impact**: Higher latency and cost for repeated or similar requests.

### 10. No Trace Privacy Controls
**Current State**: All trace events are written to disk with full payloads.

**Limitations**:
- No PII redaction
- No sensitive data filtering
- No encryption at rest
- No access controls on trace files

**Impact**: Trace files may contain sensitive information without protection.

## What the System Does NOT Guarantee

### 1. Decision Correctness
**The system does NOT guarantee that decisions are correct.**

- Decisions are based on LLM outputs, which may be incorrect
- Rule logic may not cover all scenarios
- No ground truth validation
- No accuracy metrics

### 2. Decision Consistency
**The system does NOT guarantee consistent decisions for identical inputs.**

- LLM outputs may vary between runs
- Agent outputs are non-deterministic
- Only rule evaluation is deterministic (but operates on non-deterministic inputs)

### 3. Performance SLAs
**The system does NOT guarantee performance characteristics.**

- No latency guarantees
- No throughput guarantees
- No availability guarantees
- Performance depends on LLM API response times

### 4. Data Retention
**The system does NOT guarantee data retention.**

- Trace files are not automatically archived
- No retention policies
- No backup mechanisms
- Data may be lost if files are deleted

### 5. Compliance
**The system does NOT guarantee regulatory compliance.**

- No HIPAA, GDPR, or other compliance certifications
- No audit trail validation
- No data protection guarantees
- Compliance must be evaluated separately

### 6. Security
**The system does NOT guarantee security.**

- No authentication or authorization
- No encryption in transit (unless provided by deployment)
- No encryption at rest for trace files
- No input sanitization or injection protection

### 7. Scalability
**The system does NOT guarantee scalability.**

- In-memory storage does not scale horizontally
- No load balancing considerations
- No distributed execution
- Performance degrades with high concurrency

## Intended Use Cases

The system is designed for:
- **Development and testing** of decision traceability concepts
- **Prototyping** audit and governance workflows
- **Demonstrating** agent orchestration and deterministic rule evaluation
- **Learning** about AI decision traceability patterns

The system is **NOT** designed for:
- Production workloads requiring high availability
- Systems requiring strict compliance guarantees
- High-throughput decision processing
- Multi-tenant SaaS deployments

## Future Improvements

Many limitations will be addressed in future phases:
- **Phase 7**: Persistent audit log storage
- **Phase 8**: Decision replay capability
- **Phase 9**: Audit query API
- **Phase 10**: Governance documentation and architecture diagrams
- **Phase 11**: Hardening and evaluation hooks

See `ProjectVision.ts` for the complete project roadmap.

