"""Preparation record service.

NoticeMate does not submit anything, anywhere (§32). What this creates is a
*preparation record*: a local summary the citizen can save for their own
reference once they have finished getting ready, with a NoticeMate-local
reference number.

The reference is prefixed ``NM-DEMO-`` and the record explicitly states that
nothing was sent, so it can never be mistaken for a government acknowledgement.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from ..models import Notice, ResponseDraft, Submission, WorkflowState
from . import roadmap, workflow

NOT_SUBMITTED_NOTE = (
    "Nothing has been sent to any government system. NoticeMate cannot submit, "
    "pay, or file on your behalf. This record is only for your own reference — "
    "you still need to complete the real process through the official channel "
    "named in your notice."
)


def _make_reference() -> str:
    # Six-digit synthetic sequence derived from a UUID; clearly a demo ref and
    # never a real government reference.
    n = uuid.uuid4().int % 1_000_000
    return f"NM-DEMO-2026-{n:06d}"


def create_preparation_record(db: Session, notice: Notice) -> Submission:
    """Create (or return the existing) preparation record for a notice."""
    if notice.submission is not None:
        return notice.submission

    latest_response: ResponseDraft | None = None
    if notice.responses:
        latest_response = sorted(notice.responses, key=lambda r: r.version)[-1]

    record = Submission(
        notice_id=notice.id,
        reference=_make_reference(),
        status="Prepared — not submitted",
        response_snapshot=(latest_response.content if latest_response else ""),
        next_steps=_next_steps(notice),
    )
    db.add(record)

    workflow.advance_state(db, notice, WorkflowState.READY_FOR_OFFICIAL_CHANNEL)
    workflow.log_event(
        db,
        notice,
        "prepared",
        "Preparation finished. Nothing was submitted to any government system.",
        {"reference": record.reference, "submitted_to_government": False},
    )
    roadmap.sync(db, notice)
    db.commit()
    db.refresh(record)
    return record


def _next_steps(notice: Notice) -> str:
    """Tell the citizen exactly where to go next, from the notice itself."""
    a = notice.analysis
    channels = [c for c in ((a.official_channels if a else []) or []) if c.get("value")]
    if channels:
        lines = [
            f"- {c.get('label') or c.get('kind', 'Channel').title()}: {c['value']}"
            for c in channels[:4]
        ]
        where = "Complete the process through the channel named in your notice:\n" + "\n".join(
            lines
        )
    else:
        where = (
            "Your notice does not name a portal or office clearly. Re-read it for a "
            "contact address, or contact the issuing authority to ask where to "
            "complete this."
        )
    deadline = (a.deadline if a else "") or ""
    when = f"\n\nDo this by: {deadline}." if deadline else ""
    return f"{where}{when}\n\n{NOT_SUBMITTED_NOTE}"


# Back-compat alias for the existing endpoint.
create_submission = create_preparation_record
