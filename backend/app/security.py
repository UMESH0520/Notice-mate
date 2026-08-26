"""Security helpers.

Covers the prototype's realistic threat surface:
- untrusted uploaded files (size / extension / basic content sniffing)
- filename sanitisation (path-traversal, control chars)
- prompt-injection defence for text sent to the LLM

Uploaded notices are treated as **untrusted input**. We never execute them and
never let instructions inside a notice change how the model behaves.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import PurePath

from .config import settings

# Minimal magic-byte signatures for the formats we accept.
_MAGIC = {
    b"%PDF-": "pdf",
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpg",
    b"RIFF": "webp",  # RIFF....WEBP
}


class UploadError(ValueError):
    """Raised when an uploaded file fails validation."""


def sanitize_filename(filename: str | None) -> str:
    """Return a safe, path-free filename.

    Strips directories, control chars and unsafe characters; guarantees a
    non-empty result with a reasonable length.
    """
    if not filename:
        return "upload.bin"
    # Drop any directory component (defends against path traversal).
    name = PurePath(filename.replace("\\", "/")).name
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if c.isprintable() and c not in '<>:"/\\|?*')
    name = name.strip().strip(".")
    name = re.sub(r"\s+", "_", name)
    if not name:
        name = "upload.bin"
    return name[:120]


def validate_extension(filename: str) -> str:
    """Validate the file extension against the allow-list; return the ext."""
    ext = PurePath(filename).suffix.lower()
    if ext not in settings.allowed_extensions:
        allowed = ", ".join(sorted(settings.allowed_extensions))
        raise UploadError(
            f"This file type isn't supported. Allowed types: {allowed}."
        )
    return ext


def validate_size(size: int) -> None:
    if size <= 0:
        raise UploadError("The file appears to be empty.")
    if size > settings.MAX_UPLOAD_BYTES:
        mb = settings.MAX_UPLOAD_BYTES / (1024 * 1024)
        raise UploadError(f"The file is too large. Maximum size is {mb:.0f} MB.")


def sniff_content_type(head: bytes) -> str | None:
    """Best-effort magic-byte sniff. Returns a short type label or None."""
    for sig, label in _MAGIC.items():
        if head.startswith(sig):
            if label == "webp" and b"WEBP" not in head[:16]:
                continue
            return label
    # Heuristic: mostly-printable bytes look like text.
    sample = head[:512]
    if sample and sum(1 for b in sample if b in (9, 10, 13) or 32 <= b < 127) / len(
        sample
    ) > 0.85:
        return "txt"
    return None


# --- Prompt-injection defence ---------------------------------------------
_INJECTION_PATTERNS = [
    re.compile(r"ignore (all|any|previous|the above).{0,40}instructions", re.I),
    re.compile(r"disregard (all|any|previous|the above)", re.I),
    re.compile(r"you are now\b", re.I),
    re.compile(r"system prompt", re.I),
    re.compile(r"reveal.{0,20}(prompt|instructions|system)", re.I),
    re.compile(r"\bact as\b", re.I),
    re.compile(r"forget (everything|all|previous)", re.I),
    re.compile(r"new instructions?:", re.I),
]


def detect_injection(text: str) -> list[str]:
    """Return snippets that look like prompt-injection attempts."""
    hits: list[str] = []
    for pat in _INJECTION_PATTERNS:
        for m in pat.finditer(text or ""):
            snippet = text[max(0, m.start() - 10) : m.end() + 10].strip()
            hits.append(snippet[:80])
    return hits[:10]


def neutralize_for_prompt(text: str, limit: int = 16000) -> str:
    """Prepare untrusted notice text for inclusion in an LLM prompt.

    We do not silently delete content (that could hide real notice text), but
    we defang the classic injection triggers so they read as inert data, and we
    cap the length.
    """
    text = (text or "")[:limit]
    # Insert a zero-width space to break trigger phrases without losing meaning.
    text = re.sub(
        r"(?i)\b(ignore|disregard|forget)\b(\s+)(all|any|previous|everything|the)",
        r"\1​\2\3",
        text,
    )
    return text
