/**
 * Project Vision - Single Source of Truth for Project Phases and Progress
 *
 * This file tracks all project phases, their intent, and delivery status.
 * It is authoritative and must not be reinterpreted by implementation code.
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
      status: "completed"
    },
    {
      id: "P3",
      order: 3,
      title: "Deterministic Orchestration & Guards",
      description: "Deterministic orchestration logic and guardrail enforcement",
      status: "completed"
    },
    {
      id: "P4",
      order: 4,
      title: "FastAPI Decision API",
      description: "Internal API for submitting decisions and retrieving execution results",
      status: "completed"
    },
    {
      id: "P5",
      order: 5,
      title: "Streamlit Audit UI",
      description: "User interface for viewing decisions, traces, and execution timelines",
      status: "completed"
    },
    {
      id: "P6",
      order: 6,
      title: "Documentation, Limits & Audit Narrative",
      description: "System documentation, explicit limitations, and post-hoc audit narrative generation",
      deliverables: [
        "SYSTEM_OVERVIEW.md",
        "LIMITATIONS.md",
        "AUDIT_NARRATIVE_TEMPLATE.md"
      ],
      status: "completed"
    },
    {
      id: "P7",
      order: 7,
      title: "Persistent Audit Log",
      description: "Durable storage of decision traces (JSONL) and decision results (JSON)",
      deliverables: [
        "data/traces/{run_id}.jsonl",
        "data/decisions/{run_id}.json",
        "src/persistence/decision_store.py"
      ],
      status: "completed"
    },
    {
      id: "P8",
      order: 8,
      title: "Decision Replay Engine",
      description: "Ability to replay a past decision using stored inputs and trace data",
      status: "planned"
    },
    {
      id: "P9",
      order: 9,
      title: "Audit Query API Surface",
      description: "Read-only FastAPI endpoints for querying decisions and audit trails",
      status: "planned"
    },
    {
      id: "P10",
      order: 10,
      title: "Governance README & Architecture Diagrams",
      description: "High-level governance documentation and system architecture diagrams",
      status: "planned"
    },
    {
      id: "P11",
      order: 11,
      title: "Hardening & Evaluation Hooks",
      description: "Evaluation points, metrics hooks, and non-functional hardening",
      status: "planned"
    }
  ]
};
