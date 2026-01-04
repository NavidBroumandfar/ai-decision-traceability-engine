/**
 * Project Vision - Single Source of Truth for Project Phases and Progress
 * 
 * This file tracks all project phases, their status, and associated deliverables.
 */

export const ProjectVision = {
  phases: [
    {
      id: "P0",
      order: 0,
      title: "Repo & Scaffolding",
      description: "Initial repository structure, configuration, and project vision",
      files: ["README.md", "pyproject.toml", "ProjectVision.ts", "settings.py"],
      status: "completed"
    },
    {
      id: "P1",
      order: 1,
      title: "Decision & Trace Model",
      description: "Core data models for decisions, traces, and audit records",
      status: "completed"
    },
    {
      id: "P2",
      order: 2,
      title: "Agent Graph (LangGraph)",
      description: "LangGraph-based agent orchestration and decision workflows",
      status: "planned"
    },
    {
      id: "P3",
      order: 3,
      title: "Deterministic Orchestration & Guards",
      description: "Deterministic orchestration logic and guardrail enforcement",
      status: "planned"
    },
    {
      id: "P4",
      order: 4,
      title: "FastAPI Decision API",
      description: "RESTful API for decision requests and audit queries",
      status: "planned"
    },
    {
      id: "P5",
      order: 5,
      title: "Streamlit Audit UI",
      description: "User interface for viewing decisions, traces, and audit logs",
      status: "planned"
    },
    {
      id: "P6",
      order: 6,
      title: "Documentation, Limits & Audit Narrative",
      description: "Comprehensive documentation, system limits, and audit narrative generation",
      status: "planned"
    }
  ]
};

