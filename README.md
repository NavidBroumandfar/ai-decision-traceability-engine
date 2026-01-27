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

4. **Configure environment variables:**
   
   Create a `.env` file in the project root (a template has been created for you):
   
   **For Local Models (Ollama, LM Studio, etc.):**
   ```bash
   # Local Model Configuration
   OPENAI_BASE_URL=http://localhost:11434/v1  # Ollama default
   # OPENAI_BASE_URL=http://localhost:1234/v1  # LM Studio default
   OPENAI_API_KEY=  # Leave empty for local models
   OPENAI_MODEL=llama3.2  # Your local model name
   
   # Logging
   LOG_LEVEL=INFO
   ```
   
   **For OpenAI API:**
   ```bash
   # OpenAI API Configuration
   OPENAI_BASE_URL=
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-4o-mini
   
   # Logging
   LOG_LEVEL=INFO
   ```
   
   **Local Model Setup:**
   - **Ollama**: Install from [ollama.ai](https://ollama.ai), then run `ollama serve` and pull a model (e.g., `ollama pull llama3.2`)
   - **LM Studio**: Install from [lmstudio.ai](https://lmstudio.ai), start the local server, and use port 1234
   - The system uses OpenAI-compatible API, so any local server supporting that format will work

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

## Production Contract

This system is production-credible but not enterprise-grade. It provides deterministic orchestration, full traceability, and persistent storage suitable for single-node deployments. It does not provide distributed coordination, high availability, automatic failover, or multi-tenant isolation. For detailed guarantees, limitations, and operational assumptions, see [PRODUCTION_CONTRACT.md](PRODUCTION_CONTRACT.md).

**Key Points:**
- Deterministic rule evaluation and confidence calculation
- Atomic persistence of decision results and trace events
- Single-node deployment assumption
- LLM agent outputs are non-deterministic (even with temperature=0)
- No automatic backups or replication

## Project Phases (Tracked in ProjectVision.ts)

Project phases and progress are tracked in `src/vision/ProjectVision.ts`. This file serves as the single source of truth for project status and roadmap.

