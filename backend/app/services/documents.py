"""Synthetic document validation.

We validate format, size, readability and a lightweight "does this look like the
expected document type" heuristic. We deliberately use cautious language — a
document "appears to match", never "is government-approved / legally valid".
"""

from __future__ import annotations

from pathlib import PurePath

from ..security import UploadError, sniff_content_type, validate_extension, validate_size

# Keywords that hint a filename matches an expected document type.
_TYPE_HINTS = {
    "address": ["address", "bill", "electric", "water", "utility", "passbook"],
    "identity": ["id", "identity", "passport", "license", "licence", "pan", "aadhaar"],
    "income": ["form16", "form-16", "salary", "income", "interest", "certificate"],
    "tax": ["tax", "property", "receipt", "challan"],
    "form": ["form", "declaration", "application", "response", "letter"],
    "bank": ["bank", "cheque", "passbook", "statement"],
}


def validate_document(
    expected_name: str,
    filename: str,
    content: bytes,
) -> dict:
    """Validate an uploaded document against the expected type.

    Returns a structured validation report (never raises for a *soft* mismatch;
    only hard failures such as bad type/size raise ``UploadError``).
    """
    checks: list[dict] = []

    ext = validate_extension(filename)
    checks.append({"label": "Supported file type", "ok": True, "detail": ext})

    validate_size(len(content))
    checks.append(
        {"label": "File size within limit", "ok": True, "detail": f"{len(content)} bytes"}
    )

    sniffed = sniff_content_type(content[:64])
    readable = sniffed is not None
    checks.append(
        {
            "label": "File appears readable",
            "ok": readable,
            "detail": sniffed or "unknown format",
        }
    )

    match = _looks_like_expected(expected_name, filename)
    checks.append(
        {
            "label": "Appears to match the requested document",
            "ok": match,
            "detail": "based on the file name" if match else "could not confirm from the file name",
        }
    )

    ok = all(c["ok"] for c in checks[:2]) and readable
    if match and ok:
        message = "Document appears to match the requested type."
    elif ok:
        message = (
            "File received. We could not confirm it matches the requested document "
            "from its name — please double-check it is the right file."
        )
    else:
        message = "We couldn't read this file properly. Please try another file."

    return {
        "ok": ok,
        "matched": match,
        "message": message,
        "checks": checks,
        "note": "This is a synthetic check for the demo; it does not certify legal validity.",
    }


def _looks_like_expected(expected_name: str, filename: str) -> bool:
    stem = PurePath(filename).stem.lower().replace("_", " ").replace("-", " ")
    exp = expected_name.lower()

    # Direct token overlap between expected doc name and the filename.
    exp_tokens = {t for t in exp.replace("/", " ").split() if len(t) > 3}
    if any(tok in stem for tok in exp_tokens):
        return True

    # Category hint overlap.
    for _cat, hints in _TYPE_HINTS.items():
        if any(h in exp for h in hints) and any(h in stem for h in hints):
            return True
    return False
