"""Deterministic extractors for dates, eligibility, fees, documents and channels.

Why this module exists
----------------------
Two reasons, both about reliability:

1. **The demo must work without an API key or billing quota.** These rules
   produce a genuinely useful analysis from plain text with no network call.
2. **The AI path is checked against it.** When the model returns an analysis we
   still run these extractors and merge in anything the model missed, so a
   single AI call can never silently drop a deadline (§10 of the spec: dates are
   a first-class feature).

Everything here is conservative on purpose. A relative period such as "within
15 days of receipt" is reported *as that phrase* and flagged
``is_relative=True`` — it is never converted into a calendar date, because we
do not know when the citizen received the notice.
"""

from __future__ import annotations

import re
from datetime import date, datetime

from ..schemas import (
    CATEGORIES,
    EligibilitySchema,
    FeeSchema,
    ImportantDateSchema,
    OfficialChannelSchema,
    ProcedureStepSchema,
    RequiredDocument,
)

# --- Date parsing ----------------------------------------------------------
_MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

_MONTH_ALT = "|".join(sorted(_MONTHS, key=len, reverse=True))

# "30 September 2026" / "30 Sep 2026" / "30th September, 2026"
_DMY_TEXT = re.compile(
    rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({_MONTH_ALT})\.?,?\s+(\d{{4}})\b", re.I
)
# "September 30, 2026"
_MDY_TEXT = re.compile(
    rf"\b({_MONTH_ALT})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})\b", re.I
)
# "30-09-2026" / "30/09/2026" / "30.09.2026"
_DMY_NUM = re.compile(r"\b(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})\b")
# "2026-09-30"
_ISO_NUM = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")

# Relative periods we must NOT resolve to a calendar date.
_RELATIVE = re.compile(
    r"\bwithin\s+(\d+|one|two|three|seven|ten|fifteen|thirty)\s+"
    r"(working\s+)?(day|days|week|weeks|month|months)\b"
    r"(\s+(?:of|from)\s+[^.,;\n]{0,60})?",
    re.I,
)

_TBA = re.compile(
    r"\b(to\s+be\s+(announced|notified|intimated|declared)|will\s+be\s+announced|TBA|TBD)\b",
    re.I,
)


def _mk_date(y: int, m: int, d: int) -> str | None:
    try:
        return date(y, m, d).isoformat()
    except ValueError:
        return None


def find_dates_in(fragment: str) -> list[tuple[str, str]]:
    """Return ``[(display_text, iso_or_empty), ...]`` for a text fragment."""
    found: list[tuple[str, str]] = []
    for m in _DMY_TEXT.finditer(fragment):
        iso = _mk_date(int(m.group(3)), _MONTHS[m.group(2).lower()], int(m.group(1)))
        found.append((m.group(0), iso or ""))
    for m in _MDY_TEXT.finditer(fragment):
        iso = _mk_date(int(m.group(3)), _MONTHS[m.group(1).lower()], int(m.group(2)))
        found.append((m.group(0), iso or ""))
    for m in _ISO_NUM.finditer(fragment):
        iso = _mk_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        found.append((m.group(0), iso or ""))
    for m in _DMY_NUM.finditer(fragment):
        # Indian notices are day-first. Only fall back to month-first when
        # day-first is impossible (e.g. 09/30/2026).
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        iso = _mk_date(y, mo, d) or _mk_date(y, d, mo)
        found.append((m.group(0), iso or ""))
    # De-duplicate while preserving order.
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for text, iso in found:
        key = iso or text.lower()
        if key not in seen:
            seen.add(key)
            out.append((text, iso))
    return out


