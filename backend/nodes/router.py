"""
Graph Routing Logic
Implements conditional edge for reflection loop control
"""

from backend.models.state import GraphState
from typing import Literal


def should_continue(state: GraphState) -> Literal["fixer", "end"]:
    """
    Conditional edge function that controls the reflection loop.
    
    Routing Logic:
    - Route to "fixer" if:
        1. Code is NOT safe (state.report.is_safe == False), AND
        2. Haven't exceeded max iterations (state.iterations < 3)
    
    - Route to "end" if:
        1. Code is safe (no vulnerabilities), OR
        2. Max iterations reached (prevent rate limit issues)
    
    This creates a self-healing loop where:
    auditor -> (unsafe + iterations<3) -> fixer -> auditor -> ...
    auditor -> (safe OR iterations>=3) -> END
    
    Args:
        state: Current graph state
        
    Returns:
        "fixer" to continue healing, "end" to terminate
    """
    
    # Check termination conditions
    is_unsafe = not state["report"].is_safe
    under_limit = state["iterations"] < 3
    
    # Decision tree for routing
    if is_unsafe and under_limit:
        # Code needs healing and we have iterations left
        return "fixer"
    else:
        # Either code is safe OR max iterations reached
        return "end"
