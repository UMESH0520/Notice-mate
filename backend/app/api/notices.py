"""Notice endpoints: creation, analysis, retrieval, action plan, status."""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ..config import UPLOAD_DIR, settings
from ..database import get_session
from ..schemas import (
    ActionItemOut,
    AnalysisOut,
    AnalyzeIn,
    DemoNoticeIn,
    EligibilityOut,
    ImportantDateOut,
    NoticeDetailOut,
    NoticeOut,
    PreparationIn,
    RoadmapOut,
    StatusOut,
    StepHelpIn,
    StepHelpOut,
    TextNoticeIn,
    WorkflowEventOut,
)
from ..security import UploadError, sanitize_filename, validate_extension, validate_size
from ..services import extraction, notices as notice_svc, roadmap as roadmap_svc, workflow
from .common import get_notice_or_404

logger = logging.getLogger("noticemate.api")
router = APIRouter(tags=["notices"])

_LANGS = {"en", "hi", "te"}


def _lang(language: str) -> str:
    return language if language in _LANGS else "en"


# --- Creation --------------------------------------------------------------
@router.post("/api/notices/upload", response_model=NoticeOut, status_code=201)
async def upload_notice(
    file: UploadFile = File(...),
    session_id: str | None = Form(default=None),
    db: Session = Depends(get_session),
) -> NoticeOut:
    """Create a notice from an uploaded file (PDF/image/text) instantly."""
    filename = sanitize_filename(file.filename)
    try:
        ext = validate_extension(filename)
    except UploadError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc

    content = await file.read()
    try:
        validate_size(len(content))
    except UploadError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc

    # PDFs and Text files extract text instantly (<10ms)
    note = ""
    if ext == ".txt":
        raw_text = extraction._decode_text(content).strip()
    elif ext == ".pdf":
        extracted_pdf = extraction._extract_pdf(content)
        raw_text = extracted_pdf.text.strip()
        note = extracted_pdf.note
    else:
        # Images: return immediately (<10ms) so user transitions instantly to Processing screen
        raw_text = f"[Uploaded Document Image: {filename}]"

    raw_text = raw_text or f"[Uploaded Document Image: {filename}]"

    notice = notice_svc.create_from_text(
        db, text=raw_text, filename=filename, session_id=session_id, source="upload"
    )

    # Save uploaded file bytes to UPLOAD_DIR
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        file_path = UPLOAD_DIR / f"{notice.id}_{filename}"
        file_path.write_bytes(content)
    except Exception as exc:
        logger.warning("Failed to save uploaded file: %s", exc)

    if note:
        workflow.log_event(db, notice, "note", note)
        db.commit()
    out = NoticeOut.model_validate(notice)
    return out