# Label patterns → (kind, friendly label, is_deadline)
#
# ORDER MATTERS. The first pattern that matches a line wins, so the most
# specific labels must come first: "Last date for fee payment" has to be read as
# a payment deadline, not as the application deadline.
_DATE_LABELS: list[tuple[re.Pattern[str], str, str, bool]] = [
    (re.compile(r"(?:fee\s+)?payment[^\n]{0,20}(?:deadline|due|last\s+date)|last\s+date\s+for\s+(?:\w+\s+){0,2}(?:fee|payment)|fee\s+can\s+be\s+paid", re.I),
     "payment_deadline", "Fee payment deadline", True),
    (re.compile(r"correction\s+(?:window|period|facility)|edit\s+window|modification\s+window", re.I),
     "correction_window", "Correction window", False),
    (re.compile(r"admit\s+card|hall\s+ticket", re.I),
     "admit_card", "Admit card available", False),
    (re.compile(r"(?:provisional|merit|selection|shortlist\w*)\s+list|list\s+(?:will\s+be\s+)?published|result\s+(?:date|declaration)|declaration\s+of\s+result", re.I),
     "result", "Result / list published", False),
    (re.compile(r"institutional\s+verification|verification\s+by\s+(?:the\s+)?institution", re.I),
     "institutional_verification", "Institutional verification by", False),
    (re.compile(r"application\s+(?:start|begin|open)\w*|online\s+application\s+(?:start|open)\w*|start\s+date\s+(?:of|for)\s+application|registration\s+(?:start|open)\w*", re.I),
     "application_start", "Application opens", False),
    (re.compile(r"application\s+(?:clos|end)\w*|last\s+date(?:\s+for)?(?:\s+\w+){0,4}|closing\s+date|final\s+date|deadline\s+for\s+application|registration\s+(?:clos|end)\w*", re.I),
     "application_end", "Application closes", True),
    (re.compile(r"exam(?:ination)?\s+date|date\s+of\s+exam(?:ination)?|written\s+(?:test|exam)", re.I),
     "examination", "Examination", False),
    (re.compile(r"interview\s+date|date\s+of\s+interview", re.I),
     "interview", "Interview", False),
    (re.compile(r"(?:document\s+)?verification\s+date|date\s+of\s+verification|document\s+verification", re.I),
     "verification", "Document verification", False),
    (re.compile(r"hearing\s+date|date\s+of\s+hearing|personal\s+hearing", re.I),
     "hearing", "Hearing", False),
    (re.compile(r"appointment\s+date|date\s+of\s+appointment", re.I),
     "appointment", "Appointment", False),
    (re.compile(r"disbursement|payment\s+will\s+be\s+(?:made|credited)|credit(?:ed)?\s+(?:on|by)|instalment", re.I),
     "disbursement", "Disbursement", False),
    (re.compile(r"response\s+(?:due|deadline)|reply\s+(?:by|due)|respond\s+by|action\s+required\s+by|due\s+by|compliance\s+date", re.I),
     "response_deadline", "Response deadline", True),
    (re.compile(r"date\s+of\s+(?:notice|issue|notification|publication)|notice\s+date|notification\s+date|^\s*dated\b|publication\s+date", re.I),
     "notice_date", "Notice date", False),
]

# "05 October 2026 to 08 October 2026" / "2 - 4 October 2026"
_RANGE_JOINER = re.compile(r"\b(?:to|till|until|upto|up\s+to|through)\b|[–—]|\s-\s", re.I)



