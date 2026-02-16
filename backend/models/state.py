"""
LangGraph State Management
Defines the state object that flows through the graph nodes
"""

from typing import TypedDict, List
from backend.models.schemas import AuditReport, IterationHistory


class GraphState(TypedDict):
    """
    State object managed by LangGraph's StateGraph.
    
    This state is passed between nodes and accumulates information
    across the reflection loop. LangGraph automatically handles:
    - State persistence between nodes
    - Conditional routing based on state values
    - History tracking for debugging
    """
    
    # Current code being analyzed
    current_code: str
    
    # Latest audit report from auditor node
    report: AuditReport
    
    # Iteration counter (0-indexed)
    iterations: int
    
    # History of all iterations for frontend display
    history: List[IterationHistory]
    
    # Original code submitted by user (immutable)
    original_code: str
