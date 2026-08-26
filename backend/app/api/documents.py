"""Document endpoints: list, upload (with validation), and status updates."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..config import UPLOAD_DIR
from ..database import get_session
from ..models import Document, WorkflowState
from ..schemas import DocumentOut, DocumentStatusIn
from ..security import UploadError, sanitize_filename
from ..services import documents as doc_svc, workflow
from .common import get_notice_or_404

router = APIRouter(tags=["documents"])


def _maybe_mark_documents_prepared(db: Session, notice) -> None:
    docs = notice.documents
    if docs and all(d.status in {"uploaded", "unavailable"} for d in docs):
        workflow.advance_state(db, notice, WorkflowState.DOCUMENTS_PREPARED)
        workflow.log_event(db, notice, "documents_prepared", "All documents addressed.")
    workflow.sync_plan_with_progress(db, notice)


@router.get("/api/notices/{notice_id}/documents", response_model=list[DocumentOut])
def list_documents(
    notice_id: str, db: Session = Depends(get_session)
) -> list[DocumentOut]:
    notice = get_notice_or_404(db, notice_id)
    return [DocumentOut.model_validate(d) for d in notice.documents]


@router.post("/api/notices/{notice_id}/documents", response_model=DocumentOut)
async def upload_document(
    notice_id: str,
    file: UploadFile = File(...),
    document_id: str | None = Form(default=None),
    name: str | None = Form(default=None),
    db: Session = Depends(get_session),
) -> DocumentOut:
    notice = get_notice_or_404(db, notice_id)

    # Resolve which checklist item this upload satisfies.
    doc: Document | None = None
    if document_id:
        doc = next((d for d in notice.documents if d.id == document_id), None)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document item not found.")
    expected_name = (doc.name if doc else name) or "document"

    filename = sanitize_filename(file.filename)
    content = await file.read()
    try:
        report = doc_svc.validate_document(expected_name, filename, content)
    except UploadError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc

    # Persist the file safely under an isolated per-notice directory.
    dest_dir = UPLOAD_DIR / notice.id
    dest_dir.mkdir(parents=True, exist_ok=True)
    stored_path = dest_dir / filename
    stored_path.write_bytes(content)

    if doc is None:
        doc = Document(notice_id=notice.id, name=expected_name, required=False)
        db.add(doc)
    doc.status = "uploaded"
    doc.original_filename = filename
    doc.stored_path = str(stored_path)
    doc.validation = report
    db.add(doc)
    db.flush()

    workflow.log_event(
        db, notice, "document_uploaded", f"Uploaded: {expected_name}.",
        {"matched": report.get("matched")},
    )
    _maybe_mark_documents_prepared(db, notice)
    db.commit()
    db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.patch(
    "/api/notices/{notice_id}/documents/{document_id}", response_model=DocumentOut
)
def update_document_status(
    notice_id: str,
    document_id: str,
    body: DocumentStatusIn,
    db: Session = Depends(get_session),
) -> DocumentOut:
    notice = get_notice_or_404(db, notice_id)
    doc = next((d for d in notice.documents if d.id == document_id), None)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document item not found.")
    doc.status = body.status
    if body.status == "needed":
        doc.original_filename = None
        doc.stored_path = None
        doc.validation = {}
    db.add(doc)
    workflow.log_event(
        db, notice, "document_status", f"{doc.name} marked {body.status}."
    )
    _maybe_mark_documents_prepared(db, notice)
    db.commit()
    db.refresh(doc)
    return DocumentOut.model_validate(doc)