def parse_important_dates(text: str) -> list[ImportantDateSchema]:
    """Extract every dated milestone we can identify, with its label."""
    text = text or ""
    out: list[ImportantDateSchema] = []
    seen: set[tuple[str, str]] = set()

    # Work line by line first — notices usually put "Label: date" on one line.
    for raw in text.splitlines():
        line = raw.strip()
        if not line or len(line) > 300:
            continue
        for pattern, kind, label, is_deadline in _DATE_LABELS:
            if not pattern.search(line):
                continue
            dates = find_dates_in(line)
            if dates:
                # "05 October 2026 to 08 October 2026" is one window, not two
                # separate milestones.
                if len(dates) == 2 and _looks_like_range(line, dates):
                    key = (kind, dates[0][1] or dates[0][0].lower())
                    if key not in seen:
                        seen.add(key)
                        out.append(
                            ImportantDateSchema(
                                kind=kind,
                                label=label,
                                value=f"{dates[0][0]} to {dates[1][0]}",
                                iso_date=dates[0][1] or None,
                                is_deadline=is_deadline,
                                note=_tidy_context(line),
                            )
                        )
                    break
                for display, iso in dates:
                    key = (kind, iso or display.lower())
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append(
                        ImportantDateSchema(
                            kind=kind,
                            label=label,
                            value=display,
                            iso_date=iso or None,
                            is_deadline=is_deadline,
                            note=_tidy_context(line),
                        )
                    )
                break
            rel = _RELATIVE.search(line)
            if rel:
                key = (kind, rel.group(0).lower())
                if key not in seen:
                    seen.add(key)
                    out.append(
                        ImportantDateSchema(
                            kind=kind,
                            label=label,
                            value=rel.group(0).strip(),
                            iso_date=None,
                            is_relative=True,
                            is_deadline=is_deadline,
                            note=(
                                "This is a period, not a fixed date. It depends on "
                                "when you received the notice, so we have not "
                                "converted it into a calendar date."
                            ),
                        )
                    )
                break
            if _TBA.search(line):
                key = (kind, "tba")
                if key not in seen:
                    seen.add(key)
                    out.append(
                        ImportantDateSchema(
                            kind=kind,
                            label=label,
                            value="To be announced",
                            iso_date=None,
                            is_deadline=is_deadline,
                            note=_tidy_context(line),
                        )
                    )
                break

    # A bare relative deadline anywhere in the document still matters.
    if not any(d.is_deadline for d in out):
        rel = _RELATIVE.search(text)
        if rel:
            out.append(
                ImportantDateSchema(
                    kind="response_deadline",
                    label="Response deadline",
                    value=rel.group(0).strip(),
                    is_relative=True,
                    is_deadline=True,
                    note=(
                        "The notice gives a period rather than a date. Count from "
                        "the day you received it, and confirm with the issuing "
                        "authority if you are unsure."
                    ),
                )
            )

    out.sort(key=lambda d: (d.iso_date or "9999-99-99", d.label))
    for i, item in enumerate(out):
        item.kind = item.kind or "other"
    return out


def _tidy_context(line: str) -> str:
    line = re.sub(r"\s+", " ", line).strip(" -:*\t")
    return line[:200]


def _looks_like_range(line: str, dates: list[tuple[str, str]]) -> bool:
    """True when the text *between* two dates joins them into one window."""
    first, second = dates[0][0], dates[1][0]
    start = line.find(first)
    if start < 0:
        return False
    between = line[start + len(first) : line.find(second, start + len(first))]
    if not between or len(between) > 14:
        return False
    return bool(_RANGE_JOINER.search(between))


def days_until(iso_date: str | None, today: date | None = None) -> int | None:
    """Whole days from today to ``iso_date``. Negative when already past."""
    if not iso_date:
        return None
    try:
        target = date.fromisoformat(iso_date)
    except (TypeError, ValueError):
        return None
    return (target - (today or datetime.now().date())).days


def primary_deadline(dates: list[ImportantDateSchema]) -> ImportantDateSchema | None:
    """The deadline the citizen most needs to see: soonest real date wins."""
    deadlines = [d for d in dates if d.is_deadline]
    if not deadlines:
        return None
    dated = [d for d in deadlines if d.iso_date]
    if dated:
        return min(dated, key=lambda d: d.iso_date or "")
    return deadlines[0]


