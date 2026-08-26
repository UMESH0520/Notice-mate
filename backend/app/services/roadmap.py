"""The dynamic personalized roadmap engine (§17) and "What should I do now?" (§18).

The roadmap turns a notice into a dynamic directed acyclic graph (DAG) of tasks:
- Logical prerequisites ensure steps are ordered (e.g. eligibility -> documents -> form -> submission).
- Prerequisites calculate 'blocked' state automatically when incomplete.
- Parallel tasks are highlighted so citizens can prepare simultaneously.
- 6-question breakdown (What, Why, How, When, Where, What I Need, What Happens After).
- "Help me with this step" AI breakdown drawer.

No single step ever claims NoticeMate will submit, pay or file anything.
The last step is always the citizen completing the real process on the official channel.
"""

from __future__ import annotations

import logging
import re

from sqlalchemy.orm import Session

from .. import prompts
from ..models import (
    ActionItem,
    DocumentStatus,
    Notice,
    PreparationState,
    WorkflowState,
)
from ..schemas import RoadmapOut, RoadmapStepOut, StepHelpOut
from . import ai, workflow

logger = logging.getLogger("noticemate.roadmap")

GROUP_FIRST = "Do this first"
GROUP_THEN = "Then"
GROUP_DEADLINE = "Before the deadline"
GROUP_FINAL = "Final step"
GROUP_ORDER = [GROUP_FIRST, GROUP_THEN, GROUP_DEADLINE, GROUP_FINAL]

_SLUG = re.compile(r"[^a-z0-9]+")


def step_key(title: str) -> str:
    return _SLUG.sub("_", (title or "").strip().lower()).strip("_")[:48] or "step"


