"""Eligibility engine (§11) — "Can I apply?"

Three principles, in order of importance:

1. **Never guess.** A condition is only marked met or not met when the citizen
   has given a fact that settles it. Otherwise it stays ``needs_input`` and we
   name the single fact we are missing.
2. **Ask for as little as possible.** Each question is derived from the
   requirement itself, so we only ever ask for what that condition needs.
3. **Never ask for sensitive identifiers.** Aadhaar, PAN, bank details,
   passwords, OTPs and health information are rejected outright — including if
   a model tries to ask for them.
"""

from __future__ import annotations

import logging
import re

from sqlalchemy.orm import Session

from .. import prompts
from ..models import EligibilityItem, Notice, TrustLevel
from ..schemas import EligibilityOut
from . import ai

logger = logging.getLogger("noticemate.eligibility")

# Facts we are willing to accept from the citizen. Anything else is ignored.
ALLOWED_FACTS = {
    "age": "your age in years",
    "education": "your highest qualification",
    "experience": "your years of relevant experience",
    "residency": "the state you are a resident of",
    "category": "your reservation category, if any",
    "income": "your annual family income",
}

# Never requested, never stored, never sent to a model.
FORBIDDEN_FACT = re.compile(
    r"aadhaar|aadhar|\bpan\b|\botp\b|password|bank\s*account|card\s*number|"
    r"cvv|ifsc|health|medical|biometric|passport\s*number|voter\s*id",
    re.I,
)

_NUM = re.compile(r"(\d{1,3}(?:,\d{2,3})*|\d+)(?:\s*(?:years?|yrs?))?")
_AGE_RANGE = re.compile(
    r"(?:between\s*)?(\d{2})\s*(?:to|-|–|and)\s*(\d{2})\s*years", re.I
)
_AGE_MIN = re.compile(r"(?:not\s+less\s+than|minimum|at\s+least|above)\s*(\d{2})", re.I)
_AGE_MAX = re.compile(
    r"(?:not\s+more\s+than|maximum|not\s+exceed(?:ing)?|below|under|upper\s+age\s*"
    r"(?:limit)?(?:\s*(?:is|of|:))?)\s*(\d{2})",
    re.I,
)
_MONEY = re.compile(r"(?:rs\.?|inr|₹)\s*([\d,]+)", re.I)

_EDU_LEVELS = [
    ("matriculation", 1),
    ("10th", 1),
    ("class x", 1),
    ("secondary", 1),
    ("10+2", 2),
    ("12th", 2),
    ("intermediate", 2),
    ("higher secondary", 2),
    ("diploma", 3),
    ("graduat", 4),
    ("bachelor", 4),
    ("degree", 4),
    ("post graduat", 5),
    ("postgraduat", 5),
    ("master", 5),
]


def sanitize_facts(facts: dict) -> tuple[dict, list[str]]:
    """Keep only the facts we are allowed to use. Returns ``(clean, refused)``."""
    clean: dict = {}
    refused: list[str] = []
    for key, value in (facts or {}).items():
        k = str(key).strip().lower()
        if FORBIDDEN_FACT.search(k) or FORBIDDEN_FACT.search(str(value)):
            refused.append(k)
            continue
        if k not in ALLOWED_FACTS:
            continue
        text = str(value).strip()
        if text:
            clean[k] = text[:120]
    return clean, refused


# --- Deterministic evaluation ----------------------------------------------
def _eval_age(requirement: str, facts: dict) -> tuple[str, str, str]:
    if "age" not in facts:
        return "needs_input", ALLOWED_FACTS["age"], ""
    try:
        age = int(re.sub(r"\D", "", facts["age"])[:3])
    except (ValueError, TypeError):
        return "needs_input", ALLOWED_FACTS["age"], ""

    lo = hi = None
    m = _AGE_RANGE.search(requirement)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
    else:
        mn = _AGE_MIN.search(requirement)
        mx = _AGE_MAX.search(requirement)
        if mn:
            lo = int(mn.group(1))
        if mx:
            hi = int(mx.group(1))
    if lo is None and hi is None:
        return "unknown", "", "The notice does not state a clear age limit for this condition."

    if lo is not None and age < lo:
        return "not_met", "", f"You are {age}; this requires at least {lo}."
    if hi is not None and age > hi:
        return (
            "not_met",
            "",
            f"You are {age}; the stated upper limit is {hi}. Check whether an age "
            "relaxation applies to you.",
        )
    bound = f"{lo}–{hi}" if lo is not None and hi is not None else (f"{lo}+" if lo else f"up to {hi}")
    return "met", "", f"You are {age}, which is within the stated range ({bound})."


