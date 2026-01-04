# AI Decision Traceability & Audit Engine

## Setup

### Prerequisites

- Python 3.10 or higher
- pip

### Environment Setup

This project uses a local virtual environment to ensure reproducible execution across different Python installations.

1. **Create the virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

2. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

### Running the Application

**Streamlit Audit UI:**
```bash
source .venv/bin/activate
python -m streamlit run src/ui/app.py
```

**FastAPI Server:**
```bash
source .venv/bin/activate
python src/main.py
```

Or using uvicorn directly:
```bash
source .venv/bin/activate
uvicorn src.api.app:app
```

**Note:** Always ensure the virtual environment is activated before running any commands.

## Problem Statement

Modern AI systems, particularly agentic AI applications, make decisions that impact business outcomes, regulatory compliance, and user trust. However, these systems often operate as "black boxes" with limited visibility into how decisions are made, what factors influenced them, and whether they align with organizational policies and constraints. This lack of traceability creates significant risks in enterprise environments where decisions must be auditable, explainable, and governed.

The AI Decision Traceability & Audit Engine addresses this critical gap by providing a governed, agentic AI decision system with full traceability and auditability. This system enables organizations to track every decision made by AI agents, understand the reasoning behind those decisions, enforce deterministic orchestration and guardrails, and maintain comprehensive audit logs for compliance and governance purposes.

**Important Clarifications:**
- This is **NOT** a chatbot. This system focuses on structured decision-making with full traceability.
- This is **NOT** autonomous AI. All decisions are made within a governed framework with explicit orchestration and guardrails.
- The primary focus is on **decision traceability, governance, and auditability** for enterprise AI applications.

## Project Phases (Tracked in ProjectVision.ts)

Project phases and progress are tracked in `src/vision/ProjectVision.ts`. This file serves as the single source of truth for project status and roadmap.

