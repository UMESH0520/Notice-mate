"""Pydantic schemas — the API request/response contract.

The AI (or the deterministic fallback) is required to produce a
``NoticeAnalysisSchema`` so that application logic never depends on free-form
model text. Everything the frontend renders comes through one of these models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

# Document classifications (§8). "other" is always allowed — we never force a
# false category.
CATEGORIES = (
    "recruitment",
    "job_application",
    "scholarship",
    "education",
    "examination",
    "admission",
    "pension",
    "epfo",
    "tax",
    "certificate",
    "licence",
    "municipal",
    "welfare_scheme",
    "government_benefit",
    "grievance",
    "property",
    "transport",
    "public_announcement",
    "compliance",
    "document_verification",
    "payment",
    "hearing",
    "other",
)

# Which layout the frontend uses for this document (§28–30).
NoticeMode = Literal["application", "response", "benefit"]

TrustLiteral = Literal[
    "FROM_NOTICE",
    "OFFICIAL_SOURCE",
    "RELIABLE_SECONDARY_SOURCE",
    "INFERENCE",
    "UNKNOWN",
]

AuthorityLiteral = Literal[
    "OFFICIAL", "HIGHLY_RELIABLE", "SECONDARY", "UNVERIFIED", "DEMO"
]

Language = Literal["en", "hi", "te"]


# --- AI analysis contract --------------------------------------------------
class RequiredDocument(BaseModel):
    """A document the citizen must produce (§12)."""

    name: str
    reason: str = ""
    required: bool = True
    # Richer than ``required``: some documents are only needed conditionally.
    requirement: Literal["yes", "no", "conditional"] = "yes"
    stage: Literal["application", "verification", "both", "unknown"] = "unknown"
    doc_format: str = ""
    size_limit: str = ""
    validity: str = ""
    trust: TrustLiteral = "FROM_NOTICE"
    source_note: str = ""


class ImportantDateSchema(BaseModel):
    """One dated milestone. ``iso_date`` is only set for unambiguous dates."""

    kind: str = "other"
    label: str = ""
    value: str = ""
    iso_date: Optional[str] = None
    # True for things like "within 15 days of receipt", which must never be
    # silently converted into a calendar date (§10).
    is_relative: bool = False
    is_deadline: bool = False
    trust: TrustLiteral = "FROM_NOTICE"
    note: str = ""


class EligibilitySchema(BaseModel):
    category: Literal[
        "age", "education", "experience", "residency", "category", "income", "other"
    ] = "other"
    requirement: str = ""
    detail: str = ""
    status: Literal["met", "not_met", "needs_input", "unknown"] = "needs_input"
    needs: str = ""
    trust: TrustLiteral = "FROM_NOTICE"


class FeeSchema(BaseModel):
    label: str = ""
    amount: str = ""
    who_pays: str = ""
    exemptions: str = ""
    payment_method: str = ""
    deadline: str = ""
    trust: TrustLiteral = "FROM_NOTICE"


class ProcedureStepSchema(BaseModel):
    order: int = 0
    text: str = ""
    # True when the step is general guidance rather than something the notice
    # actually says — the UI labels these differently (§16).
    inferred: bool = False


class OfficialChannelSchema(BaseModel):
    """Where the citizen completes the real process (§15). Guidance only."""

    label: str = ""
    kind: Literal["portal", "website", "email", "office", "post", "phone", "other"] = (
        "other"
    )
    value: str = ""
    url: str = ""
    note: str = ""
    trust: TrustLiteral = "FROM_NOTICE"


class GlossaryItemSchema(BaseModel):
    term: str = ""
    meaning: str = ""


class NoticeAnalysisSchema(BaseModel):
    """Structured analysis extracted from a notice.

    Every field is validated. Lists default to empty so a partial analysis is
    still usable, and ``confidence`` is clamped to [0, 1].
    """

    notice_type: str = ""
    category: str = "other"
    category_confident: bool = False
    mode: NoticeMode = "response"
    title: str = ""
    authority: str = ""
    department: str = ""
    organization: str = ""
    scheme_name: str = ""
    notice_date: str = ""
    deadline: str = ""
    reference_number: str = ""
    subject: str = ""

    one_sentence: str = ""
    summary: str = ""
    why_received: str = ""
    required_action: str = ""
    what_happens_next: str = ""
    consequences: str = ""

    required_documents: list[RequiredDocument] = Field(default_factory=list)
    important_dates: list[ImportantDateSchema] = Field(default_factory=list)
    eligibility: list[EligibilitySchema] = Field(default_factory=list)
    fees: list[FeeSchema] = Field(default_factory=list)
    application_process: list[ProcedureStepSchema] = Field(default_factory=list)
    official_channels: list[OfficialChannelSchema] = Field(default_factory=list)
    selection_process: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    unknown_information: list[str] = Field(default_factory=list)
    mentioned_laws: list[str] = Field(default_factory=list)
    mentioned_rules: list[str] = Field(default_factory=list)
    mentioned_forms: list[str] = Field(default_factory=list)
    mentioned_portals: list[str] = Field(default_factory=list)
    financial_amounts: list[str] = Field(default_factory=list)
    glossary: list[GlossaryItemSchema] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    important_notes: list[str] = Field(default_factory=list)
    # {"deadline": "Page 2, paragraph 4"} — lets the UI show where a fact came
    # from in the original document (§9).
    source_spans: dict[str, str] = Field(default_factory=dict)
    contact_information: dict[str, str] = Field(default_factory=dict)
    vacancies: dict[str, str] = Field(default_factory=dict)
    read_warning: str = ""
    confidence: float = 0.0

    @field_validator("confidence")
    @classmethod
    def _clamp_confidence(cls, v: float) -> float:
        try:
            v = float(v)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, v))

    @field_validator("category", mode="before")
    @classmethod
    def _known_category(cls, v: Any) -> str:
        key = str(v or "other").strip().lower().replace(" ", "_").replace("-", "_")
        return key if key in CATEGORIES else "other"

    @field_validator("mode", mode="before")
    @classmethod
    def _known_mode(cls, v: Any) -> str:
        key = str(v or "response").strip().lower()
        return key if key in ("application", "response", "benefit") else "response"

    @field_validator("required_documents", mode="before")
    @classmethod
    def _coerce_documents(cls, v: Any) -> Any:
        # Tolerate a model returning a plain list of strings.
        if isinstance(v, list):
            out = []
            for item in v:
                if isinstance(item, str):
                    out.append({"name": item, "reason": "", "required": True})
                else:
                    out.append(item)
            return out
        return v

    @field_validator(
        "next_steps",
        "uncertainties",
        "unknown_information",
        "mentioned_laws",
        "mentioned_rules",
        "mentioned_forms",
        "mentioned_portals",
        "financial_amounts",
        "selection_process",
        "warnings",
        "important_notes",
        mode="before",
    )
    @classmethod
    def _coerce_str_list(cls, v: Any) -> Any:
        """Models sometimes return a string, or dicts instead of strings."""
        if v is None:
            return []
        if isinstance(v, str):
            return [v] if v.strip() else []
        if isinstance(v, list):
            out = []
            for item in v:
                if isinstance(item, str):
                    if item.strip():
                        out.append(item.strip())
                elif isinstance(item, dict):
                    text = (
                        item.get("text")
                        or item.get("value")
                        or item.get("name")
                        or item.get("description")
                        or ""
                    )
                    if str(text).strip():
                        out.append(str(text).strip())
            return out
        return v

    @field_validator("application_process", mode="before")
    @classmethod
    def _coerce_steps(cls, v: Any) -> Any:
        if isinstance(v, list):
            out = []
            for i, item in enumerate(v):
                if isinstance(item, str):
                    out.append({"order": i + 1, "text": item})
                elif isinstance(item, dict):
                    item.setdefault("order", i + 1)
                    out.append(item)
            return out
        return v

    @field_validator("source_spans", "contact_information", "vacancies", mode="before")
    @classmethod
    def _coerce_str_dict(cls, v: Any) -> Any:
        if not isinstance(v, dict):
            return {}
        return {str(k): str(val) for k, val in v.items() if val not in (None, "")}


# --- Research contract -----------------------------------------------------
class ResearchQueryOut(BaseModel):
    id: str
    order: int
    query: str
    purpose: str
    status: str
    result_count: int

    model_config = {"from_attributes": True}


class ResearchSourceOut(BaseModel):
    id: str
    order: int
    claim: str
    title: str
    url: str
    domain: str
    authority_level: str
    source_type: str
    excerpt: str
    evidence: str
    why_it_matters: str
    relevance: float
    supports_notice: Optional[bool] = None
    conflict: bool = False
    conflict_detail: str = ""
    retrieved_at: datetime

    model_config = {"from_attributes": True}


class ConflictOut(BaseModel):
    """A disagreement between the notice and an authoritative source (§22)."""

    topic: str
    notice_says: str
    source_says: str
    source_title: str = ""
    source_url: str = ""
    domain: str = ""
    advice: str = (
        "These appear inconsistent. Please verify with the issuing authority "
        "before you act."
    )


class ResearchOut(BaseModel):
    notice_id: str
    # live | demo | unavailable | disabled
    mode: Literal["live", "demo", "unavailable", "disabled"] = "unavailable"
    checked_at: Optional[datetime] = None
    queries: list[ResearchQueryOut] = Field(default_factory=list)
    sources: list[ResearchSourceOut] = Field(default_factory=list)
    verified_claims: list[str] = Field(default_factory=list)
    unverified_claims: list[str] = Field(default_factory=list)
    conflicts: list[ConflictOut] = Field(default_factory=list)
    summary: str = ""
    message: str = ""
    # True when nothing here came from a live web retrieval, so the UI can say
    # so plainly instead of implying it did.
    is_live: bool = False


class ResearchIn(BaseModel):
    language: Language = "en"
    force: bool = False


# --- Notice input ----------------------------------------------------------
class TextNoticeIn(BaseModel):
    """Create a notice from pasted text (used by tests / power users)."""

    text: str = Field(min_length=1, max_length=100_000)
    filename: Optional[str] = None
    session_id: Optional[str] = None


class DemoNoticeIn(BaseModel):
    demo_id: str
    session_id: Optional[str] = None


class AnalyzeIn(BaseModel):
    language: Language = "en"


# --- Notice output ---------------------------------------------------------
class DocumentOut(BaseModel):
    id: str
    name: str
    reason: str
    required: bool
    requirement: str = "yes"
    stage: str = "unknown"
    doc_format: str = ""
    size_limit: str = ""
    validity: str = ""
    trust: str = "FROM_NOTICE"
    source_note: str = ""
    status: str
    original_filename: Optional[str] = None
    validation: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class ImportantDateOut(BaseModel):
    id: str
    order: int
    kind: str
    label: str
    value: str
    iso_date: Optional[str] = None
    is_relative: bool = False
    is_deadline: bool = False
    trust: str = "FROM_NOTICE"
    note: str = ""
    conflict_note: str = ""

    model_config = {"from_attributes": True}


class EligibilityOut(BaseModel):
    id: str
    order: int
    category: str
    requirement: str
    detail: str
    status: str
    needs: str
    trust: str = "FROM_NOTICE"

    model_config = {"from_attributes": True}


class ActionItemOut(BaseModel):
    id: str
    order: int
    title: str
    description: str
    state: str

    model_config = {"from_attributes": True}


RoadmapStatus = Literal[
    "not_started",
    "in_progress",
    "completed",
    "blocked",
    "needs_verification",
    "not_applicable",
]

RoadmapPriority = Literal["urgent", "high", "normal", "low"]


class RoadmapStepOut(BaseModel):
    id: str
    key: str
    order: int
    title: str
    short_description: str = ""
    detailed_description: str = ""
    status: RoadmapStatus = "not_started"
    priority: RoadmapPriority = "normal"
    required: bool = True
    deadline: Optional[str] = None
    is_deadline_official: bool = True
    suggested_target: Optional[str] = None
    documents: list[dict] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    blocker_reason: str = ""
    actions: list[dict] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    estimated_effort: str = ""
    can_do_in_parallel: bool = False
    parallel_with: list[str] = Field(default_factory=list)
    completion_criteria: str = ""
    official_channel: bool = False
    group: str = ""

    # 6-Question Breakdown (§30)
    what: str = ""
    why: str = ""
    how: str = ""
    when: str = ""
    where: str = ""
    what_i_need: str = ""
    what_happens_after: str = ""

    model_config = {"from_attributes": True}


class RoadmapOut(BaseModel):
    notice_id: str
    steps: list[RoadmapStepOut] = Field(default_factory=list)
    completed: int = 0
    total: int = 0
    headline: str = ""
    next_step: Optional[RoadmapStepOut] = None
    do_this_now: str = ""
    do_this_next: str = ""
    dont_forget: list[str] = Field(default_factory=list)
    parallel_info: str = ""


class PreparationIn(BaseModel):
    step_key: str = Field(min_length=1, max_length=64)
    state: RoadmapStatus


class StepHelpIn(BaseModel):
    step_id: str = Field(min_length=1, max_length=64)
    question: Optional[str] = Field(default=None, max_length=500)
    language: Language = "en"


class StepHelpOut(BaseModel):
    step_id: str
    title: str
    explanation: str
    actionable_tip: str
    grounded_source: str = ""



class AnalysisOut(NoticeAnalysisSchema):
    analysis_source: str = "demo-fallback"
    language: str = "en"
    translated: bool = True


class ResponseDraftOut(BaseModel):
    id: str
    content: str
    draft_source: str
    status: str
    version: int

    model_config = {"from_attributes": True}


class NoticeOut(BaseModel):
    id: str
    source: str
    demo_id: Optional[str] = None
    original_filename: Optional[str] = None
    language: str
    workflow_state: str
    created_at: datetime
    disclaimer: str = (
        "NoticeMate is an independent demonstration prototype. It is not an "
        "official government service and does not submit applications or "
        "responses to government systems."
    )

    model_config = {"from_attributes": True}


class NoticeDetailOut(NoticeOut):
    analysis: Optional[AnalysisOut] = None
    documents: list[DocumentOut] = Field(default_factory=list)
    important_dates: list[ImportantDateOut] = Field(default_factory=list)
    eligibility: list[EligibilityOut] = Field(default_factory=list)
    action_items: list[ActionItemOut] = Field(default_factory=list)
    roadmap: Optional[RoadmapOut] = None
    research: Optional[ResearchOut] = None
    response: Optional[ResponseDraftOut] = None
    raw_text: str = ""


# --- Documents -------------------------------------------------------------
class DocumentStatusIn(BaseModel):
    status: Literal[
        "NOT_STARTED",
        "READY",
        "UPLOADED",
        "VERIFIED_FORMAT",
        "NEEDS_REVIEW",
        "COMPLETED",
        "UNAVAILABLE",
    ]


# --- Responses -------------------------------------------------------------
class ResponseGenerateIn(BaseModel):
    language: Language = "en"
    extra_context: Optional[str] = Field(default=None, max_length=4000)


class ResponseSaveIn(BaseModel):
    content: str = Field(min_length=1, max_length=20_000)
    accept: bool = False


# --- Ask about this notice -------------------------------------------------
class AskIn(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    language: Language = "en"


class AskOut(BaseModel):
    question: str
    answer: str
    # openai | demo-fallback
    answer_source: str = "demo-fallback"
    grounded: bool = True
    disclaimer: str = (
        "This answer is based only on your notice and any sources shown. "
        "Verify important details with the issuing authority."
    )


# --- Preparation record ----------------------------------------------------
class SubmitIn(BaseModel):
    confirmed: bool = Field(..., description="User confirms the info is correct")


class SubmissionOut(BaseModel):
    id: str
    notice_id: str
    reference: str
    status: str
    next_steps: str
    submitted_at: datetime
    disclaimer: str = (
        "This is a NoticeMate preparation record for your own reference. "
        "Nothing has been sent to any government system — you still need to "
        "complete the real process through the official channel."
    )

    model_config = {"from_attributes": True}


# --- Status / tracking -----------------------------------------------------
class WorkflowEventOut(BaseModel):
    id: str
    event_type: str
    message: str
    meta: dict = Field(default_factory=dict)
    created_at: datetime

    model_config = {"from_attributes": True}


class StatusStep(BaseModel):
    key: str
    label: str
    done: bool
    # "noticemate" steps happen in this app; "official" steps are the ones the
    # citizen must complete themselves on a government channel.
    system: Literal["noticemate", "official"] = "noticemate"
    note: str = ""


class StatusOut(BaseModel):
    notice_id: str
    workflow_state: str
    steps: list[StatusStep]
    events: list[WorkflowEventOut]


# --- Demo catalog ----------------------------------------------------------
class DemoNoticeSummary(BaseModel):
    id: str
    title: str
    category: str
    icon: str
    authority: str
    blurb: str
    mode: str = "response"


# --- Health ----------------------------------------------------------------
class HealthOut(BaseModel):
    status: str = "ok"
    app: str
    version: str
    ai_enabled: bool
    # openai | demo-fallback | quota-exhausted | unreachable
    ai_mode: str
    ai_note: str = ""
    research_enabled: bool = False
    model: str = ""
    environment: str
