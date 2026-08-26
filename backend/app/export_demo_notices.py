"""Export the curated synthetic demo notices to ``demo/notices/*.txt``.

Keeps the plain-text sample files in sync with ``demo_data.py`` (the single
source of truth) so the upload path can be demonstrated with realistic files.

Run with:  python -m app.export_demo_notices
"""

from __future__ import annotations

from .config import DEMO_DIR
from .demo_data import DEMO_NOTICES


def main() -> None:
    target = DEMO_DIR / "notices"
    target.mkdir(parents=True, exist_ok=True)
    for demo in DEMO_NOTICES:
        path = target / f"{demo['id']}.txt"
        path.write_text(demo["raw_text"].strip() + "\n", encoding="utf-8")
        print(f"wrote {path}")
    print(f"{len(DEMO_NOTICES)} synthetic notices exported.")


if __name__ == "__main__":
    main()
