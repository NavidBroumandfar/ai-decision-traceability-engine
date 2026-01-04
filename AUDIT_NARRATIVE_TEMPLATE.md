# Audit Narrative Template

This template provides a structured, human-readable audit explanation for decision executions. Use this template to generate audit narratives for compliance officers, auditors, and senior engineers.

## Template Structure

```
DECISION EXECUTION AUDIT NARRATIVE
==================================

Run ID: {run_id}
Request ID: {request_id}
Execution Timestamp: {timestamp}
Final Decision: {final_decision}
Confidence Score: {confidence_score}

EXECUTION SUMMARY
-----------------
This decision execution processed a request through a three-agent workflow,
followed by deterministic rule evaluation. The final decision was {final_decision}
with a confidence score of {confidence_score} (on a scale of 0.0 to 1.0).

AGENT EXECUTION FLOW
--------------------
1. Context Agent
   - Extracted {facts_count} facts from the input payload
   - Identified {assumptions_count} assumptions
   - Flagged {missing_fields_count} missing field(s): {missing_fields_list}

2. Policy Agent
   - Identified {applicable_rules_count} applicable policy rule(s)
   - Detected {ambiguities_count} policy ambiguity(ies): {ambiguities_list}

3. Recommendation Agent
   - Proposed recommendation: {recommendation_text}
   - Self-reported confidence: {agent_confidence}
   - Identified {known_risks_count} known risk(s): {known_risks_list}

DETERMINISTIC RULE EVALUATION
------------------------------
The orchestrator applied deterministic rules to agent outputs:

{rule_evaluation_details}

Rule evaluation produced the following reason codes:
{reason_codes_list}

CONFIDENCE CALCULATION
----------------------
The final confidence score was calculated using a weighted formula:
- Base confidence (agent self-report): {agent_confidence} × 0.6 = {base_score}
- Missing fields penalty: -{missing_penalty} (from {missing_fields_count} missing field(s))
- Ambiguities penalty: -{ambiguities_penalty} (from {ambiguities_count} ambiguity(ies))
- Triggered rules penalty: -{rule_penalty} (from {triggered_rules_count} triggered rule(s))
- Final confidence score: {confidence_score}

POLICY ENFORCEMENT
------------------
Policy text was evaluated by the Policy Agent, which identified:
- Applicable rules: {applicable_rules_list}
- Rule explanations: {rule_explanations_dict}

{policy_enforcement_details}

TRACEABILITY
------------
All execution steps were logged to trace file: data/traces/{run_id}.jsonl

Trace events captured:
1. input_received - Request received with payload
2. agent_output (context_agent) - Context extraction completed
3. agent_output (policy_agent) - Policy interpretation completed
4. agent_output (recommendation_agent) - Recommendation generated
5. rule_evaluation - Deterministic rules evaluated
6. final_decision - Final decision produced

AUDIT CONCLUSION
----------------
This decision was processed through a governed workflow with full traceability.
The final decision of {final_decision} was determined by deterministic rule
evaluation operating on AI agent outputs. All execution steps are recorded in
the trace log for review.
```

## Field Substitution Guide

### Basic Fields
- `{run_id}`: The unique identifier for this decision execution (UUID)
- `{request_id}`: The unique identifier for the original request (UUID)
- `{timestamp}`: ISO 8601 timestamp of execution
- `{final_decision}`: One of: "accept", "reject", "review", "escalate"
- `{confidence_score}`: Float between 0.0 and 1.0

### Context Agent Fields
- `{facts_count}`: Number of facts extracted
- `{assumptions_count}`: Number of assumptions identified
- `{missing_fields_count}`: Number of missing fields
- `{missing_fields_list}`: Comma-separated list of missing field names

### Policy Agent Fields
- `{applicable_rules_count}`: Number of applicable rules
- `{ambiguities_count}`: Number of ambiguities detected
- `{ambiguities_list}`: Comma-separated list of ambiguity descriptions
- `{applicable_rules_list}`: List of rule identifiers
- `{rule_explanations_dict}`: Dictionary mapping rule IDs to explanations

### Recommendation Agent Fields
- `{recommendation_text}`: The proposed recommendation text
- `{agent_confidence}`: Agent's self-reported confidence (0.0 to 1.0)
- `{known_risks_count}`: Number of known risks identified
- `{known_risks_list}`: Comma-separated list of risk descriptions

### Rule Evaluation Fields
- `{rule_evaluation_details}`: Detailed explanation of which rules triggered and why
- `{reason_codes_list}`: Bulleted list of reason codes
- `{triggered_rules_count}`: Number of rules that triggered (excluding default "ACCEPT")

### Confidence Calculation Fields
- `{base_score}`: Calculated base confidence score
- `{missing_penalty}`: Penalty amount for missing fields
- `{ambiguities_penalty}`: Penalty amount for ambiguities
- `{rule_penalty}`: Penalty amount for triggered rules

