"""Workflow engine.

NoticeMate's core is not "chat about a notice" — it is a preparation workflow
that turns a notice into ordered, stateful tasks and tracks progress.

Two rules shape this module:

* The workflow is **deterministic Python**, never an AI call (§10). Model output
  can describe a step; only this code decides which state the notice is in.
* The journey ends at *"ready to use the official channel"*. There is no
  "submitted" state, because NoticeMate never submits anything (§32).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import ActionItem, DocumentStatus, Notice, WorkflowEvent, WorkflowState

# Document statuses that mean "the citizen has dealt with this one".
DOCS_SETTLED = {
    DocumentStatus.UPLOADED,
    DocumentStatus.VERIFIED_FORMAT,
    DocumentStatus.COMPLETED,
    DocumentStatus.READY,
    DocumentStatus.UNAVAILABLE,
}


def log_event(
    db: Session, notice: Notice, event_type: str, message: str, meta: dict | None = None
) -> WorkflowEvent:
    event = WorkflowEvent(
        notice_id=notice.id,
        event_type=event_type,
        message=message,
        meta=meta or {},
    )
    db.add(event)
    return event


def advance_state(db: Session, notice: Notice, target: str) -> None:
    """Advance the workflow state, never moving backwards."""
    order = WorkflowState.ORDER
    if target not in order:
        return
    if order.index(target) > order.index(notice.workflow_state):
        notice.workflow_state = target
        db.add(notice)


def set_action_state(db: Session, item: ActionItem, state: str) -> None:
    item.state = state
    db.add(item)


def documents_settled(notice: Notice) -> bool:
    return bool(notice.documents) and all(
        d.status in DOCS_SETTLED for d in notice.documents
    )


def sync_plan_with_progress(db: Session, notice: Notice) -> None:
    """Sync action items state with preparation progress."""
    from . import roadmap
    roadmap.sync(db, notice)


# --- Status timeline -------------------------------------------------------
def status_steps(notice: Notice) -> list[dict]:
    """The tracking timeline.

    The last step is deliberately marked ``system="official"`` and is never
    "done": it happens outside NoticeMate, on the government's own channel, and
    we have no way to know whether the citizen completed it.
    """
    state_idx = WorkflowState.ORDER.index(notice.workflow_state)

    def done(state: str) -> bool:
        return state_idx >= WorkflowState.ORDER.index(state)

    steps = [
        {
            "key": "received",
            "label": "Notice received",
            "done": True,
            "system": "noticemate",
            "note": "",
        },
        {
            "key": "understood",
            "label": "Notice explained",
            "done": done(WorkflowState.ANALYZED),
            "system": "noticemate",
            "note": "",
        },
        {
            "key": "researched",
            "label": "Checked against public sources",
            "done": done(WorkflowState.RESEARCHED),
            "system": "noticemate",
            "note": "",
        },
        {
            "key": "documents",
            "label": "Documents prepared",
            "done": done(WorkflowState.DOCUMENTS_PREPARED),
            "system": "noticemate",
            "note": "",
        },
        {
            "key": "response",
            "label": "Draft prepared",
            "done": done(WorkflowState.RESPONSE_PREPARED),
            "system": "noticemate",
            "note": "",
        },
        {
            "key": "reviewed",
            "label": "You reviewed everything",
            "done": done(WorkflowState.USER_REVIEWED),
            "system": "noticemate",
            "note": "",
        },
        {
            "key": "ready",
            "label": "Ready for the official channel",
            "done": done(WorkflowState.READY_FOR_OFFICIAL_CHANNEL),
            "system": "noticemate",
            "note": "",
        },
        {
            "key": "official_action",
            "label": "You complete the process officially",
            "done": False,
            "system": "official",
            "note": (
                "This last step happens outside NoticeMate, on the official "
                "channel. NoticeMate does not submit anything for you and cannot "
                "see whether it is done."
            ),
        },
    ]
    return steps
