"""
CVBoost AI — ATS Compliance Checker
Validates generated PDF text layer for ATS compatibility.
"""
from __future__ import annotations

import io
import re
from typing import Any

from app.core.logging import get_logger
from app.schemas.cv import AtsCheckResult

logger = get_logger(__name__)

# ── Section detection patterns (EN/FR/AR) ─────────────────────────────────────

_SECTION_PATTERNS: dict[str, list[str]] = {
    "summary": [
        r"professional\s+summary", r"summary", r"profile", r"objective",
        r"résumé\s+professionnel", r"profil", r"الملخص",
    ],
    "education": [
        r"education", r"formation", r"academic", r"التعليم", r"الدراسة",
    ],
    "experience": [
        r"experience", r"work\s+experience", r"employment", r"expérience",
        r"الخبرة",
    ],
    "projects": [
        r"projects?", r"projets?", r"المشاريع",
    ],
    "skills": [
        r"skills?", r"compétences?", r"technical\s+skills", r"المهارات",
    ],
    "languages": [
        r"languages?", r"langues?", r"اللغات",
    ],
}

# ── Regex for contact info ─────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"[\+\d][\d\s\-\(\)\.]{7,20}\d")

# ── Garbled text detection ─────────────────────────────────────────────────────
_GARBLED_RE = re.compile(r"[^\x09\x0A\x0D\x20-\x7E\u0080-\uFFFF]{3,}")


async def run_ats_check(pdf_bytes: bytes) -> AtsCheckResult:
    """Run ATS compliance check on PDF bytes."""
    import asyncio
    return await asyncio.to_thread(_run_ats_check_sync, pdf_bytes)


def _run_ats_check_sync(pdf_bytes: bytes) -> AtsCheckResult:
    text = _extract_text(pdf_bytes)
    if not text:
        return AtsCheckResult(
            score=0,
            issues=["No extractable text found in PDF. This CV will fail all ATS systems."],
            suggestions=["Regenerate the PDF using CVBoost AI to ensure a proper text layer."],
        )

    text_lower = text.lower()
    sections_found: list[str] = []
    sections_missing: list[str] = []

    # Section detection
    for section_name, patterns in _SECTION_PATTERNS.items():
        found = any(re.search(p, text_lower) for p in patterns)
        if found:
            sections_found.append(section_name)
        else:
            sections_missing.append(section_name)

    # Contact info
    email_found = bool(_EMAIL_RE.search(text))
    phone_found = bool(_PHONE_RE.search(text))

    # Skills presence (look for comma-separated lists)
    skills_found = "skills" in sections_found or bool(
        re.search(r"\w+,\s*\w+,\s*\w+", text)
    )

    # Reading order check (heuristic: name/contact should appear before experience)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    reading_order_ok = len(lines) > 5  # Basic check

    # Garbled characters
    garbled_matches = _GARBLED_RE.findall(text)
    garbled = len(garbled_matches) > 0

    # Build score
    score = _compute_score(
        sections_found, email_found, phone_found, skills_found, garbled, reading_order_ok
    )

    # Issues and suggestions
    issues: list[str] = []
    suggestions: list[str] = []

    if not email_found:
        issues.append("Email address not found in extracted text")
        suggestions.append("Ensure your email is visible in the PDF text layer")
    if not phone_found:
        issues.append("Phone number not found")
        suggestions.append("Add your phone number in the Personal Details section")
    for s in sections_missing:
        if s in ("summary", "skills"):
            issues.append(f"Section '{s}' not detected")
            suggestions.append(f"Add a '{s}' section to improve ATS compatibility")
    if garbled:
        issues.append(f"Garbled/non-readable characters detected ({len(garbled_matches)} instances)")
        suggestions.append("Regenerate the PDF — some characters failed to encode correctly")
    if not reading_order_ok:
        issues.append("PDF has very little extractable text")
        suggestions.append("Use ATS-safe mode (no photo, single column) for better parsing")

    return AtsCheckResult(
        score=score,
        sections_found=sections_found,
        sections_missing=sections_missing,
        email_found=email_found,
        phone_found=phone_found,
        skills_found=skills_found,
        reading_order_ok=reading_order_ok,
        garbled_chars=garbled,
        issues=issues,
        suggestions=suggestions,
    )


def _extract_text(pdf_bytes: bytes) -> str:
    """Extract text using pdfplumber (primary) then PyMuPDF fallback."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            parts = []
            for page in pdf.pages:
                t = page.extract_text() or ""
                if t:
                    parts.append(t)
            return "\n\n".join(parts)
    except Exception as exc:
        logger.warning("ats_pdfplumber_failed", error=str(exc))

    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        parts = [page.get_text("text") for page in doc]
        doc.close()
        return "\n\n".join(parts)
    except Exception as exc:
        logger.error("ats_pymupdf_failed", error=str(exc))
        return ""


def _compute_score(
    sections_found: list[str],
    email_found: bool,
    phone_found: bool,
    skills_found: bool,
    garbled: bool,
    reading_order_ok: bool,
) -> int:
    score = 0
    # Sections (up to 50 pts)
    key_sections = {"summary", "education", "skills"}
    optional_sections = {"experience", "projects", "languages"}
    for s in key_sections:
        if s in sections_found:
            score += 14
    for s in optional_sections:
        if s in sections_found:
            score += 4

    # Contact (up to 20 pts)
    if email_found:
        score += 10
    if phone_found:
        score += 10

    # Skills (10 pts)
    if skills_found:
        score += 10

    # No garbled (10 pts)
    if not garbled:
        score += 10

    # Reading order (10 pts)
    if reading_order_ok:
        score += 10

    return min(score, 100)
