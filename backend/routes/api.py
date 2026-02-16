"""
FastAPI Routes
Defines API endpoints for code auditing and healing
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.models import HealingResponse, IterationHistory, GraphState
from backend.utils import healing_graph


router = APIRouter()


class CodeSubmission(BaseModel):
    """Request body for code audit endpoint"""

    code: str


@router.post("/audit", response_model=HealingResponse)
async def audit_code(submission: CodeSubmission):
    """
    Audits and heals code using the reflection pattern.

    This endpoint:
    1. Initializes graph state with submitted code
    2. Executes the healing_graph workflow
    3. Returns complete history of healing process

    The response includes:
    - Original and final code
    - All iterations with audit reports and fixes
    - Final status (safe, healed, or max_iterations_reached)

    Frontend can use this to display:
    - Timeline of AI decision-making
    - Vulnerability evolution across iterations
    - Applied fixes and their effectiveness

    Args:
        submission: Code to audit

    Returns:
        HealingResponse with complete iteration history

    Raises:
        HTTPException: If graph execution fails
    """

    try:
        # Initialize graph state
        initial_state: GraphState = {
            "current_code": submission.code,
            "original_code": submission.code,
            "report": None,  # Will be populated by first auditor run
            "iterations": 0,
            "history": [],
        }

        # Execute the healing graph workflow
        # This runs the full auditor -> fixer loop until termination
        final_state = healing_graph.invoke(initial_state)

        # Determine final status based on termination reason
        if final_state["report"].is_safe:
            if final_state["iterations"] == 0:
                status = "safe"  # Code was safe from the start
            else:
                status = "healed"  # Code was fixed successfully
        else:
            status = "max_iterations_reached"  # Still unsafe after 3 iterations

        # Build comprehensive response for frontend
        response = HealingResponse(
            original_code=final_state["original_code"],
            final_code=final_state["current_code"],
            final_status=status,
            total_iterations=final_state["iterations"],
            history=final_state["history"],
        )

        return response

    except Exception as e:
        import traceback

        traceback.print_exc()  # Print full error to console
        raise HTTPException(
            status_code=500, detail=f"Error during code healing: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "self-healing-auditor"}
