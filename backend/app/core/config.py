"""Backend configuration — loaded once at startup via pydantic-settings.

All required variables raise a clear ValueError at import time (not at first request)
so the process never starts in a misconfigured state.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(REPO_ROOT / ".env", ".env"), extra="ignore")

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = Field(alias="DATABASE_URL")

    # ── Clerk auth ────────────────────────────────────────────────────────────
    clerk_secret_key: str = Field(alias="CLERK_SECRET_KEY")
    clerk_publishable_key: str = Field(alias="NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
    clerk_jwt_issuer: str | None = Field(default=None, alias="CLERK_JWT_ISSUER")

    # ── NVIDIA Build API ──────────────────────────────────────────────────────
    nvidia_api_key: str = Field(alias="NVIDIA_API_KEY")
    nvidia_base_url: str = Field(default="https://integrate.api.nvidia.com/v1", alias="NVIDIA_BASE_URL")
    nvidia_text_model: str = Field(default="meta/llama-3.1-70b-instruct", alias="NVIDIA_TEXT_MODEL")
    nvidia_vision_model: str = Field(default="meta/llama-3.2-90b-vision-instruct", alias="NVIDIA_VISION_MODEL")
    nvidia_evaluation_model: str = Field(default="nvidia/nemotron-4-340b-instruct", alias="NVIDIA_EVALUATION_MODEL")
    nvidia_request_timeout: float = Field(default=25, alias="NVIDIA_REQUEST_TIMEOUT")
    nvidia_max_attempts: int = Field(default=2, alias="NVIDIA_MAX_ATTEMPTS")

    # ── UploadThing ───────────────────────────────────────────────────────────
    uploadthing_token: str | None = Field(default=None, alias="UPLOADTHING_TOKEN")
    uploadthing_secret: str | None = Field(default=None, alias="UPLOADTHING_SECRET")
    uploadthing_app_id: str | None = Field(default=None, alias="UPLOADTHING_APP_ID")

    # ── App / CORS ────────────────────────────────────────────────────────────
    app_url: str = Field(default="http://localhost:3000", alias="APP_URL")
    backend_cors_origins: str = Field(default="http://localhost:3000", alias="BACKEND_CORS_ORIGINS")

    # ── Local storage (dev fallback only) ─────────────────────────────────────
    upload_dir: str = Field(default="public/uploads", alias="UPLOAD_DIR")
    render_dir: str = Field(default="public/renders", alias="RENDER_DIR")

    # ── Render subprocess ─────────────────────────────────────────────────────
    node_binary: str = Field(default="node", alias="NODE_BINARY")

    # ── Auth bypass (NEVER set True in production) ────────────────────────────
    auth_bypass: bool = Field(default=False, alias="MOTIONFORGE_AUTH_BYPASS")

    # ── Startup validation ─────────────────────────────────────────────────────
    @model_validator(mode="after")
    def _validate_required_secrets(self) -> "Settings":
        """Fail fast with a clear message if critical env vars are missing or placeholder."""
        placeholder_db = "driver://user:pass@localhost/dbname"
        problems: list[str] = []

        if not self.database_url or self.database_url == placeholder_db:
            problems.append("DATABASE_URL — must be a valid PostgreSQL connection string")
        if not self.clerk_secret_key or self.clerk_secret_key in ("", "your_clerk_secret_key"):
            problems.append("CLERK_SECRET_KEY — Clerk backend secret (sk_test_... / sk_live_...)")
        if not self.nvidia_api_key or self.nvidia_api_key in ("", "your_nvidia_api_key"):
            problems.append("NVIDIA_API_KEY — NVIDIA Build API key")

        if problems:
            bullet_list = "\n  • ".join(problems)
            raise ValueError(
                f"\n\nMotionForge startup aborted — missing required environment variables:\n"
                f"  • {bullet_list}\n\n"
                "Set these in your .env file (local) or in Render/Vercel environment settings.\n"
                "See .env.example for the full list of required variables.\n"
            )

        if self.auth_bypass:
            import warnings
            warnings.warn(
                "MOTIONFORGE_AUTH_BYPASS=true — authentication is disabled. "
                "This must NEVER be used in production.",
                stacklevel=2,
            )

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