# --- Deterministic baseline steps per notice category ----------------------
def _baseline_steps(notice: Notice) -> tuple[str, str, str, list[str], str, list[dict]]:
    a = notice.analysis
    category = (a.category if a else "other") or "other"
    mode = (a.mode if a else "response") or "response"
    deadline = (a.deadline if a else "") or ""
    docs = [d for d in (a.required_documents if a else []) or [] if d.get("name")]
    fees = [f for f in (a.fees if a else []) or [] if f.get("amount")]
    channels = [c for c in (a.official_channels if a else []) or [] if c.get("value")]
    has_eligibility = bool(notice.eligibility_items)

    channel_label = ""
    for c in channels:
        if c.get("kind") in ("website", "portal"):
            channel_label = c.get("value", "")
            break
    if not channel_label and channels:
        channel_label = channels[0].get("value", "")

    doc_names = ", ".join(d["name"] for d in docs[:3]) if docs else "required documents"
    more_docs = f" and {len(docs) - 3} more" if len(docs) > 3 else ""

    # Category-specific step templates
    steps: list[dict] = []

    # 1. Understanding step
    steps.append({
        "key": "understand_notice",
        "title": "Understand your notice & key details",
        "short_description": "Read the summary and why you received this document.",
        "detailed_description": "Make sure you understand what this notice is about, who issued it, and what is requested.",
        "group": GROUP_FIRST,
        "priority": "high",
        "required": True,
        "estimated_effort": "3 mins",
        "can_do_in_parallel": False,
        "prerequisites": [],
        "completion_criteria": "You understand the notice summary and why you received it.",
        "what": "Understand the notice purpose, department, and deadlines.",
        "why": "Prevents mistakes or missing key response criteria.",
        "how": "Read the plain-language breakdown provided by NoticeMate.",
        "when": "Immediately upon opening the notice.",
        "where": "Inside NoticeMate.",
        "what_i_need": "The uploaded notice or text.",
        "what_happens_after": "Proceed to verify eligibility and important dates.",
    })

    # 2. Dates step
    steps.append({
        "key": "check_dates",
        "title": "Check important dates & deadlines",
        "short_description": f"The key date to watch is {deadline or 'stated in notice'}.",
        "detailed_description": "Add key dates to your calendar. Check both notice date and verified web sources.",
        "group": GROUP_FIRST,
        "priority": "urgent" if deadline else "high",
        "required": True,
        "deadline": deadline,
        "estimated_effort": "2 mins",
        "can_do_in_parallel": True,
        "prerequisites": ["understand_notice"],
        "completion_criteria": "Key dates are noted and added to your calendar.",
        "what": "Check application open date, last date, and correction/exam windows.",
        "why": "Missing a government deadline often cancels eligibility.",
        "how": "Review the Important Dates section in NoticeMate.",
        "when": "Today.",
        "where": "NoticeMate Important Dates card.",
        "what_i_need": "Your calendar.",
        "what_happens_after": "Check eligibility or prepare documents.",
    })

    # 3. Eligibility step
    if has_eligibility or mode != "response":
        steps.append({
            "key": "check_eligibility",
            "title": "Verify your eligibility ('Can I apply?')",
            "short_description": "Confirm age, qualification, residency, and category rules.",
            "detailed_description": "Check every condition before investing time in document preparation.",
            "group": GROUP_FIRST,
            "priority": "high",
            "required": True,
            "estimated_effort": "5 mins",
            "can_do_in_parallel": True,
            "prerequisites": ["understand_notice"],
            "completion_criteria": "You confirmed you meet all stated requirements.",
            "what": "Check whether you qualify under age, education, and income rules.",
            "why": "Applying without eligibility leads to immediate rejection.",
            "how": "Use the Eligibility Check card in NoticeMate.",
            "when": "Before gathering documents.",
            "where": "NoticeMate Eligibility engine.",
            "what_i_need": "Your personal details (age, degree, category).",
            "what_happens_after": "Gather required documents.",
        })

    # 4. Documents step
    doc_prereqs = ["check_eligibility"] if any(s["key"] == "check_eligibility" for s in steps) else ["understand_notice"]
    steps.append({
        "key": "prepare_documents",
        "title": f"Gather required documents ({len(docs)} required)",
        "short_description": f"Collect {doc_names}{more_docs}.",
        "detailed_description": "Collect, scan, and format each required document according to size and format rules.",
        "group": GROUP_THEN,
        "priority": "high",
        "required": True,
        "documents": docs,
        "estimated_effort": "1-2 hours",
        "can_do_in_parallel": True,
        "parallel_with": ["check_eligibility"],
        "prerequisites": doc_prereqs,
        "completion_criteria": "All required documents are prepared and ready.",
        "what": f"Collect and verify {doc_names}{more_docs}.",
        "why": "Incomplete or improperly formatted documents stall your application.",
        "how": "Use the Document Preparation Checklist in NoticeMate.",
        "when": "Before starting the online form.",
        "where": "Your personal document storage.",
        "what_i_need": "Identity proof, qualification certificates, photo, signature.",
        "what_happens_after": "Fill application or draft response.",
    })

    # 5. Form/Draft step
    if mode == "response":
        steps.append({
            "key": "prepare_written_reply",
            "title": "Prepare & edit your written response draft",
            "short_description": "Use the AI draft as a starting point, then customize it.",
            "detailed_description": "Review the generated response, fill in personal placeholders, and verify accuracy.",
            "group": GROUP_THEN,
            "priority": "normal",
            "required": True,
            "estimated_effort": "15 mins",
            "can_do_in_parallel": False,
            "prerequisites": ["prepare_documents"],
            "completion_criteria": "Draft response is edited and accepted.",
            "what": "Prepare a formal written explanation responding to the notice.",
            "why": "Addressing each point raised by the authority is mandatory.",
            "how": "Use the Response Draft Editor in NoticeMate.",
            "when": "After documents are collected.",
            "where": "NoticeMate Response Editor.",
            "what_i_need": "Supporting documents and notice reference number.",
            "what_happens_after": "Final review before submitting on official channel.",
        })
    else:
        steps.append({
            "key": "fill_application_details",
            "title": "Prepare application details & information",
            "short_description": "Double-check names, registration numbers, and choices.",
            "detailed_description": "Prepare all information needed for the official application form.",
            "group": GROUP_THEN,
            "priority": "normal",
            "required": True,
            "estimated_effort": "20 mins",
            "can_do_in_parallel": False,
            "prerequisites": ["prepare_documents"],
            "completion_criteria": "All application details are verified and error-free.",
            "what": "Organize your details for the official application form.",
            "why": "Prevents spelling or numerical typos on the official portal.",
            "how": "Review NoticeMate application steps.",
            "when": "Right before logging into the official portal.",
            "where": "NoticeMate Preparation view.",
            "what_i_need": "Personal details and prepared documents.",
            "what_happens_after": "Review and proceed to official channel.",
        })

    # 6. Fees step if applicable
    if fees:
        amounts = " / ".join(f.get("amount", "") for f in fees[:2] if f.get("amount"))
        if amounts and amounts.lower() != "no fee":
            steps.append({
                "key": "arrange_fee_payment",
                "title": f"Check fee requirements ({amounts})",
                "short_description": "Verify fee amount, payment mode, and exemptions.",
                "detailed_description": "Check if you qualify for a fee waiver or exemption. You pay this directly on the official portal.",
                "group": GROUP_DEADLINE,
                "priority": "normal",
                "required": False,
                "estimated_effort": "5 mins",
                "can_do_in_parallel": True,
                "prerequisites": ["prepare_documents"],
                "completion_criteria": "Fee payment method and amount are confirmed.",
                "what": f"Verify the fee of {amounts}.",
                "why": "Unpaid fees invalidate applications.",
                "how": "Pay using official payment options on the department site.",
                "when": "During official portal submission.",
                "where": "Official portal payment gateway.",
                "what_i_need": "Debit/Credit card or Netbanking details.",
                "what_happens_after": "Final review and submission.",
            })

    # 7. Review step
    last_prereqs = [s["key"] for s in steps if s["key"] in ("prepare_written_reply", "fill_application_details")]
    steps.append({
        "key": "final_review",
        "title": "Review everything thoroughly",
        "short_description": "Cross-check all information, dates, and attachments.",
        "detailed_description": "Verify every document, reference number, and detail against your original notice.",
        "group": GROUP_DEADLINE,
        "priority": "high",
        "required": True,
        "estimated_effort": "10 mins",
        "can_do_in_parallel": False,
        "prerequisites": last_prereqs,
        "completion_criteria": "All items reviewed and verified correct.",
        "what": "Final audit of your prepared application/response.",
        "why": "Eliminates preventable errors before official submission.",
        "how": "Check NoticeMate review summary.",
        "when": "Just before official submission.",
        "where": "NoticeMate Review view.",
        "what_i_need": "Prepared response or application checklist.",
        "what_happens_after": "Submit through official government portal.",
    })

    # 8. Official Channel step
    where_text = f" on {channel_label}" if channel_label else " through the official portal/office"
    steps.append({
        "key": "submit_official_channel",
        "title": f"Complete the process officially{where_text}",
        "short_description": "Submit your application or response on the official channel.",
        "detailed_description": "This final step happens outside NoticeMate. Use the official website, postal address, or office named in your notice. Save your acknowledgement number.",
        "group": GROUP_FINAL,
        "priority": "urgent" if deadline else "high",
        "required": True,
        "official_channel": True,
        "deadline": deadline,
        "estimated_effort": "15 mins",
        "can_do_in_parallel": False,
        "prerequisites": ["final_review"],
        "completion_criteria": "Official reference/acknowledgement receipt obtained.",
        "what": "Submit your completed application/response on the official channel.",
        "why": "NoticeMate is an assistant layer — official processing only occurs when submitted to the authority.",
        "how": "Log in to the official portal or visit the official department office.",
        "when": f"Before {deadline or 'the closing date'}.",
        "where": channel_label or "Official Department Website",
        "what_i_need": "Your prepared documents, response draft, and login details.",
        "what_happens_after": "Save your receipt/reference number and track progress.",
    })

    headline = _headline(mode, category, deadline)
    do_this_now = steps[0]["short_description"]
    do_this_next = steps[1]["short_description"] if len(steps) > 1 else ""
    dont_forget = [
        f"Application/response deadline is {deadline}." if deadline else "Keep a copy of your submitted document.",
        "NoticeMate is an independent helper and does not submit anything to government systems.",
        "Save your official reference or receipt number after completing the process.",
    ]
    parallel_info = "You can prepare your required documents while checking eligibility and dates."

    return headline, do_this_now, do_this_next, dont_forget, parallel_info, steps


