"""Shared API helpers."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import Notice, Submission


def get_notice_or_404(db: Session, notice_id: str) -> Notice:
    notice = db.get(Notice, notice_id)
    if notice is None:
        raise HTTPException(status_code=404, detail="Notice not found.")
    return notice


def get_submission_or_404(db: Session, submission_id: str) -> Submission:
    submission = db.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return submission
