"""
CVBoost AI — Shared Pydantic v2 CV Schema
Single source of truth for: extraction output, form state,
JSON export, PDF template input, and DB storage.
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class LanguageLevel(str, Enum):
    native = "native"
    advanced = "advanced"
    intermediate = "intermediate"
    basic = "basic"

class SectionType(str, Enum):
    profile = "profile"
    education = "education"
    experience = "experience"
    projects = "projects"
    skills = "skills"
    languages = "languages"
    hobbies = "hobbies"
    courses = "courses"
    internships = "internships"
    extracurricular = "extracurricular"
    references = "references"
    qualities = "qualities"
    certificates = "certificates"
    achievements = "achievements"
    signature = "signature"
    footer = "footer"
    custom = "custom"

class CVLanguage(str, Enum):
    en = "en"
    fr = "fr"
    ar = "ar"

class Template(str, Enum):
    simple = "simple"           # Template 1: Simple (Sebastian Bennett Style) - Default
    sidebar = "sidebar"         # Template 2: Classic Navy
    executive = "executive"     # Template 3: Executive Slate (Laura G. Levell Style)
    classic = "classic"         # Alias for sidebar
    minimal = "minimal"         # Alias for simple

class FontFamily(str, Enum):
    inter = "Inter"
    arial = "Arial"
    roboto = "Roboto"
    lato = "Lato"
    georgia = "Georgia"
    open_sans = "Open Sans"

class SpacingPreset(str, Enum):
    compact = "compact"
    normal = "normal"
    relaxed = "relaxed"

class PhotoShape(str, Enum):
    circle = "circle"
    square = "square"
    none = "none"

class SidebarPosition(str, Enum):
    left = "left"
    right = "right"
    none = "none"


# ─────────────────────────────────────────────────────────────────────────────
# Sub-models
# ─────────────────────────────────────────────────────────────────────────────

class ExtraPersonalField(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    label: str = Field(max_length=60)
    value: str = Field(max_length=200)


class PersonalDetails(BaseModel):
    first_name: str = Field(default="", max_length=80)
    last_name: str = Field(default="", max_length=80)
    headline: str = Field(default="", max_length=120, description="Job title / desired position")
    use_headline: bool = True
    email: str = ""
    phone: str = Field(default="", max_length=30)
    address: str = Field(default="", max_length=200)
    postcode: str = Field(default="", max_length=20)
    city: str = Field(default="", max_length=80)
    country: str = Field(default="", max_length=80)
    date_of_birth: str = Field(default="", max_length=20)
    photo_url: str = Field(default="", description="Local path or base64 data URI")

    # Optional add-on fields (revealed by chips)
    place_of_birth: str = Field(default="", max_length=100)
    driving_licence: str = Field(default="", max_length=60)
    gender: str = Field(default="", max_length=30)
    nationality: str = Field(default="", max_length=60)
    marital_status: str = Field(default="", max_length=30)
    website: str = Field(default="", max_length=200)
    linkedin: str = Field(default="", max_length=200)
    extras: list[ExtraPersonalField] = Field(default_factory=list)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email_format(cls, v: Any) -> str:
        s = str(v or "").strip()
        if not s:
            return ""
        from email_validator import validate_email, EmailNotValidError
        try:
            return validate_email(s, check_deliverability=False).normalized
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {v}") from e


class BulletPoint(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    text: str = Field(max_length=1000)
    improved_text: str | None = None  # AI-improved alternative


class EducationEntry(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    degree: str = Field(default="", max_length=150)
    institution: str = Field(default="", max_length=150)
    location: str = Field(default="", max_length=100)
    start_date: str = Field(default="", max_length=20)
    end_date: str = Field(default="", max_length=20)
    current: bool = False
    description: list[BulletPoint] = Field(default_factory=list)
    gpa: str = Field(default="", max_length=20)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ProjectEntry(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    title: str = Field(default="", max_length=150)
    role: str = Field(default="", max_length=100)
    organization: str = Field(default="", max_length=150)
    location: str = Field(default="", max_length=100)
    start_date: str = Field(default="", max_length=20)
    end_date: str = Field(default="", max_length=20)
    current: bool = False
    url: str = Field(default="", max_length=300)
    description: list[BulletPoint] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ExperienceEntry(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    job_title: str = Field(default="", max_length=150)
    company: str = Field(default="", max_length=150)
    location: str = Field(default="", max_length=100)
    start_date: str = Field(default="", max_length=20)
    end_date: str = Field(default="", max_length=20)
    current: bool = False
    description: list[BulletPoint] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class SkillGroup(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    category: str = Field(max_length=100)
    items: list[str] = Field(default_factory=list)


class LanguageEntry(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    name: str = Field(max_length=60)
    level: LanguageLevel = LanguageLevel.intermediate


class CertificateEntry(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    name: str = Field(max_length=150)
    issuer: str = Field(default="", max_length=100)
    date: str = Field(default="", max_length=20)
    url: str = Field(default="", max_length=300)


class CustomSection(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    title: str = Field(max_length=80)
    items: list[BulletPoint] = Field(default_factory=list)
    hidden: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Style / Layout settings
# ─────────────────────────────────────────────────────────────────────────────

class ColorTheme(BaseModel):
    sidebar_bg: str = Field(default="#09637E", pattern=r"^#[0-9A-Fa-f]{6}$")
    sidebar_text: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    heading_color: str = Field(default="#09637E", pattern=r"^#[0-9A-Fa-f]{6}$")
    accent_color: str = Field(default="#7AB2B2", pattern=r"^#[0-9A-Fa-f]{6}$")
    body_text: str = Field(default="#0F2A33", pattern=r"^#[0-9A-Fa-f]{6}$")
    background: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")


class CVStyle(BaseModel):
    template: Template = Template.simple
    font: FontFamily = FontFamily.inter
    spacing: SpacingPreset = SpacingPreset.normal
    photo_shape: PhotoShape = PhotoShape.circle
    sidebar_position: SidebarPosition = SidebarPosition.left
    sidebar_width_percent: int = Field(default=32, ge=20, le=45)
    colors: ColorTheme = Field(default_factory=ColorTheme)
    cv_language: CVLanguage = CVLanguage.en
    ats_safe_mode: bool = False  # drops photo, single-column


# ─────────────────────────────────────────────────────────────────────────────
# Root CV schema
# ─────────────────────────────────────────────────────────────────────────────

class CVSchema(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    version: int = 1

    personal: PersonalDetails = Field(default_factory=PersonalDetails)
    summary: str = Field(default="", max_length=2000)

    # Section ordering (list of SectionType values)
    sections_order: list[str] = Field(
        default_factory=lambda: [
            "profile", "education", "projects", "skills", "languages"
        ]
    )

    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    skills: list[SkillGroup] = Field(default_factory=list)
    languages: list[LanguageEntry] = Field(default_factory=list)
    certificates: list[CertificateEntry] = Field(default_factory=list)
    hobbies: list[str] = Field(default_factory=list)
    custom_sections: list[CustomSection] = Field(default_factory=list)

    style: CVStyle = Field(default_factory=CVStyle)

    # Metadata
    source_language: str = "en"  # Detected language of uploaded CV
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "personal": {
                    "first_name": "Alex",
                    "last_name": "Morgan",
                    "headline": "Senior Data Scientist",
                    "email": "alex.morgan@example.com",
                },
                "summary": "Results-driven Data Scientist with 4+ years of expertise in Machine Learning, Generative AI, and predictive analytics...",
                "sections_order": ["profile", "education", "experience", "projects", "skills", "languages"],
                "education": [],
                "skills": [
                    {"category": "Machine Learning & AI", "items": ["Python", "PyTorch", "Transformers"]}
                ],
            }
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# Agent output schemas (structured output via with_structured_output)
# ─────────────────────────────────────────────────────────────────────────────

class SuggestedSkill(BaseModel):
    category: str = Field(max_length=100)
    name: str = Field(max_length=80)
    importance: int = Field(ge=1, le=5, description="1=nice-to-have, 5=must-have")
    evidence_urls: list[str] = Field(default_factory=list)
    why: str = Field(default="", max_length=300, description="Short explanation for tooltip")
    model_knowledge: bool = Field(
        default=False,
        description="True if no evidence URL backs this suggestion"
    )


class SuggestedLanguage(BaseModel):
    name: str = Field(max_length=60)
    level: LanguageLevel = LanguageLevel.intermediate
    why: str = Field(default="", max_length=200)


class JobAnalysisResult(BaseModel):
    role_detected: str = Field(max_length=100)
    skills: list[SuggestedSkill] = Field(default_factory=list)
    languages: list[SuggestedLanguage] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    search_queries_used: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class FieldConfidence(BaseModel):
    field_path: str
    confidence: float = Field(ge=0.0, le=1.0)
    note: str = ""


class CVExtractionResult(BaseModel):
    cv: CVSchema
    confidences: list[FieldConfidence] = Field(default_factory=list)
    detected_language: str = "en"
    warnings: list[str] = Field(default_factory=list)


class ImproveBulletResult(BaseModel):
    original: str
    improved: str
    explanation: str = ""


class ImproveSummaryResult(BaseModel):
    original: str
    improved: str
    explanation: str = "Enhanced with executive professional tone"


# ─────────────────────────────────────────────────────────────────────────────
# API request / response helpers
# ─────────────────────────────────────────────────────────────────────────────

class ContactMessage(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(min_length=10, max_length=2000)
    honeypot: str = Field(default="", description="Must be empty; spam trap")


class AtsCheckResult(BaseModel):
    score: int = Field(ge=0, le=100)
    sections_found: list[str] = Field(default_factory=list)
    sections_missing: list[str] = Field(default_factory=list)
    email_found: bool = False
    phone_found: bool = False
    skills_found: bool = False
    reading_order_ok: bool = False
    garbled_chars: bool = False
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
