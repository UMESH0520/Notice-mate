"""Database engine and session management (SQLAlchemy 2.0).

SQLite is used for the prototype. The URL is the only thing that needs to
change to migrate to PostgreSQL, and no SQLite-specific SQL is used elsewhere.
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


# ``check_same_thread`` is a SQLite-only knob needed because FastAPI serves
# requests from a threadpool. It is ignored for other backends.
_connect_args = (
    {"check_same_thread": False, "timeout": 30.0}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create tables if they do not exist."""
    # Import models so they register with ``Base.metadata`` before create_all.
    from . import models  # noqa: F401

    if settings.DATABASE_URL.startswith("sqlite"):
        try:
            with engine.connect() as conn:
                conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
        except Exception:
            pass

    Base.metadata.create_all(bind=engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
