# System Overview

This document describes the end-to-end decision flow of the AI Decision Traceability Engine, explicitly separating deterministic logic, AI reasoning, orchestration, and trace collection.

## Architecture Components

The system consists of four distinct layers:

1. **AI Reasoning Layer**: Three agents that perform LLM-based analysis
2. **Deterministic Orchestration Layer**: Rule-based decision logic that operates on agent outputs
3. **Trace Collection Layer**: Event logging system that captures all execution steps
4. **API/UI Layer**: Interfaces for submitting decisions and viewing results

## End-to-End Decision Flow

### 1. Request Submission

A decision request is submitted via:
- **FastAPI endpoint**: `POST /decision/run`
- **Streamlit UI**: Interactive form interface

The request contains:
- `request_id`: Unique identifier for the request
- `input_payload`: Structured data for decision processing
- `metadata`: Optional contextual information

### 2. Orchestration Initialization

The `DecisionOrchestrator` receives the request and:

1. **Generates a `run_id`**: UUID that uniquely identifies this decision execution
2. **Emits `input_received` trace event**: Logs the incoming request with full payload
3. **Initializes agent graph state**: Prepares state for LangGraph execution

**This is deterministic**: UUID generation and event emission follow fixed algorithms.

### 3. Agent Graph Execution (AI Reasoning)

The orchestrator invokes a LangGraph-based agent workflow with three sequential nodes:

#### 3.1 Context Agent
- **Input**: `input_payload` (raw request data)
- **Process**: LLM analyzes the input to extract structured information
- **Output**: `ContextAgentOutput`
  - `facts`: Explicit facts extracted from input
  - `assumptions`: Assumptions made during extraction
  - `missing_fields`: Fields that are missing or unclear
- **Trace Event**: `agent_output` with source `context_agent`

**This is AI reasoning**: The LLM interprets unstructured input and produces structured output.

#### 3.2 Policy Agent
- **Input**: `context_output` (from Context Agent) + `policy_text` (configured policy)
- **Process**: LLM interprets policy rules in the context of extracted facts
- **Output**: `PolicyAgentOutput`
  - `applicable_rules`: List of policy rules that apply
  - `rule_explanations`: Explanations of rule relevance
  - `ambiguities`: Ambiguities or unclear aspects in policy interpretation
- **Trace Event**: `agent_output` with source `policy_agent`

**This is AI reasoning**: The LLM interprets policy text and maps it to the context.

#### 3.3 Recommendation Agent
- **Input**: `context_output` + `policy_output`
- **Process**: LLM synthesizes a recommendation based on context and policy interpretation
- **Output**: `RecommendationAgentOutput`
  - `recommendation`: Proposed recommendation (not a final decision)
  - `justification`: List of justification entries referencing facts and rules
  - `confidence_self_report`: Agent's self-reported confidence (0.0 to 1.0)
  - `known_risks`: Known risks or uncertainties
- **Trace Event**: `agent_output` with source `recommendation_agent`

**This is AI reasoning**: The LLM produces a recommendation proposal with justification.

### 4. Deterministic Rule Evaluation

After all agents complete, the orchestrator applies deterministic rules:

**Input**: All three agent outputs (`context_output`, `policy_output`, `recommendation_output`)

**Process**: `evaluate_decision_rules()` applies explicit, interpretable rules in priority order:

1. **Rule 1**: If `missing_fields` is non-empty → `decision = "reject"`, reason code `REJECT_MISSING_FIELDS`
2. **Rule 2**: If `ambiguities` exist → `decision = "review"`, reason code `REVIEW_POLICY_AMBIGUITIES`
3. **Rule 3**: If `confidence_self_report < 0.5` → `decision = "escalate"`, reason code `ESCALATE_LOW_CONFIDENCE`
4. **Rule 4**: If recommendation is empty → `decision = "reject"`, reason code `REJECT_EMPTY_RECOMMENDATION`
5. **Rule 5**: If `known_risks` count > 3 → `decision = "review"`, reason code `REVIEW_HIGH_RISK_COUNT`
6. **Default**: If no rules trigger → `decision = "accept"`, reason code `ACCEPT_RECOMMENDATION`