def _headline(mode: str, category: str, deadline: str) -> str:
    cat_label = category.replace("_", " ").title()
    if mode == "application":
        base = f"Dynamic roadmap for your {cat_label} application."
    elif mode == "benefit":
        base = f"Step-by-step roadmap to claim your {cat_label} benefit."
    else:
        base = f"Step-by-step roadmap to respond to this {cat_label} notice."
    if deadline:
        return f"{base} Key deadline: {deadline}."
    return base


# --- AI enriched steps -----------------------------------------------------
def _ai_steps(notice: Notice, language: str) -> tuple[str, str, str, list[str], str, list[dict]] | None:
    a = notice.analysis
    if a is None or not ai.ai_available():
        return None
    payload = {
        "category": a.category,
        "mode": a.mode,
        "notice_type": a.notice_type,
        "title": a.title,
        "authority": a.authority,
        "required_action": a.required_action,
        "deadline": a.deadline,
        "important_dates": [{"label": d.label, "value": d.value} for d in notice.important_dates],
        "eligibility": [e.requirement for e in notice.eligibility_items],
        "required_documents": [d.get("name") for d in (a.required_documents or [])],
        "fees": a.fees,
        "application_process": a.application_process,
        "official_channels": a.official_channels,
        "what_happens_next": a.what_happens_next,
    }
    data = ai.json_call(prompts.roadmap_prompt(payload, language))
    if not data or not isinstance(data.get("steps"), list):
        return None

    raw_steps = data.get("steps") or []
    if len(raw_steps) < 3:
        return None

    steps: list[dict] = []
    for i, s in enumerate(raw_steps):
        title = str(s.get("title", "")).strip()
        if not title:
            continue
        key = step_key(s.get("key") or title)
        group = str(s.get("group", "")).strip()
        steps.append({
            "key": key,
            "title": title[:200],
            "short_description": str(s.get("short_description") or s.get("detail", "")).strip()[:300],
            "detailed_description": str(s.get("detailed_description") or s.get("detail", "")).strip()[:600],
            "group": group if group in GROUP_ORDER else GROUP_THEN,
            "priority": str(s.get("priority", "normal")).strip().lower(),
            "required": bool(s.get("required", True)),
            "deadline": str(s.get("deadline", "")).strip()[:120] if s.get("deadline") else None,
            "prerequisites": [step_key(p) for p in (s.get("prerequisites") or []) if p],
            "actions": s.get("actions") or [],
            "estimated_effort": str(s.get("estimated_effort", "10 mins")).strip()[:60],
            "can_do_in_parallel": bool(s.get("can_do_in_parallel")),
            "completion_criteria": str(s.get("completion_criteria", "")).strip()[:200],
            "official_channel": bool(s.get("official_channel")),
            "what": str(s.get("what", "")).strip()[:300],
            "why": str(s.get("why", "")).strip()[:300],
            "how": str(s.get("how", "")).strip()[:300],
            "when": str(s.get("when", "")).strip()[:300],
            "where": str(s.get("where", "")).strip()[:300],
            "what_i_need": str(s.get("what_i_need", "")).strip()[:300],
            "what_happens_after": str(s.get("what_happens_after", "")).strip()[:300],
        })

    # Enforce official channel invariant on the last step
    for s in steps[:-1]:
        s["official_channel"] = False
    steps[-1]["official_channel"] = True
    steps[-1]["group"] = GROUP_FINAL

    headline = str(data.get("headline", "")).strip()
    do_this_now = str(data.get("do_this_now", "")).strip()
    do_this_next = str(data.get("do_this_next", "")).strip()
    dont_forget = [str(x).strip() for x in (data.get("dont_forget") or []) if str(x).strip()]
    parallel_info = str(data.get("parallel_info", "")).strip()

    return headline, do_this_now, do_this_next, dont_forget, parallel_info, steps[:8]


