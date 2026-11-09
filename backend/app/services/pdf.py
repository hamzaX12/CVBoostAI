"""
CVBoost AI — WeasyPrint PDF Renderer
Generates ATS-friendly, text-layer PDFs from CV data using Jinja2 templates.
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.cv import CVSchema, Template, SpacingPreset, LanguageLevel

logger = get_logger(__name__)
settings = get_settings()

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "pdf"

# ── Jinja2 env (autoescape ON for XSS prevention) ─────────────────────────────

_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def _safe_url_fetcher(url: str):
    """
    WeasyPrint url_fetcher: only allow local file:// for fonts and assets.
    Blocks ALL external URLs to prevent SSRF/LFI.
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme == "file":
        # Only allow paths inside our assets directory
        assets_dir = str(Path(__file__).parent.parent / "templates" / "assets")
        file_path = parsed.path
        if not os.path.normpath(file_path).startswith(os.path.normpath(assets_dir)):
            raise ValueError(f"Blocked: file path outside assets dir: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Asset not found: {file_path}")
        with open(file_path, "rb") as f:
            data = f.read()
        return {"string": data, "mime_type": _guess_mime(file_path)}
    elif parsed.scheme in ("data",):
        # Allow data URIs (for embedded photos)
        return None  # WeasyPrint handles data: URIs natively
    else:
        raise ValueError(f"Blocked external URL in PDF renderer: {url}")


def _guess_mime(path: str) -> str:
    ext = Path(path).suffix.lower()
    return {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml", ".woff2": "font/woff2", ".woff": "font/woff",
            ".ttf": "font/truetype"}.get(ext, "application/octet-stream")


# ── Spacing presets ────────────────────────────────────────────────────────────

SPACING = {
    SpacingPreset.compact:  {"body_size": "10px", "heading_size": "13px", "section_gap": "10px", "line_height": "1.3"},
    SpacingPreset.normal:   {"body_size": "11px", "heading_size": "14px", "section_gap": "14px", "line_height": "1.45"},
    SpacingPreset.relaxed:  {"body_size": "12px", "heading_size": "15px", "section_gap": "18px", "line_height": "1.6"},
}

# ── Section title translations ─────────────────────────────────────────────────

SECTION_TITLES = {
    "en": {
        "profile": "Professional Summary",
        "education": "Education",
        "experience": "Work Experience",
        "projects": "Projects",
        "skills": "Skills",
        "languages": "Languages",
        "certificates": "Certificates",
        "hobbies": "Hobbies & Interests",
        "courses": "Courses",
        "achievements": "Achievements",
        "contact": "Contact",
    },
    "fr": {
        "profile": "Résumé Professionnel",
        "education": "Formation",
        "experience": "Expérience Professionnelle",
        "projects": "Projets",
        "skills": "Compétences",
        "languages": "Langues",
        "certificates": "Certifications",
        "hobbies": "Loisirs",
        "courses": "Formations",
        "achievements": "Réalisations",
        "contact": "Contact",
    },
    "ar": {
        "profile": "الملخص المهني",
        "education": "التعليم",
        "experience": "الخبرة المهنية",
        "projects": "المشاريع",
        "skills": "المهارات",
        "languages": "اللغات",
        "certificates": "الشهادات",
        "hobbies": "الهوايات",
        "courses": "الدورات",
        "achievements": "الإنجازات",
        "contact": "التواصل",
    },
}

LANGUAGE_LEVEL_DOTS = {
    LanguageLevel.native: 5,
    LanguageLevel.advanced: 4,
    LanguageLevel.intermediate: 3,
    LanguageLevel.basic: 1,
}


def _build_template_context(cv: CVSchema) -> dict[str, Any]:
    lang = cv.style.cv_language.value
    titles = SECTION_TITLES.get(lang, SECTION_TITLES["en"])
    spacing = SPACING.get(cv.style.spacing, SPACING[SpacingPreset.normal])
    colors = cv.style.colors

    return {
        "cv": cv,
        "titles": titles,
        "spacing": spacing,
        "colors": colors,
        "font": cv.style.font.value,
        "template": cv.style.template.value,
        "photo_shape": cv.style.photo_shape.value,
        "sidebar_pos": cv.style.sidebar_position.value,
        "sidebar_width": cv.style.sidebar_width_percent,
        "ats_safe": cv.style.ats_safe_mode,
        "is_rtl": lang == "ar",
        "lang": lang,
        "language_dots": LANGUAGE_LEVEL_DOTS,
        "now": datetime.now().strftime("%Y"),
        "sections_order": cv.sections_order,
    }


async def render_pdf(cv: CVSchema) -> bytes:
    """Async wrapper: render PDF in a thread (WeasyPrint is CPU-bound)."""
    return await asyncio.to_thread(_render_pdf_sync, cv)


_WEASYPRINT_AVAILABLE = None


def is_weasyprint_available() -> bool:
    global _WEASYPRINT_AVAILABLE
    if _WEASYPRINT_AVAILABLE is None:
        import sys, shutil
        if sys.platform == 'win32' and not shutil.which('libgobject-2.0-0.dll'):
            _WEASYPRINT_AVAILABLE = False
            return False
        try:
            import weasyprint
            _WEASYPRINT_AVAILABLE = True
        except (ImportError, OSError):
            _WEASYPRINT_AVAILABLE = False
    return _WEASYPRINT_AVAILABLE


