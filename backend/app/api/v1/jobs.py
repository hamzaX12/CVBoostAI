"""
CVBoost AI — Jobs Analysis API (SSE streaming)
POST /jobs/analyze → Server-Sent Events
"""
from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.v1.auth import _get_any_user
from app.core.limits import limiter, AI_LIMIT
from app.core.logging import get_logger
from app.models.db import User
from app.schemas.cv import JobAnalysisResult

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = get_logger(__name__)


class JobAnalyzeRequest(BaseModel):
    query: str
    country: str = ""
    seniority: str = ""
    current_skills: list[str] = []
    existing_categories: list[dict] = []
    cv_id: str = ""


@router.post("/analyze", summary="Analyze job requirements via AI (SSE)")
@limiter.limit(AI_LIMIT)
async def analyze_job(
    request: Request,
    body: JobAnalyzeRequest,
    current_user: User | None = Depends(_get_any_user),
) -> StreamingResponse:
    """
    Streams Server-Sent Events:
      data: {"type": "progress", "message": "Searching the web..."}
      data: {"type": "result", "data": {...JobAnalysisResult...}}
      data: {"type": "error", "message": "..."}
    """
    return StreamingResponse(
        _stream_analysis(body, current_user),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


async def _stream_analysis(
    body: JobAnalyzeRequest,
    user: User | None,
) -> AsyncGenerator[str, None]:
    from app.agents.job_agent import run_job_agent

    async def emit(event_type: str, payload: dict | str) -> str:
        if isinstance(payload, str):
            data = {"type": event_type, "message": payload}
        else:
            data = {"type": event_type, **payload}
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    try:
        yield await emit("progress", "Detecting role and requirements...")
        async for event in run_job_agent(
            query=body.query,
            country=body.country,
            seniority=body.seniority,
            current_skills=body.current_skills,
            existing_categories=body.existing_categories,
        ):
            if event.get("type") == "progress":
                yield await emit("progress", event["message"])
            elif event.get("type") == "result":
                yield await emit("result", {"data": event["data"]})
    except Exception as exc:
        logger.error("job_agent_error", error=str(exc))
        yield await emit("error", f"Analysis failed: {str(exc)[:200]}")