@router.post("/api/notices/demo", response_model=NoticeOut, status_code=201)
def create_demo_notice(
    body: DemoNoticeIn, db: Session = Depends(get_session)
) -> NoticeOut:
    """Create a notice from a seeded synthetic demo notice."""
    try:
        notice = notice_svc.create_from_demo(db, body.demo_id, body.session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown demo notice.") from exc
    return NoticeOut.model_validate(notice)


@router.post("/api/notices/text", response_model=NoticeOut, status_code=201)
def create_text_notice(
    body: TextNoticeIn, db: Session = Depends(get_session)
) -> NoticeOut:
    """Create a notice from pasted text."""
    filename = sanitize_filename(body.filename) if body.filename else None
    notice = notice_svc.create_from_text(
        db, text=body.text, filename=filename, session_id=body.session_id, source="text"
    )
    return NoticeOut.model_validate(notice)


# --- Analysis --------------------------------------------------------------
@router.post("/api/notices/{notice_id}/analyze", response_model=AnalysisOut)
def analyze_notice(
    notice_id: str,
    body: AnalyzeIn | None = None,
    db: Session = Depends(get_session),
) -> AnalysisOut:
    notice = get_notice_or_404(db, notice_id)
    language = _lang(body.language if body else "en")

    images = None
    if notice.original_filename:
        ext = ("." + notice.original_filename.rsplit(".", 1)[-1]).lower()
        if ext in extraction.IMAGE_EXTS:
            file_path = UPLOAD_DIR / f"{notice.id}_{notice.original_filename}"
            if file_path.exists():
                mime = extraction._MIME.get(ext, "image/png")
                images = [(file_path.read_bytes(), mime)]

    if not (notice.raw_text or "").strip() and not notice.demo_id and not images:
        raise HTTPException(
            status_code=422,
            detail=(
                "We couldn't read any text from this notice, so it can't be analysed. "
                "Try pasting the text or a demo notice."
            ),
        )

    notice_svc.analyze(db, notice, language=language, images=images)
    analysis = notice_svc.localized_analysis(notice, language)
    if analysis is None:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Analysis failed unexpectedly.")
    return analysis


# --- Retrieval -------------------------------------------------------------
@router.get("/api/notices/{notice_id}", response_model=NoticeDetailOut)
def get_notice(
    notice_id: str,
    language: str = Query("en"),
    db: Session = Depends(get_session),
) -> NoticeDetailOut:
    notice = get_notice_or_404(db, notice_id)
    return notice_svc.serialize_detail(notice, _lang(language))


# --- Action plan -----------------------------------------------------------
@router.get(
    "/api/notices/{notice_id}/action-plan", response_model=list[ActionItemOut]
)
def get_action_plan(
    notice_id: str, db: Session = Depends(get_session)
) -> list[ActionItemOut]:
    notice = get_notice_or_404(db, notice_id)
    workflow.sync_plan_with_progress(db, notice)
    db.commit()
    return [
        ActionItemOut.model_validate(i)
        for i in sorted(notice.action_items, key=lambda x: x.order)
    ]


@router.patch(
    "/api/notices/{notice_id}/action-plan/{item_id}", response_model=ActionItemOut
)
def update_action_item(
    notice_id: str,
    item_id: str,
    state: str = Query(..., pattern="^(not_started|in_progress|completed|needs_attention)$"),
    db: Session = Depends(get_session),
) -> ActionItemOut:
    notice = get_notice_or_404(db, notice_id)
    item = next((i for i in notice.action_items if i.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Action item not found.")
    workflow.set_action_state(db, item, state)
    db.commit()
    db.refresh(item)
    return ActionItemOut.model_validate(item)


# --- Status timeline -------------------------------------------------------
@router.get("/api/notices/{notice_id}/status", response_model=StatusOut)
def get_status(
    notice_id: str, db: Session = Depends(get_session)
) -> StatusOut:
    notice = get_notice_or_404(db, notice_id)
    return StatusOut(
        notice_id=notice.id,
        workflow_state=notice.workflow_state,
        steps=workflow.status_steps(notice),
        events=[
            WorkflowEventOut.model_validate(e)
            for e in sorted(notice.events, key=lambda x: x.created_at)
        ],
    )


# --- Sub-resource endpoints (§51) ------------------------------------------
@router.get(
    "/api/notices/{notice_id}/dates", response_model=list[ImportantDateOut]
)
def get_important_dates(
    notice_id: str, db: Session = Depends(get_session)
) -> list[ImportantDateOut]:
    notice = get_notice_or_404(db, notice_id)
    return [
        ImportantDateOut.model_validate(d)
        for d in sorted(notice.important_dates, key=lambda x: x.order)
    ]


@router.get(
    "/api/notices/{notice_id}/eligibility", response_model=list[EligibilityOut]
)
def get_eligibility(
    notice_id: str, db: Session = Depends(get_session)
) -> list[EligibilityOut]:
    notice = get_notice_or_404(db, notice_id)
    return [
        EligibilityOut.model_validate(e)
        for e in sorted(notice.eligibility_items, key=lambda x: x.order)
    ]


@router.get("/api/notices/{notice_id}/roadmap", response_model=RoadmapOut)
def get_roadmap(
    notice_id: str,
    language: str = Query("en"),
    db: Session = Depends(get_session),
) -> RoadmapOut:
    notice = get_notice_or_404(db, notice_id)
    if not notice.action_items:
        roadmap_svc.build(db, notice, language=_lang(language))
        db.commit()
        db.refresh(notice)
    return roadmap_svc.serialize(notice)


@router.put("/api/notices/{notice_id}/preparation", response_model=RoadmapOut)
def update_preparation_progress(
    notice_id: str,
    body: PreparationIn,
    db: Session = Depends(get_session),
) -> RoadmapOut:
    notice = get_notice_or_404(db, notice_id)
    return roadmap_svc.set_step_state(db, notice, body.step_key, body.state)


@router.post("/api/notices/{notice_id}/roadmap/step-help", response_model=StepHelpOut)
def help_roadmap_step(
    notice_id: str,
    body: StepHelpIn,
    db: Session = Depends(get_session),
) -> StepHelpOut:
    notice = get_notice_or_404(db, notice_id)
    return roadmap_svc.step_help(
        db, notice, body.step_id, body.question, _lang(body.language)
    )


