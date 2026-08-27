"""Application configuration.

All settings are loaded from environment variables (optionally via a ``.env``
file).  Crucially, the OpenAI API key is **optional**: when it is missing the
application still runs and falls back to a deterministic offline "Demo
analysis".  This keeps the demo reliable for a judge with zero configuration.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository layout anchors -------------------------------------------------
# config.py -> app -> backend -> notice-mate (repo root)
BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = REPO_ROOT / "frontend"
DEMO_DIR = REPO_ROOT / "demo"
UPLOAD_DIR = BACKEND_DIR / "uploads"


class Settings(BaseSettings):
    """Runtime configuration for the NoticeMate backend."""

    APP_NAME: str = "NoticeMate"
    VERSION: str = "2.0.0"
    # ``APP_ENV`` is the documented public name; ``ENVIRONMENT`` is kept as an
    # alias so older configs keep working.
    APP_ENV: str = Field("development", description="deployment environment")
    ENVIRONMENT: str | None = Field(
        default=None, description="deprecated alias for APP_ENV"
    )

    # Database (SQLite for the prototype; the model layer is written so it can
    # migrate to PostgreSQL by only changing this URL).
    DATABASE_URL: str = Field(
        default=f"sqlite:///{(BACKEND_DIR / 'noticemate.db').as_posix()}",
        description="SQLAlchemy database URL",
    )

    # OpenAI — OPTIONAL. Absence triggers the deterministic demo fallback.
    #
    # The model id lives in exactly one place (here). Application logic never
    # hard-codes a model name, so switching models is a config change only.
    OPENAI_API_KEY: str | None = Field(default=None, description="OpenAI API key")
    OPENAI_MODEL: str = Field("gpt-4o-mini", description="OpenAI model id")
    # Web research may use a different (search-capable) model. Falls back to
    # OPENAI_MODEL when unset.
    OPENAI_RESEARCH_MODEL: str | None = Field(
        default=None, description="model used for web research; defaults to OPENAI_MODEL"
    )
    # Reading a photographed notice needs a multimodal model. Defaults to
    # OPENAI_MODEL so a single setting is enough for the common case.
    OPENAI_VISION_MODEL_NAME: str | None = Field(
        default=None,
        alias="OPENAI_VISION_MODEL",
        description="multimodal model used to read notice images; defaults to OPENAI_MODEL",
    )
    OPENAI_TIMEOUT: float = Field(12.0, description="OpenAI request timeout (s)")
    OPENAI_RESEARCH_TIMEOUT: float = Field(
        90.0, description="OpenAI web-research timeout (s) — searching is slower"
    )

    # Web research -----------------------------------------------------------
    ENABLE_WEB_RESEARCH: bool = Field(
        True, description="Allow server-side web research via the OpenAI API"
    )
    RESEARCH_MAX_QUERIES: int = Field(
        5, description="Maximum research queries generated per notice"
    )

    # Uploads / security
    MAX_UPLOAD_SIZE_MB: int = Field(20, description="Max upload size in megabytes")
    ALLOWED_UPLOAD_EXTENSIONS: str = Field(
        default=".pdf,.png,.jpg,.jpeg,.txt,.webp",
        description="Comma-separated allowed upload extensions",
    )
    # PDF handling: pages are never silently dropped — we read up to this many
    # and tell the user when a document is longer.
    MAX_PDF_PAGES: int = Field(30, description="Maximum PDF pages read per upload")

    # CORS — same-origin by default (frontend is served by this app), but a
    # comma-separated list can be supplied for split deployments.
    CORS_ORIGINS: str = Field("", description="Comma-separated allowed CORS origins")

    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Convenience -----------------------------------------------------------
    @property
    def environment(self) -> str:
        """Effective environment name (``ENVIRONMENT`` overrides ``APP_ENV``)."""
        return (self.ENVIRONMENT or self.APP_ENV or "development").strip()

    @property
    def MAX_UPLOAD_BYTES(self) -> int:
        return max(1, int(self.MAX_UPLOAD_SIZE_MB)) * 1024 * 1024

    @property
    def research_model(self) -> str:
        return (self.OPENAI_RESEARCH_MODEL or self.OPENAI_MODEL).strip()

    @property
    def OPENAI_VISION_MODEL(self) -> str:
        return (self.OPENAI_VISION_MODEL_NAME or self.OPENAI_MODEL).strip()

    @property
    def allowed_extensions(self) -> set[str]:
        return {
            e.strip().lower()
            for e in self.ALLOWED_UPLOAD_EXTENSIONS.split(",")
            if e.strip()
        }

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def ai_enabled(self) -> bool:
        """True only when a non-placeholder API key is configured.

        Note this reports *configuration*, not reachability. A key can be
        configured and still fail (no billing quota, network down). The AI
        service tracks that separately so the UI can be honest about it.
        """
        key = (self.OPENAI_API_KEY or "").strip()
        if not key:
            return False
        if key.lower().startswith("sk-placeholder"):
            return False
        return key.startswith("sk-") or key.startswith("AQ.") or key.startswith("AIzaSy")

    @property
    def research_enabled(self) -> bool:
        """Web research needs both the feature flag and a usable API key."""
        return bool(self.ENABLE_WEB_RESEARCH) and self.ai_enabled


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