# --- Build & Persist -------------------------------------------------------
def build(db: Session, notice: Notice, language: str = "en") -> list[ActionItem]:
    """Create the dynamic roadmap for a notice (idempotent)."""
    headline, do_now, do_next, dont_forget, parallel_info, steps = _baseline_steps(notice)
    enriched = _ai_steps(notice, language)
    if enriched:
        ai_h, ai_now, ai_next, ai_forget, ai_par, ai_list = enriched
        headline = ai_h or headline
        do_now = ai_now or do_now
        do_next = ai_next or do_next
        dont_forget = ai_forget or dont_forget
        parallel_info = ai_par or parallel_info
        steps = ai_list

    for existing in list(notice.action_items):
        db.delete(existing)
    notice.action_items.clear()
    db.flush()

    items: list[ActionItem] = []
    for i, s in enumerate(steps):
        item = ActionItem(
            notice_id=notice.id,
            order=i,
            title=s["title"],
            description=s.get("detailed_description") or s.get("short_description") or "",
            state="not_started",
        )
        db.add(item)
        items.append(item)
    db.flush()

    if notice.analysis is not None:
        meta = dict(notice.analysis.meta or {})
        meta["roadmap_headline"] = headline
        meta["roadmap_do_now"] = do_now
        meta["roadmap_do_next"] = do_next
        meta["roadmap_dont_forget"] = dont_forget
        meta["roadmap_parallel_info"] = parallel_info
        meta["roadmap_steps_detail"] = steps
        notice.analysis.meta = meta

    sync(db, notice)
    return items


