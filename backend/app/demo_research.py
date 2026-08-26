"""Curated demo research.

Every entry here is **illustrative, not retrieved**. It exists so the research
screen can be demonstrated when live web search is unavailable, and it is
loaded with ``authority_level="DEMO"`` and surfaced with ``is_live=False`` and
``mode="demo"``, which the UI renders as an explicit statement that no live web
search was performed.

Two honesty rules shape the data below and must not be relaxed:

1. **No fabricated URLs.** The ``domain`` values are the fictional
   ``*.example.gov`` hosts that appear inside the synthetic demo notices
   themselves. No entry claims a retrieved deep link, so ``url`` is empty and
   the UI has nothing to present as a real fetched page.
2. **Conflicts are shown, never resolved.** Where a demo entry disagrees with
   its notice, both values are displayed and the citizen is told to verify.
"""

from __future__ import annotations

# The disclaimer the API attaches to every demo research payload.
DEMO_RESEARCH_MESSAGE = (
    "No live web search was performed. Live AI web research is implemented but "
    "is not available in this environment, so the sources below are illustrative "
    "examples that ship with the demo notice — not pages retrieved from the "
    "internet. They are marked \"Demo source\" throughout."
)

DEMO_RESEARCH: dict[str, dict] = {
    # --- Income tax response ------------------------------------------------
    "tax-143-1": {
        "summary": (
            "The demo sources describe how an intimation under a self-assessment "
            "review is normally handled: you either agree with the computation or "
            "file a written explanation with supporting proof, within the period "
            "stated on the intimation itself."
        ),
        "queries": [
            {
                "query": "intimation under section 143(1) how to respond timeline",
                "purpose": "Check how long a citizen normally has to respond to this kind of intimation.",
            },
            {
                "query": "documents required to support interest income mismatch reply",
                "purpose": "Check which proofs are normally accepted for an interest income mismatch.",
            },
        ],
        "sources": [
            {
                "claim": "How long you have to respond",
                "title": "Responding to an assessment intimation (illustrative demo source)",
                "domain": "demoincometax.example.gov",
                "source_type": "government department",
                "evidence": (
                    "An intimation of this kind states its own response period. "
                    "The period runs from the date you receive the intimation, not "
                    "from the date printed on it."
                ),
                "why_it_matters": "It tells you which date your clock actually starts from.",
                "supports_notice": True,
            },
            {
                "claim": "What proof is accepted for an interest mismatch",
                "title": "Supporting documents for income mismatch replies (illustrative demo source)",
                "domain": "demoincometax.example.gov",
                "source_type": "government department",
                "evidence": (
                    "A bank interest certificate for the relevant year and the "
                    "corresponding salary statement are the usual supporting proofs."
                ),
                "why_it_matters": "These are the two documents your notice already asks for.",
                "supports_notice": True,
            },
            {
                "claim": "Where a reply is filed",
                "title": "Filing a reply to an intimation (illustrative demo source)",
                "domain": "demoincometax.example.gov",
                "source_type": "public-service portal",
                "evidence": (
                    "A reply is filed through the official portal account of the "
                    "taxpayer, or delivered to the assessing office named on the intimation."
                ),
                "why_it_matters": "NoticeMate cannot file this for you — you complete it here.",
                "supports_notice": None,
            },
        ],
        "unverified": [
            "Whether an extension of the response period can be requested in your case.",
        ],
        "conflicts": [],
    },
    # --- EPF KYC ------------------------------------------------------------
    "epf-kyc": {
        "summary": (
            "The demo sources describe the usual KYC correction route: the member "
            "submits the correction through their own portal account, and bank "
            "details are confirmed with a cancelled cheque or passbook copy."
        ),
        "queries": [
            {
                "query": "provident fund KYC bank detail correction process member portal",
                "purpose": "Check how a member normally corrects bank details on a PF account.",
            },
            {
                "query": "documents accepted to verify bank account for provident fund KYC",
                "purpose": "Check which bank proof is accepted.",
            },
        ],
        "sources": [
            {
                "claim": "Who submits the correction",
                "title": "Member KYC corrections (illustrative demo source)",
                "domain": "demoepf.example.gov",
                "source_type": "government department",
                "evidence": (
                    "KYC corrections are submitted by the member through their own "
                    "portal account and are then approved by the employer."
                ),
                "why_it_matters": "Two parties are involved, so allow time for the employer step.",
                "supports_notice": True,
            },
            {
                "claim": "Accepted bank proof",
                "title": "Bank account verification for PF members (illustrative demo source)",
                "domain": "demoepf.example.gov",
                "source_type": "government department",
                "evidence": (
                    "A cancelled cheque or the first page of a bank passbook showing "
                    "the account number, name and IFSC is accepted."
                ),
                "why_it_matters": "Matches the document your notice asks for.",
                "supports_notice": True,
            },
        ],
        "unverified": [
            "Whether your specific claim is on hold for any additional reason.",
        ],
        "conflicts": [],
    },
    # --- Municipal address verification ------------------------------------
    "muni-address": {
        "summary": (
            "The demo sources describe address verification for municipal records: "
            "one recent proof of address plus a completed verification form, "
            "submitted at the ward office or through the municipal portal."
        ),
        "queries": [
            {
                "query": "municipal property records address verification accepted proof",
                "purpose": "Check which address proofs are normally accepted.",
            },
            {
                "query": "ward office address verification form submission process",
                "purpose": "Check where the form is submitted.",
            },
        ],
        "sources": [
            {
                "claim": "Accepted proof of address",
                "title": "Address proof for municipal records (illustrative demo source)",
                "domain": "demomunicipal.example.gov",
                "source_type": "government department",
                "evidence": (
                    "A recent utility bill, the latest property tax receipt, or a "
                    "registered rent agreement is accepted as proof of current address."
                ),
                "why_it_matters": "You only need one of these, not all of them.",
                "supports_notice": True,
            },
            {
                "claim": "Where the form is submitted",
                "title": "Ward office submissions (illustrative demo source)",
                "domain": "demomunicipal.example.gov",
                "source_type": "public-service portal",
                "evidence": (
                    "The completed verification form is submitted at the ward office "
                    "named on the notice, or uploaded through the municipal portal account."
                ),
                "why_it_matters": "This is the official channel you use yourself.",
                "supports_notice": None,
            },
        ],
        "unverified": [
            "Whether your ward office accepts submissions without a prior appointment.",
        ],
        "conflicts": [],
    },
    # --- Recruitment --------------------------------------------------------
    "recruit-jr-assistant": {
        "summary": (
            "The demo sources broadly agree with the advertisement on eligibility, "
            "fees and documents. One entry states a different last date to apply, "
            "which NoticeMate shows as a conflict rather than picking a winner."
        ),
        "queries": [
            {
                "query": "Demo State Public Service Commission junior assistant recruitment eligibility",
                "purpose": "Check the age and qualification rules for this kind of post.",
            },
            {
                "query": "junior assistant recruitment application fee exemption categories",
                "purpose": "Check who is exempt from the application fee.",
            },
            {
                "query": "typing test qualifying stage junior assistant selection process",
                "purpose": "Check whether the typing test is qualifying or scored.",
            },
            {
                "query": "Demo State Public Service Commission last date to apply junior assistant",
                "purpose": "Confirm the last date to apply.",
            },
        ],
        "sources": [
            {
                "claim": "Age limit and relaxation",
                "title": "Age limits for clerical posts (illustrative demo source)",
                "domain": "demopsc.example.gov",
                "source_type": "government department",
                "evidence": (
                    "For clerical grade posts the age band is 18 to 32 years, with "
                    "5 years' relaxation for SC/ST and 3 years for OBC candidates."
                ),
                "why_it_matters": "Confirms the age rule in your advertisement.",
                "supports_notice": True,
            },
            {
                "claim": "Application fee and exemption",
                "title": "Application fees for commission recruitments (illustrative demo source)",
                "domain": "demopsc.example.gov",
                "source_type": "government department",
                "evidence": (
                    "The standard fee for unreserved and OBC candidates is Rs. 500, "
                    "reduced to Rs. 250 for SC/ST/EWS candidates. Fees are not refundable."
                ),
                "why_it_matters": "Tells you which fee applies to you before you pay.",
                "supports_notice": True,
            },
            {
                "claim": "Whether the typing test is qualifying",
                "title": "Selection stages for junior assistant posts (illustrative demo source)",
                "domain": "demopsc.example.gov",
                "source_type": "government department",
                "evidence": (
                    "The typing test is qualifying in nature; marks from it are not "
                    "added to the written examination score."
                ),
                "why_it_matters": "You must pass it, but a higher speed earns no extra marks.",
                "supports_notice": True,
            },
            {
                "claim": "Last date to apply",
                "title": "Recruitment calendar (illustrative demo source)",
                "domain": "demopsc.example.gov",
                "source_type": "government department",
                "evidence": (
                    "The illustrative recruitment calendar for this cycle shows the "
                    "online application window closing on 28 September 2026."
                ),
                "why_it_matters": "This is earlier than the date printed on your advertisement.",
                "supports_notice": False,
                "conflict": True,
                "conflict_detail": (
                    "The advertisement says 30 September 2026; this demo source says "
                    "28 September 2026."
                ),
            },
        ],
        "unverified": [
            "The examination centre you would be allotted.",
            "Whether the vacancy count has been revised since the advertisement.",
        ],
        "conflicts": [
            {
                "topic": "Last date to apply",
                "notice_says": "30 September 2026",
                "source_says": "28 September 2026",
                "source_title": "Recruitment calendar (illustrative demo source)",
                "domain": "demopsc.example.gov",
            }
        ],
    },
    # --- Scholarship --------------------------------------------------------
    "scholarship-merit": {
        "summary": (
            "The demo sources agree with the notice on the income ceiling, the "
            "no-fee rule and the need for institutional verification, and add that "
            "the scholarship cannot be combined with another government scholarship "
            "for the same year."
        ),
        "queries": [
            {
                "query": "state merit scholarship income ceiling eligibility undergraduate",
                "purpose": "Check the family income limit for this kind of scholarship.",
            },
            {
                "query": "merit scholarship institutional verification bonafide certificate requirement",
                "purpose": "Check what the institution has to verify.",
            },
            {
                "query": "can a student hold two government scholarships same academic year",
                "purpose": "Check whether the scholarship can be combined with another.",
            },
        ],
        "sources": [
            {
                "claim": "Family income ceiling",
                "title": "Income criteria for merit scholarships (illustrative demo source)",
                "domain": "demodhe.example.gov",
                "source_type": "government department",
                "evidence": (
                    "Annual family income from all sources must not exceed "
                    "Rs. 2,50,000, certified by the competent revenue authority."
                ),
                "why_it_matters": "Confirms both the limit and who must certify it.",
                "supports_notice": True,
            },
            {
                "claim": "No application fee",
                "title": "Scholarship application charges (illustrative demo source)",
                "domain": "demoscholarship.example.gov",
                "source_type": "public-service portal",
                "evidence": (
                    "No fee is charged for scholarship applications on the official "
                    "portal. Applicants should not pay any agent."
                ),
                "why_it_matters": "Anyone asking you for money for this is not official.",
                "supports_notice": True,
            },
            {
                "claim": "Institutional verification",
                "title": "Role of the institution (illustrative demo source)",
                "domain": "demodhe.example.gov",
                "source_type": "government department",
                "evidence": (
                    "The institution must verify enrolment and the bonafide "
                    "certificate before the application moves to scrutiny."
                ),
                "why_it_matters": "Your application can stall at the college, so follow up there.",
                "supports_notice": True,
            },
            {
                "claim": "Holding two scholarships at once",
                "title": "Duplicate benefit rule (illustrative demo source)",
                "domain": "demodhe.example.gov",
                "source_type": "government department",
                "evidence": (
                    "A student may not hold two government scholarships for the same "
                    "academic year. An existing award must be surrendered first."
                ),
                "why_it_matters": "Worth checking before you apply if you already hold one.",
                "supports_notice": True,
            },
        ],
        "unverified": [
            "The exact date the amount would be credited.",
            "Whether the merit cut-off changes between academic years.",
        ],
        "conflicts": [],
    },
}


def get_demo_research(demo_id: str | None) -> dict | None:
    if not demo_id:
        return None
    return DEMO_RESEARCH.get(demo_id)
