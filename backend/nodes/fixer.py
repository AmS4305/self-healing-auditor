"""
Fixer Node - Automated Vulnerability Remediation
Uses meta/llama-3.1-70b-instruct for secure code generation
"""

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from backend.models.state import GraphState


# Initialize fixer LLM
# Model: meta/llama-3.1-70b-instruct
# - Standardizing on Meta Llama 3.1 70B for both audit and fix
# - Reliable code generation and instructions following
fixer_llm = ChatNVIDIA(
    model="meta/llama-3.1-70b-instruct",
    temperature=0.2,  # Slightly higher for creative code solutions
    max_tokens=3072,
)


def fixer_node(state: GraphState) -> GraphState:
    """
    Applies fixes to remediate detected vulnerabilities.

    This node:
    1. Takes vulnerabilities from state.report
    2. Generates fixed code using specialized Nemotron model
    3. Updates state with healed code
    4. Increments iteration counter

    The fixed code will be re-audited in the next iteration via
    the conditional edge routing logic.

    Args:
        state: Current graph state with audit report

    Returns:
        Updated state with fixed code and incremented iteration
    """
    print(f"🔧 Fixer running iteration {state['iterations']}...")

    # Extract vulnerabilities for context
    vulnerabilities = state["report"].vulnerabilities
    print(f"   Fixing {len(vulnerabilities)} vulnerabilities...")

    # Build detailed fix prompt with vulnerability context
    vuln_details = "\n\n".join(
        [
            f"**Vulnerability {i + 1}:**\n"
            f"- CWE: {v.cwe_id}\n"
            f"- Severity: {v.severity}\n"
            f"- Issue: {v.description}\n"
            f"- Suggested Fix:\n```\n{v.suggested_fix_snippet}\n```"
            for i, v in enumerate(vulnerabilities)
        ]
    )

    prompt = f"""You are an expert security engineer tasked with fixing code vulnerabilities.

**Original Code:**
```
{state["current_code"]}
```

**Detected Vulnerabilities:**
{vuln_details}

**Instructions:**
1. Apply ALL suggested fixes to remediate the vulnerabilities
2. Preserve the original code's functionality and logic
3. Use secure coding best practices
4. Add inline comments explaining security improvements
5. Return ONLY the fixed code, no explanations

**Fixed Code:**"""

    try:
        # Invoke fixer LLM to generate secure code
        response = fixer_llm.invoke(prompt)
        fixed_code = response.content.strip()
        print("✅ Fix generated.")
    except Exception as e:
        print(f"❌ Fixer LLM failed: {e}")
        raise e

    # Clean up markdown code blocks if present
    if fixed_code.startswith("```"):
        lines = fixed_code.split("\n")
        # Remove first and last lines (``` markers)
        fixed_code = "\n".join(lines[1:-1])

    # Update the last history entry with the fix
    # Handle both object and dict (LangGraph behavior can vary)
    import copy

    updated_history = copy.deepcopy(state["history"])

    if updated_history:
        last_entry = updated_history[-1]
        if isinstance(last_entry, dict):
            last_entry["fix_applied"] = fixed_code
        else:
            last_entry.fix_applied = fixed_code

    # Return updated state with healed code
    # LangGraph will merge this with existing state
    return {
        "current_code": fixed_code,
        "iterations": state["iterations"] + 1,
        "history": updated_history,
    }
