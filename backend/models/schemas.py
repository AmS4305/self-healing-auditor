"""
Pydantic Models for Self-Healing Code Auditor
Defines structured outputs for vulnerability detection and audit reports
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Vulnerability(BaseModel):
    """
    Represents a single code vulnerability detected by the auditor.
    Uses structured output to ensure consistent LLM responses.
    """
    severity: str = Field(
        description="Severity level: 'critical', 'high', 'medium', 'low'"
    )
    description: str = Field(
        description="Human-readable description of the vulnerability"
    )
    line_number: Optional[int] = Field(
        default=None,
        description="Line number where the vulnerability was found"
    )
    cwe_id: str = Field(
        description="Common Weakness Enumeration ID (e.g., 'CWE-89' for SQL Injection)"
    )
    suggested_fix_snippet: str = Field(
        description="Code snippet showing the recommended fix"
    )


class AuditReport(BaseModel):
    """
    Complete audit report containing all vulnerabilities and safety status.
    This is the primary structured output from the auditor node.
    """
    is_safe: bool = Field(
        description="True if no vulnerabilities found, False otherwise"
    )
    vulnerabilities: List[Vulnerability] = Field(
        default_factory=list,
        description="List of all detected vulnerabilities"
    )
    summary: str = Field(
        description="Overall summary of the security audit"
    )


class IterationHistory(BaseModel):
    """
    Captures a single iteration in the self-healing loop.
    Used for frontend timeline display.
    """
    iteration: int = Field(description="Iteration number (0-indexed)")
    code_snapshot: str = Field(description="Code state at this iteration")
    audit_report: AuditReport = Field(description="Audit results for this iteration")
    fix_applied: Optional[str] = Field(
        default=None,
        description="Fixed code if fixer was invoked, None if safe"
    )
    
    
class HealingResponse(BaseModel):
    """
    Final response returned to the frontend.
    Contains complete history of the self-healing process.
    """
    original_code: str = Field(description="The code submitted for audit")
    final_code: str = Field(description="Final healed code after all iterations")
    final_status: str = Field(description="'safe', 'healed', or 'max_iterations_reached'")
    total_iterations: int = Field(description="Number of audit-fix cycles executed")
    history: List[IterationHistory] = Field(
        description="Complete timeline of the healing process"
    )
