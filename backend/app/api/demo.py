"""Demo catalog endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from ..demo_data import demo_summaries
from ..schemas import DemoNoticeSummary

router = APIRouter(tags=["demo"])


@router.get("/api/demo/notices", response_model=list[DemoNoticeSummary])
def list_demo_notices() -> list[DemoNoticeSummary]:
    return [DemoNoticeSummary(**d) for d in demo_summaries()]
