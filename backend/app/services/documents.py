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


def _parse_size_bytes(size_str: str) -> int | None:
    """Parse strings like '200 KB', '2 MB', '500 KB max', '50 KB' into bytes."""
    if not size_str:
        return None
    import re
    m = re.search(r"(\d+(?:\.\d+)?)\s*(kb|mb|gb|bytes|b)\b", size_str.lower())
    if not m:
        return None
    val, unit = float(m.group(1)), m.group(2)
    if unit in ("kb", "k"):
        return int(val * 1024)
    elif unit in ("mb", "m"):
        return int(val * 1024 * 1024)
    elif unit in ("gb", "g"):
        return int(val * 1024 * 1024 * 1024)
    return int(val)


def validate_document(
    expected_name: str,
    filename: str,
    content: bytes,
    expected_format: str = "",
    expected_size_limit: str = "",
) -> dict:
    """Validate an uploaded document against the expected type, format and portal size limits.

    Returns a structured validation report (never raises for a *soft* mismatch;
    only hard failures such as bad type/size raise ``UploadError``).
    """
    checks: list[dict] = []

    ext = validate_extension(filename)
    checks.append({"label": "Supported file type", "ok": True, "detail": ext})

    # Hard security upper bound
    validate_size(len(content))

    # Check against portal specific size limit if defined
    max_bytes = _parse_size_bytes(expected_size_limit)
    size_kb = round(len(content) / 1024, 1)
    if max_bytes is not None:
        within_portal_limit = len(content) <= max_bytes
        checks.append(
            {
                "label": f"Official portal size limit ({expected_size_limit})",
                "ok": within_portal_limit,
                "detail": f"{size_kb} KB ({'Within limit' if within_portal_limit else 'Exceeds limit'})",
            }
        )
    else:
        checks.append(
            {"label": "File size within limit", "ok": True, "detail": f"{size_kb} KB"}
        )

    # Check against portal specific format if defined
    if expected_format:
        fmt_low = expected_format.lower()
        ext_clean = ext.lower().lstrip(".")
        matches_format = (
            ("pdf" in fmt_low and ext_clean == "pdf")
            or (any(img in fmt_low for img in ["jpg", "jpeg", "png", "photo", "image"]) and ext_clean in ["jpg", "jpeg", "png", "webp"])
            or ("doc" in fmt_low and ext_clean in ["doc", "docx", "pdf"])
        )
        checks.append(
            {
                "label": f"Prescribed format ({expected_format})",
                "ok": matches_format,
                "detail": f"{ext_clean.upper()} {'matches' if matches_format else 'differs from'} {expected_format}",
            }
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

    all_checks_ok = all(c["ok"] for c in checks)
    if match and all_checks_ok:
        message = "Document appears to match the requested type and meets all official portal format & size specifications."
    elif all_checks_ok:
        message = (
            "File received and meets size/format criteria. We could not confirm it matches the requested document "
            "from its name — please double-check it is the right file."
        )
    elif not all_checks_ok:
        failed_labels = [c["label"] for c in checks if not c["ok"]]
        message = f"File uploaded with potential issues: {', '.join(failed_labels)}. Please check portal guidelines."
    else:
        message = "We couldn't read this file properly. Please try another file."

    return {
        "ok": all_checks_ok,
        "matched": match,
        "message": message,
        "checks": checks,
        "note": "This is an automated verification check against official portal rules; it does not certify legal validity.",
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
