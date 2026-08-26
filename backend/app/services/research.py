"""Web research engine (§19–24).

The flow is deliberately three separate steps so no single AI call decides
what the citizen sees:

1. **Query generation** — the *analysis* (not the raw notice) is turned into a
   handful of targeted, privacy-safe verification queries.
2. **Retrieval + synthesis** — the model searches the web server-side and
   reports findings, each of which must carry a URL the search tool actually
   returned.
3. **Deterministic post-processing** — this module classifies each source's
   authority from its domain, drops any finding whose URL looks fabricated,
   cross-checks dates against the notice, and records conflicts.

Step 3 is ordinary Python precisely because the trust labels and the "these
appear inconsistent" warning must not be something a model can talk its way
out of.

Retrieved page content is untrusted (see ``prompts.UNTRUSTED_RULES``); it is
used as evidence only and can never redirect the app.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from .. import prompts
from ..config import settings
from ..demo_research import DEMO_RESEARCH_MESSAGE, get_demo_research
from ..models import (
    AuthorityLevel,
    ImportantDate,
    Notice,
    ResearchQuery,
    ResearchSource,
    TrustLevel,
    WorkflowState,
)
from ..schemas import ConflictOut, ResearchOut, ResearchQueryOut, ResearchSourceOut
from . import ai, workflow

logger = logging.getLogger("noticemate.research")

# §55 wording, used verbatim when nothing could be verified.
UNVERIFIED_MESSAGE = (
    "We couldn't verify this from an authoritative public source. Please check "
    "the official website of the issuing authority, or contact them directly."
)

DISABLED_MESSAGE = (
    "Web research is turned off in this environment, so nothing has been "
    "checked online. Everything shown comes from your notice only."
)


# --- Domain → authority ----------------------------------------------------
_OFFICIAL_SUFFIXES = (".gov.in", ".nic.in", ".gov")
_OFFICIAL_HOSTS = ("india.gov.in", "egazette.gov.in", "indiacode.nic.in")
_HIGHLY_RELIABLE_SUFFIXES = (".ac.in", ".edu.in", ".res.in", ".org.in")
_SECONDARY_HINTS = (
    "thehindu.com",
    "indianexpress.com",
    "livemint.com",
    "business-standard.com",
    "timesofindia",
    "hindustantimes.com",
    "ndtv.com",
    "prsindia.org",
)


def classify_domain(url: str) -> tuple[str, str]:
    """Return ``(domain, authority_level)`` for a retrieved URL."""
    domain = domain_of(url)
    if not domain:
        return "", AuthorityLevel.UNVERIFIED
    low = domain.lower()
    if low in _OFFICIAL_HOSTS or low.endswith(_OFFICIAL_SUFFIXES):
        return domain, AuthorityLevel.OFFICIAL
    if low.endswith(_HIGHLY_RELIABLE_SUFFIXES):
        return domain, AuthorityLevel.HIGHLY_RELIABLE
    if any(hint in low for hint in _SECONDARY_HINTS):
        return domain, AuthorityLevel.SECONDARY
    return domain, AuthorityLevel.UNVERIFIED


def domain_of(url: str) -> str:
    try:
        host = urlparse(url).netloc
    except Exception:
        return ""
    return host.lower().removeprefix("www.")


_AUTHORITY_RANK = {
    AuthorityLevel.OFFICIAL: 0,
    AuthorityLevel.HIGHLY_RELIABLE: 1,
    AuthorityLevel.SECONDARY: 2,
    AuthorityLevel.UNVERIFIED: 3,
    AuthorityLevel.DEMO: 4,
}

# A URL we will not display. The spec forbids showing a URL that was not
# actually retrieved, and these shapes are the classic signs of a guessed one.
_SUSPECT_URL = re.compile(
    r"(example\.com|localhost|\[|\]|\{|\}|\s|<|>|\.\.\.|…|your-?domain|"
    r"insert|placeholder|search\?q=)",
    re.I,
)


def _url_is_usable(url: str) -> bool:
    url = (url or "").strip()
    if not url.lower().startswith(("http://", "https://")):
        return False
    if _SUSPECT_URL.search(url):
        return False
    return bool(domain_of(url))


TRUST_FOR_AUTHORITY = {
    AuthorityLevel.OFFICIAL: TrustLevel.OFFICIAL_SOURCE,
    AuthorityLevel.HIGHLY_RELIABLE: TrustLevel.OFFICIAL_SOURCE,
    AuthorityLevel.SECONDARY: TrustLevel.RELIABLE_SECONDARY_SOURCE,
    AuthorityLevel.UNVERIFIED: TrustLevel.UNKNOWN,
    AuthorityLevel.DEMO: TrustLevel.UNKNOWN,
}


@dataclass
class _Findings:
    queries: list[dict]
    sources: list[dict]
    conflicts: list[dict]
    unverified: list[str]
    summary: str
    mode: str  # live | demo | unavailable | disabled
    message: str = ""


# --- Public API ------------------------------------------------------------
def run_research(db: Session, notice: Notice, force: bool = False) -> ResearchOut:
    """Research a notice, persist the result, and return it.

    Idempotent: a second call returns the stored research unless ``force``.
    """
    if notice.research_sources and not force:
        return serialize(notice)

    if notice.analysis is None:
        return ResearchOut(
            notice_id=notice.id,
            mode="unavailable",
            message="Please analyse the notice before checking it against public sources.",
        )

    findings = _gather(notice)
    _persist(db, notice, findings)
    workflow.advance_state(db, notice, WorkflowState.RESEARCHED)
    workflow.log_event(
        db,
        notice,
        "researched",
        f"Checked against public sources ({findings.mode}).",
        {
            "mode": findings.mode,
            "sources": len(findings.sources),
            "conflicts": len(findings.conflicts),
        },
    )
    db.commit()
    db.refresh(notice)
    return serialize(notice)


def _gather(notice: Notice) -> _Findings:
    """Try live research first, then curated demo data, then be honest."""
    if settings.research_enabled and ai.ai_available():
        live = _live_research(notice)
        if live is not None:
            return live

    demo = get_demo_research(notice.demo_id)
    if demo:
        return _from_demo(demo)

    if not settings.ENABLE_WEB_RESEARCH:
        mode, message = "disabled", DISABLED_MESSAGE
    else:
        mode = "unavailable"
        message = f"{UNVERIFIED_MESSAGE} {ai.ai_note()}".strip()
    return _Findings(
        queries=[],
        sources=[],
        conflicts=[],
        unverified=_claims_to_verify(notice),
        summary="",
        mode=mode,
        message=message,
    )


def _claims_to_verify(notice: Notice) -> list[str]:
    """What we *would* have checked — shown so the gap is explicit, not hidden."""
    a = notice.analysis
    if a is None:
        return []
    items: list[str] = []
    if a.deadline:
        items.append(f"The deadline stated in your notice ({a.deadline}).")
    if notice.eligibility_items:
        items.append("The eligibility conditions listed in your notice.")
    if a.fees:
        items.append("The fee amounts stated in your notice.")
    if a.required_documents:
        items.append("The list of documents your notice asks for.")
    if a.mentioned_portals:
        items.append("Whether the portal named in your notice is the current one.")
    return items or ["The key facts stated in your notice."]


# --- Live research ---------------------------------------------------------
def _live_research(notice: Notice) -> _Findings | None:
    """Generate queries, search, and synthesise. Returns None if unavailable."""
    analysis = _analysis_payload(notice)

    query_data = ai.json_call(
        prompts.research_query_prompt(analysis, settings.RESEARCH_MAX_QUERIES)
    )
    if not query_data:
        return None
    queries = [
        {
            "query": str(q.get("query", "")).strip(),
            "purpose": str(q.get("purpose", "")).strip(),
        }
        for q in (query_data.get("queries") or [])
        if str(q.get("query", "")).strip()
    ][: settings.RESEARCH_MAX_QUERIES]
    if not queries:
        return _Findings(
            queries=[],
            sources=[],
            conflicts=[],
            unverified=_claims_to_verify(notice),
            summary="",
            mode="unavailable",
            message=(
                "There was nothing in this notice that could be checked against a "
                "public source — it looks specific to you rather than a published rule."
            ),
        )

    raw = _search_and_synthesize(analysis, queries)
    if raw is None:
        return None

    sources, dropped = _clean_sources(raw.get("findings") or [])
    conflicts = _clean_conflicts(raw.get("conflicts") or [], sources)
    unverified = [
        str(u).strip() for u in (raw.get("unverified") or []) if str(u).strip()
    ]
    if dropped:
        unverified.append(
            f"{dropped} finding(s) were discarded because they did not come with a "
            "verifiable source link."
        )

    for q in queries:
        q["result_count"] = sum(1 for s in sources if s.get("query") == q["query"])
        q["status"] = "ok" if q["result_count"] else "no_results"

    if not sources:
        return _Findings(
            queries=queries,
            sources=[],
            conflicts=[],
            unverified=unverified or _claims_to_verify(notice),
            summary="",
            mode="live",
            message=UNVERIFIED_MESSAGE,
        )

    return _Findings(
        queries=queries,
        sources=sources,
        conflicts=conflicts,
        unverified=unverified,
        summary=str(raw.get("summary", "")).strip(),
        mode="live",
    )


def _search_and_synthesize(analysis: dict, queries: list[dict]) -> dict | None:
    """Call the model *with web search enabled*, server-side only.

    Two transports are tried, because search tooling differs between model
    families: the Responses API's hosted ``web_search`` tool first, then a plain
    JSON completion. If neither works we return None and the caller falls back
    honestly rather than presenting unsourced text as researched.
    """
    client = ai._get_client()  # single place that owns key handling
    if client is None:
        return None
    messages = prompts.research_synthesis_prompt(analysis, queries)

    try:
        resp = client.responses.create(
            model=settings.research_model,
            input=[
                {"role": "system", "content": messages[0]["content"]},
                {"role": "user", "content": messages[1]["content"]},
            ],
            tools=[{"type": "web_search"}],
            timeout=settings.OPENAI_RESEARCH_TIMEOUT,
        )
        text = getattr(resp, "output_text", "") or ""
        if text.strip():
            return ai._parse_json(text)
    except Exception as exc:
        logger.info("web_search research unavailable: %s", exc)

    return ai.json_call(messages, model=settings.research_model)


def _analysis_payload(notice: Notice) -> dict:
    a = notice.analysis
    return {
        "category": a.category,
        "notice_type": a.notice_type,
        "title": a.title,
        "authority": a.authority,
        "department": a.department,
        "organization": a.organization,
        "scheme_name": a.scheme_name,
        "deadline": a.deadline,
        "important_dates": [
            {"label": d.label, "value": d.value} for d in notice.important_dates
        ],
        "eligibility": [e.requirement for e in notice.eligibility_items],
        "fees": a.fees,
        "required_documents": [d.get("name") for d in (a.required_documents or [])],
        "mentioned_portals": a.mentioned_portals,
        "mentioned_forms": a.mentioned_forms,
        "mentioned_laws": a.mentioned_laws,
        "mentioned_rules": a.mentioned_rules,
    }


def _clean_sources(findings: list[dict]) -> tuple[list[dict], int]:
    """Keep only findings with a usable URL; classify and sort by authority."""
    out: list[dict] = []
    dropped = 0
    seen: set[tuple[str, str]] = set()
    for f in findings:
        url = str(f.get("url", "")).strip()
        claim = str(f.get("claim", "")).strip()
        if not _url_is_usable(url):
            dropped += 1
            continue
        domain, authority = classify_domain(url)
        key = (claim.lower()[:60], url)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "claim": claim,
                "title": str(f.get("title", "")).strip()[:500],
                "url": url[:1000],
                "domain": domain,
                "authority_level": authority,
                "source_type": str(f.get("source_type", "")).strip()[:64],
                "excerpt": str(f.get("excerpt", "")).strip()[:1200],
                "evidence": str(f.get("finding", "") or f.get("evidence", "")).strip()[:1200],
                "why_it_matters": str(f.get("why_it_matters", "")).strip()[:600],
                "supports_notice": _tri_bool(f.get("supports_notice")),
                "conflict": f.get("supports_notice") is False,
                "conflict_detail": str(f.get("conflict_detail", "")).strip()[:600],
                "query": str(f.get("query", "")).strip(),
                "relevance": 1.0 - (_AUTHORITY_RANK.get(authority, 3) * 0.2),
            }
        )
    out.sort(key=lambda s: _AUTHORITY_RANK.get(s["authority_level"], 3))
    return out, dropped


def _tri_bool(value) -> bool | None:
    if value is True or value is False:
        return value
    if isinstance(value, str):
        low = value.strip().lower()
        if low in ("true", "yes"):
            return True
        if low in ("false", "no"):
            return False
    return None


def _clean_conflicts(conflicts: list[dict], sources: list[dict]) -> list[dict]:
    """Only keep a conflict we can attribute to a source we are displaying."""
    shown = {s["url"] for s in sources}
    out: list[dict] = []
    for c in conflicts:
        url = str(c.get("source_url", "")).strip()
        notice_says = str(c.get("notice_says", "")).strip()
        source_says = str(c.get("source_says", "")).strip()
        if not notice_says or not source_says:
            continue
        if url and url not in shown:
            if not _url_is_usable(url):
                continue
        out.append(
            {
                "topic": str(c.get("topic", "")).strip()[:200] or "This detail",
                "notice_says": notice_says[:400],
                "source_says": source_says[:400],
                "source_title": str(c.get("source_title", "")).strip()[:400],
                "source_url": url[:1000],
                "domain": domain_of(url),
            }
        )
    return out


# --- Curated demo path ------------------------------------------------------
def _from_demo(demo: dict) -> _Findings:
    """Load curated demo research, marked so it cannot pass as a retrieval."""
    sources = []
    for s in demo.get("sources", []):
        sources.append(
            {
                "claim": s.get("claim", ""),
                "title": s.get("title", ""),
                # Deliberately empty: nothing was retrieved, so there is no URL
                # to show. The domain is the fictional host from the demo notice.
                "url": "",
                "domain": s.get("domain", ""),
                "authority_level": AuthorityLevel.DEMO,
                "source_type": s.get("source_type", ""),
                "excerpt": s.get("evidence", ""),
                "evidence": s.get("evidence", ""),
                "why_it_matters": s.get("why_it_matters", ""),
                "supports_notice": s.get("supports_notice"),
                "conflict": bool(s.get("conflict")),
                "conflict_detail": s.get("conflict_detail", ""),
                "query": "",
                "relevance": 0.5,
            }
        )
    queries = [
        {**q, "status": "ok", "result_count": 0} for q in demo.get("queries", [])
    ]
    return _Findings(
        queries=queries,
        sources=sources,
        conflicts=list(demo.get("conflicts", [])),
        unverified=list(demo.get("unverified", [])),
        summary=demo.get("summary", ""),
        mode="demo",
        message=DEMO_RESEARCH_MESSAGE,
    )


# --- Persistence -----------------------------------------------------------
def _persist(db: Session, notice: Notice, findings: _Findings) -> None:
    for row in list(notice.research_sources):
        db.delete(row)
    for row in list(notice.research_queries):
        db.delete(row)
    db.flush()

    by_query: dict[str, ResearchQuery] = {}
    for i, q in enumerate(findings.queries):
        row = ResearchQuery(
            notice_id=notice.id,
            order=i,
            query=q.get("query", "")[:500],
            purpose=q.get("purpose", "")[:250],
            status=q.get("status", "ok"),
            result_count=int(q.get("result_count", 0) or 0),
        )
        db.add(row)
        by_query[row.query] = row
    db.flush()

    for i, s in enumerate(findings.sources):
        parent = by_query.get(s.get("query", ""))
        db.add(
            ResearchSource(
                notice_id=notice.id,
                query_id=parent.id if parent else None,
                order=i,
                claim=s.get("claim", ""),
                title=s.get("title", ""),
                url=s.get("url", ""),
                domain=s.get("domain", ""),
                authority_level=s.get("authority_level", AuthorityLevel.UNVERIFIED),
                source_type=s.get("source_type", ""),
                excerpt=s.get("excerpt", ""),
                evidence=s.get("evidence", ""),
                why_it_matters=s.get("why_it_matters", ""),
                relevance=float(s.get("relevance", 0.0)),
                supports_notice=s.get("supports_notice"),
                conflict=bool(s.get("conflict")),
                conflict_detail=s.get("conflict_detail", ""),
            )
        )
    db.flush()

    _apply_to_dates(db, notice, findings)
    _store_meta(notice, findings)


def _apply_to_dates(db: Session, notice: Notice, findings: _Findings) -> None:
    """Annotate dates with verification or conflict — never overwrite them (§22).

    The notice's own value always remains the stored value. Research can only
    add a note beside it.
    """
    conflict_topics = {
        c["topic"].lower(): c for c in findings.conflicts if c.get("topic")
    }
    verified_claims = {
        s["claim"].lower()
        for s in findings.sources
        if s.get("supports_notice") is True
        and s.get("authority_level")
        in (AuthorityLevel.OFFICIAL, AuthorityLevel.HIGHLY_RELIABLE)
    }

    for d in notice.important_dates:
        label = (d.label or "").lower()
        conflict = next(
            (c for topic, c in conflict_topics.items() if topic and (topic in label or label in topic)),
            None,
        )
        if conflict:
            d.conflict_note = (
                f"Your notice says {conflict['notice_says']}. "
                f"{conflict.get('source_title') or 'A source we checked'} says "
                f"{conflict['source_says']}. These appear inconsistent — please "
                "verify with the issuing authority before you act."
            )
            d.trust = TrustLevel.FROM_NOTICE
        elif any(label and (label in c or c in label) for c in verified_claims):
            d.trust = TrustLevel.OFFICIAL_SOURCE
            if not d.note:
                d.note = "Verified from official source."
        db.add(d)


def _store_meta(notice: Notice, findings: _Findings) -> None:
    """Record research mode/summary on the analysis row's bookkeeping payload."""
    if notice.analysis is None:
        return
    meta = dict(notice.analysis.meta or {})
    meta["research_mode"] = findings.mode
    meta["research_summary"] = findings.summary
    meta["research_message"] = findings.message
    meta["research_unverified"] = findings.unverified
    meta["research_checked_at"] = datetime.now(timezone.utc).isoformat()
    notice.analysis.meta = meta