def sync(db: Session, notice: Notice) -> None:
    """Reconcile step states with preparation progress and DAG dependencies."""
    prep = {p.step_key: p.state for p in notice.preparation_states}
    docs_done = workflow.documents_settled(notice)
    has_draft = bool(notice.responses)
    reviewed = any(r.status == "accepted" for r in notice.responses)

    items = sorted(notice.action_items, key=lambda x: x.order)
    meta = dict((notice.analysis.meta if notice.analysis else {}) or {})
    steps_detail = meta.get("roadmap_steps_detail") or []
    key_to_detail = {s["key"]: s for s in steps_detail if "key" in s}

    completed_keys: set[str] = set()

    for item in items:
        key = step_key(item.title)
        detail = key_to_detail.get(key, {})
        prereqs = detail.get("prerequisites") or []

        # Check explicit preparation state set by user
        if key in prep:
            state = prep[key]
        else:
            t = item.title.lower()
            if "read" in t or "explanation" in t or "understand" in t or "date" in t:
                state = "completed"
            elif "document" in t or "collect" in t or "gather" in t:
                state = "completed" if docs_done else "in_progress"
            elif "reply" in t or "draft" in t or "application details" in t or "written" in t:
                state = "completed" if has_draft else ("in_progress" if docs_done else "not_started")
            elif "review" in t:
                state = "completed" if reviewed else ("in_progress" if has_draft else "not_started")
            else:
                state = "not_started"

        # Check DAG dependencies: if prerequisite is not completed, mark as blocked
        unmet = [p for p in prereqs if p not in completed_keys and p != key]
        if unmet and state != "completed":
            state = "blocked"

        if state == "completed":
            completed_keys.add(key)

        item.state = state
        db.add(item)

    _advance_from_progress(db, notice, docs_done, has_draft, reviewed)


def _advance_from_progress(
    db: Session, notice: Notice, docs_done: bool, has_draft: bool, reviewed: bool
) -> None:
    if docs_done:
        workflow.advance_state(db, notice, WorkflowState.DOCUMENTS_PREPARED)
    if has_draft:
        workflow.advance_state(db, notice, WorkflowState.RESPONSE_PREPARED)
    if reviewed:
        workflow.advance_state(db, notice, WorkflowState.USER_REVIEWED)


def set_step_state(db: Session, notice: Notice, key: str, state: str) -> RoadmapOut:
    """Record the citizen's progress on a roadmap step."""
    row = next((p for p in notice.preparation_states if p.step_key == key), None)
    if row is None:
        row = PreparationState(notice_id=notice.id, step_key=key, state=state)
        db.add(row)
        notice.preparation_states.append(row)
    else:
        row.state = state
        db.add(row)
    db.flush()
    sync(db, notice)

    steps = sorted(notice.action_items, key=lambda x: x.order)
    if steps and all(s.state == "completed" for s in steps[:-1]):
        workflow.advance_state(db, notice, WorkflowState.READY_FOR_OFFICIAL_CHANNEL)
    db.commit()
    db.refresh(notice)
    return serialize(notice)


