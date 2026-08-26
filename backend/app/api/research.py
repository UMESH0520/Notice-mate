"""Research endpoints: run web research and fetch sources."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import ResearchOut
from ..services import research as research_svc
from .common import get_notice_or_404

logger = logging.getLogger("noticemate.api.research")
router = APIRouter(tags=["research"])


@router.post("/api/notices/{notice_id}/research", response_model=ResearchOut)
def run_research(
    notice_id: str,
    force: bool = Query(default=False),
    db: Session = Depends(get_session),
) -> ResearchOut:
    """Run web research for a notice to cross-check dates and facts."""
    notice = get_notice_or_404(db, notice_id)
    return research_svc.run_research(db, notice, force=force)


@router.get("/api/notices/{notice_id}/sources", response_model=ResearchOut)
def get_sources(
    notice_id: str,
    db: Session = Depends(get_session),
) -> ResearchOut:
    """Get research sources and verified claims for a notice."""
    notice = get_notice_or_404(db, notice_id)
    return research_svc.serialize(notice)
