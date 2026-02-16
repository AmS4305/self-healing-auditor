# 🛡️ Self-Healing Code Auditor

An AI-powered security vulnerability detection and **automated remediation** system built with **LangGraph's Reflection Pattern**, **NVIDIA NIM APIs**, and **FastAPI**.

The auditor analyzes your code for security vulnerabilities, automatically generates fixes, then re-audits the fixed code — repeating until the code is secure or the iteration limit is reached.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![NVIDIA NIM](https://img.shields.io/badge/NVIDIA_NIM-Llama_3.1_70B-76b900?logo=nvidia&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Reflection_Pattern-orange)

---

## ✨ Features

- **Automated Vulnerability Detection** — Scans code for security issues using `meta/llama-3.1-70b-instruct`
- **Self-Healing Loop** — Iterative audit → fix → re-audit cycle (configurable iterations)
- **Structured JSON Output** — Enforced Pydantic schemas for consistent vulnerability reports
- **CWE Classification** — Each vulnerability tagged with its CWE ID and severity level
- **Full History Tracking** — Complete timeline of every audit iteration and applied fix
- **Professional Dark UI** — VS Code / GitHub-inspired purple & black theme
- **Cross-Origin Support** — Works with Live Server (port 5500) or served directly from FastAPI (port 8000)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                 FastAPI Server (:8000)               │
│                                                     │
│   /api/audit (POST)    /api/health (GET)            │
│         │                                           │
│   ┌─────▼──────────────────────────────────────┐    │
│   │           LangGraph Workflow               │    │
│   │                                            │    │
│   │   START ──► Auditor ──► should_continue    │    │
│   │              (LLM)         │       │       │    │
│   │                        unsafe &   safe OR  │    │
│   │                        iter < 3   iter ≥ 3 │    │
│   │               ┌───────────┘       │        │    │
│   │               ▼                   ▼        │    │
│   │            Fixer ──► Auditor    END        │    │
│   │             (LLM)   (re-audit)             │    │
│   └────────────────────────────────────────────┘    │
│                                                     │
│   / (Static)  →  frontend/index.html, app.js, css   │
└─────────────────────────────────────────────────────┘
```

Both **Auditor** and **Fixer** nodes use `meta/llama-3.1-70b-instruct` via NVIDIA NIM APIs.

---

## 📁 Project Structure

```
self-healing-auditor/
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic models (AuditReport, Vulnerability, etc.)
│   │   └── state.py            # LangGraph state definition (GraphState)
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── auditor.py          # Security vulnerability detection node
│   │   ├── fixer.py            # Automated code remediation node
│   │   └── router.py           # Conditional routing logic (should_continue)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py              # FastAPI endpoints (/api/audit, /api/health)
│   └── utils/
│       ├── __init__.py
│       └── graph.py            # LangGraph workflow compilation
├── frontend/
│   ├── index.html              # Main UI page
│   ├── app.js                  # Frontend logic (API calls, rendering)
│   └── style.css               # Dark theme styling
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **NVIDIA NIM API Key** — [Get one free here](https://build.nvidia.com/)

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/<your-username>/self-healing-auditor.git
   cd self-healing-auditor
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv

   # Windows (PowerShell)
   venv\Scripts\activate

   # Windows (Git Bash / WSL)
   source venv/Scripts/activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API key:**

   ```bash
   # Copy the example config
   cp .env.example .env     # Linux/macOS/Git Bash
   copy .env.example .env   # Windows CMD
   ```

   Edit `.env` and paste your NVIDIA API key:

   ```env
   NVIDIA_API_KEY=nvapi-your-key-here
   APP_HOST=0.0.0.0
   APP_PORT=8000
   MAX_ITERATIONS=3
   ```

5. **Run the application:**

   ```bash
   python main.py
   ```

6. **Open in browser:**
   ```
   http://localhost:8000
   ```

You should see:

```
╔═══════════════════════════════════════════════════════════╗
║     Self-Healing Code Auditor - NVIDIA NIM Edition        ║
╚═══════════════════════════════════════════════════════════╝

🚀 Server starting on http://0.0.0.0:8000
📊 Auditor Model: meta/llama-3.1-70b-instruct
🔧 Fixer Model:   meta/llama-3.1-70b-instruct
🔄 Max Iterations: 3
```

---

## 🔧 API Reference

### `POST /api/audit`

Audits code for security vulnerabilities and automatically applies fixes.

**Request:**

```json
{
  "code": "from flask import Flask, request\nimport sqlite3\n\napp = Flask(__name__)\n\n@app.route('/user')\ndef get_user():\n    user_id = request.args.get('id')\n    query = f\"SELECT * FROM users WHERE id = {user_id}\"\n    ..."
}
```

**Response:**

```json
{
  "original_code": "...",
  "final_code": "...",
  "final_status": "healed",
  "total_iterations": 2,
  "history": [
    {
      "iteration": 0,
      "code_snapshot": "...",
      "audit_report": {
        "is_safe": false,
        "vulnerabilities": [
          {
            "severity": "critical",
            "description": "SQL Injection via string interpolation",
            "line_number": 9,
            "cwe_id": "CWE-89",
            "suggested_fix_snippet": "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
          }
        ],
        "summary": "Critical SQL injection vulnerability detected"
      },
      "fix_applied": "..."
    }
  ]
}
```

**Status Values:**
| Status | Meaning |
|--------|---------|
| `safe` | Code had no vulnerabilities from the start |
| `healed` | Vulnerabilities were found and successfully fixed |
| `max_iterations_reached` | Vulnerabilities remain after all iterations |

### `GET /api/health`

Health check endpoint.

**Response:** `{"status": "healthy", "service": "self-healing-auditor"}`

---

## 📊 Data Models

### Vulnerability

```python
class Vulnerability(BaseModel):
    severity: str                    # "critical", "high", "medium", "low"
    description: str                 # Human-readable explanation
    line_number: Optional[int]       # Source code line number
    cwe_id: str                      # e.g., "CWE-89"
    suggested_fix_snippet: str       # Corrected code snippet
```

### AuditReport

```python
class AuditReport(BaseModel):
    is_safe: bool                    # True if no vulnerabilities found
    vulnerabilities: List[Vulnerability]
    summary: str                     # Overall security assessment
```

---

## 🔄 How the Reflection Loop Works

1. **Auditor** analyzes the code and produces a structured `AuditReport` (JSON parsed from LLM output)
2. **Router** checks: Is the code safe? Have we hit the iteration limit?
   - If **unsafe** and **under limit** → route to **Fixer**
   - If **safe** or **at limit** → route to **END**
3. **Fixer** applies security patches based on the audit report
4. Loop back to step 1 with the fixed code

Each iteration is recorded in the `history` array for full transparency.

---

## 🎨 Frontend

- **Dark Theme** — Professional purple/black aesthetic inspired by VS Code
- **Code Editor** — Pre-loaded with a sample vulnerable Flask app
- **Loading States** — Shows which AI models are working
- **Timeline View** — Expandable cards for each iteration showing vulnerabilities and fixes
- **Status Badges** — Color-coded indicators (✓ Safe, 🛡️ Healed, ⚠️ Max Iterations)
- **Keyboard Shortcuts** — `Ctrl+Enter` to analyze

The frontend auto-detects whether it's served from port 8000 (FastAPI) or port 5500 (Live Server) and adjusts API URLs accordingly.

---

## ⚙️ Configuration

| Variable         | Description         | Default   | Required |
| ---------------- | ------------------- | --------- | -------- |
| `NVIDIA_API_KEY` | NVIDIA NIM API key  | —         | ✅ Yes   |
| `APP_HOST`       | Server bind address | `0.0.0.0` | No       |
| `APP_PORT`       | Server port         | `8000`    | No       |
| `MAX_ITERATIONS` | Max healing cycles  | `3`       | No       |

---

## 🐛 Troubleshooting

| Problem                          | Solution                                               |
| -------------------------------- | ------------------------------------------------------ |
| `NVIDIA_API_KEY not found`       | Copy `.env.example` to `.env` and add your API key     |
| `ModuleNotFoundError`            | Activate venv first: `venv\Scripts\activate` (Windows) |
| 405 Method Not Allowed           | Open `http://localhost:8000` instead of port 5500      |
| 500 Internal Server Error        | Check terminal for traceback; verify API key is valid  |
| Warnings about "type is unknown" | Harmless — the model works despite the warning         |

---

## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **AI Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph) (Reflection Pattern)
- **LLM**: [NVIDIA NIM](https://build.nvidia.com/) — `meta/llama-3.1-70b-instruct`
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Frontend**: Vanilla HTML/CSS/JS (no framework)

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 🗺️ Roadmap

- [ ] Rate limiting (per-IP request throttling)
- [ ] Language dropdown (Python, JavaScript, Java, C++, Go)
- [ ] Side-by-side code editor layout
- [ ] User-configurable iteration count
- [ ] Human-in-the-loop refinement (review fixes before next iteration)
- [ ] Streaming responses (real-time progress)

---

**Built with ❤️ using NVIDIA NIM + LangGraph**
