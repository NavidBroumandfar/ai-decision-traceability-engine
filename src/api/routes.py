"""
API routes for the AI Decision Traceability Engine.

This module implements the REST endpoints that expose the decision
orchestration functionality. It serves as a thin wrapper around the
orchestration layer, with no business logic reimplementation.
"""

import logging
from typing import Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.core.decision_models import DecisionRequest, DecisionResult
from src.orchestration.orchestrator import DecisionOrchestrator
from src.persistence.decision_store import FileDecisionStore
from src.replay.replay_engine import ReplayReport, replay_decision

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/decision", tags=["decision"])

# File-based store for decision results (persistent)
_decision_store = FileDecisionStore()

# Initialize orchestrator with default policy text
# In a production system, this would come from configuration
_orchestrator = DecisionOrchestrator(policy_text="")


@router.post("/run", response_model=DecisionResult)
async def run_decision(request: DecisionRequest) -> DecisionResult:
    """
    Execute a decision request through the orchestration layer.

    Args:
        request: The decision request to process

    Returns:
        DecisionResult with final decision, confidence, and reason codes

    Raises:
        HTTPException: If the decision process fails
    """
    try:
        result = _orchestrator.run_decision(request)
        # Persist result to disk
        _decision_store.save(result)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(
            status_code=500, detail=f"Decision execution failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/{run_id}")
async def get_decision_metadata(run_id: str) -> Dict:
    """
    Retrieve basic metadata about a decision run.

    Args:
        run_id: The unique identifier for the decision run

    Returns:
        Dictionary with basic metadata about the decision run

    Raises:
        HTTPException: 404 if the decision run is not found
    """
    result = _decision_store.load(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Decision run {run_id} not found")

    return {
        "run_id": result.run_id,
        "final_decision": result.final_decision,
        "confidence_score": result.confidence_score,
        "created_at": result.created_at.isoformat(),
    }


@router.post("/{run_id}/replay", status_code=200)
async def replay_decision_endpoint(run_id: str) -> Dict:
    """
    Replay a decision run using persisted decision and trace.

    Loads the decision result and trace for run_id, re-executes the
    decision with the same input via the Replay Engine, and returns
    a ReplayReport comparing original vs replayed results.

    Args:
        run_id: The unique identifier for the decision run to replay

    Returns:
        ReplayReport as JSON (run_id, replay_run_id, same_final_decision,
        same_reason_codes, confidence_delta, agent_diffs, notes)

    Raises:
        404: Decision or trace file missing for run_id
        400: Trace exists but no input_received event (malformed trace)
        502: Replay execution failed (e.g. LLM connection/config)
        500: Unexpected server error
    """
    try:
        report = replay_decision(_orchestrator, run_id)
        return report.model_dump(mode="json")
    except FileNotFoundError as e:
        return JSONResponse(
            status_code=404,
            content={"error": "Decision or trace not found", "detail": str(e)},
        )
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid or incomplete trace", "detail": str(e)},
        )
    except RuntimeError as e:
        return JSONResponse(
            status_code=502,
            content={"error": "Replay execution failed", "detail": str(e)},
        )
    except Exception:
        logger.exception("Replay failed for run_id=%s", run_id)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred during replay.",
            },
        )
