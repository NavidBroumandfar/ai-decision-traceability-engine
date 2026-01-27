"""
FastAPI application for AI Decision Traceability Engine.

This module provides the FastAPI application instance that exposes
the decision engine through a RESTful API interface.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.api.routes import router
from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to read version from pyproject.toml, fallback to default
VERSION = "0.1.0"
try:
    import re
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Simple regex to extract version from [project] section
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                VERSION = match.group(1)
except (FileNotFoundError, AttributeError):
    pass


def validate_startup_configuration():
    """
    Validate configuration on application startup.
    
    In production, this will fail fast with clear error messages.
    In local, this will log warnings but allow the app to start.
    """
    errors = settings.validate_production_config()
    
    if errors:
        error_msg = "Configuration validation failed:\n  " + "\n  ".join(errors)
        
        if settings.env == "prod":
            logger.critical(error_msg)
            raise RuntimeError(
                f"Production configuration is invalid. Fix the following issues:\n  "
                + "\n  ".join(errors)
            )
        else:
            # In local, log warnings but don't fail
            for error in errors:
                logger.warning(f"Configuration issue (non-fatal in local): {error}")
    
    # Log startup summary (no secrets)
    logger.info("=" * 60)
    logger.info("AI Decision Traceability Engine - Startup Configuration")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.env}")
    logger.info(f"LLM Provider: {settings.llm_provider.value}")
    logger.info(f"Model: {settings.openai_model if settings.openai_model else '(not set)'}")
    logger.info(f"Base URL: {settings.openai_base_url if settings.openai_base_url else '(default for provider)'}")
    logger.info(f"API Key: {'***configured***' if settings.openai_api_key and settings.openai_api_key.strip() else '(not set)'}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info(f"Max Request Size: {settings.max_request_size} bytes")
    logger.info("=" * 60)


# Validate configuration on module import
validate_startup_configuration()

app = FastAPI(
    title="AI Decision Traceability Engine",
    description="RESTful API for governed AI decision requests and audit queries"
)


class RequestSizeGuardMiddleware(BaseHTTPMiddleware):
    """Middleware to reject requests that exceed the configured size limit."""
    
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > settings.max_request_size:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "Request entity too large",
                            "detail": f"Request body size ({size} bytes) exceeds maximum allowed size ({settings.max_request_size} bytes)"
                        }
                    )
            except ValueError:
                # Invalid content-length header, let it pass (will fail later if needed)
                pass
        
        response = await call_next(request)
        return response


app.add_middleware(RequestSizeGuardMiddleware)
app.include_router(router)


@app.get("/health", tags=["health"])
async def health_check() -> Dict:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        Dictionary with status, version, and current time
    """
    return {
        "status": "ok",
        "version": VERSION,
        "time": datetime.utcnow().isoformat() + "Z"
    }