# --- Serialization ---------------------------------------------------------
def serialize(notice: Notice) -> RoadmapOut:
    meta = dict((notice.analysis.meta if notice.analysis else {}) or {})
    steps_detail = meta.get("roadmap_steps_detail") or []
    key_to_detail = {s["key"]: s for s in steps_detail if "key" in s}

    items = sorted(notice.action_items, key=lambda x: x.order)
    steps: list[RoadmapStepOut] = []
    completed_keys = {step_key(i.title) for i in items if i.state == "completed"}

    for i, item in enumerate(items):
        key = step_key(item.title)
        d = key_to_detail.get(key, {})
        prereqs = d.get("prerequisites") or []
        unmet_prereqs = [p for p in prereqs if p not in completed_keys and p != key]

        VALID_STATUSES = {"not_started", "in_progress", "completed", "blocked", "needs_verification", "not_applicable"}
        VALID_PRIORITIES = {"urgent", "high", "normal", "low"}

        status = item.state if item.state in VALID_STATUSES else "not_started"
        blocker_reason = ""
        if unmet_prereqs and status != "completed":
            status = "blocked"
            prereq_titles = [key_to_detail.get(p, {}).get("title", p) for p in unmet_prereqs]
            blocker_reason = f"Complete previous step ('{prereq_titles[0]}') first."

        raw_priority = str(d.get("priority", "")).lower()
        if raw_priority in ("medium", "med"):
            priority = "high"
        elif raw_priority in VALID_PRIORITIES:
            priority = raw_priority
        else:
            priority = "urgent" if d.get("deadline") else "normal"

        steps.append(
            RoadmapStepOut(
                id=key,
                key=key,
                order=item.order + 1,
                title=d.get("title") or item.title,
                short_description=d.get("short_description") or item.description,
                detailed_description=d.get("detailed_description") or item.description,
                status=status,
                priority=priority,
                required=d.get("required", True),
                deadline=d.get("deadline"),
                prerequisites=prereqs,
                blocker_reason=blocker_reason,
                actions=d.get("actions") or [],
                estimated_effort=d.get("estimated_effort") or "10 mins",
                can_do_in_parallel=d.get("can_do_in_parallel", False),
                completion_criteria=d.get("completion_criteria") or "",
                official_channel=d.get("official_channel", i == len(items) - 1),
                group=d.get("group") or _fallback_group(i, len(items)),
                what=d.get("what") or "",
                why=d.get("why") or "",
                how=d.get("how") or "",
                when=d.get("when") or "",
                where=d.get("where") or "",
                what_i_need=d.get("what_i_need") or "",
                what_happens_after=d.get("what_happens_after") or "",
            )
        )

    completed_count = sum(1 for s in steps if s.status == "completed")
    next_step = next((s for s in steps if s.status not in ("completed", "not_applicable")), None)

    do_now = meta.get("roadmap_do_now") or (next_step.title if next_step else "Proceed to official portal")
    do_next = meta.get("roadmap_do_next") or ""
    dont_forget = meta.get("roadmap_dont_forget") or [
        "Check all document size and format limits.",
        "NoticeMate does not submit applications on your behalf.",
        "Save your final reference/acknowledgement receipt.",
    ]
    parallel_info = meta.get("roadmap_parallel_info") or "You can gather documents while checking eligibility."

    return RoadmapOut(
        notice_id=notice.id,
        steps=steps,
        completed=completed_count,
        total=len(steps),
        headline=meta.get("roadmap_headline") or "Here is your personalized preparation roadmap.",
        next_step=next_step,
        do_this_now=do_now,
        do_this_next=do_next,
        dont_forget=dont_forget,
        parallel_info=parallel_info,
    )


def _fallback_group(index: int, total: int) -> str:
    if index == total - 1:
        return GROUP_FINAL
    if index < 2:
        return GROUP_FIRST
    if index >= total - 3:
        return GROUP_DEADLINE
    return GROUP_THEN


# --- Interactive Step Help (§31) --------------------------------------------
def step_help(
    db: Session,
    notice: Notice,
    step_id: str,
    user_question: str | None = None,
    language: str = "en",
) -> StepHelpOut:
    """Provide step-specific AI assistance."""
    roadmap = serialize(notice)
    target = next((s for s in roadmap.steps if s.id == step_id or s.key == step_id), None)
    if target is None:
        target = roadmap.steps[0] if roadmap.steps else RoadmapStepOut(id="step", key="step", order=1, title="General Step")

    if notice.analysis and ai.ai_available():
        a = {
            "title": notice.analysis.title,
            "authority": notice.analysis.authority,
            "required_action": notice.analysis.required_action,
            "deadline": notice.analysis.deadline,
        }
        res = ai.json_call(prompts.step_help_prompt(target.model_dump(), a, user_question, language))
        if res and res.get("explanation"):
            return StepHelpOut(
                step_id=target.id,
                title=target.title,
                explanation=str(res.get("explanation")),
                actionable_tip=str(res.get("actionable_tip") or "Verify details against your notice."),
                grounded_source=str(res.get("grounded_source") or "Notice summary"),
            )

    return StepHelpOut(
        step_id=target.id,
        title=target.title,
        explanation=target.detailed_description or target.short_description or "Follow the step instructions carefully.",
        actionable_tip=f"Complete this step before proceeding to: {target.what_happens_after or 'the next step'}.",
        grounded_source="Extracted notice facts",
    )
