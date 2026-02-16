"""
LangGraph Workflow Configuration
Defines the StateGraph for the self-healing reflection pattern
"""

from langgraph.graph import StateGraph, END
from backend.models.state import GraphState
from backend.nodes import auditor_node, fixer_node, should_continue


def create_healing_graph() -> StateGraph:
    """
    Constructs the self-healing code auditor workflow.
    
    Graph Structure:
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ auditor │ (meta/llama-3.1-70b-instruct)
    └────┬────┘
         │
         ▼
    ┌─────────────────┐
    │ should_continue │ (conditional edge)
    └────┬────────┬───┘
         │        │
    unsafe &     safe OR
    iter<3      iter>=3
         │        │
         ▼        ▼
    ┌────────┐  END
    │  fixer │ (nvidia/llama-3.1-nemotron-70b-instruct)
    └────┬───┘
         │
         └──────> (loop back to auditor)
    
    State Flow:
    1. Auditor analyzes code, produces AuditReport
    2. Conditional edge checks is_safe and iterations
    3. If unsafe and under limit: route to fixer
    4. Fixer generates secure code, increments iteration
    5. Loop continues until safe or max iterations
    
    Memory Management:
    - GraphState persists across all nodes
    - Each node returns partial state updates
    - LangGraph merges updates automatically
    - History accumulates in state.history list
    
    Returns:
        Compiled StateGraph ready for execution
    """
    
    # Initialize state graph with GraphState schema
    graph = StateGraph(GraphState)
    
    # Add nodes to the graph
    # Node names must match the routing logic strings
    graph.add_node("auditor", auditor_node)
    graph.add_node("fixer", fixer_node)
    
    # Set entry point - graph always starts at auditor
    graph.set_entry_point("auditor")
    
    # Add conditional edge from auditor
    # The should_continue function determines next node
    graph.add_conditional_edges(
        "auditor",  # Source node
        should_continue,  # Routing function
        {
            "fixer": "fixer",  # If "fixer" returned, go to fixer node
            "end": END  # If "end" returned, terminate graph
        }
    )
    
    # Add edge from fixer back to auditor
    # This creates the reflection loop for re-evaluation
    graph.add_edge("fixer", "auditor")
    
    # Compile the graph for execution
    return graph.compile()


# Export pre-compiled graph instance
healing_graph = create_healing_graph()
