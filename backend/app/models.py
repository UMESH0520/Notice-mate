"""SQLAlchemy ORM models for NoticeMate.

Entities: Notice, NoticeAnalysis, Document, ActionItem, ResponseDraft,
Submission, WorkflowEvent. IDs are synthetic UUIDs. No real personal data is
ever stored — uploaded notices are synthetic demo content.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --- Workflow states -------------------------------------------------------
class WorkflowState:
    """Preparation-journey states.

    NoticeMate never submits anything to a government system, so the terminal
    state is "ready to use the official channel" — not "submitted".
    """

    RECEIVED = "RECEIVED"
    ANALYZED = "ANALYZED"
    RESEARCHED = "RESEARCHED"
    DOCUMENTS_PREPARED = "DOCUMENTS_PREPARED"
    RESPONSE_PREPARED = "RESPONSE_PREPARED"
    USER_REVIEWED = "USER_REVIEWED"
    READY_FOR_OFFICIAL_CHANNEL = "READY_FOR_OFFICIAL_CHANNEL"

    ORDER = [
        RECEIVED,
        ANALYZED,
        RESEARCHED,
        DOCUMENTS_PREPARED,
        RESPONSE_PREPARED,
        USER_REVIEWED,
        READY_FOR_OFFICIAL_CHANNEL,
    ]


class TrustLevel:
    """Where a piece of information came from (§24 trust model).

    Stored internally; the UI simplifies these into three friendly labels.
    """

    FROM_NOTICE = "FROM_NOTICE"
    OFFICIAL_SOURCE = "OFFICIAL_SOURCE"
    RELIABLE_SECONDARY_SOURCE = "RELIABLE_SECONDARY_SOURCE"
    INFERENCE = "INFERENCE"
    UNKNOWN = "UNKNOWN"


class AuthorityLevel:
    """Authority ranking for a researched source."""

    OFFICIAL = "OFFICIAL"
    HIGHLY_RELIABLE = "HIGHLY_RELIABLE"
    SECONDARY = "SECONDARY"
    UNVERIFIED = "UNVERIFIED"
    # Used only for curated demo data, so a demo source can never be mistaken
    # for something that was actually retrieved from the live web.
    DEMO = "DEMO"


class DocumentStatus:
    NOT_STARTED = "NOT_STARTED"
    READY = "READY"
    UPLOADED = "UPLOADED"
    VERIFIED_FORMAT = "VERIFIED_FORMAT"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    COMPLETED = "COMPLETED"
    UNAVAILABLE = "UNAVAILABLE"

    ALL = [
        NOT_STARTED,
        READY,
        UPLOADED,
        VERIFIED_FORMAT,
        NEEDS_REVIEW,
        COMPLETED,
        UNAVAILABLE,
    ]


class Notice(Base):
    __tablename__ = "notices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    # Anonymous "user" handle — never PII. Groups a citizen's session.
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[str] = mapped_column(String(16), default="upload")  # upload|demo|text
    demo_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String(8), default="en")
    workflow_state: Mapped[str] = mapped_column(
        String(32), default=WorkflowState.RECEIVED
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )

    analysis: Mapped["NoticeAnalysis | None"] = relationship(
        back_populates="notice", uselist=False, cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )
    action_items: Mapped[list["ActionItem"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )
    responses: Mapped[list["ResponseDraft"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )
    submission: Mapped["Submission | None"] = relationship(
        back_populates="notice", uselist=False, cascade="all, delete-orphan"
    )
    events: Mapped[list["WorkflowEvent"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )
    important_dates: Mapped[list["ImportantDate"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )
    eligibility_items: Mapped[list["EligibilityItem"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )
    research_queries: Mapped[list["ResearchQuery"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )
    research_sources: Mapped[list["ResearchSource"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )
    preparation_states: Mapped[list["PreparationState"]] = relationship(
        back_populates="notice", cascade="all, delete-orphan"
    )


class NoticeAnalysis(Base):
    __tablename__ = "notice_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(
        ForeignKey("notices.id"), unique=True, index=True
    )

    notice_type: Mapped[str] = mapped_column(String(255), default="")
    # Machine-readable classification key (see schemas.CATEGORIES).
    category: Mapped[str] = mapped_column(String(48), default="other")
    category_confident: Mapped[bool] = mapped_column(Boolean, default=False)
    # Which layout the frontend should use: application | response | benefit
    mode: Mapped[str] = mapped_column(String(24), default="response")
    title: Mapped[str] = mapped_column(String(512), default="")
    authority: Mapped[str] = mapped_column(String(255), default="")
    department: Mapped[str] = mapped_column(String(255), default="")
    organization: Mapped[str] = mapped_column(String(255), default="")
    scheme_name: Mapped[str] = mapped_column(String(255), default="")
    notice_date: Mapped[str] = mapped_column(String(64), default="")
    deadline: Mapped[str] = mapped_column(String(64), default="")
    reference_number: Mapped[str] = mapped_column(String(128), default="")
    subject: Mapped[str] = mapped_column(String(512), default="")
    one_sentence: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    why_received: Mapped[str] = mapped_column(Text, default="")
    required_action: Mapped[str] = mapped_column(Text, default="")
    what_happens_next: Mapped[str] = mapped_column(Text, default="")
    consequences: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    # "openai" | "demo-curated" | "demo-fallback"
    analysis_source: Mapped[str] = mapped_column(String(32), default="demo-fallback")
    # Set when part of an image/PDF could not be read confidently.
    read_warning: Mapped[str] = mapped_column(Text, default="")

    # Structured / list fields stored as JSON (portable to PostgreSQL JSONB).
    required_documents: Mapped[list] = mapped_column(JSON, default=list)
    next_steps: Mapped[list] = mapped_column(JSON, default=list)
    uncertainties: Mapped[list] = mapped_column(JSON, default=list)
    fees: Mapped[list] = mapped_column(JSON, default=list)
    application_process: Mapped[list] = mapped_column(JSON, default=list)
    official_channels: Mapped[list] = mapped_column(JSON, default=list)
    selection_process: Mapped[list] = mapped_column(JSON, default=list)
    mentioned_laws: Mapped[list] = mapped_column(JSON, default=list)
    mentioned_rules: Mapped[list] = mapped_column(JSON, default=list)
    mentioned_forms: Mapped[list] = mapped_column(JSON, default=list)
    mentioned_portals: Mapped[list] = mapped_column(JSON, default=list)
    financial_amounts: Mapped[list] = mapped_column(JSON, default=list)
    glossary: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    important_notes: Mapped[list] = mapped_column(JSON, default=list)
    unknown_information: Mapped[list] = mapped_column(JSON, default=list)
    # {"deadline": "Page 2, paragraph 4", ...} — lets the UI say where a fact
    # was found in the original document.
    source_spans: Mapped[dict] = mapped_column(JSON, default=dict)
    contact_information: Mapped[dict] = mapped_column(JSON, default=dict)
    vacancies: Mapped[dict] = mapped_column(JSON, default=dict)
    # Internal bookkeeping (roadmap grouping, research mode/timestamp). Never
    # part of the analysis contract and never shown as extracted content.
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    # Per-language narrative overrides: {"hi": {...}, "te": {...}}
    translations: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    notice: Mapped[Notice] = relationship(back_populates="analysis")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(ForeignKey("notices.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    reason: Mapped[str] = mapped_column(Text, default="")
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    # "yes" | "no" | "conditional" — richer than the boolean above, which is
    # kept for backwards compatibility with the existing UI.
    requirement: Mapped[str] = mapped_column(String(16), default="yes")
    # application | verification | both | unknown
    stage: Mapped[str] = mapped_column(String(24), default="unknown")
    doc_format: Mapped[str] = mapped_column(String(120), default="")
    size_limit: Mapped[str] = mapped_column(String(120), default="")
    validity: Mapped[str] = mapped_column(String(120), default="")
    # Where this requirement came from: FROM_NOTICE / OFFICIAL_SOURCE / ...
    trust: Mapped[str] = mapped_column(String(32), default=TrustLevel.FROM_NOTICE)
    source_note: Mapped[str] = mapped_column(String(255), default="")
    # See DocumentStatus
    status: Mapped[str] = mapped_column(String(24), default=DocumentStatus.NOT_STARTED)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stored_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    validation: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )

    notice: Mapped[Notice] = relationship(back_populates="documents")


class ImportantDate(Base):
    """A single dated milestone (§10 — dates are a first-class feature)."""

    __tablename__ = "important_dates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(ForeignKey("notices.id"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    # e.g. application_start, application_end, examination, response_deadline
    kind: Mapped[str] = mapped_column(String(48), default="other")
    label: Mapped[str] = mapped_column(String(160), default="")
    # Human-readable value exactly as stated ("30 September 2026",
    # "within 15 days of receipt", "To be announced").
    value: Mapped[str] = mapped_column(String(255), default="")
    # ISO date, only when an unambiguous calendar date was stated. Never
    # inferred — a relative period stays relative.
    iso_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_relative: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deadline: Mapped[bool] = mapped_column(Boolean, default=False)
    trust: Mapped[str] = mapped_column(String(32), default=TrustLevel.FROM_NOTICE)
    note: Mapped[str] = mapped_column(Text, default="")
    # Populated when research found a different date for the same milestone.
    conflict_note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    notice: Mapped[Notice] = relationship(back_populates="important_dates")


class EligibilityItem(Base):
    """One eligibility condition and, when determinable, whether it is met."""

    __tablename__ = "eligibility_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(ForeignKey("notices.id"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    # age | education | experience | residency | category | income | other
    category: Mapped[str] = mapped_column(String(32), default="other")
    requirement: Mapped[str] = mapped_column(Text, default="")
    detail: Mapped[str] = mapped_column(Text, default="")
    # met | not_met | needs_input | unknown
    status: Mapped[str] = mapped_column(String(16), default="needs_input")
    # What we would need from the user to decide (e.g. "your age").
    needs: Mapped[str] = mapped_column(String(160), default="")
    trust: Mapped[str] = mapped_column(String(32), default=TrustLevel.FROM_NOTICE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )

    notice: Mapped[Notice] = relationship(back_populates="eligibility_items")


class ResearchQuery(Base):
    """A targeted search generated from the analysis (never the raw notice)."""

    __tablename__ = "research_queries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(ForeignKey("notices.id"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    query: Mapped[str] = mapped_column(String(512), default="")
    # What this query is trying to verify, in plain language.
    purpose: Mapped[str] = mapped_column(String(255), default="")
    # ok | no_results | failed | skipped
    status: Mapped[str] = mapped_column(String(16), default="ok")
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    notice: Mapped[Notice] = relationship(back_populates="research_queries")


class ResearchSource(Base):
    """One retrieved source plus the claim it supports or contradicts.

    ``url`` is only ever populated with a URL that was actually returned by the
    search tool. Curated demo sources are marked ``authority_level='DEMO'`` so
    they can never be presented as live retrievals.
    """

    __tablename__ = "research_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(ForeignKey("notices.id"), index=True)
    query_id: Mapped[str | None] = mapped_column(
        ForeignKey("research_queries.id"), nullable=True
    )
    order: Mapped[int] = mapped_column(Integer, default=0)
    claim: Mapped[str] = mapped_column(Text, default="")
    title: Mapped[str] = mapped_column(String(512), default="")
    url: Mapped[str] = mapped_column(String(1024), default="")
    domain: Mapped[str] = mapped_column(String(255), default="")
    # OFFICIAL | HIGHLY_RELIABLE | SECONDARY | UNVERIFIED | DEMO
    authority_level: Mapped[str] = mapped_column(
        String(24), default=AuthorityLevel.UNVERIFIED
    )
    source_type: Mapped[str] = mapped_column(String(64), default="")
    excerpt: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[str] = mapped_column(Text, default="")
    why_it_matters: Mapped[str] = mapped_column(Text, default="")
    relevance: Mapped[float] = mapped_column(Float, default=0.0)
    # True/False/None — does this source agree with the notice?
    supports_notice: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    conflict: Mapped[bool] = mapped_column(Boolean, default=False)
    conflict_detail: Mapped[str] = mapped_column(Text, default="")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    notice: Mapped[Notice] = relationship(back_populates="research_sources")


class PreparationState(Base):
    """Progress the citizen has made on a roadmap step.

    Keyed by an opaque step key so the roadmap can evolve without migrations.
    """

    __tablename__ = "preparation_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(ForeignKey("notices.id"), index=True)
    step_key: Mapped[str] = mapped_column(String(64), index=True)
    # not_started | in_progress | completed
    state: Mapped[str] = mapped_column(String(20), default="not_started")
    note: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )

    notice: Mapped[Notice] = relationship(back_populates="preparation_states")


class ActionItem(Base):
    __tablename__ = "action_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(ForeignKey("notices.id"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    # not_started | in_progress | completed | needs_attention
    state: Mapped[str] = mapped_column(String(20), default="not_started")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )

    notice: Mapped[Notice] = relationship(back_populates="action_items")


class ResponseDraft(Base):
    __tablename__ = "response_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(ForeignKey("notices.id"), index=True)
    content: Mapped[str] = mapped_column(Text, default="")
    # "openai" | "demo-fallback" | "user-edited"
    draft_source: Mapped[str] = mapped_column(String(32), default="demo-fallback")
    status: Mapped[str] = mapped_column(String(16), default="draft")  # draft|accepted
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    notice: Mapped[Notice] = relationship(back_populates="responses")


class Submission(Base):
    """A *preparation record* the citizen saves for their own reference.

    NoticeMate never submits anything to a government system. This row records
    that the user finished preparing, together with a NoticeMate-local
    reference. It is explicitly **not** a government acknowledgement number.
    """

    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(
        ForeignKey("notices.id"), unique=True, index=True
    )
    reference: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="Received")
    response_snapshot: Mapped[str] = mapped_column(Text, default="")
    next_steps: Mapped[str] = mapped_column(Text, default="")
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    notice: Mapped[Notice] = relationship(back_populates="submission")


class WorkflowEvent(Base):
    __tablename__ = "workflow_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(ForeignKey("notices.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(48))
    message: Mapped[str] = mapped_column(Text, default="")
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    notice: Mapped[Notice] = relationship(back_populates="events")
