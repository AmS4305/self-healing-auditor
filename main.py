"""
Self-Healing Code Auditor - FastAPI Application
Main entry point for the backend server
"""

import os

from pathlib import Path
from dotenv import load_dotenv

# Load environment variables BEFORE importing backend modules
# (ChatNVIDIA objects are created at import time and need the API key)
load_dotenv()

# Validate NVIDIA API key is configured
if not os.getenv("NVIDIA_API_KEY"):
    raise ValueError(
        "NVIDIA_API_KEY not found in environment. "
        "Please copy .env.example to .env and add your API key."
    )

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import router

# Initialize FastAPI app
app = FastAPI(
    title="Self-Healing Code Auditor",
    description="AI-powered security vulnerability detection and remediation",
    version="1.0.0",
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes (must be before static mount so /api/* takes priority)
app.include_router(router, prefix="/api", tags=["audit"])

# Mount frontend at root with html=True to auto-serve index.html
# This also serves style.css and app.js at their relative paths
frontend_path = Path(__file__).parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))

    print(f"""
╔═══════════════════════════════════════════════════════════╗
║     Self-Healing Code Auditor - NVIDIA NIM Edition        ║
╚═══════════════════════════════════════════════════════════╝

🚀 Server starting on http://{host}:{port}

📊 Auditor Model: meta/llama-3.1-70b-instruct
🔧 Fixer Model:   meta/llama-3.1-70b-instruct
🔄 Max Iterations: {os.getenv("MAX_ITERATIONS", 3)}

Press CTRL+C to stop
""")

    uvicorn.run("main:app", host=host, port=port, reload=True)