def _eval_income(requirement: str, facts: dict) -> tuple[str, str, str]:
    if "income" not in facts:
        return "needs_input", ALLOWED_FACTS["income"], ""
    m = _MONEY.search(requirement)
    if not m:
        return "unknown", "", "The notice does not state a clear income limit."
    ceiling = int(m.group(1).replace(",", ""))
    digits = re.sub(r"\D", "", facts["income"])
    if not digits:
        return "needs_input", ALLOWED_FACTS["income"], ""
    income = int(digits)
    if income > ceiling:
        return "not_met", "", f"The stated ceiling is Rs. {ceiling:,} and you entered Rs. {income:,}."
    return "met", "", f"Rs. {income:,} is within the stated ceiling of Rs. {ceiling:,}."


def _eval_education(requirement: str, facts: dict) -> tuple[str, str, str]:
    if "education" not in facts:
        return "needs_input", ALLOWED_FACTS["education"], ""
    need = _edu_level(requirement)
    have = _edu_level(facts["education"])
    if need == 0 or have == 0:
        return (
            "needs_input",
            ALLOWED_FACTS["education"],
            "We could not match your qualification to the one the notice asks for.",
        )
    if have >= need:
        return "met", "", "Your qualification meets or exceeds what the notice asks for."
    return "not_met", "", "The notice asks for a higher qualification than the one you entered."


def _edu_level(text: str) -> int:
    low = (text or "").lower()
    level = 0
    for token, value in _EDU_LEVELS:
        if token in low:
            level = max(level, value)
    return level


def _eval_experience(requirement: str, facts: dict) -> tuple[str, str, str]:
    if "experience" not in facts:
        return "needs_input", ALLOWED_FACTS["experience"], ""
    m = re.search(r"(\d+)\s*(?:years?|yrs?)", requirement, re.I)
    if not m:
        return "unknown", "", "The notice does not state a clear number of years."
    need = int(m.group(1))
    digits = re.sub(r"\D", "", facts["experience"])
    if not digits:
        return "needs_input", ALLOWED_FACTS["experience"], ""
    have = int(digits)
    if have >= need:
        return "met", "", f"{have} years meets the stated {need}."
    return "not_met", "", f"The notice asks for {need} years; you entered {have}."


def _eval_residency(requirement: str, facts: dict) -> tuple[str, str, str]:
    if "residency" not in facts:
        return "needs_input", ALLOWED_FACTS["residency"], ""
    stated = facts["residency"].strip().lower()
    if stated and stated in requirement.lower():
        return "met", "", "Matches the residency condition in the notice."
    return (
        "needs_input",
        ALLOWED_FACTS["residency"],
        "We could not confirm this from what you entered. Check the exact wording in your notice.",
    )


def _eval_category(requirement: str, facts: dict) -> tuple[str, str, str]:
    if "category" not in facts:
        return "needs_input", ALLOWED_FACTS["category"], ""
    cat = facts["category"].strip().upper()
    if cat and cat in requirement.upper():
        return "met", "", f"Your category ({cat}) is named in this condition."
    return (
        "unknown",
        "",
        "This condition mentions categories. Check whether it applies to you.",
    )


_EVALUATORS = {
    "age": _eval_age,
    "income": _eval_income,
    "education": _eval_education,
    "experience": _eval_experience,
    "residency": _eval_residency,
    "category": _eval_category,
}


