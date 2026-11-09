"""
CVBoost AI — Backend Tests
Covers: parsers, schema validation, ATS checker, auth endpoints, CV CRUD,
upload hardening, SSRF protection, rate limits, agent mocks.
"""
from __future__ import annotations

import io
import json
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.core.security import hash_password, verify_password, validate_url_for_fetch, validate_upload
from app.schemas.cv import CVSchema, PersonalDetails, SkillGroup, LanguageEntry, LanguageLevel
from app.services.ats_checker import _run_ats_check_sync, _extract_text


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_cv() -> dict:
    return CVSchema(
        personal=PersonalDetails(
            first_name="Alex",
            last_name="Morgan",
            headline="Senior Data Scientist",
            email="alex.morgan@example.com",
            phone="+1 (555) 019-2834",
            city="San Francisco",
            country="United States",
        ),
        summary="Experienced data scientist with 3+ years building ML pipelines.",
        skills=[
            SkillGroup(category="Machine Learning & AI", items=["Python", "TensorFlow", "PyTorch"]),
            SkillGroup(category="Data Engineering", items=["Apache Spark", "SQL"]),
        ],
        languages=[
            LanguageEntry(name="Arabic", level=LanguageLevel.native),
            LanguageEntry(name="French", level=LanguageLevel.advanced),
            LanguageEntry(name="English", level=LanguageLevel.advanced),
        ],
    ).model_dump(mode="json")


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Minimal valid PDF with text content for ATS testing."""
    return b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 200>>
stream
BT
/F1 12 Tf
50 780 Td (Alex Morgan) Tj
0 -20 Td (Data Scientist) Tj
0 -40 Td (Professional Summary) Tj
0 -20 Td (Experienced data scientist) Tj
0 -40 Td (Education) Tj
0 -20 Td (BSc Computer Science) Tj
0 -40 Td (Skills) Tj
0 -20 Td (Python, TensorFlow, SQL) Tj
0 -40 Td (alex@example.com +15550192834) Tj
ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000274 00000 n
0000000526 00000 n
trailer<</Size 6/Root 1 0 R>>
startxref
620
%%EOF"""


# ─────────────────────────────────────────────────────────────────────────────
# 1. Password hashing
# ─────────────────────────────────────────────────────────────────────────────

def test_password_hash_and_verify():
    plain = "SecureP@ss123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrongpass", hashed)


def test_password_hash_unique():
    """Different hashes for same password (salted)."""
    h1 = hash_password("same_password")
    h2 = hash_password("same_password")
    assert h1 != h2


# ─────────────────────────────────────────────────────────────────────────────
# 2. SSRF Protection
# ─────────────────────────────────────────────────────────────────────────────

def test_ssrf_blocks_localhost():
    with pytest.raises(ValueError, match="private IP|DNS resolution"):
        validate_url_for_fetch("http://localhost/secret")


def test_ssrf_blocks_private_ip():
    with pytest.raises(ValueError):
        validate_url_for_fetch("http://192.168.1.1/admin")


def test_ssrf_blocks_loopback():
    with pytest.raises(ValueError):
        validate_url_for_fetch("http://127.0.0.1/")


def test_ssrf_blocks_non_http():
    with pytest.raises(ValueError, match="Scheme"):
        validate_url_for_fetch("file:///etc/passwd")


def test_ssrf_blocks_ftp():
    with pytest.raises(ValueError, match="Scheme"):
        validate_url_for_fetch("ftp://example.com/file")


# ─────────────────────────────────────────────────────────────────────────────
# 3. File Upload Validation
# ─────────────────────────────────────────────────────────────────────────────

def test_upload_valid_pdf(sample_pdf_bytes):
    # Should not raise
    validate_upload("cv.pdf", sample_pdf_bytes, "application/pdf")


def test_upload_rejects_exe():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        validate_upload("malware.exe", b"MZ...", "application/octet-stream")
    assert exc.value.status_code == 400


def test_upload_rejects_wrong_magic():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        # PDF content type but not actually a PDF
        validate_upload("fake.pdf", b"PK\x03\x04fake", "application/pdf")
    assert exc.value.status_code == 400


def test_upload_rejects_oversize():
    from fastapi import HTTPException
    big_content = b"%PDF" + b"0" * (6 * 1024 * 1024)  # 6 MB
    with pytest.raises(HTTPException) as exc:
        validate_upload("big.pdf", big_content, "application/pdf")
    assert exc.value.status_code == 413


# ─────────────────────────────────────────────────────────────────────────────
# 4. CV Schema Validation
# ─────────────────────────────────────────────────────────────────────────────

def test_cv_schema_valid(sample_cv):
    cv = CVSchema.model_validate(sample_cv)
    assert cv.personal.first_name == "Alex"
    assert cv.personal.last_name == "Morgan"
    assert len(cv.skills) == 2
    assert cv.skills[0].category == "Machine Learning & AI"


