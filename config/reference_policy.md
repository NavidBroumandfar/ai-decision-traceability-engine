# Reference Decision Policy

This sample policy is intentionally generic and public-safe. It gives the
policy agent meaningful text to interpret without embedding private business
rules, customer data, or regulated-domain advice.

## Rules

1. Require enough context to identify the request, the affected user or system,
   the intended action, and the expected impact.
2. Reject requests when required facts are missing, contradictory, or impossible
   to verify from the submitted payload.
3. Escalate requests that mention legal, financial, medical, safety, credential,
   or security-sensitive consequences.
4. Flag requests for human review when the policy text or input context is
   ambiguous.
5. Prefer reversible, low-impact recommendations when the available evidence is
   incomplete.

## Output Expectations

- Cite the applicable rule identifiers in the policy interpretation.
- Describe ambiguity explicitly rather than filling gaps with assumptions.
- Treat the recommendation agent output as advisory only; the orchestrator's
  deterministic rules remain the final decision authority.
