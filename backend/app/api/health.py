"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from ..config import settings
from ..schemas import HealthOut
from ..services import ai

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(
        app=settings.APP_NAME,
        version=settings.VERSION,
        ai_enabled=settings.ai_enabled,
        ai_mode=ai.ai_mode(),
        environment=settings.environment,
    )