# --- Classification --------------------------------------------------------
_CATEGORY_HINTS: list[tuple[str, str, tuple[str, ...]]] = [
    ("recruitment", "application", ("recruitment", "vacanc", "post of", "posts of", "appointment to the post", "eligible candidates are invited", "apply online for the post")),
    ("scholarship", "benefit", ("scholarship", "merit-cum-means", "fellowship", "stipend", "tuition assistance")),
    ("examination", "application", ("examination notification", "exam notification", "admit card", "hall ticket", "written examination")),
    ("admission", "application", ("admission", "counselling", "seat allotment")),
    ("welfare_scheme", "benefit", ("welfare scheme", "beneficiary", "yojana", "scheme benefit", "subsidy")),
    ("government_benefit", "benefit", ("benefit transfer", "direct benefit", "pension benefit", "entitlement")),
    ("tax", "response", ("income tax", "income-tax", "assessing officer", "form 26as", "tds", "section 143", "gst", "assessment year")),
    ("epfo", "response", ("provident fund", "epfo", "epf", "uan", "kyc update")),
    ("pension", "response", ("pension", "pensioner", "life certificate", "jeevan pramaan")),
    ("certificate", "response", ("certificate issuance", "birth certificate", "death certificate", "caste certificate", "income certificate", "domicile")),
    ("licence", "response", ("licence", "license renewal", "permit renewal", "trade licence")),
    ("municipal", "response", ("municipal", "corporation", "property tax", "ward office", "sanitation", "water connection")),
    ("property", "response", ("mutation", "land record", "khata", "encumbrance", "registry of property")),
    ("transport", "response", ("driving licence", "rto", "vehicle registration", "fitness certificate", "challan")),
    ("grievance", "response", ("grievance", "complaint reference", "ticket number", "public grievance")),
    ("document_verification", "response", ("document verification", "verify the documents", "produce the originals")),
    ("payment", "response", ("outstanding amount", "demand notice", "payment is due", "arrears")),
    ("hearing", "response", ("personal hearing", "appear before", "hearing is fixed")),
    ("compliance", "response", ("compliance", "show cause", "non-compliance", "you are hereby directed")),
    ("education", "application", ("board of education", "school", "university", "college")),
    ("public_announcement", "response", ("public notice", "general public is informed", "public announcement")),
]


def classify(text: str) -> tuple[str, str, bool]:
    """Return ``(category, mode, confident)`` from keyword evidence.

    ``confident`` is False when nothing matched, so the UI can honestly say
    "Document type could not be determined confidently." (§8)
    """
    low = (text or "").lower()
    scores: dict[str, tuple[int, str]] = {}
    for category, mode, hints in _CATEGORY_HINTS:
        hits = sum(1 for h in hints if h in low)
        if hits:
            scores[category] = (hits, mode)
    if not scores:
        return "other", "response", False
    best = max(scores.items(), key=lambda kv: kv[1][0])
    category, (hits, mode) = best
    if category not in CATEGORIES:
        return "other", mode, False
    return category, mode, hits >= 2


# Matches a list marker at the start of a line: "1.", "2)", "-", "*", "(a)".
_BULLET = re.compile(r"^\s*(?:\d+[.)]|[-*•▪◦]|\([a-z0-9]\))\s*")


# --- Eligibility -----------------------------------------------------------
_ELIG_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("age", re.compile(r"\bage\s+(?:limit|criteria|between|should|must|as\s+on)[^.\n]{0,160}", re.I)),
    ("age", re.compile(r"\b(?:minimum|maximum)\s+age[^.\n]{0,160}", re.I)),
    ("age", re.compile(r"\bage\s+relaxation[^.\n]{0,160}", re.I)),
    ("education", re.compile(r"\b(?:educational\s+qualification|minimum\s+qualification|must\s+have\s+passed|graduat\w+|bachelor\w*|10\+2|intermediate|matriculation|diploma|post-?graduat\w+)[^.\n]{0,160}", re.I)),
    ("experience", re.compile(r"\b(?:work\s+experience|years?\s+of\s+experience|prior\s+experience)[^.\n]{0,160}", re.I)),
    ("residency", re.compile(r"\b(?:resident\s+of|domicile|permanent\s+resident|local\s+candidate)[^.\n]{0,160}", re.I)),
    ("residency", re.compile(r"\b(?:citizen\s+of\s+India|Indian\s+national|nationality)[^.\n]{0,160}", re.I)),
    ("category", re.compile(r"\b(?:reserved\s+category|SC/ST|OBC|EWS|category\s+certificate|belonging\s+to\s+\w+\s+category)[^.\n]{0,160}", re.I)),
    ("income", re.compile(r"\b(?:annual\s+(?:family\s+)?income|income\s+(?:limit|ceiling|should\s+not\s+exceed))[^.\n]{0,160}", re.I)),
]

