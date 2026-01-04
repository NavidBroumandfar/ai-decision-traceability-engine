"""
FastAPI application for AI Decision Traceability Engine.

This module provides the FastAPI application instance that exposes
the decision engine through a RESTful API interface.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI

from src.api.routes import router

app = FastAPI(
    title="AI Decision Traceability Engine",
    description="RESTful API for governed AI decision requests and audit queries"
)

app.include_router(router)

