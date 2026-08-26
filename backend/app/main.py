"""FastAPI application entry point.

A single server that exposes the REST API under ``/api`` and serves the
mobile-first single-page frontend for everything else. One process, no build
step, works offline and with no API key.

DEMO PROTOTYPE — NOT AN OFFICIAL GOVERNMENT SERVICE.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_DIR, UPLOAD_DIR, settings
from .database import init_db
from .api import demo, documents, health, notices, research, responses, submissions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("noticemate")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(
        "NoticeMate started (env=%s, ai_mode=%s)",
        settings.environment,
        "openai" if settings.ai_enabled else "demo-fallback",
    )
    yield


app = FastAPI(
    title="NoticeMate API",
    description=(
        "Citizen-friendly assistant that turns a complex (synthetic) government "
        "notice into a clear, actionable workflow. DEMO PROTOTYPE — not an "
        "official government service."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- API routers -----------------------------------------------------------
for module in (health, demo, notices, documents, research, responses, submissions):
    app.include_router(module.router)


# --- Friendly error handling ----------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Never leak stack traces to users; log the detail for developers."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Something went wrong on our side. Please try again.",
        },
    )





# --- Frontend (mounted last so /api/* keeps priority) ----------------------
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:  # pragma: no cover
    logger.warning("Frontend directory not found at %s", FRONTEND_DIR)

    @app.get("/")
    def _root():
        return {"app": settings.APP_NAME, "docs": "/docs", "health": "/api/health"}
