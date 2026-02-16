# 🏗️ System Architecture

## Component Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Frontend (HTML/CSS/JS)                                 │  │
│  │  • Dark Theme UI (Purple/Black VS Code style)           │  │
│  │  • Code Editor with syntax highlighting                 │  │
│  │  • Real-time timeline visualization                     │  │
│  │  • Collapsible iteration cards                          │  │
│  └──────────────────┬──────────────────────────────────────┘  │
└─────────────────────┼─────────────────────────────────────────┘
                      │ HTTP POST /api/audit
                      ▼
┌───────────────────────────────────────────────────────────────┐
│                        API LAYER                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  FastAPI Routes (backend/routes/api.py)                 │  │
│  │  • POST /api/audit → audit_code()                       │  │
│  │  • GET /api/health → health_check()                     │  │
│  │  • JSON request/response with Pydantic validation       │  │
│  └──────────────────┬──────────────────────────────────────┘  │
└─────────────────────┼─────────────────────────────────────────┘
                      │ Initialize GraphState
                      ▼
┌───────────────────────────────────────────────────────────────┐
│                    LANGGRAPH WORKFLOW                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  StateGraph (backend/utils/graph.py)                    │  │
│  │                                                         │  │
│  │  START                                                  │  │
│  │    │                                                    │  │
│  │    ▼                                                    │  │
│  │  ┌────────────────────────────────────┐                 │  │
│  │  │  AUDITOR NODE                      │                 │  │
│  │  │  (backend/nodes/auditor.py)        │                 │  │
│  │  │                                    │                 │  │
│  │  │  Model: meta/llama-3.1-70b-instruct│                 │  │
│  │  │  • Analyze code for vulnerabilities│                 │  │
│  │  │  • Use structured output schema    │                 │  │
│  │  │  • Generate AuditReport with CWEs  │                 │  │
│  │  └────────┬───────────────────────────┘                 │  │
│  │           │                                             │  │
│  │           ▼                                             │  │
│  │  ┌────────────────────────────────────┐                 │  │
│  │  │  CONDITIONAL ROUTER                │                 │  │
│  │  │  (backend/nodes/router.py)         │                 │  │
│  │  │                                    │                 │  │
│  │  │  should_continue(state):           │                 │  │
│  │  │    if NOT safe AND iter < 3:       │                 │  │
│  │  │      → FIXER                       │                 │  │
│  │  │    else:                           │                 │  │
│  │  │      → END                         │                 │  │
│  │  └────┬──────────────────────┬────────┘                 │  │
│  │       │ unsafe & iter<3      │ safe OR iter>=3          │  │
│  │       ▼                      ▼                          │  │
│  │  ┌────────────────────┐   END                           │  │
│  │  │  FIXER NODE        │                                 │  │
│  │  │  (backend/nodes/   │                                 │  │
│  │  │   fixer.py)        │                                 │  │
│  │  │                    │                                 │  │
│  │  │  Model: meta/      │                                 │  │
│  │  │  llama-3.1-70b-    │                                 │  │
│  │  │  instruct          │                                 │  │
│  │  │                    │                                 │  │
│  │  │                    │                                 │  │
│  │  │  • Apply security  │                                 │  │
│  │  │    fixes           │                                 │  │
│  │  │  • Preserve logic  │                                 │  │
│  │  │  • Increment iter  │                                 │  │
│  │  └────────┬───────────┘                                 │  │
│  │           │                                             │  │
│  │           └──────────────┐                              │  │
│  │                          ▼                              │  │
│  │                    (loop back to AUDITOR)               │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────┬─────────────────────────────────────────┘
                      │ Final GraphState
                      ▼
┌───────────────────────────────────────────────────────────────┐
│                      DATA MODELS                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Pydantic Schemas (backend/models/schemas.py)           │  │
│  │                                                         │  │
│  │  Vulnerability:                                         │  │
│  │    • severity: str                                      │  │
│  │    • description: str                                   │  │
│  │    • line_number: Optional[int]                         │  │
│  │    • cwe_id: str                                        │  │
│  │    • suggested_fix_snippet: str                         │  │
│  │                                                         │  │
│  │  AuditReport:                                           │  │
│  │    • is_safe: bool                                      │  │
│  │    • vulnerabilities: List[Vulnerability]               │  │
│  │    • summary: str                                       │  │
│  │                                                         │  │
│  │  IterationHistory:                                      │  │
│  │    • iteration: int                                     │  │
│  │    • code_snapshot: str                                 │  │
│  │    • audit_report: AuditReport                          │  │
│  │    • fix_applied: Optional[str]                         │  │
│  │                                                         │  │
│  │  HealingResponse:                                       │  │
│  │    • original_code: str                                 │  │
│  │    • final_code: str                                    │  │
│  │    • final_status: str                                  │  │
│  │    • total_iterations: int                              │  │
│  │    • history: List[IterationHistory]                    │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Submits Code

