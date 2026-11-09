"""
CVBoost AI — Structured Logging
Uses structlog with JSON output in production, human-readable in dev.
Falls back to stdlib logging if structlog is not installed.
"""
from __future__ import annotations

import logging
import sys
import uuid

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import get_settings


class _StdlibLoggerWrapper:
    """Wrapper around standard library Logger to support structlog-style kwargs."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def _format(self, event: str, kwargs: dict) -> str:
        if kwargs:
            extra = " ".join(f"{k}={v}" for k, v in kwargs.items())
            return f"{event} {extra}"
        return event

    def info(self, event: str, **kwargs):
        self._logger.info(self._format(event, kwargs))

    def warning(self, event: str, **kwargs):
        self._logger.warning(self._format(event, kwargs))

    def error(self, event: str, **kwargs):
        self._logger.error(self._format(event, kwargs))

    def debug(self, event: str, **kwargs):
        self._logger.debug(self._format(event, kwargs))

    def exception(self, event: str, **kwargs):
        self._logger.exception(self._format(event, kwargs))


def configure_logging() -> None:
    settings = get_settings()
    if HAS_STRUCTLOG:
        shared_processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.stdlib.add_logger_name,
        ]
        if settings.is_production:
            renderer = structlog.processors.JSONRenderer()
        else:
            renderer = structlog.dev.ConsoleRenderer()

        structlog.configure(
            processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        formatter = structlog.stdlib.ProcessorFormatter(
            processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta, renderer],
            foreign_pre_chain=shared_processors,
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        root = logging.getLogger()
        root.handlers = [handler]
        root.setLevel(logging.DEBUG if not settings.is_production else logging.INFO)
    else:
        logging.basicConfig(
            level=logging.DEBUG if not settings.is_production else logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            stream=sys.stdout,
        )

    # Suppress noisy loggers
    for noisy in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str = __name__):
    if HAS_STRUCTLOG:
        return structlog.get_logger(name)
    return _StdlibLoggerWrapper(logging.getLogger(name))


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Inject a unique request-id into structlog context and response headers."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        if HAS_STRUCTLOG:
            structlog.contextvars.clear_contextvars()
            structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
