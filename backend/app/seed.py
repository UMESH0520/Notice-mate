"""Database initialisation helper / seed script.

The demo runs on-demand (the demo catalog is always available and each demo
notice is created fresh when selected), so no rows need pre-seeding for the
happy path. This script simply ensures the schema exists and prints the demo
catalog — handy for a quick sanity check.

Run with:  python -m app.seed
"""

from __future__ import annotations

from .database import init_db
from .demo_data import demo_summaries


def main() -> None:
    init_db()
    print("NoticeMate database initialised.")
    print("Available synthetic demo notices:")
    for d in demo_summaries():
        print(f"  - [{d['id']}] {d['title']} ({d['category']})")


if __name__ == "__main__":
    main()
