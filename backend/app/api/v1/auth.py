"""
CVBoost AI — Auth API Routes
POST /auth/register, /auth/login, /auth/logout, /auth/refresh, /auth/me
"""
from __future__ import annotations

try:
    from datetime import UTC, datetime, timedelta
except ImportError:
    from datetime import datetime, timedelta, timezone
    UTC = timezone.utc

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.limits import limiter, DEFAULT_LIMIT
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_guest_token,
    create_refresh_token,
    decode_token,
    hash_password,
    needs_rehash,
    set_auth_cookies,
    clear_auth_cookies,
    verify_password,
    CookieOrBearerAuth,
)
from app.models.database import get_db
from app.models.db import RefreshToken, User

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)
settings = get_settings()
auth_scheme = CookieOrBearerAuth(auto_error=False)


# ── Request / Response schemas ────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""

    def validate_password(self) -> None:
        if len(self.password) < 8:
            raise HTTPException(400, "Password must be at least 8 characters.")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_guest: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def _get_current_user(
    token: str | None = Depends(auth_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(token)
    user_id: str = payload.get("sub", "")
    if not user_id or user_id.startswith("guest:"):
        raise HTTPException(status_code=401, detail="Full account required")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


async def _get_any_user(
    token: str | None = Depends(auth_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Returns user or None for guest/anonymous."""
    if not token:
        return None
    try:
        payload = decode_token(token)
        sub = payload.get("sub", "")
        if sub.startswith("guest:"):
            return None
        result = await db.execute(select(User).where(User.id == sub))
        return result.scalar_one_or_none()
    except Exception:
        return None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    body.validate_password()
    existing = await _get_user_by_email(db, str(body.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")
    user = User(
        email=str(body.email),
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    await db.flush()
    access = create_access_token(user.id, {"role": "user"})
    refresh = create_refresh_token(user.id)
    # Store refresh token JTI for revocation
    jti = decode_token(refresh).get("jti", "")
    db.add(RefreshToken(
        jti=jti,
        user_id=user.id,
        expires_at=datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expire_days),
    ))
    set_auth_cookies(response, access, refresh)
    logger.info("user_registered", user_id=user.id)
    return TokenResponse(
        access_token=access,
        user=UserResponse(id=user.id, email=user.email, full_name=user.full_name, is_guest=False),
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await _get_user_by_email(db, str(body.email))
    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled.")
    # Rehash if needed
    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(body.password)
    access = create_access_token(user.id, {"role": "user"})
    refresh = create_refresh_token(user.id)
    jti = decode_token(refresh).get("jti", "")
    db.add(RefreshToken(
        jti=jti,
        user_id=user.id,
        expires_at=datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expire_days),
    ))
    set_auth_cookies(response, access, refresh)
    logger.info("user_logged_in", user_id=user.id)
    return TokenResponse(
        access_token=access,
        user=UserResponse(id=user.id, email=user.email, full_name=user.full_name, is_guest=False),
    )


@router.post("/logout")
async def logout(response: Response) -> dict:
    clear_auth_cookies(response)
    return {"detail": "Logged out successfully."}


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    token = request.cookies.get("cvboost_refresh")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token.")
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type.")
    jti = payload.get("jti", "")
    result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    rt = result.scalar_one_or_none()
    if not rt or rt.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found.")
    # Rotate: revoke old, issue new
    rt.revoked = True
    user_id = payload["sub"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found.")
    new_access = create_access_token(user.id, {"role": "user"})
    new_refresh = create_refresh_token(user.id)
    new_jti = decode_token(new_refresh).get("jti", "")
    db.add(RefreshToken(
        jti=new_jti,
        user_id=user.id,
        expires_at=datetime.now(UTC) + timedelta(days=settings.jwt_refresh_expire_days),
    ))
    set_auth_cookies(response, new_access, new_refresh)
    return TokenResponse(
        access_token=new_access,
        user=UserResponse(id=user.id, email=user.email, full_name=user.full_name, is_guest=False),
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(_get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_guest=current_user.is_guest,
    )


@router.post("/guest", response_model=TokenResponse)
@limiter.limit("30/minute")
async def guest_session(request: Request, response: Response) -> TokenResponse:
    token = create_guest_token()
    return TokenResponse(
        access_token=token,
        user=UserResponse(id="guest", email="", full_name="Guest", is_guest=True),
    )


@router.delete("/me")
async def delete_account(
    response: Response,
    current_user: User = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """GDPR 'Delete my data' endpoint."""
    await db.delete(current_user)
    clear_auth_cookies(response)
    logger.info("user_deleted", user_id=current_user.id)
    return {"detail": "Account and all data deleted."}
