"""Turn an uploaded file into analysable content.

Three input modes (§7):

* **Text** — pasted text or a ``.txt`` upload. Used directly.
* **PDF** — every page is read and prefixed with ``--- Page N ---`` so page
  context survives into the analysis and can be cited in ``source_spans``.
  Later pages are never silently ignored: if a document exceeds the page cap we
  say exactly how many pages were read and how many were not.
* **Image** — handed to the multimodal model as image bytes. When no vision
  model is reachable we say so plainly rather than pretending we read it.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass, field

from ..config import settings

logger = logging.getLogger("noticemate.extraction")

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


@dataclass
class ExtractedInput:
    """What we managed to get out of an upload."""

    text: str = ""
    # Page images for the multimodal path: [(bytes, mime), ...]
    images: list[tuple[bytes, str]] = field(default_factory=list)
    # User-facing caveat, shown verbatim. Empty when there is nothing to say.
    note: str = ""
    page_count: int = 0
    pages_read: int = 0
    kind: str = "text"  # text | pdf | image | unknown

    @property
    def has_content(self) -> bool:
        return bool(self.text.strip() or self.images)


def extract(content: bytes, ext: str) -> ExtractedInput:
    """Extract text and/or images from an uploaded file."""
    ext = (ext or "").lower()

    if ext == ".txt":
        return ExtractedInput(text=_decode_text(content), kind="text")

    if ext == ".pdf":
        return _extract_pdf(content)

    if ext in IMAGE_EXTS:
        return _extract_image(content, ext)

    # Last resort: attempt a text decode so an unexpected-but-textual file works.
    text = _decode_text(content)
    if text.strip():
        return ExtractedInput(text=text, kind="text")
    return ExtractedInput(
        kind="unknown",
        note="We couldn't read this file. Please upload a PDF, an image, or paste the text.",
    )


def extract_text(content: bytes, ext: str) -> tuple[str, str | None]:
    """Backwards-compatible wrapper returning ``(text, note)``."""
    result = extract(content, ext)
    return result.text, (result.note or None)


# --- PDF -------------------------------------------------------------------
def _extract_pdf(content: bytes) -> ExtractedInput:
    try:
        import pypdf
    except Exception:
        return ExtractedInput(
            kind="pdf",
            note=(
                "We received your PDF but PDF reading is not available in this "
                "installation. You can paste the notice text instead, or try a demo notice."
            ),
        )

    try:
        reader = pypdf.PdfReader(io.BytesIO(content))
        if getattr(reader, "is_encrypted", False):
            try:
                reader.decrypt("")
            except Exception:
                return ExtractedInput(
                    kind="pdf",
                    note=(
                        "This PDF is password protected, so we could not read it. "
                        "Please upload an unprotected copy or paste the text."
                    ),
                )
        total = len(reader.pages)
    except Exception as exc:
        logger.info("pdf open failed: %s", exc)
        return ExtractedInput(
            kind="pdf",
            note=(
                "We received your PDF but could not open it. It may be damaged. "
                "You can paste the notice text instead."
            ),
        )

    cap = max(1, int(settings.MAX_PDF_PAGES))
    read = min(total, cap)
    chunks: list[str] = []
    empty_pages: list[int] = []

    for i in range(read):
        try:
            page_text = reader.pages[i].extract_text() or ""
        except Exception as exc:  # a single bad page must not lose the rest
            logger.info("pdf page %s failed: %s", i + 1, exc)
            page_text = ""
        if page_text.strip():
            chunks.append(f"--- Page {i + 1} ---\n{page_text.strip()}")
        else:
            empty_pages.append(i + 1)

    notes: list[str] = []
    if total > read:
        notes.append(
            f"This PDF has {total} pages. We read the first {read}; "
            f"pages {read + 1}–{total} were not analysed."
        )
    if empty_pages and chunks:
        listed = ", ".join(str(p) for p in empty_pages[:8])
        more = "…" if len(empty_pages) > 8 else ""
        notes.append(
            f"No text could be read from page(s) {listed}{more}. They may be "
            "scanned images — you can upload them as photos so they can be read."
        )

    if not chunks:
        return ExtractedInput(
            kind="pdf",
            page_count=total,
            pages_read=read,
            note=(
                f"We received your {total}-page PDF but found no readable text in it. "
                "It is probably a scan. Try uploading the pages as photos, or paste the text."
            ),
        )

    return ExtractedInput(
        text="\n\n".join(chunks),
        kind="pdf",
        page_count=total,
        pages_read=read,
        note=" ".join(notes),
    )


_OCR_INSTANCE = None


def get_ocr_engine():
    """Return a cached singleton instance of RapidOCR to avoid repeated ONNX initialization."""
    global _OCR_INSTANCE
    if _OCR_INSTANCE is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _OCR_INSTANCE = RapidOCR()
        except Exception as exc:
            logger.info("RapidOCR initialization failed: %s", exc)
            return None
    return _OCR_INSTANCE


# --- Images ----------------------------------------------------------------
def _extract_image(content: bytes, ext: str) -> ExtractedInput:
    """Extract real text from uploaded notice images using on-device RapidOCR."""
    mime = _MIME.get(ext, "image/png")
    extracted_text = ""
    try:
        ocr = get_ocr_engine()
        if ocr is not None:
            result, _ = ocr(content)
            if result:
                lines = [line[1] for line in result if line and len(line) > 1 and line[1].strip()]
                extracted_text = "\n".join(lines)
    except Exception as exc:
        logger.info("Local OCR extraction failed: %s", exc)

    return ExtractedInput(
        text=extracted_text,
        images=[(content, mime)],
        page_count=1,
        pages_read=1,
        kind="image",
    )


# --- Text ------------------------------------------------------------------
def _decode_text(content: bytes) -> str:
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")