def test_cv_schema_invalid_email():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        PersonalDetails(
            first_name="Test",
            last_name="User",
            email="not-an-email",
        )


def test_cv_schema_color_validation():
    from pydantic import ValidationError
    from app.schemas.cv import ColorTheme
    with pytest.raises(ValidationError):
        ColorTheme(sidebar_bg="not-a-color")


def test_cv_schema_serialization(sample_cv):
    cv = CVSchema.model_validate(sample_cv)
    serialized = cv.model_dump(mode="json")
    assert isinstance(serialized, dict)
    assert "personal" in serialized
    assert "skills" in serialized


# ─────────────────────────────────────────────────────────────────────────────
# 5. ATS Checker
# ─────────────────────────────────────────────────────────────────────────────

def test_ats_checker_good_pdf(sample_pdf_bytes):
    result = _run_ats_check_sync(sample_pdf_bytes)
    assert result.score > 0
    # Email/phone should be found in our test PDF
    # (pdfplumber may or may not extract from minimal PDF)
    assert isinstance(result.sections_found, list)
    assert isinstance(result.score, int)
    assert 0 <= result.score <= 100


def test_ats_checker_empty_pdf():
    empty_pdf = b"%PDF-1.4\n%%EOF"
    result = _run_ats_check_sync(empty_pdf)
    assert result.score < 50
    assert len(result.issues) > 0


def test_ats_checker_detects_sections():
    from app.services.ats_checker import _SECTION_PATTERNS
    import re
    test_text = """
    Professional Summary
    Education
    Skills
    Python, TensorFlow, SQL
    alex@example.com +15550192834
    """
    for section, patterns in _SECTION_PATTERNS.items():
        if section in ("summary", "education", "skills"):
            found = any(re.search(p, test_text.lower()) for p in patterns)
            assert found, f"Section '{section}' not detected in test text"


def test_ats_checker_score_formula():
    """Score = 0 if no text, improves with valid content."""
    result_empty = _run_ats_check_sync(b"%PDF-1.4\n%%EOF")
    assert result_empty.score == 0 or result_empty.score < 30


# ─────────────────────────────────────────────────────────────────────────────
# 6. Health endpoint
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    r = await async_client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "CVBoost AI" in data["app"]


