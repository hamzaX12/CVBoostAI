"""
CVBoost AI — Application Configuration
Pydantic Settings v2, validated at startup.
"""
from __future__ import annotations

import secrets
from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, EmailStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    app_env: Literal["development", "production", "test"] = "development"
    app_name: str = "CVBoost AI"
    app_tagline: str = "Enhance your CV for better job chances"
    app_version: str = "1.0.0"
    app_secret_key: str = secrets.token_hex(32)
    app_allowed_origins: list[str] | str = ["http://localhost:8501"]

    # ── Database ─────────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./cvboost.db"

    # ── JWT ──────────────────────────────────────────────────────────────
    jwt_secret_key: str = secrets.token_hex(64)
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7

    # ── LLM Provider ─────────────────────────────────────────────────────
    llm_provider: Literal["groq", "gemini"] = "groq"

    # ── Groq AI (Default / Fast & Free) ───────────────────────────────────
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    groq_temperature: float = 0.1
    groq_max_tokens: int = 8192

    # ── Gemini AI ────────────────────────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    gemini_max_tokens: int = 8192
    gemini_temperature: float = 0.2

    # ── Search ───────────────────────────────────────────────────────────
    tavily_api_key: str = ""
    search_provider: Literal["tavily", "duckduckgo"] = "tavily"
    search_max_results: int = 5

    # ── SMTP ─────────────────────────────────────────────────────────────
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = "CVBoost AI <noreply@cvboost.ai>"
    contact_recipient: str = "support@cvboost.ai"

    # ── Storage ──────────────────────────────────────────────────────────
    upload_dir: str = "./uploads"
    max_upload_bytes: int = 5_242_880  # 5 MB
    max_pdf_pages: int = 20

    # ── Rate Limits ──────────────────────────────────────────────────────
    rate_limit_default: str = "100/minute"
    rate_limit_ai: str = "10/minute"
    rate_limit_upload: str = "20/minute"
    rate_limit_contact: str = "5/minute"

    # ── Google OAuth ─────────────────────────────────────────────────────
    google_client_id: str = ""
    google_client_secret: str = ""

    # ── Redis ────────────────────────────────────────────────────────────
    redis_url: str = ""
    cache_ttl_seconds: int = 3600

    # ── Agent guardrails ─────────────────────────────────────────────────
    agent_max_tool_calls: int = 10
    agent_timeout_seconds: int = 60
    per_user_daily_token_quota: int = 500_000

    # ── Contact info (used in landing page and PDF) ──────────────────────
    contact_name: str = "CVBoost AI Team"
    contact_email: str = "support@cvboost.ai"
    contact_phone: str = "+1 (555) 019-2834"
    contact_location: str = "Global / Remote"
    contact_linkedin: str = "https://linkedin.com"

    # ── Security flags ───────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @field_validator("app_allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @model_validator(mode="after")
    def validate_required_secrets(self) -> "Settings":
        if self.app_env == "production":
            missing = []
            if self.llm_provider == "groq" and not self.groq_api_key:
                missing.append("GROQ_API_KEY")
            elif self.llm_provider == "gemini" and not self.gemini_api_key:
                missing.append("GEMINI_API_KEY")
            if not self.jwt_secret_key or len(self.jwt_secret_key) < 32:
                missing.append("JWT_SECRET_KEY (min 32 chars)")
            if not self.app_secret_key or len(self.app_secret_key) < 32:
                missing.append("APP_SECRET_KEY (min 32 chars)")
            if missing:
                raise ValueError(
                    f"Missing required secrets for production: {', '.join(missing)}"
                )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
