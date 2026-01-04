"""
API routes for the AI Decision Traceability Engine.

This module implements the REST endpoints that expose the decision
orchestration functionality. It serves as a thin wrapper around the
orchestration layer, with no business logic reimplementation.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict

from src.core.decision_models import DecisionRequest, DecisionResult
from src.orchestration.orchestrator import DecisionOrchestrator

router = APIRouter(prefix="/decision", tags=["decision"])

# In-memory store for decision results (minimal, no persistence)
# This is a temporary solution for basic metadata retrieval
_decision_store: Dict[str, DecisionResult] = {}

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
        # Store result for basic metadata retrieval
        _decision_store[result.run_id] = result
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Decision execution failed: {str(e)}")
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
    if run_id not in _decision_store:
        raise HTTPException(status_code=404, detail=f"Decision run {run_id} not found")
    
    result = _decision_store[run_id]
    return {
        "run_id": result.run_id,
        "final_decision": result.final_decision,
        "confidence_score": result.confidence_score,
        "created_at": result.created_at.isoformat()
    }


@router.post("/{run_id}/replay", status_code=501)
async def replay_decision(run_id: str) -> Dict:
    """
    Replay a decision run (placeholder endpoint).
    
    This endpoint is not yet implemented. Replay logic will be added
    in a future phase to allow re-execution of decision runs for
    audit and debugging purposes.
    
    Args:
        run_id: The unique identifier for the decision run to replay
        
    Returns:
        Not Implemented response
    """
    return {
        "status": "not_implemented",
        "message": "Decision replay functionality will be implemented in a future phase"
    }