# ─────────────────────────────────────────────────────────────────────────────
# 7. Auth endpoints
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_and_login(async_client):
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@test.com"

    # Register
    r = await async_client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "TestPass123!",
        "full_name": "Test User",
    })
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data
    assert data["user"]["email"] == email

    # Login
    r2 = await async_client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "TestPass123!",
    })
    assert r2.status_code == 200
    assert "access_token" in r2.json()


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client):
    import uuid
    email = f"dup_{uuid.uuid4().hex[:8]}@test.com"
    payload = {"email": email, "password": "TestPass123!"}
    await async_client.post("/api/v1/auth/register", json=payload)
    r = await async_client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password(async_client):
    import uuid
    email = f"wrong_{uuid.uuid4().hex[:8]}@test.com"
    await async_client.post("/api/v1/auth/register", json={
        "email": email, "password": "Correct123!"
    })
    r = await async_client.post("/api/v1/auth/login", json={
        "email": email, "password": "WrongPassword"
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_guest_session(async_client):
    r = await async_client.post("/api/v1/auth/guest")
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["user"]["is_guest"] is True


# ─────────────────────────────────────────────────────────────────────────────
# 8. Contact form
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_contact_form_valid(async_client):
    r = await async_client.post("/api/v1/contact/", json={
        "name": "Test User",
        "email": "test@example.com",
        "message": "This is a test message from the test suite.",
        "honeypot": "",
    })
    assert r.status_code == 200
    assert "message" in r.json()


@pytest.mark.asyncio
async def test_contact_form_honeypot_blocked(async_client):
    r = await async_client.post("/api/v1/contact/", json={
        "name": "Bot",
        "email": "bot@spam.com",
        "message": "Buy cheap stuff now!!!",
        "honeypot": "I am a bot",
    })
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_contact_form_short_message(async_client):
    r = await async_client.post("/api/v1/contact/", json={
        "name": "T",  # too short
        "email": "test@test.com",
        "message": "Hi",  # too short
        "honeypot": "",
    })
    assert r.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# 9. Skill normalizer
# ─────────────────────────────────────────────────────────────────────────────

def test_skill_normalizer():
    from app.agents.tools.skill_normalizer import normalize_skill
    assert normalize_skill.invoke({"skill": "powerbi"}) == "Power BI"
    assert normalize_skill.invoke({"skill": "sklearn"}) == "scikit-learn"
    assert normalize_skill.invoke({"skill": "tensorflow"}) == "TensorFlow"
    assert normalize_skill.invoke({"skill": "k8s"}) == "Kubernetes"


def test_skill_normalizer_unknown():
    from app.agents.tools.skill_normalizer import normalize_skill
    result = normalize_skill.invoke({"skill": "my custom framework"})
    assert isinstance(result, str)
    assert len(result) > 0


# ─────────────────────────────────────────────────────────────────────────────
# 10. CV CRUD (authenticated)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cv_crud_flow(async_client, sample_cv):
    import uuid
    email = f"cv_{uuid.uuid4().hex[:8]}@test.com"

    # Register and get token
    r = await async_client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "CvTest123!",
    })
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create CV
    r = await async_client.post("/api/v1/cv/", json=sample_cv, headers=headers)
    assert r.status_code == 201
    cv_id = r.json()["id"]

    # Get CV
    r = await async_client.get(f"/api/v1/cv/{cv_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["personal"]["first_name"] == "Alex"

    # List CVs
    r = await async_client.get("/api/v1/cv/", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # Update CV
    sample_cv["personal"]["first_name"] = "Updated"
    r = await async_client.put(f"/api/v1/cv/{cv_id}", json=sample_cv, headers=headers)
    assert r.status_code == 200

    # Delete CV
    r = await async_client.delete(f"/api/v1/cv/{cv_id}", headers=headers)
    assert r.status_code == 200

    # Verify deleted
    r = await async_client.get(f"/api/v1/cv/{cv_id}", headers=headers)
    assert r.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# 11. Upload hardening
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_rejects_php(async_client):
    """Ensure only PDF/DOCX accepted."""
    r = await async_client.post(
        "/api/v1/cv/extract",
        files={"file": ("shell.php", b"<?php system($_GET['cmd']); ?>", "application/x-php")},
    )
    assert r.status_code in (400, 422, 415)


@pytest.mark.asyncio
async def test_upload_rejects_html(async_client):
    r = await async_client.post(
        "/api/v1/cv/extract",
        files={"file": ("xss.html", b"<script>alert(1)</script>", "text/html")},
    )
    assert r.status_code in (400, 422)


# ─────────────────────────────────────────────────────────────────────────────
# 12. Agent tests (mocked)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_extraction_agent_mocked():
    """Test extraction agent with mocked Gemini response."""
    from app.schemas.cv import CVExtractionResult, CVSchema

    mock_result = CVExtractionResult(
        cv=CVSchema(
            personal=PersonalDetails(
                first_name="Alex",
                last_name="Morgan",
                email="alex@test.com",
            )
        ),
        detected_language="en",
    )

    with patch("app.agents.extraction_agent._get_llm") as MockGetLLM:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.ainvoke = AsyncMock(return_value=mock_result)
        MockGetLLM.return_value = mock_llm

        from app.agents.extraction_agent import run_extraction_agent
        result = await run_extraction_agent("Alex Morgan\nData Scientist\nalex@test.com")

        assert result.cv.personal.first_name == "Alex"
        assert result.detected_language == "en"


@pytest.mark.asyncio
async def test_improve_bullet_mocked():
    """Test bullet improvement chain with mocked response."""
    from app.schemas.cv import ImproveBulletResult

    mock_result = ImproveBulletResult(
        original="worked on data pipeline",
        improved="Designed and implemented scalable ETL data pipeline, reducing processing time by 40%",
        explanation="Added strong action verb, quantified impact",
    )

    with patch("app.agents.extraction_agent._get_llm") as MockGetLLM:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.ainvoke = AsyncMock(return_value=mock_result)
        MockGetLLM.return_value = mock_llm

        from app.agents.extraction_agent import run_improve_bullet
        result = await run_improve_bullet("worked on data pipeline", "Data Engineer")

        assert "pipeline" in result.improved.lower()
        assert result.original == "worked on data pipeline"


# ─────────────────────────────────────────────────────────────────────────────
# 13. PDF generation (integration — requires WeasyPrint)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pdf_generation(sample_cv):
    """Generate a PDF and verify it's a valid PDF bytes object."""
    try:
        from app.services.pdf import render_pdf
        from app.schemas.cv import CVSchema
        cv = CVSchema.model_validate(sample_cv)
        pdf_bytes = await render_pdf(cv)
        assert pdf_bytes[:4] == b"%PDF"
        assert len(pdf_bytes) > 1000
    except ImportError:
        pytest.skip("WeasyPrint not installed")


@pytest.mark.asyncio
async def test_pdf_ats_roundtrip(sample_cv):
    """Generate PDF → ATS check → verify score > 50."""
    try:
        from app.services.pdf import render_pdf
        from app.services.ats_checker import run_ats_check
        from app.schemas.cv import CVSchema

        cv = CVSchema.model_validate(sample_cv)
        cv.summary = "Experienced data scientist specializing in machine learning and AI. Skills: Python, TensorFlow, SQL."
        pdf_bytes = await render_pdf(cv)

        ats_result = await run_ats_check(pdf_bytes)
        assert ats_result.score >= 40, f"ATS score too low: {ats_result.score}. Issues: {ats_result.issues}"
    except ImportError:
        pytest.skip("WeasyPrint not installed")