_NEEDS = {
    "age": "your date of birth",
    "education": "your highest qualification",
    "experience": "your years of relevant experience",
    "residency": "your state of residence",
    "category": "your category, if you are claiming one",
    "income": "your annual family income",
}

_ELIG_HEADER = re.compile(
    r"^\s*(?:eligibility(?:\s+(?:conditions?|criteria|requirements?))?"
    r"|who\s+can\s+apply|conditions?\s+(?:of|for)\s+eligibility"
    r"|essential\s+qualifications?)\s*[:\-]?\s*$",
    re.I,
)
# Headers that end an eligibility block.
_SECTION_BREAK = re.compile(
    r"^\s*(?:[A-Z][A-Z\s/&()-]{6,}|(?:application\s+fee|documents?\s+required|how\s+to\s+apply"
    r"|selection\s+process|important\s+dates)\b[^\n]{0,40})\s*[:\-]?\s*$"
)

# Keyword → eligibility category, checked in order.
_ELIG_CATEGORY: list[tuple[str, re.Pattern[str]]] = [
    ("age", re.compile(r"\bage\b|\byears?\s+of\s+age\b|date\s+of\s+birth|age\s+relaxation", re.I)),
    ("income", re.compile(r"\bincome\b|\bearnings\b", re.I)),
    ("education", re.compile(r"\b(?:qualification|passed|degree|graduat\w+|bachelor|master|10\+2|intermediate|matriculation|diploma|marks|percent)\b", re.I)),
    ("experience", re.compile(r"\bexperience\b|\byears?\s+of\s+service\b", re.I)),
    ("residency", re.compile(r"\b(?:resident|domicile|nationality|citizen|permanent\s+resident|local\s+candidate)\b", re.I)),
    ("category", re.compile(r"\b(?:SC/ST|OBC|EWS|reserved\s+category|category\s+certificate|caste)\b", re.I)),
]


def _section_lines(text: str, header: re.Pattern[str]) -> list[str]:
    """Return the lines under ``header`` up to the next section heading."""
    lines = (text or "").splitlines()
    for i, line in enumerate(lines):
        if not header.match(line.strip()):
            continue
        block: list[str] = []
        blanks = 0
        for follow in lines[i + 1 : i + 60]:
            s = follow.strip()
            if not s:
                blanks += 1
                if blanks >= 2 and block:
                    break
                continue
            if _SECTION_BREAK.match(s) and block:
                break
            if s.startswith("***"):
                break
            blanks = 0
            block.append(follow)
        return block
    return []


def _classify_eligibility(item: str) -> str:
    for category, pattern in _ELIG_CATEGORY:
        if pattern.search(item):
            return category
    return "other"


def parse_eligibility(text: str) -> list[EligibilitySchema]:
    """Pull out stated eligibility conditions.

    When the notice has an "Eligibility" section we read it item by item, which
    gives one clean condition per numbered point. Only when there is no such
    section do we fall back to scanning the whole document for eligibility-shaped
    sentences.

    Status is always ``needs_input``: the notice states a *requirement*, and we
    cannot know whether the citizen meets it until they tell us. We never guess,
    and we ask only for the minimum detail needed (§11).
    """
    text = text or ""
    out: list[EligibilitySchema] = []
    seen: set[str] = set()

    block = _section_lines(text, _ELIG_HEADER)
    if block:
        # Numbered/bulleted items may wrap onto continuation lines.
        items: list[str] = []
        for raw in block:
            if _BULLET.match(raw) or not items:
                items.append(_BULLET.sub("", raw.strip()).strip())
            else:
                items[-1] = f"{items[-1]} {raw.strip()}"
        for item in items:
            requirement = re.sub(r"\s+", " ", item).strip(" -:*.")
            if len(requirement) < 8:
                continue
            key = requirement.lower()[:80]
            if key in seen:
                continue
            seen.add(key)
            category = _classify_eligibility(requirement)
            out.append(
                EligibilitySchema(
                    category=category,  # type: ignore[arg-type]
                    requirement=requirement[:400],
                    status="needs_input",
                    needs=_NEEDS.get(category, ""),
                )
            )
            if len(out) >= 14:
                break
        return out

    for category, pattern in _ELIG_PATTERNS:
        for m in pattern.finditer(text):
            requirement = re.sub(r"\s+", " ", m.group(0)).strip(" -:*")
            if len(requirement) < 8:
                continue
            key = requirement.lower()[:80]
            if key in seen:
                continue
            seen.add(key)
            out.append(
                EligibilitySchema(
                    category=category,  # type: ignore[arg-type]
                    requirement=requirement[:400],
                    status="needs_input",
                    needs=_NEEDS.get(category, ""),
                )
            )
            if len(out) >= 12:
                return out
    return out


