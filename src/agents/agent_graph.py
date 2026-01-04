"""
LangGraph DAG for agent orchestration.

This module defines a deterministic execution graph that wires together
the Context Agent, Policy Agent, and Recommendation Agent in sequence.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, END, START

from src.agents.agent_models import (
    ContextAgentOutput,
    PolicyAgentOutput,
    RecommendationAgentOutput
)
from src.agents.context_agent import run_context_agent
from src.agents.policy_agent import run_policy_agent
from src.agents.recommendation_agent import run_recommendation_agent


class AgentGraphState(TypedDict):
    """State passed between graph nodes."""
    
    input_payload: dict
    policy_text: str
    context_output: ContextAgentOutput | None
    policy_output: PolicyAgentOutput | None
    recommendation_output: RecommendationAgentOutput | None


def context_node(state: AgentGraphState) -> AgentGraphState:
    """
    Context Agent node.
    
    Processes input_payload and produces context_output.
    """
    context_output = run_context_agent(state["input_payload"])
    return {
        **state,
        "context_output": context_output
    }


def policy_node(state: AgentGraphState) -> AgentGraphState:
    """
    Policy Agent node.
    
    Processes context_output and policy_text to produce policy_output.
    """
    if state["context_output"] is None:
        raise ValueError("context_output is required for policy_node")
    
    policy_output = run_policy_agent(
        state["context_output"],
        state["policy_text"]
    )
    return {
        **state,
        "policy_output": policy_output
    }


def recommendation_node(state: AgentGraphState) -> AgentGraphState:
    """
    Recommendation Agent node.
    
    Processes context_output and policy_output to produce recommendation_output.
    """
    if state["context_output"] is None:
        raise ValueError("context_output is required for recommendation_node")
    if state["policy_output"] is None:
        raise ValueError("policy_output is required for recommendation_node")
    
    recommendation_output = run_recommendation_agent(
        state["context_output"],
        state["policy_output"]
    )
    return {
        **state,
        "recommendation_output": recommendation_output
    }


def build_agent_graph() -> StateGraph:
    """
    Build and compile the agent execution graph.
    
    Graph structure:
    START -> ContextAgent -> PolicyAgent -> RecommendationAgent -> END
    
    Returns:
        Compiled LangGraph StateGraph ready for execution
    """
    graph = StateGraph(AgentGraphState)
    
    # Add nodes
    graph.add_node("context_agent", context_node)
    graph.add_node("policy_agent", policy_node)
    graph.add_node("recommendation_agent", recommendation_node)
    
    # Define edges (deterministic linear flow)
    graph.add_edge(START, "context_agent")
    graph.add_edge("context_agent", "policy_agent")
    graph.add_edge("policy_agent", "recommendation_agent")
    graph.add_edge("recommendation_agent", END)
    
    # Compile and return
    return graph.compile()

