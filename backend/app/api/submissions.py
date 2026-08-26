"""Submission endpoints: simulated submit and retrieval."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_session
from ..schemas import SubmissionOut, SubmitIn
from ..services import submission as submission_svc
from .common import get_notice_or_404, get_submission_or_404

router = APIRouter(tags=["submissions"])


@router.post("/api/notices/{notice_id}/submit", response_model=SubmissionOut, status_code=201)
def submit_notice(
    notice_id: str,
    body: SubmitIn,
    db: Session = Depends(get_session),
) -> SubmissionOut:
    notice = get_notice_or_404(db, notice_id)
    if not body.confirmed:
        raise HTTPException(
            status_code=422,
            detail="Please confirm that the information is correct before submitting.",
        )
    if notice.analysis is None:
        raise HTTPException(
            status_code=409, detail="Analyse the notice before submitting."
        )
    submission = submission_svc.create_submission(db, notice)
    return SubmissionOut.model_validate(submission)


@router.get("/api/submissions/{submission_id}", response_model=SubmissionOut)
def get_submission(
    submission_id: str, db: Session = Depends(get_session)
) -> SubmissionOut:
    submission = get_submission_or_404(db, submission_id)
    return SubmissionOut.model_validate(submission)