**Output**: Dictionary with `decision` (str) and `reason_codes` (list[str])

**Trace Event**: `rule_evaluation` with source `orchestrator`

**This is deterministic**: Rules are explicit Python logic with no LLM involvement. The same inputs always produce the same outputs.

### 5. Confidence Score Calculation

The orchestrator calculates a final confidence score:

**Input**:
- `agent_confidence`: From `recommendation_output.confidence_self_report`
- `missing_fields_count`: From `context_output.missing_fields`
- `ambiguities_count`: From `policy_output.ambiguities`
- `triggered_rules_count`: From `rule_result["reason_codes"]`

**Process**: `calculate_confidence_score()` applies weighted formula:
- Base: `agent_confidence * 0.6`
- Penalty: `-min(missing_fields_count * 0.1, 0.2)`
- Penalty: `-min(ambiguities_count * 0.05, 0.15)`
- Penalty: `-min(max(triggered_rules_count - 1, 0) * 0.02, 0.05)`
- Final: Clamped to [0.0, 1.0]

**Output**: `confidence_score` (float between 0.0 and 1.0)

**This is deterministic**: The formula is fixed and produces the same output for the same inputs.

### 6. Final Decision Production

The orchestrator produces the final `DecisionResult`:

- `run_id`: The unique identifier for this execution
- `final_decision`: The decision from rule evaluation (`"accept"`, `"reject"`, `"review"`, or `"escalate"`)
- `confidence_score`: The calculated confidence score
- `reason_codes`: List of reason codes explaining the decision
- `created_at`: Timestamp of result creation

**Trace Event**: `final_decision` with source `orchestrator`

**This is deterministic**: The result is assembled from deterministic rule outputs.

### 7. Trace Collection

Throughout execution, trace events are emitted and written to disk:

**Trace Event Types**:
1. `input_received`: When request is received
2. `agent_output`: When each agent completes (three events)
3. `rule_evaluation`: When deterministic rules are evaluated
4. `final_decision`: When final decision is produced

**Storage**: Events are written to `data/traces/{run_id}.jsonl` in JSONL format (one event per line, append-only).

**This is deterministic**: Event emission follows fixed patterns, and file writes are append-only.

## Separation of Concerns

### Deterministic Logic
- UUID generation
- Rule evaluation (`evaluate_decision_rules`)
- Confidence calculation (`calculate_confidence_score`)
- Trace event emission
- File I/O operations

**Guarantee**: Same inputs → same outputs, no randomness.

### AI Reasoning
- Context extraction (Context Agent)
- Policy interpretation (Policy Agent)
- Recommendation synthesis (Recommendation Agent)

**Note**: LLM outputs may vary between runs with identical inputs due to model non-determinism.

### Orchestration
- Agent graph execution coordination
- State management between agents
- Error handling and validation
- Result assembly

**Responsibility**: Ensures agents execute in correct order and outputs are validated before rule evaluation.

### Trace Collection
- Event serialization
- File writing (`write_trace_event`)
- Event structure (`TraceEvent` model)

**Responsibility**: Captures all execution steps for auditability without affecting decision logic.

## Decision Authority

**Critical Principle**: The `DecisionOrchestrator` is the final authority for decisions. No LLM makes final decisions. Agents produce structured outputs that are evaluated by deterministic rules.

The recommendation agent produces a `recommendation` field, but this is a proposal, not a decision. The final decision comes from `evaluate_decision_rules()`, which operates on agent outputs using explicit logic.

## Execution Guarantees

1. **Traceability**: Every decision execution produces a complete trace log with all agent outputs and rule evaluations.
2. **Deterministic Final Decision**: Given the same agent outputs, the final decision is always the same.
3. **Agent Output Validation**: Agent outputs are validated against Pydantic schemas before rule evaluation.
4. **Error Handling**: If agent outputs are missing or invalid, the orchestrator raises exceptions rather than proceeding.

## Current Limitations

- No persistent storage of decision results (results are stored in-memory only)
- Trace files are written to disk but not indexed for querying
- No replay capability for past decisions
- No audit query API endpoints

See `LIMITATIONS.md` for a complete list of system limitations and non-goals.