# --- Fees ------------------------------------------------------------------
_AMOUNT = re.compile(
    r"(?:₹|Rs\.?|INR)\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)(?:\s*/-)?", re.I
)
_FEE_LINE = re.compile(
    r"[^\n]*\b(fee|fees|charges?|application\s+fee|examination\s+fee|processing\s+charge)\b[^\n]*",
    re.I,
)
_EXEMPT = re.compile(
    r"\b(exempt\w*|no\s+fee|nil\s+fee|free\s+of\s+(?:cost|charge)|waiv\w+)\b", re.I
)
# A stronger signal than _EXEMPT: the line says the amount itself is zero.
_NO_FEE = re.compile(
    r"\b(no\s+fee|nil\s+fee|free\s+of\s+(?:cost|charge)|fee\s+is\s+waived)\b", re.I
)


def parse_fees(text: str) -> list[FeeSchema]:
    """Collect fee lines verbatim. Amounts are never rounded or converted.

    A line that states an exemption but no figure ("No fee is payable by
    SC/ST candidates") still matters, so we record it with an explicit
    ``"No fee"`` amount rather than an empty one, which the UI would otherwise
    render as an unknown value.
    """
    out: list[FeeSchema] = []
    seen: set[str] = set()
    for m in _FEE_LINE.finditer(text or ""):
        line = re.sub(r"\s+", " ", m.group(0)).strip(" -:*")
        if len(line) < 6 or line.lower() in seen:
            continue
        amounts = _AMOUNT.findall(line)
        exempt = _EXEMPT.search(line)
        if not amounts and not exempt:
            continue
        seen.add(line.lower())
        if amounts:
            amount = f"Rs. {amounts[0]}"
        elif _NO_FEE.search(line):
            amount = "No fee"
        else:
            amount = ""
        out.append(
            FeeSchema(
                label=line[:200],
                amount=amount,
                exemptions=(line[:200] if exempt else ""),
            )
        )
        if len(out) >= 8:
            break
    return out


def parse_financial_amounts(text: str) -> list[str]:
    """Every currency amount, kept verbatim. We never invent or round these."""
    out: list[str] = []
    seen: set[str] = set()
    for m in _AMOUNT.finditer(text or ""):
        value = re.sub(r"\s+", " ", m.group(0)).strip()
        if value.lower() not in seen:
            seen.add(value.lower())
            out.append(value)
        if len(out) >= 20:
            break
    return out


# --- Documents -------------------------------------------------------------
_DOC_HEADER = re.compile(
    r"^\s*(?:required\s+documents?|documents?\s+(?:required|needed|to\s+be\s+(?:attached|submitted)|to\s+keep\s+ready|checklist)"
    r"|enclosures?|attachments?|documents?)\s*[:\-]?\s*$",
    re.I,
)
# Notices rarely use a tidy heading. This catches the common real-world shape:
# a short line that mentions documents/enclosures and ends with a colon, e.g.
# "Documents that may support your response:".
_DOC_HEADER_LOOSE = re.compile(
    r"^\s*[^\n]{0,80}\b(?:documents?|enclosures?|attachments?|papers|certificates?)\b[^\n]{0,60}:\s*$",
    re.I,
)