def _render_pdf_sync(cv: CVSchema) -> bytes:
    if is_weasyprint_available():
        try:
            from weasyprint import HTML, CSS
            from weasyprint.urls import URLFetchingError

            template_name = f"template_{cv.style.template.value}.html"
            try:
                tmpl = _jinja_env.get_template(template_name)
            except Exception:
                tmpl = _jinja_env.get_template("template_sidebar.html")

            context = _build_template_context(cv)
            html_content = tmpl.render(**context)

            html = HTML(
                string=html_content,
                base_url=str(TEMPLATES_DIR),
                url_fetcher=_safe_url_fetcher,
            )
            pdf_bytes = html.write_pdf(
                uncompressed_pdf=False,
                presentational_hints=True,
            )
            logger.info("pdf_generated", template=cv.style.template.value, pages="?")
            return pdf_bytes
        except Exception as e:
            logger.warning("weasyprint_failed_fallback_reportlab", error=str(e))
            return _render_pdf_reportlab(cv)
    else:
        logger.info("rendering_pdf_via_reportlab", template=cv.style.template.value)
        return _render_pdf_reportlab(cv)


def _render_pdf_reportlab(cv: CVSchema) -> bytes:
    """Generate ATS-friendly PDF using ReportLab as a robust standalone fallback."""
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    name_style = ParagraphStyle(
        'CVName', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=20, leading=24,
        textColor=colors.HexColor('#2B4257'),
    )
    title_style = ParagraphStyle(
        'CVTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=16,
        textColor=colors.HexColor('#111827'),
    )
    contact_style = ParagraphStyle(
        'CVContact', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#4B5563'),
    )
    heading_style = ParagraphStyle(
        'CVHeading', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=colors.HexColor('#2B4257'), spaceBefore=8, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        'CVBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12.5,
        textColor=colors.HexColor('#374151'),
    )
    bullet_style = ParagraphStyle(
        'CVBullet', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#374151'), leftIndent=12,
    )

    story = []
    p = cv.personal
    full_name = f"{p.first_name} {p.last_name}".strip()
    if full_name:
        story.append(Paragraph(full_name.upper(), name_style))
    if p.headline:
        story.append(Paragraph(p.headline, title_style))

    contacts = [p.email, p.phone, p.address or p.city, p.linkedin, p.website]
    contact_line = "  •  ".join(filter(None, contacts))
    if contact_line:
        story.append(Spacer(1, 4))
        story.append(Paragraph(contact_line, contact_style))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=8))

    if cv.summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        story.append(Paragraph(cv.summary, body_style))
        story.append(Spacer(1, 4))

    exp_list = cv.experience if cv.experience else cv.projects
    if exp_list:
        story.append(Paragraph("EXPERIENCE", heading_style))
        for exp in exp_list:
            title = getattr(exp, "title", None) or getattr(exp, "job_title", "")
            dates = ""
            if exp.start_date and (getattr(exp, "end_date", None) or getattr(exp, "current", False)):
                dates = f"{exp.start_date} – {'Present' if getattr(exp, 'current', False) else exp.end_date}"
            elif exp.start_date:
                dates = exp.start_date
            elif getattr(exp, "end_date", None):
                dates = exp.end_date

            t_line = f"<b>{title}</b>" + (f"  |  <i>{dates}</i>" if dates else "")
            story.append(Paragraph(t_line, body_style))

            org = getattr(exp, "company", None) or getattr(exp, "organization", None) or getattr(exp, "subtitle", None)
            loc = getattr(exp, "location", None)
            sub = " • ".join(filter(None, [org, loc]))
            if sub:
                story.append(Paragraph(f"<i>{sub}</i>", contact_style))

            bullets = getattr(exp, "bullets", None) or getattr(exp, "description", None) or []
            for b in bullets:
                txt = getattr(b, "text", b) if hasattr(b, "text") else (b.get("text") if isinstance(b, dict) else str(b))
                if txt:
                    story.append(Paragraph(f"• {txt}", bullet_style))
            story.append(Spacer(1, 3))

    if cv.education:
        story.append(Paragraph("EDUCATION", heading_style))
        for edu in cv.education:
            deg = edu.degree or ""
            dates = f"{edu.start_date} – {'Present' if edu.current else edu.end_date}" if (edu.start_date and (edu.end_date or edu.current)) else (edu.end_date or edu.start_date or "")
            e_line = f"<b>{deg}</b>" + (f"  |  <i>{dates}</i>" if dates else "")
            story.append(Paragraph(e_line, body_style))
            inst = " • ".join(filter(None, [edu.institution, edu.location]))
            if inst:
                story.append(Paragraph(f"<i>{inst}</i>", contact_style))
            story.append(Spacer(1, 3))

    if cv.skills:
        story.append(Paragraph("SKILLS", heading_style))
        for g in cv.skills:
            items_str = ", ".join(getattr(item, "name", str(item)) for item in g.items)
            story.append(Paragraph(f"<b>{g.category}:</b> {items_str}", body_style))
        story.append(Spacer(1, 3))

    if cv.languages:
        story.append(Paragraph("LANGUAGES", heading_style))
        lang_strs = [f"{l.name} ({l.level.value if hasattr(l.level, 'value') else l.level})" for l in cv.languages]
        story.append(Paragraph(", ".join(lang_strs), body_style))
        story.append(Spacer(1, 3))

    if getattr(cv, "custom_sections", None):
        for cs in cv.custom_sections:
            c_label = getattr(cs, "label", None) or getattr(cs, "title", None) or getattr(cs, "id", "SECTION")
            story.append(Paragraph(c_label.upper(), heading_style))
            for item in (getattr(cs, "items", []) or []):
                txt = getattr(item, "text", item) if hasattr(item, "text") else (item.get("text") if isinstance(item, dict) else str(item))
                if txt:
                    story.append(Paragraph(f"• {txt}", bullet_style))
            story.append(Spacer(1, 3))

    doc.build(story)
    return buffer.getvalue()