def evaluate(db: Session, notice: Notice, facts: dict) -> tuple[list[EligibilityOut], list[str]]:
    """Evaluate every stored condition against the supplied facts.

    Deterministic rules decide first; the model is only consulted for conditions
    the rules could not settle, and it can never turn an unmet condition into a
    met one — it may only add a plain-language explanation or refine a
    ``needs_input`` question.
    """
    clean, refused = sanitize_facts(facts)
    items = sorted(notice.eligibility_items, key=lambda x: x.order)

    unresolved: list[EligibilityItem] = []
    for item in items:
        evaluator = _EVALUATORS.get(item.category)
        if evaluator is None:
            item.status = "needs_input" if not clean else "unknown"
            item.needs = ""
            item.detail = item.detail or (
                "Read this condition and confirm it applies to you. NoticeMate cannot "
                "check it automatically."
            )
            unresolved.append(item)
        else:
            status, needs, detail = evaluator(item.requirement, clean)
            item.status = status
            item.needs = needs
            if detail:
                item.detail = detail
            if status in ("unknown",):
                unresolved.append(item)
        item.trust = TrustLevel.FROM_NOTICE
        db.add(item)

    if unresolved and clean and ai.ai_available():
        _refine(unresolved, clean, db)

    db.commit()
    db.refresh(notice)
    out = [
        EligibilityOut.model_validate(i)
        for i in sorted(notice.eligibility_items, key=lambda x: x.order)
    ]
    return out, refused


def _refine(items: list[EligibilityItem], facts: dict, db: Session) -> None:
    """Ask the model to explain the conditions our rules could not settle."""
    payload = [
        {"requirement": i.requirement, "category": i.category} for i in items
    ]
    data = ai.json_call(prompts.eligibility_prompt(payload, facts))
    if not data:
        return
    by_req = {i.requirement.strip().lower()[:60]: i for i in items}
    for row in data.get("items") or []:
        item = by_req.get(str(row.get("requirement", "")).strip().lower()[:60])
        if item is None:
            continue
        status = str(row.get("status", "")).strip()
        if status in ("met", "not_met", "needs_input", "unknown"):
            item.status = status
        needs = str(row.get("needs", "")).strip()
        # Guard: the model must not ask for anything sensitive or unlisted.
        if needs and not FORBIDDEN_FACT.search(needs):
            item.needs = needs[:160]
        elif needs:
            logger.warning("eligibility prompt asked for a forbidden fact; dropped")
            item.needs = ""
        detail = str(row.get("detail", "")).strip()
        if detail:
            item.detail = detail[:600]
        db.add(item)


def summary(notice: Notice) -> dict:
    """A one-line verdict for the dashboard card."""
    items = list(notice.eligibility_items)
    if not items:
        return {
            "verdict": "unknown",
            "message": "This notice does not list eligibility conditions.",
            "met": 0,
            "not_met": 0,
            "needs_input": 0,
            "total": 0,
            "questions": [],
        }
    met = sum(1 for i in items if i.status == "met")
    not_met = sum(1 for i in items if i.status == "not_met")
    needs = [i.needs for i in items if i.status == "needs_input" and i.needs]

    if not_met:
        verdict = "not_met"
        message = (
            f"{not_met} condition(s) do not appear to be met. Check whether a "
            "relaxation or exemption applies to you before you rule yourself out."
        )
    elif needs:
        verdict = "needs_input"
        unique = list(dict.fromkeys(needs))
        message = "To check your eligibility, we need " + ", ".join(unique[:3]) + "."
    elif met == len(items):
        verdict = "met"
        message = "You appear to meet every condition stated in the notice."
    else:
        verdict = "unknown"
        message = (
            "Some conditions cannot be checked automatically. Please read them and "
            "confirm they apply to you."
        )

    return {
        "verdict": verdict,
        "message": message,
        "met": met,
        "not_met": not_met,
        "needs_input": len(needs),
        "total": len(items),
        "questions": list(dict.fromkeys(needs))[:6],
    }