def _is_doc_header(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > 140:
        return False
    return bool(_DOC_HEADER.match(s) or _DOC_HEADER_LOOSE.match(s))


_CONDITIONAL = re.compile(r"\b(if\s+applicable|where\s+applicable|if\s+any|conditional|only\s+for)\b", re.I)
_FORMAT_HINT = re.compile(r"\b(PDF|JPE?G|PNG|scanned\s+copy|self-?attested|photocopy|original)\b", re.I)
_SIZE_HINT = re.compile(r"\b(?:max(?:imum)?\s+)?(\d+\s?(?:KB|MB))\b", re.I)


def parse_documents(text: str) -> list[RequiredDocument]:
    """Collect documents listed under a "documents required" style heading."""
    lines = [ln.rstrip() for ln in (text or "").splitlines()]
    out: list[RequiredDocument] = []
    seen: set[str] = set()

    for i, line in enumerate(lines):
        if not _is_doc_header(line):
            continue
        blanks = 0
        for follow in lines[i + 1 : i + 26]:
            s = follow.strip()
            if not s:
                blanks += 1
                if blanks >= 2 and out:
                    break
                continue
            # A new section heading ends the list.
            if s.endswith(":") or s.startswith("***") or s.isupper() and len(s) > 24:
                break
            if not _BULLET.match(follow) and out:
                break
            item = _BULLET.sub("", s).strip()
            if len(item) < 3:
                continue
            name = re.split(r"\s{2,}|\s*[–—]\s*|\s*\(", item)[0].strip(" .;,")
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            fmt = _FORMAT_HINT.search(item)
            size = _SIZE_HINT.search(item)
            conditional = bool(_CONDITIONAL.search(item))
            out.append(
                RequiredDocument(
                    name=name[:160],
                    reason=(item[len(name):].strip(" .;,()-") or "")[:240],
                    required=not conditional,
                    requirement="conditional" if conditional else "yes",
                    stage="application",
                    doc_format=(fmt.group(0) if fmt else ""),
                    size_limit=(size.group(1) if size else ""),
                    trust="FROM_NOTICE",
                    source_note="Listed in your notice",
                )
            )
            if len(out) >= 15:
                break
        if out:
            break
    return out


# --- Procedure -------------------------------------------------------------
_PROC_HEADER = re.compile(
    r"^\s*(?:how\s+to\s+(?:apply|respond)|application\s+(?:procedure|process)|procedure"
    r"|steps?\s+to\s+(?:apply|follow|respond)|mode\s+of\s+(?:application|response)"
    r"|how\s+to\s+submit|response\s+procedure)\s*[:\-]?\s*$",
    re.I,
)


def parse_procedure(text: str) -> list[ProcedureStepSchema]:
    lines = [ln.rstrip() for ln in (text or "").splitlines()]
    out: list[ProcedureStepSchema] = []
    for i, line in enumerate(lines):
        if not _PROC_HEADER.match(line.strip()):
            continue
        blanks = 0
        for follow in lines[i + 1 : i + 26]:
            s = follow.strip()
            if not s:
                blanks += 1
                if blanks >= 2 and out:
                    break
                continue
            if s.endswith(":") or s.startswith("***"):
                break
            if not _BULLET.match(follow) and out:
                break
            step = _BULLET.sub("", s).strip()
            if len(step) < 5:
                continue
            out.append(ProcedureStepSchema(order=len(out) + 1, text=step[:400]))
            if len(out) >= 15:
                break
        if out:
            break
    return out


# --- Official channels -----------------------------------------------------
_URL = re.compile(r"\bhttps?://[^\s<>\"')\]]+|\bwww\.[^\s<>\"')\]]+", re.I)
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE = re.compile(r"\b(?:\+91[-\s]?)?(?:1800[-\s]?\d{3}[-\s]?\d{3,4}|0\d{2,4}[-\s]?\d{6,8}|\d{10})\b")
_PORTAL_WORD = re.compile(
    # The host part must be greedy across sub-domains, otherwise
    # "demopsc.example.gov" is captured as just "example.gov".
    r"\b((?:[a-z0-9-]+\.)+(?:gov\.in|nic\.in|gov|org\.in|ac\.in|edu\.in|co\.in|org|com))\b",
    re.I,
)


def _domain_of(url: str) -> str:
    url = re.sub(r"^https?://", "", (url or "").strip(), flags=re.I)
    return url.split("/")[0].lower().removeprefix("www.")


def parse_channels(text: str) -> list[OfficialChannelSchema]:
    """Portals, emails, phones and addresses that the notice itself mentions.

    These are only ever taken from the document — we never guess a portal URL.
    """
    text = text or ""
    out: list[OfficialChannelSchema] = []
    seen: set[str] = set()

    for m in _URL.finditer(text):
        raw = m.group(0).rstrip(".,;)")
        url = raw if raw.lower().startswith("http") else f"https://{raw}"
        key = url.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(
            OfficialChannelSchema(
                label=_domain_of(url),
                kind="portal",
                value=raw,
                url=url,
                note="Mentioned in your notice",
            )
        )

    if not out:
        for m in _PORTAL_WORD.finditer(text):
            host = m.group(1).lower()
            if host in seen:
                continue
            seen.add(host)
            out.append(
                OfficialChannelSchema(
                    label=host,
                    kind="website",
                    value=host,
                    url=f"https://{host}",
                    note="Mentioned in your notice",
                )
            )

    for m in _EMAIL.finditer(text):
        addr = m.group(0)
        if addr.lower() in seen:
            continue
        seen.add(addr.lower())
        out.append(
            OfficialChannelSchema(
                label="Email", kind="email", value=addr,
                note="Mentioned in your notice",
            )
        )

    for m in _PHONE.finditer(text):
        num = m.group(0)
        if num in seen:
            continue
        seen.add(num)
        out.append(
            OfficialChannelSchema(
                label="Phone", kind="phone", value=num,
                note="Mentioned in your notice",
            )
        )
        if sum(1 for c in out if c.kind == "phone") >= 2:
            break

    return out[:10]


def parse_mentions(text: str) -> dict[str, list[str]]:
    """Laws, rules, forms and portals referenced by the document."""
    text = text or ""

    def uniq(items: list[str], limit: int = 10) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in items:
            v = re.sub(r"\s+", " ", item).strip(" .,;:")
            if v and v.lower() not in seen:
                seen.add(v.lower())
                out.append(v)
            if len(out) >= limit:
                break
        return out

    laws = re.findall(
        r"\b(?:the\s+)?[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,5}\s+Act,?\s+\d{4}\b", text
    )
    rules = re.findall(
        r"\b(?:Rule|Section|Sub-?section|Clause|Regulation|Article)\s+\d+[A-Za-z]?(?:\(\d+\))?"
        r"(?:\s+of\s+[^,.\n]{3,60})?",
        text,
    )
    forms = re.findall(r"\bForm\s+(?:No\.?\s*)?[A-Z0-9][A-Za-z0-9\-/]{0,12}\b", text)
    portals = [m.group(1) for m in _PORTAL_WORD.finditer(text)]

    return {
        "mentioned_laws": uniq(laws),
        "mentioned_rules": uniq(rules, 12),
        "mentioned_forms": uniq(forms),
        "mentioned_portals": uniq(portals),
    }


def parse_contact(text: str) -> dict[str, str]:
    contact: dict[str, str] = {}
    email = _EMAIL.search(text or "")
    if email:
        contact["email"] = email.group(0)
    phone = _PHONE.search(text or "")
    if phone:
        contact["phone"] = phone.group(0)
    m = re.search(r"(?:office\s+address|address)\s*[:\-]\s*([^\n]{6,200})", text or "", re.I)
    if m:
        contact["address"] = re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r"(?:helpline|help\s?desk)\s*[:\-]\s*([^\n]{4,120})", text or "", re.I)
    if m:
        contact["helpline"] = re.sub(r"\s+", " ", m.group(1)).strip()
    return contact
