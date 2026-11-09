"""
CVBoost AI — Rate Limiting, Quotas & Request Limits
Uses slowapi (Starlette-compatible limiter) with fallback if not yet installed.
"""
from __future__ import annotations

from app.core.config import get_settings

settings = get_settings()

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.rate_limit_default],
        storage_uri=settings.redis_url or "memory://",
    )
except ImportError:
    class RateLimitExceeded(Exception):  # type: ignore[no-redef]
        pass

    def _rate_limit_exceeded_handler(request, exc):  # type: ignore[no-redef]
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})

    class Limiter:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    limiter = Limiter()

# ── Per-endpoint decorators (used as @limiter.limit("N/period")) ─────────────
AI_LIMIT = settings.rate_limit_ai
UPLOAD_LIMIT = settings.rate_limit_upload
CONTACT_LIMIT = settings.rate_limit_contact
DEFAULT_LIMIT = settings.rate_limit_default

# ── Request body size limit (enforced in middleware) ─────────────────────────
MAX_REQUEST_BODY_BYTES = 10 * 1024 * 1024  # 10 MB outer limit