```
User → Frontend → POST /api/audit → FastAPI
```

### 2. Graph Initialization

```python
initial_state = {
    "current_code": submitted_code,
    "original_code": submitted_code,
    "report": None,
    "iterations": 0,
    "history": []
}
```

### 3. Reflection Loop Execution

```
Iteration 0:
  Auditor → Detect vulnerabilities → AuditReport(is_safe=False)
  Router → Check state → Route to Fixer
  Fixer → Generate fix → Update code, increment iteration

Iteration 1:
  Auditor → Re-evaluate fixed code → AuditReport(is_safe=False)
  Router → Check state → Route to Fixer (if iter < 3)
  Fixer → Apply additional fixes

Iteration 2:
  Auditor → Final validation → AuditReport(is_safe=True)
  Router → Check state → Route to END

Final State:
  {
    "current_code": healed_code,
    "iterations": 2,
    "history": [iter0, iter1, iter2],
    "report": final_audit
  }
```

### 4. Response Generation

```
FastAPI → Build HealingResponse → JSON → Frontend
```

### 5. Frontend Rendering

```
JavaScript → Parse history → Render timeline → Display to user
```

## State Management

### GraphState Flow Through Nodes

```
┌───────────────────────────────────────────────────────────┐
│  GraphState (persisted by LangGraph)                      │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  current_code: str       ← Updated by fixer_node          │
│  report: AuditReport     ← Updated by auditor_node        │
│  iterations: int         ← Incremented by fixer_node      │
│  history: List[...]      ← Appended by both nodes         │
│  original_code: str      ← Immutable reference            │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Node Responsibilities

**Auditor Node:**

- Receives: `state["current_code"]`
- Invokes: LLM with structured output
- Returns: `{"report": AuditReport, "history": updated_list}`
- LangGraph merges with existing state

**Fixer Node:**

- Receives: `state["report"].vulnerabilities`
- Invokes: LLM to generate fixes
- Returns: `{"current_code": fixed, "iterations": state["iterations"] + 1}`
- LangGraph merges with existing state

**Router Function:**

- Receives: Complete GraphState
- Logic: `not state["report"].is_safe and state["iterations"] < 3`
- Returns: `"fixer"` or `"end"` (string literal)

## Security Model

### Model: `meta/llama-3.1-70b-instruct`

Both the **Auditor** and **Fixer** nodes use the same model for consistency and reliability.

```
┌───────────────────────────────────────────────────────────┐
│  meta/llama-3.1-70b-instruct (Auditor + Fixer)            │
├───────────────────────────────────────────────────────────┤
│  Strengths:                                               │
│  • Broad security knowledge base                          │
│  • Accurate CWE classification                            │
│  • Comprehensive vulnerability pattern detection          │
│  • Reliable code generation and instruction following     │
│  • Context-aware fixes that preserve original logic       │
│                                                           │
│  Auditor Role:                                            │
│  Analyzes code for vulnerabilities using OWASP/CWE        │
│  standards and returns structured JSON audit reports.      │
│                                                           │
│  Fixer Role:                                              │
│  Applies security patches based on audit findings while   │
│  preserving the original code's functionality.            │
└───────────────────────────────────────────────────────────┘
```

## File Organization Rationale

```
backend/
├── models/          # Data schemas and state definitions
│   ├── schemas.py   # Pydantic models for API contracts
│   └── state.py     # LangGraph state structure
│
├── nodes/           # Graph computation nodes
│   ├── auditor.py   # Security analysis logic
│   ├── fixer.py     # Code remediation logic
│   └── router.py    # Conditional routing logic
│
├── routes/          # HTTP endpoint handlers
│   └── api.py       # FastAPI route definitions
│
└── utils/           # Shared utilities
    └── graph.py     # LangGraph workflow assembly
```

**Design Principles:**

- **Separation of Concerns**: Each module has single responsibility
- **Testability**: Nodes can be unit tested independently
- **Maintainability**: Clear boundaries between components
- **Extensibility**: Easy to add new nodes or modify graph

---

## Deployment Architecture

```
┌───────────────────────────────────────────────────────────┐
│  Production Deployment                                    │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐         ┌──────────────┐                │
│  │  Load        │         │  Uvicorn     │                |
│  │  Balancer    │───────▶ │  Workers     │                │
│  │  (Nginx)     │         │  (FastAPI)   │                │
│  └──────────────┘         └──────┬───────┘                │
│                                   │                       │
│                           ┌───────▼────────┐              │
│                           │  NVIDIA NIM    │              │
│                           │  API Endpoint  │              │
│                           └────────────────┘              │
│                                                           │
│  Environment:                                             │
│  • Docker container with Python 3.9+                      │
│  • Environment variables via .env                         │
│  • HTTPS with SSL certificate                             │
│  • Rate limiting middleware                               │
│  • Health check monitoring                                │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

**For implementation details, see individual module files.**
