"""
CVBoost AI — CV CRUD API Routes
GET/POST/PUT/DELETE /cv, plus /cv/extract, /cv/pdf, /cv/ats-check
"""
from __future__ import annotations

import json
import os
import uuid
try:
    from datetime import UTC, datetime
except ImportError:
    from datetime import datetime, timezone
    UTC = timezone.utc
from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import _get_any_user, _get_current_user
from app.core.limits import limiter, AI_LIMIT, UPLOAD_LIMIT
from app.core.logging import get_logger
from app.core.security import sanitize_filename, validate_upload
from app.core.config import get_settings
from app.models.database import get_db
from app.models.db import CVRecord, User
from app.schemas.cv import CVSchema, AtsCheckResult

router = APIRouter(prefix="/cv", tags=["cv"])
logger = get_logger(__name__)
settings = get_settings()


# ── List CVs ──────────────────────────────────────────────────────────────────

@router.get("/", summary="List user CVs")
async def list_cvs(
    current_user: User = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    result = await db.execute(
        select(CVRecord).where(CVRecord.user_id == current_user.id)
    )
    records = result.scalars().all()
    return [
        {"id": r.id, "title": r.title, "updated_at": str(r.updated_at), "is_draft": r.is_draft}
        for r in records
    ]


# ── Get single CV ─────────────────────────────────────────────────────────────

@router.get("/{cv_id}", summary="Get a CV by ID")
async def get_cv(
    cv_id: str,
    current_user: User = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    record = await _get_cv_record(cv_id, current_user.id, db)
    return record.data


# ── Create CV ─────────────────────────────────────────────────────────────────

@router.post("/", summary="Save a new CV", status_code=status.HTTP_201_CREATED)
async def create_cv(
    body: CVSchema,
    current_user: User = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    now = datetime.now(UTC).isoformat()
    body.created_at = now
    body.updated_at = now
    record = CVRecord(
        user_id=current_user.id,
        title=f"{body.personal.first_name} {body.personal.last_name}".strip() or "My CV",
        data=body.model_dump(mode="json"),
    )
    db.add(record)
    await db.flush()
    return {"id": record.id, "message": "CV created"}


# ── Update CV ─────────────────────────────────────────────────────────────────

@router.put("/{cv_id}", summary="Update an existing CV")
async def update_cv(
    cv_id: str,
    body: CVSchema,
    current_user: User = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    record = await _get_cv_record(cv_id, current_user.id, db)
    body.updated_at = datetime.now(UTC).isoformat()
    record.data = body.model_dump(mode="json")
    record.title = (
        f"{body.personal.first_name} {body.personal.last_name}".strip() or record.title
    )
    return {"id": record.id, "message": "CV updated"}


# ── Delete CV ─────────────────────────────────────────────────────────────────

@router.delete("/{cv_id}", summary="Delete a CV")
async def delete_cv(
    cv_id: str,
    current_user: User = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    record = await _get_cv_record(cv_id, current_user.id, db)
    await db.delete(record)
    return {"message": "CV deleted"}


# ── Upload + Extract CV ───────────────────────────────────────────────────────

@router.post("/extract", summary="Upload CV file and extract structured data")
@limiter.limit(UPLOAD_LIMIT)
async def extract_cv(
    request: Request,
    file: UploadFile = File(..., description="PDF or DOCX CV file, max 5 MB"),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(_get_any_user),
) -> dict:
    content = await file.read()
    validate_upload(file.filename or "upload", content, file.content_type or "")

    # Save to upload dir with randomized name
    os.makedirs(settings.upload_dir, exist_ok=True)
    safe_name = sanitize_filename(file.filename or "upload")
    upload_path = os.path.join(settings.upload_dir, safe_name)

    try:
        with open(upload_path, "wb") as f:
            f.write(content)

        # Parse → AI extraction
        from app.services.parsers import parse_cv_file
        from app.agents.extraction_agent import run_extraction_agent

        try:
            raw_text, layout_hints = await parse_cv_file(upload_path)
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))

        if not raw_text or not raw_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No readable text found in this file. Please use the 'Paste CV as text' option."
            )

        result = await run_extraction_agent(raw_text, layout_hints)
        return result.model_dump(mode="json")
    finally:
        # Always delete uploaded file after processing
        if os.path.exists(upload_path):
            os.remove(upload_path)


@router.post("/extract-text", summary="Extract structured CV data from raw pasted text")
@limiter.limit(UPLOAD_LIMIT)
async def extract_cv_text(
    request: Request,
    body: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(_get_any_user),
) -> dict:
    text = (body.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="CV text cannot be empty")
    from app.agents.extraction_agent import run_extraction_agent
    result = await run_extraction_agent(text)
    return result.model_dump(mode="json")


# ── Generate PDF ──────────────────────────────────────────────────────────────

@router.post("/pdf", summary="Generate ATS-friendly PDF from CV data")
@limiter.limit(AI_LIMIT)
async def generate_pdf(
    request: Request,
    body: CVSchema,
    current_user: User | None = Depends(_get_any_user),
) -> StreamingResponse:
    from app.services.pdf import render_pdf

    pdf_bytes = await render_pdf(body)
    base_name = getattr(body, "cv_name", None) or getattr(body, "title", None)
    if base_name and base_name.strip():
        safe_base = re.sub(r'[/\\?%*:|"<>]+', '_', base_name.strip()).removesuffix(".pdf")
        name = f"{safe_base}.pdf"
    else:
        name = f"CV_{body.personal.last_name}_{body.personal.first_name}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


# ── ATS Check ─────────────────────────────────────────────────────────────────

@router.post("/ats-check", summary="Validate PDF for ATS compliance", response_model=AtsCheckResult)
@limiter.limit(AI_LIMIT)
async def ats_check(
    request: Request,
    file: UploadFile = File(...),
    current_user: User | None = Depends(_get_any_user),
) -> AtsCheckResult:
    content = await file.read()
    validate_upload(file.filename or "check.pdf", content, file.content_type or "application/pdf")
    from app.services.ats_checker import run_ats_check
    return await run_ats_check(content)


# ── Improve Bullet ────────────────────────────────────────────────────────────

@router.post("/improve-bullet", summary="Rewrite a CV bullet with strong action verbs")
@limiter.limit(AI_LIMIT)
async def improve_bullet(
    request: Request,
    bullet: Annotated[str, Body(embed=True, max_length=1000)],
    context: Annotated[str, Body(embed=True, max_length=500)] = "",
    current_user: User | None = Depends(_get_any_user),
) -> dict:
    from app.agents.extraction_agent import run_improve_bullet
    result = await run_improve_bullet(bullet, context)
    return result.model_dump()


# ── Improve Summary ───────────────────────────────────────────────────────────

@router.post("/improve-summary", summary="Rewrite a CV summary with professional executive tone")
@limiter.limit(AI_LIMIT)
async def improve_summary(
    request: Request,
    summary: Annotated[str, Body(embed=True, max_length=2000)],
    context: Annotated[str, Body(embed=True, max_length=500)] = "",
    current_user: User | None = Depends(_get_any_user),
) -> dict:
    from app.agents.extraction_agent import run_improve_summary
    result = await run_improve_summary(summary, context)
    return result.model_dump()


# ── Export JSON ───────────────────────────────────────────────────────────────

@router.get("/{cv_id}/export-json", summary="Export CV as JSON")
async def export_json(
    cv_id: str,
    current_user: User = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    record = await _get_cv_record(cv_id, current_user.id, db)
    json_bytes = json.dumps(record.data, indent=2, ensure_ascii=False).encode()
    return StreamingResponse(
        iter([json_bytes]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="cv_{cv_id}.json"'},
    )


# ── Internal helper ───────────────────────────────────────────────────────────

async def _get_cv_record(cv_id: str, user_id: str, db: AsyncSession) -> CVRecord:
    result = await db.execute(
        select(CVRecord).where(CVRecord.id == cv_id, CVRecord.user_id == user_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="CV not found.")
    return record
