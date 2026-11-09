"""
CVBoost AI — File Parsers
Extracts raw text from PDF (pdfplumber/PyMuPDF + OCR fallback) and DOCX.
"""
from __future__ import annotations

import os
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


async def parse_cv_file(file_path: str) -> tuple[str, dict[str, Any]]:
    """
    Parse a CV file and return (raw_text, layout_hints).
    layout_hints includes font sizes, positions, etc. for extraction guidance.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return await _parse_pdf(file_path)
    elif ext == ".docx":
        return await _parse_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


async def _parse_pdf(path: str) -> tuple[str, dict]:
    """Parse PDF with pdfplumber (primary) + PyMuPDF + OCR fallback."""
    import asyncio
    return await asyncio.to_thread(_parse_pdf_sync, path)


def _parse_pdf_sync(path: str) -> tuple[str, dict]:
    layout_hints: dict = {"pages": [], "fonts": [], "has_text_layer": False}
    text_parts = []

    # ── pdfplumber (primary) ──────────────────────────────────────────────
    try:
        import pdfplumber
        from app.core.config import get_settings
        settings = get_settings()

        with pdfplumber.open(path) as pdf:
            if len(pdf.pages) > settings.max_pdf_pages:
                raise ValueError(f"PDF exceeds {settings.max_pdf_pages} pages limit")

            layout_hints["total_pages"] = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                if page_text.strip():
                    layout_hints["has_text_layer"] = True
                    text_parts.append(page_text)

                # Collect font info for layout hints
                words = page.extract_words(extra_attrs=["fontname", "size"])
                fonts = [{"text": w.get("text",""), "size": w.get("size",0), "font": w.get("fontname","")} for w in words[:20]]
                layout_hints["pages"].append({"page": i+1, "fonts": fonts[:10]})

        if layout_hints["has_text_layer"] and text_parts:
            return "\n\n".join(text_parts), layout_hints

    except Exception as exc:
        logger.warning("pdfplumber_failed", error=str(exc))

    # ── PyMuPDF fallback ──────────────────────────────────────────────────
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(path)
        for page in doc:
            text_parts.append(page.get_text("text"))
        doc.close()
        combined = "\n\n".join(text_parts).strip()
        if combined:
            layout_hints["has_text_layer"] = True
            return combined, layout_hints
    except Exception as exc:
        logger.warning("pymupdf_failed", error=str(exc))

    # ── OCR fallback (pytesseract or Gemini Vision) ───────────────────────
    logger.info("falling_back_to_ocr", path=path)
    ocr_parts = []
    try:
        import fitz
        import pytesseract
        from PIL import Image
        import io

        doc = fitz.open(path)
        for page in doc:
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img, lang="eng+fra+ara")
            if text.strip():
                ocr_parts.append(text)
        doc.close()
        if ocr_parts:
            layout_hints["used_ocr"] = True
            return "\n\n".join(ocr_parts), layout_hints
    except Exception as exc:
        logger.warning("pytesseract_ocr_failed", error=str(exc))

    # ── Gemini Vision fallback for image-based PDFs ───────────────────────
    try:
        from app.core.config import get_settings
        settings = get_settings()
        if settings.gemini_api_key:
            import fitz
            import base64
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage

            doc = fitz.open(path)
            vision_llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.gemini_api_key,
                temperature=0.0
            )
            gemini_parts = []
            for page in doc:
                mat = fitz.Matrix(1.5, 1.5)
                pix = page.get_pixmap(matrix=mat)
                b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
                msg = HumanMessage(content=[
                    {"type": "text", "text": "Extract all CV text verbatim from this page image. Preserve all contact details, work history, education, skills, and dates."},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{b64}"}
                ])
                res = vision_llm.invoke([msg])
                if res and res.content:
                    gemini_parts.append(str(res.content))
            doc.close()
            if gemini_parts:
                layout_hints["used_gemini_vision"] = True
                return "\n\n".join(gemini_parts), layout_hints
    except Exception as exc:
        logger.warning("gemini_vision_fallback_failed", error=str(exc))

    raise ValueError("No readable text could be extracted from this PDF. If it is an image or scan, please use the 'Paste CV as text' option.")


async def _parse_docx(path: str) -> tuple[str, dict]:
    """Parse DOCX with python-docx."""
    import asyncio
    return await asyncio.to_thread(_parse_docx_sync, path)


def _parse_docx_sync(path: str) -> tuple[str, dict]:
    from docx import Document
    doc = Document(path)
    text_parts = []
    fonts: list[dict] = []

    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)
            if para.runs and para.runs[0].font.size:
                fonts.append({
                    "text": para.text[:30],
                    "size": para.runs[0].font.size.pt if para.runs[0].font.size else None,
                    "bold": para.runs[0].bold,
                })

    # Tables
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                text_parts.append(row_text)

    layout_hints = {"has_text_layer": True, "fonts": fonts[:20], "format": "docx"}
    return "\n\n".join(text_parts), layout_hints
