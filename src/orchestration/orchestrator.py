"""
Deterministic orchestration layer for AI decision traceability.

This module implements the DecisionOrchestrator, which serves as the final
authority for decision-making. It executes agent graphs, evaluates outputs,
enforces hard constraints, and produces auditable decision results.
"""

import uuid
from datetime import datetime

from src.agents.agent_graph import build_agent_graph
from src.agents.agent_models import (
    ContextAgentOutput,
    PolicyAgentOutput,
    RecommendationAgentOutput
)
from src.core.decision_models import DecisionRequest, DecisionResult
from src.orchestration.confidence import calculate_confidence_score
from src.orchestration.decision_rules import evaluate_decision_rules
from src.tracing.trace_models import TraceEvent
from src.tracing.trace_writer import write_trace_event


class DecisionOrchestrator:
    """
    Deterministic orchestrator for AI decision processes.
    
    This class is the FINAL AUTHORITY. No LLM may decide outcomes.
    It executes agent graphs, evaluates outputs, enforces constraints,
    and produces traceable decision results.
    """
    
    def __init__(self, policy_text: str):
        """
        Initialize the orchestrator.
        
        Args:
            policy_text: The policy text to be used by the Policy Agent
        """
        self.policy_text = policy_text
        self.agent_graph = build_agent_graph()
    
    def run_decision(self, request: DecisionRequest) -> DecisionResult:
        """
        Execute a decision request through the agent graph and produce a result.
        
        This method:
        1. Generates a run_id
        2. Executes the agent graph
        3. Collects agent outputs
        4. Applies deterministic rules
        5. Calculates confidence
        6. Produces DecisionResult
        7. Emits trace events
        
        Args:
            request: The decision request to process
            
        Returns:
            DecisionResult with final decision, confidence, and reason codes
            
        Raises:
            ValueError: If agent outputs violate expected schemas
            RuntimeError: If graph execution fails
        """
        # Generate unique run_id
        run_id = str(uuid.uuid4())
        
        # Emit input_received trace event
        input_event = TraceEvent(
            event_id=str(uuid.uuid4()),
            run_id=run_id,
            event_type="input_received",
            source="orchestrator",
            payload={
                "request_id": request.request_id,
                "input_payload": request.input_payload,
                "metadata": request.metadata
            },
            timestamp=datetime.utcnow()
        )
        write_trace_event(input_event)
        
        # Execute agent graph
        initial_state = {
            "input_payload": request.input_payload,
            "policy_text": self.policy_text,
            "context_output": None,
            "policy_output": None,
            "recommendation_output": None
        }
        
        final_state = self.agent_graph.invoke(initial_state)
        
        # Extract agent outputs
        context_output: ContextAgentOutput = final_state["context_output"]
        policy_output: PolicyAgentOutput = final_state["policy_output"]
        recommendation_output: RecommendationAgentOutput = final_state["recommendation_output"]
        
        # Validate outputs exist
        if context_output is None:
            raise ValueError("context_output is None after graph execution")
        if policy_output is None:
            raise ValueError("policy_output is None after graph execution")
        if recommendation_output is None:
            raise ValueError("recommendation_output is None after graph execution")
        
        # Emit agent_output trace events
        context_event = TraceEvent(
            event_id=str(uuid.uuid4()),
            run_id=run_id,
            event_type="agent_output",
            source="context_agent",
            payload=context_output.model_dump(),
            timestamp=datetime.utcnow()
        )
        write_trace_event(context_event)
        
        policy_event = TraceEvent(
            event_id=str(uuid.uuid4()),
            run_id=run_id,
            event_type="agent_output",
            source="policy_agent",
            payload=policy_output.model_dump(),
            timestamp=datetime.utcnow()
        )
        write_trace_event(policy_event)
        
        recommendation_event = TraceEvent(
            event_id=str(uuid.uuid4()),
            run_id=run_id,
            event_type="agent_output",
            source="recommendation_agent",
            payload=recommendation_output.model_dump(),
            timestamp=datetime.utcnow()
        )
        write_trace_event(recommendation_event)
        
        # Apply deterministic rules
        rule_result = evaluate_decision_rules(
            context_output=context_output,
            policy_output=policy_output,
            recommendation_output=recommendation_output
        )
        
        # Emit rule_evaluation trace event
        rule_event = TraceEvent(
            event_id=str(uuid.uuid4()),
            run_id=run_id,
            event_type="rule_evaluation",
            source="orchestrator",
            payload={
                "decision": rule_result["decision"],
                "reason_codes": rule_result["reason_codes"]
            },
            timestamp=datetime.utcnow()
        )
        write_trace_event(rule_event)
        
        # Calculate confidence score
        confidence_score = calculate_confidence_score(
            agent_confidence=recommendation_output.confidence_self_report,
            missing_fields_count=len(context_output.missing_fields),
            ambiguities_count=len(policy_output.ambiguities),
            triggered_rules_count=len(rule_result["reason_codes"])
        )
        
        # Produce final decision
        final_decision = rule_result["decision"]
        
        # Emit final_decision trace event
        decision_event = TraceEvent(
            event_id=str(uuid.uuid4()),
            run_id=run_id,
            event_type="final_decision",
            source="orchestrator",
            payload={
                "final_decision": final_decision,
                "confidence_score": confidence_score,
                "reason_codes": rule_result["reason_codes"]
            },
            timestamp=datetime.utcnow()
        )
        write_trace_event(decision_event)
        
        # Return DecisionResult
        return DecisionResult(
            run_id=run_id,
            final_decision=final_decision,
            confidence_score=confidence_score,
            reason_codes=rule_result["reason_codes"],
            created_at=datetime.utcnow()
        )

