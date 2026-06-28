import unittest

from src.agents.agent_models import (
    ContextAgentOutput,
    PolicyAgentOutput,
    RecommendationAgentOutput,
)
from src.orchestration.confidence import calculate_confidence_score
from src.orchestration.decision_rules import evaluate_decision_rules


def make_outputs(
    *,
    missing_fields=None,
    ambiguities=None,
    recommendation="approve with controls",
    confidence=0.8,
    risks=None,
):
    context = ContextAgentOutput(
        facts=["request is complete"],
        assumptions=[],
        missing_fields=missing_fields or [],
    )
    policy = PolicyAgentOutput(
        applicable_rules=["rule-1"],
        rule_explanations={"rule-1": "Relevant sample rule"},
        ambiguities=ambiguities or [],
    )
    recommendation_output = RecommendationAgentOutput(
        recommendation=recommendation,
        justification=[{"type": "rule", "reference": "rule-1", "reason": "matches"}],
        confidence_self_report=confidence,
        known_risks=risks or [],
    )
    return context, policy, recommendation_output


class DecisionRuleTests(unittest.TestCase):
    def test_missing_fields_rejects_before_other_rules(self):
        context, policy, recommendation = make_outputs(
            missing_fields=["impact"], ambiguities=["policy wording"], confidence=0.1
        )

        result = evaluate_decision_rules(context, policy, recommendation)

        self.assertEqual(result["decision"], "reject")
        self.assertEqual(len(result["reason_codes"]), 1)
        self.assertTrue(result["reason_codes"][0].startswith("REJECT_MISSING_FIELDS"))

    def test_policy_ambiguity_and_low_confidence_escalates(self):
        context, policy, recommendation = make_outputs(
            ambiguities=["threshold unclear"], confidence=0.49
        )

        result = evaluate_decision_rules(context, policy, recommendation)

        self.assertEqual(result["decision"], "escalate")
        self.assertEqual(len(result["reason_codes"]), 2)
        self.assertTrue(result["reason_codes"][0].startswith("REVIEW_POLICY_AMBIGUITIES"))
        self.assertTrue(result["reason_codes"][1].startswith("ESCALATE_LOW_CONFIDENCE"))

    def test_high_risk_count_requires_review(self):
        context, policy, recommendation = make_outputs(
            risks=["hazard-one", "hazard-two", "hazard-three", "hazard-four"]
        )

        result = evaluate_decision_rules(context, policy, recommendation)

        self.assertEqual(result["decision"], "review")
        self.assertTrue(result["reason_codes"][0].startswith("REVIEW_HIGH_RISK_COUNT"))

    def test_empty_recommendation_rejects(self):
        context, policy, recommendation = make_outputs(recommendation=" ")

        result = evaluate_decision_rules(context, policy, recommendation)

        self.assertEqual(result["decision"], "reject")
        self.assertEqual(result["reason_codes"], ["REJECT_EMPTY_RECOMMENDATION: Recommendation agent produced empty output"])


class ConfidenceCalculationTests(unittest.TestCase):
    def test_confidence_formula_with_penalties(self):
        score = calculate_confidence_score(
            agent_confidence=1.0,
            missing_fields_count=2,
            ambiguities_count=3,
            triggered_rules_count=4,
        )

        self.assertAlmostEqual(score, 0.2)

    def test_accept_reason_code_does_not_add_rule_penalty(self):
        score = calculate_confidence_score(
            agent_confidence=0.8,
            missing_fields_count=0,
            ambiguities_count=0,
            triggered_rules_count=1,
        )

        self.assertEqual(score, 0.48)

    def test_confidence_clamps_to_zero(self):
        score = calculate_confidence_score(
            agent_confidence=0.1,
            missing_fields_count=10,
            ambiguities_count=10,
            triggered_rules_count=10,
        )

        self.assertEqual(score, 0.0)

    def test_invalid_agent_confidence_raises(self):
        with self.assertRaises(ValueError):
            calculate_confidence_score(
                agent_confidence=1.1,
                missing_fields_count=0,
                ambiguities_count=0,
                triggered_rules_count=0,
            )


if __name__ == "__main__":
    unittest.main()