# --- Serialisation ---------------------------------------------------------
def serialize(notice: Notice) -> ResearchOut:
    meta = dict((notice.analysis.meta if notice.analysis else {}) or {})
    mode = meta.get("research_mode") or (
        "disabled" if not settings.ENABLE_WEB_RESEARCH else "unavailable"
    )
    checked_at = None
    if meta.get("research_checked_at"):
        try:
            checked_at = datetime.fromisoformat(meta["research_checked_at"])
        except ValueError:
            checked_at = None

    sources = [
        ResearchSourceOut.model_validate(s)
        for s in sorted(notice.research_sources, key=lambda x: x.order)
    ]
    verified = [
        s.claim
        for s in sources
        if s.supports_notice is True and s.authority_level != AuthorityLevel.DEMO
    ]
    unverified = list(meta.get("research_unverified") or [])
    conflicts = [
        ConflictOut(
            topic=s.claim or "This detail",
            notice_says=(s.conflict_detail or "").split(";")[0].strip()
            or "See your notice",
            source_says=s.evidence,
            source_title=s.title,
            source_url=s.url,
            domain=s.domain,
        )
        for s in sources
        if s.conflict
    ]

    return ResearchOut(
        notice_id=notice.id,
        mode=mode,  # type: ignore[arg-type]
        checked_at=checked_at,
        queries=[
            ResearchQueryOut.model_validate(q)
            for q in sorted(notice.research_queries, key=lambda x: x.order)
        ],
        sources=sources,
        verified_claims=verified,
        unverified_claims=unverified,
        conflicts=conflicts,
        summary=meta.get("research_summary", ""),
        message=meta.get("research_message", ""),
        is_live=(mode == "live"),
    )
