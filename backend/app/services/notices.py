"""Notice orchestration: create, analyse, and serialise notices.

This is the glue between the API layer, the AI service, and the deterministic
workflow. It keeps endpoints thin, and it is the only place that turns a
validated ``NoticeAnalysisSchema`` into database rows — so every screen reads
from the same persisted facts rather than from a fresh model call.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..demo_data import get_demo
from ..models import (
    Document,
    DocumentStatus,
    EligibilityItem,
    ImportantDate,
    Notice,
    NoticeAnalysis,
    WorkflowState,
)
from ..schemas import (
    ActionItemOut,
    AnalysisOut,
    DocumentOut,
    EligibilityOut,
    ImportantDateOut,
    NoticeDetailOut,
    ResponseDraftOut,
)
from . import ai, research, roadmap, workflow

# Narrative fields we can swap for a curated translation.
_NARRATIVE_FIELDS = (
    "one_sentence",
    "summary",
    "why_received",
    "required_action",
    "what_happens_next",
    "consequences",
)

# Scalar analysis columns copied straight through.
_SCALAR_COLUMNS = (
    "notice_type",
    "category",
    "category_confident",
    "mode",
    "title",
    "authority",
    "department",
    "organization",
    "scheme_name",
    "notice_date",
    "deadline",
    "reference_number",
    "subject",
    "one_sentence",
    "summary",
    "why_received",
    "required_action",
    "what_happens_next",
    "consequences",
    "confidence",
    "read_warning",
)

# Plain list / dict columns copied straight through.
_PLAIN_COLUMNS = (
    "next_steps",
    "uncertainties",
    "unknown_information",
    "selection_process",
    "mentioned_laws",
    "mentioned_rules",
    "mentioned_forms",
    "mentioned_portals",
    "financial_amounts",
    "warnings",
    "important_notes",
    "source_spans",
    "contact_information",
    "vacancies",
)


# --- Creation --------------------------------------------------------------
def create_from_demo(db: Session, demo_id: str, session_id: str | None) -> Notice:
    demo = get_demo(demo_id)
    if demo is None:
        raise KeyError(demo_id)
    notice = Notice(
        session_id=session_id,
        source="demo",
        demo_id=demo_id,
        original_filename=None,
        raw_text=demo["raw_text"],
        workflow_state=WorkflowState.RECEIVED,
    )
    db.add(notice)
    db.flush()
    workflow.log_event(db, notice, "received", f"Demo notice loaded: {demo['title']}.")
    db.commit()
    db.refresh(notice)
    return notice


def create_from_text(
    db: Session,
    text: str,
    filename: str | None,
    session_id: str | None,
    source: str = "text",
) -> Notice:
    notice = Notice(
        session_id=session_id,
        source=source,
        original_filename=filename,
        raw_text=text,
        workflow_state=WorkflowState.RECEIVED,
    )
    db.add(notice)
    db.flush()
    label = filename or "pasted text"
    workflow.log_event(db, notice, "received", f"Notice received ({label}).")
    db.commit()
    db.refresh(notice)
    return notice


# --- Analysis --------------------------------------------------------------
def analyze(
    db: Session,
    notice: Notice,
    language: str = "en",
    images: list[tuple[bytes, str]] | None = None,
    read_note: str = "",
) -> NoticeAnalysis:
    """Run analysis, persist it, and derive every dependent record.

    Idempotent: re-analysing replaces the analysis, dates, eligibility and
    roadmap, but never touches documents the citizen has already uploaded.
    """
    demo = get_demo(notice.demo_id) if notice.demo_id else None
    curated = demo["analysis"] if demo else None

    result = ai.analyze_notice(notice.raw_text, curated=curated, images=images)
    a = result.analysis
    if read_note:
        a.read_warning = (a.read_warning + " " + read_note).strip()

    translations = curated.get("translations", {}) if curated else {}

    if notice.analysis is not None:
        db.delete(notice.analysis)
        db.flush()

    analysis = NoticeAnalysis(notice_id=notice.id, analysis_source=result.source)
    for field in _SCALAR_COLUMNS:
        setattr(analysis, field, getattr(a, field))
    for field in _PLAIN_COLUMNS:
        setattr(analysis, field, getattr(a, field))
    analysis.required_documents = [
        d.model_dump() if hasattr(d, "model_dump") else d
        for d in (a.required_documents or [])
    ]
    analysis.fees = [
        f.model_dump() if hasattr(f, "model_dump") else f
        for f in (a.fees or [])
    ]
    analysis.application_process = [
        s.model_dump() if hasattr(s, "model_dump") else s
        for s in (a.application_process or [])
    ]
    analysis.official_channels = [
        c.model_dump() if hasattr(c, "model_dump") else c
        for c in (a.official_channels or [])
    ]
    analysis.glossary = [
        g.model_dump() if hasattr(g, "model_dump") else g
        for g in (a.glossary or [])
    ]
    analysis.translations = translations
    analysis.meta = {"degraded_reason": result.degraded_reason}
    db.add(analysis)
    notice.analysis = analysis
    db.flush()

    _sync_documents(db, notice, a)
    _sync_dates(db, notice, a)
    _sync_eligibility(db, notice, a)

    workflow.advance_state(db, notice, WorkflowState.ANALYZED)
    roadmap.build(db, notice, language)
    workflow.log_event(
        db,
        notice,
        "analyzed",
        f"Notice explained ({result.source}).",
        {
            "confidence": a.confidence,
            "source": result.source,
            "category": a.category,
            "mode": a.mode,
        },
    )
    db.commit()
    db.refresh(notice)
    return analysis


def _sync_documents(db: Session, notice: Notice, a) -> None:
    """Create or refresh the document checklist without losing uploads."""
    docs_list = list(a.required_documents or [])
    
    from .extractors import parse_documents
    raw = notice.raw_text or f"{a.authority} {a.department} {a.title} {a.category}"
    derived = parse_documents(raw)
    
    names_present = {
        (getattr(d, "name", None) or (d.get("name") if isinstance(d, dict) else str(d))).strip().lower()
        for d in docs_list
        if getattr(d, "name", None) or (isinstance(d, dict) and d.get("name"))
    }
    
    for dev_doc in derived:
        d_name = dev_doc.name.strip().lower()
        if d_name not in names_present:
            docs_list.append(dev_doc)
            names_present.add(d_name)
            
    a.required_documents = docs_list

    existing = {d.name.strip().lower(): d for d in notice.documents}
    for rd in docs_list:
        rd_name = getattr(rd, "name", None) or (rd.get("name") if isinstance(rd, dict) else str(rd))
        rd_reason = getattr(rd, "reason", None) or (rd.get("reason") if isinstance(rd, dict) else "")
        rd_required = getattr(rd, "required", True) if hasattr(rd, "required") else (rd.get("required", True) if isinstance(rd, dict) else True)
        rd_requirement = getattr(rd, "requirement", "yes") if hasattr(rd, "requirement") else (rd.get("requirement", "yes") if isinstance(rd, dict) else "yes")
        rd_stage = getattr(rd, "stage", "application") if hasattr(rd, "stage") else (rd.get("stage", "application") if isinstance(rd, dict) else "application")
        rd_doc_format = getattr(rd, "doc_format", "") if hasattr(rd, "doc_format") else (rd.get("doc_format", "") if isinstance(rd, dict) else "")
        rd_size_limit = getattr(rd, "size_limit", "") if hasattr(rd, "size_limit") else (rd.get("size_limit", "") if isinstance(rd, dict) else "")
        rd_validity = getattr(rd, "validity", "") if hasattr(rd, "validity") else (rd.get("validity", "") if isinstance(rd, dict) else "")
        rd_trust = getattr(rd, "trust", "OFFICIAL_SOURCE") if hasattr(rd, "trust") else (rd.get("trust", "OFFICIAL_SOURCE") if isinstance(rd, dict) else "OFFICIAL_SOURCE")
        rd_source_note = getattr(rd, "source_note", "Official Portal & Regulations") if hasattr(rd, "source_note") else (rd.get("source_note", "Official Portal & Regulations") if isinstance(rd, dict) else "Official Portal & Regulations")

        row = existing.pop(rd_name.strip().lower(), None)
        if row is None:
            row = Document(
                notice_id=notice.id,
                name=rd_name,
                status=DocumentStatus.NOT_STARTED,
            )
            db.add(row)
        # Refresh the requirement metadata; never the citizen's own progress.
        row.reason = rd_reason
        row.required = rd_required
        row.requirement = rd_requirement
        row.stage = rd_stage
        row.doc_format = rd_doc_format
        row.size_limit = rd_size_limit
        row.validity = rd_validity
        row.trust = rd_trust
        row.source_note = rd_source_note
        db.add(row)
    # Anything left in ``existing`` is no longer required; keep it only if the
    # citizen already attached a file to it.
    for leftover in existing.values():
        if leftover.stored_path is None:
            db.delete(leftover)
    db.flush()


def _sync_dates(db: Session, notice: Notice, a) -> None:
    for row in list(notice.important_dates):
        db.delete(row)
    db.flush()
    for i, d in enumerate(a.important_dates):
        db.add(
            ImportantDate(
                notice_id=notice.id,
                order=i,
                kind=d.kind,
                label=d.label,
                value=d.value,
                iso_date=d.iso_date,
                is_relative=d.is_relative,
                is_deadline=d.is_deadline,
                trust=d.trust,
                note=d.note,
            )
        )
    db.flush()


def _sync_eligibility(db: Session, notice: Notice, a) -> None:
    """Replace stored conditions, preserving any answer the citizen gave."""
    prior = {
        e.requirement.strip().lower()[:60]: (e.status, e.detail)
        for e in notice.eligibility_items
        if e.status in ("met", "not_met")
    }
    for row in list(notice.eligibility_items):
        db.delete(row)
    db.flush()
    for i, e in enumerate(a.eligibility):
        key = e.requirement.strip().lower()[:60]
        status, detail = prior.get(key, (e.status, e.detail))
        db.add(
            EligibilityItem(
                notice_id=notice.id,
                order=i,
                category=e.category,
                requirement=e.requirement,
                detail=detail,
                status=status,
                needs=e.needs,
                trust=e.trust,
            )
        )
    db.flush()


# --- Localisation & serialisation -----------------------------------------
def localized_analysis(notice: Notice, language: str = "en") -> AnalysisOut | None:
    a = notice.analysis
    if a is None:
        return None

    data = {
        field: getattr(a, field)
        for field in _SCALAR_COLUMNS + _PLAIN_COLUMNS
    }
    data.update(
        {
            "required_documents": a.required_documents,
            "fees": a.fees,
            "application_process": a.application_process,
            "official_channels": a.official_channels,
            "glossary": a.glossary,
            "important_dates": [
                {
                    "kind": d.kind,
                    "label": d.label,
                    "value": d.value,
                    "iso_date": d.iso_date,
                    "is_relative": d.is_relative,
                    "is_deadline": d.is_deadline,
                    "trust": d.trust,
                    "note": d.note,
                }
                for d in sorted(notice.important_dates, key=lambda x: x.order)
            ],
            "eligibility": [
                {
                    "category": e.category,
                    "requirement": e.requirement,
                    "detail": e.detail,
                    "status": e.status,
                    "needs": e.needs,
                    "trust": e.trust,
                }
                for e in sorted(notice.eligibility_items, key=lambda x: x.order)
            ],
            "analysis_source": a.analysis_source,
            "language": language,
            "translated": True,
        }
    )

    if language != "en":
        override = (a.translations or {}).get(language)
        if override:
            for f in _NARRATIVE_FIELDS:
                if override.get(f):
                    data[f] = override[f]
        else:
            # No curated translation available; show English and say so.
            data["translated"] = False

    return AnalysisOut(**data)


def latest_response(notice: Notice) -> ResponseDraftOut | None:
    if not notice.responses:
        return None
    r = sorted(notice.responses, key=lambda x: x.version)[-1]
    return ResponseDraftOut.model_validate(r)


def serialize_detail(notice: Notice, language: str = "en") -> NoticeDetailOut:
    return NoticeDetailOut(
        id=notice.id,
        source=notice.source,
        demo_id=notice.demo_id,
        original_filename=notice.original_filename,
        language=language,
        workflow_state=notice.workflow_state,
        created_at=notice.created_at,
        analysis=localized_analysis(notice, language),
        documents=[
            DocumentOut.model_validate(d)
            for d in sorted(notice.documents, key=lambda x: x.created_at)
        ],
        important_dates=[
            ImportantDateOut.model_validate(d)
            for d in sorted(notice.important_dates, key=lambda x: x.order)
        ],
        eligibility=[
            EligibilityOut.model_validate(e)
            for e in sorted(notice.eligibility_items, key=lambda x: x.order)
        ],
        action_items=[
            ActionItemOut.model_validate(i)
            for i in sorted(notice.action_items, key=lambda x: x.order)
        ],
        roadmap=roadmap.serialize(notice) if notice.action_items else None,
        research=research.serialize(notice) if notice.analysis else None,
        response=latest_response(notice),
        raw_text=notice.raw_text,
    )