### Policy Enforcement Fields
- `{policy_enforcement_details}`: Explanation of how policy was applied

## Example Narrative

```
DECISION EXECUTION AUDIT NARRATIVE
==================================

Run ID: 550e8400-e29b-41d4-a716-446655440000
Request ID: 123e4567-e89b-12d3-a456-426614174000
Execution Timestamp: 2024-01-15T10:30:45.123456Z
Final Decision: review
Confidence Score: 0.65

EXECUTION SUMMARY
-----------------
This decision execution processed a request through a three-agent workflow,
followed by deterministic rule evaluation. The final decision was review
with a confidence score of 0.65 (on a scale of 0.0 to 1.0).

AGENT EXECUTION FLOW
--------------------
1. Context Agent
   - Extracted 5 facts from the input payload
   - Identified 2 assumptions
   - Flagged 0 missing field(s): (none)

2. Policy Agent
   - Identified 3 applicable policy rule(s)
   - Detected 1 policy ambiguity(ies): Rule 4.2 requires clarification on threshold interpretation

3. Recommendation Agent
   - Proposed recommendation: Approve with conditions
   - Self-reported confidence: 0.75
   - Identified 2 known risk(s): Potential regulatory change, Market volatility

DETERMINISTIC RULE EVALUATION
------------------------------
The orchestrator applied deterministic rules to agent outputs:

Rule 2 triggered: Policy ambiguities were detected (1 ambiguity identified).
This caused the decision to be flagged for review.

Rule evaluation produced the following reason codes:
- REVIEW_POLICY_AMBIGUITIES: 1 ambiguity(ies) identified

CONFIDENCE CALCULATION
----------------------
The final confidence score was calculated using a weighted formula:
- Base confidence (agent self-report): 0.75 × 0.6 = 0.45
- Missing fields penalty: -0.0 (from 0 missing field(s))
- Ambiguities penalty: -0.05 (from 1 ambiguity(ies))
- Triggered rules penalty: -0.0 (from 1 triggered rule(s))
- Final confidence score: 0.65

POLICY ENFORCEMENT
------------------
Policy text was evaluated by the Policy Agent, which identified:
- Applicable rules: ["RULE_4.1", "RULE_4.2", "RULE_7.3"]
- Rule explanations: {
    "RULE_4.1": "Applies to transactions exceeding $10,000",
    "RULE_4.2": "Requires risk assessment for volatile markets",
    "RULE_7.3": "Mandates documentation for conditional approvals"
  }

The Policy Agent detected an ambiguity in RULE_4.2 regarding threshold
interpretation, which triggered Rule 2 of the deterministic evaluation,
resulting in a review decision.

TRACEABILITY
------------
All execution steps were logged to trace file: data/traces/550e8400-e29b-41d4-a716-446655440000.jsonl

Trace events captured:
1. input_received - Request received with payload
2. agent_output (context_agent) - Context extraction completed
3. agent_output (policy_agent) - Policy interpretation completed
4. agent_output (recommendation_agent) - Recommendation generated
5. rule_evaluation - Deterministic rules evaluated
6. final_decision - Final decision produced

AUDIT CONCLUSION
----------------
This decision was processed through a governed workflow with full traceability.
The final decision of review was determined by deterministic rule evaluation
operating on AI agent outputs. All execution steps are recorded in the trace
log for review.
```

## Usage Instructions

1. **Retrieve Trace Events**: Load all trace events for the `run_id` from `data/traces/{run_id}.jsonl`
2. **Extract Agent Outputs**: Parse `agent_output` events to extract agent outputs
3. **Extract Rule Evaluation**: Parse `rule_evaluation` event to extract decision and reason codes
4. **Extract Final Decision**: Parse `final_decision` event to extract final decision and confidence
5. **Substitute Fields**: Replace template placeholders with actual values from trace events
6. **Format Output**: Format the narrative as plain text or markdown

## Key Audit Points

### For Auditors
- **Traceability**: Every decision has a complete trace log
- **Deterministic Rules**: Final decisions are made by explicit, auditable rules
- **Agent Outputs**: All AI reasoning is captured in structured outputs
- **Confidence Calculation**: Confidence scores are computed using a transparent formula

### For Compliance Officers
- **Policy Enforcement**: Policy is explicitly evaluated and applied
- **Reason Codes**: Every decision includes explicit reason codes
- **Review Triggers**: Ambiguities and low confidence trigger review/escalation
- **Audit Trail**: Complete execution history is preserved

### For Senior Engineers
- **Separation of Concerns**: AI reasoning is separate from deterministic decision logic
- **Error Handling**: Agent output validation prevents invalid decisions
- **Extensibility**: Rule logic can be extended without changing agent behavior
- **Observability**: Full traceability enables debugging and analysis

## Notes

- This template is designed for post-hoc audit narrative generation
- Actual implementation should parse trace events programmatically
- Narrative generation is not currently implemented in the system (planned for future phases)
- Trace files must be read from disk to generate narratives

