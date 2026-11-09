"""
CVBoost AI — Security Utilities
JWT, Argon2 hashing, cookie helpers, SSRF protection.
"""
from __future__ import annotations

import ipaddress
import re
import secrets
import socket
try:
    from datetime import UTC, datetime, timedelta
except ImportError:
    from datetime import datetime, timedelta, timezone
    UTC = timezone.utc
from typing import Any
from urllib.parse import urlparse

from argon2 import PasswordHasher
try:
    from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash as InvalidHashError
except ImportError:
    from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError  # type: ignore[no-redef]
try:
    from jose import JWTError, jwt
except ImportError:
    import jwt
    from jwt.exceptions import PyJWTError as JWTError  # type: ignore[no-redef]
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings

# ─────────────────────────────────────────────────────────────────────────────
# Password hashing (Argon2id)
# ─────────────────────────────────────────────────────────────────────────────

_ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(hashed: str) -> bool:
    return _ph.check_needs_rehash(hashed)


# ─────────────────────────────────────────────────────────────────────────────
# JWT helpers
# ─────────────────────────────────────────────────────────────────────────────

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "access",
        **(extra or {}),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expire_days)
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "refresh",
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise _CREDENTIALS_EXCEPTION from e


def create_guest_token() -> str:
    """Signed session token for anonymous users with strict quotas."""
    return create_access_token(
        subject=f"guest:{secrets.token_hex(16)}",
        extra={"role": "guest", "quota": 3},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Cookie helpers
# ─────────────────────────────────────────────────────────────────────────────

COOKIE_ACCESS = "cvboost_access"
COOKIE_REFRESH = "cvboost_refresh"


def set_auth_cookies(response: Any, access_token: str, refresh_token: str) -> None:
    settings = get_settings()
    secure = settings.is_production
    response.set_cookie(
        key=COOKIE_ACCESS,
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.jwt_access_expire_minutes * 60,
    )
    response.set_cookie(
        key=COOKIE_REFRESH,
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.jwt_refresh_expire_days * 86400,
        path="/api/v1/auth/refresh",
    )


def clear_auth_cookies(response: Any) -> None:
    response.delete_cookie(COOKIE_ACCESS)
    response.delete_cookie(COOKIE_REFRESH, path="/api/v1/auth/refresh")


# ─────────────────────────────────────────────────────────────────────────────
# Bearer token extractor (reads cookie first, then Authorization header)
# ─────────────────────────────────────────────────────────────────────────────

class CookieOrBearerAuth(HTTPBearer):
    async def __call__(self, request: Request) -> str | None:  # type: ignore[override]
        # Prefer httpOnly cookie
        token = request.cookies.get(COOKIE_ACCESS)
        if token:
            return token
        # Fall back to Authorization header
        try:
            creds: HTTPAuthorizationCredentials = await super().__call__(request)
            return creds.credentials
        except Exception:
            return None


# ─────────────────────────────────────────────────────────────────────────────
# SSRF protection
# ─────────────────────────────────────────────────────────────────────────────

_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),   # link-local
    ipaddress.ip_network("100.64.0.0/10"),    # shared address space
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def is_private_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return any(addr in net for net in _PRIVATE_NETWORKS)
    except ValueError:
        return True  # fail-safe


def validate_url_for_fetch(url: str, max_redirects: int = 3) -> str:
    """
    Validate a URL before fetching:
    - Only http/https
    - Resolve DNS and block private/loopback IPs
    - Block after redirects (caller must pass resolved URL)
    Raises ValueError if blocked.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Scheme '{parsed.scheme}' not allowed")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Missing hostname")
    # Resolve and check all IPs
    try:
        results = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed: {exc}") from exc
    for result in results:
        ip = result[4][0]
        if is_private_ip(ip):
            raise ValueError(f"URL resolves to private IP: {ip}")
    return url


# ─────────────────────────────────────────────────────────────────────────────
# File upload security
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def validate_upload(filename: str, content: bytes, content_type: str) -> None:
    """Validate uploaded file: extension, magic bytes, size."""
    import os
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Please upload a PDF (.pdf) or Word document (.docx)."
        )

    settings = get_settings()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large (max 5 MB).")

    # Validate file magic bytes based on extension
    if ext == ".pdf":
        if not content[:4] == b"%PDF":
            raise HTTPException(status_code=400, detail="Invalid PDF file: magic bytes mismatch.")
    elif ext == ".docx":
        if not content[:4] == b"PK\x03\x04":
            raise HTTPException(status_code=400, detail="Invalid DOCX file: magic bytes mismatch.")


def sanitize_filename(original: str) -> str:
    """Return a UUID-based safe filename preserving extension."""
    import os
    import uuid
    ext = os.path.splitext(original)[1].lower()
    return f"{uuid.uuid4().hex}{ext}"


# ─────────────────────────────────────────────────────────────────────────────
# Content sanitization (XSS / HTML injection prevention)
# ─────────────────────────────────────────────────────────────────────────────

import bleach

ALLOWED_TAGS: list[str] = []   # No HTML in user-submitted plain text fields
ALLOWED_ATTRS: dict = {}


def sanitize_text(value: str) -> str:
    """Strip all HTML tags from a string."""
    return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)


BULLET_ALLOWED_TAGS = ["b", "i", "strong", "em", "u"]
BULLET_ALLOWED_ATTRS: dict = {}


def sanitize_rich_text(value: str) -> str:
    """Allow only safe inline formatting in bullet points."""
    return bleach.clean(value, tags=BULLET_ALLOWED_TAGS, attributes=BULLET_ALLOWED_ATTRS, strip=True)


# ─────────────────────────────────────────────────────────────────────────────
# Honeypot field for contact form spam protection
# ─────────────────────────────────────────────────────────────────────────────

def check_honeypot(value: str) -> None:
    """Raise if honeypot field is not empty (bot detected)."""
    if value:
        raise HTTPException(status_code=400, detail="Invalid submission.")
