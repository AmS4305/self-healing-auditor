"""
Auditor Node - Security Vulnerability Detection
Uses meta/llama-3.1-70b-instruct for broad security knowledge
"""

import json
import re
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from backend.models.state import GraphState
from backend.models.schemas import AuditReport, IterationHistory


# Initialize auditor LLM
# Model: meta/llama-3.1-70b-instruct
# - Chosen for comprehensive security vulnerability detection
# - Excellent at identifying CWE patterns and security anti-patterns
auditor_llm = ChatNVIDIA(
    model="meta/llama-3.1-70b-instruct",
    temperature=0.1,  # Low temperature for consistent security analysis
    max_tokens=2048,
)


def _parse_audit_response(response_text: str) -> AuditReport:
    """
    Parse the LLM's raw text response into a structured AuditReport.

    Attempts to extract JSON from the response and validate it against
    the AuditReport Pydantic schema. Falls back to a safe report if
    parsing fails.
    """
    try:
        # Try to extract JSON from the response (may be wrapped in ```json blocks)
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response_text)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # Try to find raw JSON object in response
            json_match = re.search(r"\{[\s\S]*\}", response_text)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response_text.strip()

        data = json.loads(json_str)
        return AuditReport.model_validate(data)
    except (json.JSONDecodeError, Exception) as e:
        # If parsing fails, create a fallback report indicating the issue
        return AuditReport(
            is_safe=True,
            vulnerabilities=[],
            summary=f"Audit completed but structured parsing failed: {str(e)}. Raw response: {response_text[:500]}",
        )


def auditor_node(state: GraphState) -> GraphState:
    """
    Analyzes code for security vulnerabilities.

    This node:
    1. Takes current_code from state
    2. Invokes LLM and parses JSON response into AuditReport
    3. Updates state with audit results and history
    4. Returns updated state for next node or END

    Args:
        state: Current graph state containing code to audit

    Returns:
        Updated state with new audit report and history entry
    """

    print(f"🕵️ Auditor running iteration {state['iterations']}...")

    # Build security audit prompt - explicitly request JSON output
    prompt = f"""You are a senior security auditor specializing in code vulnerability detection.

Analyze the following code for security vulnerabilities:

```
{state["current_code"]}
```

Identify ALL security issues including but not limited to:
- Injection vulnerabilities (SQL, XSS, Command Injection)
- Authentication/Authorization flaws
- Sensitive data exposure
- Security misconfigurations
- Insecure cryptography
- Input validation issues

For each vulnerability:
1. Assign appropriate CWE ID (e.g., CWE-89, CWE-79)
2. Provide severity: critical, high, medium, or low
3. Give a clear description
4. Include a suggested_fix_snippet showing corrected code

If the code is secure, set is_safe to true with an empty vulnerabilities list.

IMPORTANT: You MUST respond with ONLY a valid JSON object in this exact format:
{{
    "is_safe": false,
    "vulnerabilities": [
        {{
            "severity": "high",
            "description": "Description of the issue",
            "line_number": 10,
            "cwe_id": "CWE-89",
            "suggested_fix_snippet": "fixed code here"
        }}
    ],
    "summary": "Overall audit summary"
}}"""

    # Invoke LLM and parse the response into AuditReport
    response = auditor_llm.invoke(prompt)
    audit_report = _parse_audit_response(response.content)

    # Create history entry for this iteration
    history_entry = IterationHistory(
        iteration=state["iterations"],
        code_snapshot=state["current_code"],
        audit_report=audit_report,
        fix_applied=None,  # No fix applied yet, will be updated by fixer
    )

    print(
        f"✅ Audit complete. Found {len(audit_report.vulnerabilities)} vulnerabilities. Safe: {audit_report.is_safe}"
    )

    # Update state with audit results
    # LangGraph merges this with existing state automatically
    return {
        "report": audit_report,
        "history": state["history"] + [history_entry],
        "iterations": state["iterations"],
    }
