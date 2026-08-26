"""Response draft endpoints: generate (AI/fallback) and save/accept."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_session
from ..demo_data import get_demo
from ..models import ResponseDraft, WorkflowState
from ..schemas import ResponseDraftOut, ResponseGenerateIn, ResponseSaveIn
from ..services import ai, notices as notice_svc, workflow
from .common import get_notice_or_404

router = APIRouter(tags=["responses"])


def _next_version(notice) -> int:
    return (max((r.version for r in notice.responses), default=0)) + 1


@router.post("/api/notices/{notice_id}/response", response_model=ResponseDraftOut)
def generate_response(
    notice_id: str,
    body: ResponseGenerateIn | None = None,
    db: Session = Depends(get_session),
) -> ResponseDraftOut:
    notice = get_notice_or_404(db, notice_id)
    if notice.analysis is None:
        raise HTTPException(
            status_code=409,
            detail="Please analyse the notice before preparing a response.",
        )
    body = body or ResponseGenerateIn()
    language = body.language if body.language in {"en", "hi", "te"} else "en"

    analysis_dict = {
        "reference_number": notice.analysis.reference_number,
        "subject": notice.analysis.subject,
        "authority": notice.analysis.authority,
        "required_action": notice.analysis.required_action,
        "deadline": notice.analysis.deadline,
    }
    documents = [
        {"name": d.name} for d in notice.documents if d.status != "unavailable"
    ]
    demo = get_demo(notice.demo_id) if notice.demo_id else None
    template = demo.get("response_template") if demo else None

    content, source = ai.generate_response_text(
        analysis_dict, documents, language, body.extra_context, template
    )

    draft = ResponseDraft(
        notice_id=notice.id,
        content=content,
        draft_source=source,
        status="draft",
        version=_next_version(notice),
    )
    db.add(draft)
    workflow.advance_state(db, notice, WorkflowState.RESPONSE_PREPARED)
    workflow.log_event(
        db, notice, "response_generated", f"Draft response generated ({source}).",
        {"source": source, "language": language},
    )
    workflow.sync_plan_with_progress(db, notice)
    db.commit()
    db.refresh(draft)
    return ResponseDraftOut.model_validate(draft)


@router.put("/api/notices/{notice_id}/response", response_model=ResponseDraftOut)
def save_response(
    notice_id: str,
    body: ResponseSaveIn,
    db: Session = Depends(get_session),
) -> ResponseDraftOut:
    """Save a user-edited draft (and optionally mark it accepted)."""
    notice = get_notice_or_404(db, notice_id)
    draft = ResponseDraft(
        notice_id=notice.id,
        content=body.content,
        draft_source="user-edited",
        status="accepted" if body.accept else "draft",
        version=_next_version(notice),
    )
    db.add(draft)
    workflow.advance_state(db, notice, WorkflowState.RESPONSE_PREPARED)
    workflow.log_event(
        db, notice, "response_saved",
        "Response accepted by user." if body.accept else "Response edited by user.",
    )
    workflow.sync_plan_with_progress(db, notice)
    db.commit()
    db.refresh(draft)
    return ResponseDraftOut.model_validate(draft)


@router.get("/api/notices/{notice_id}/response", response_model=ResponseDraftOut)
def get_response(
    notice_id: str, db: Session = Depends(get_session)
) -> ResponseDraftOut:
    notice = get_notice_or_404(db, notice_id)
    latest = notice_svc.latest_response(notice)
    if latest is None:
        raise HTTPException(status_code=404, detail="No response drafted yet.")
    return latest
