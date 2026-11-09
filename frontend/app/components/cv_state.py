"""
CVBoost AI — CV State Management
Single source of truth in st.session_state["cv"]
"""
from __future__ import annotations

import copy
import uuid
from typing import Any

import streamlit as st


def init_cv_state(force_sample: bool = False) -> None:
    """Initialize the CV state if not present or if stale/personal data detected."""
    import json
    curr_cv = st.session_state.get("cv")
    should_reset = False
    if curr_cv is None or force_sample or not isinstance(curr_cv, dict):
        should_reset = True
    else:
        try:
            raw = json.dumps(curr_cv).lower()
            if any(w in raw for w in ["hamza", "ben allou", "benallou", "safi", "devo soft", "est safi"]) or not curr_cv.get("personal", {}).get("first_name"):
                should_reset = True
        except Exception:
            should_reset = True

    if should_reset:
        st.session_state["cv"] = _empty_cv()
    if "cv_id" not in st.session_state:
        st.session_state["cv_id"] = None
    if "suggested_skills" not in st.session_state:
        st.session_state["suggested_skills"] = []
    if "suggested_languages" not in st.session_state:
        st.session_state["suggested_languages"] = []
    if "job_sources" not in st.session_state:
        st.session_state["job_sources"] = []


def reorder_sections(new_order: list[str]) -> None:
    """Update sections display order."""
    cv = get_cv()
    cv["sections_order"] = new_order


def move_section_up(section_key: str) -> None:
    """Move a section up by one in the display order."""
    cv = get_cv()
    order = cv.get("sections_order", [])
    if section_key in order:
        idx = order.index(section_key)
        if idx > 0:
            order[idx], order[idx - 1] = order[idx - 1], order[idx]


def move_section_down(section_key: str) -> None:
    """Move a section down by one in the display order."""
    cv = get_cv()
    order = cv.get("sections_order", [])
    if section_key in order:
        idx = order.index(section_key)
        if idx < len(order) - 1:
            order[idx], order[idx + 1] = order[idx + 1], order[idx]


def get_cv() -> dict:
    return st.session_state["cv"]


def update_cv(path: list[str | int], value: Any) -> None:
    """Update a nested field in the CV state."""
    d = st.session_state["cv"]
    for key in path[:-1]:
        d = d[key]
    d[path[-1]] = value


def load_cv_from_extraction(extraction_result: dict) -> None:
    """Load extracted CV data into session state."""
    if "cv" in extraction_result:
        st.session_state["cv"] = extraction_result["cv"]
        # Highlight low-confidence fields
        st.session_state["low_confidence_fields"] = [
            c["field_path"] for c in extraction_result.get("confidences", [])
            if c.get("confidence", 1.0) < 0.7
        ]


def _empty_cv() -> dict:
    return {
        "id": uuid.uuid4().hex,
        "version": 1,
        "cv_name": "CV Alex Morgan",
        "personal": {
            "first_name": "Alex",
            "last_name": "Morgan",
            "headline": "Senior Data Scientist",
            "use_headline": True,
            "email": "alex.morgan@example.com",
            "phone": "+1 (555) 019-2834",
            "address": "San Francisco, CA",
            "postcode": "94105",
            "city": "San Francisco",
            "country": "United States",
            "date_of_birth": "1998-05-14",
            "photo_url": "",
            "place_of_birth": "California",
            "driving_licence": "Class C",
            "gender": "",
            "nationality": "American",
            "marital_status": "",
            "website": "alexmorgan.dev",
            "linkedin": "linkedin.com/in/alex-morgan-ai",
            "extras": [],
        },
        "summary": "Results-driven Senior Data Scientist with 4+ years of expertise in Machine Learning, Generative AI, and predictive analytics. Proven track record of architecting scalable ML pipelines and production-ready LLM solutions that enhance decision-making and drive high-impact business outcomes. Passionate about transforming complex datasets into actionable strategic intelligence.",
        "sections_order": ["profile", "education", "experience", "projects", "skills", "languages"],
        "education": [
            {
                "id": "edu1",
                "degree": "Master of Science in Artificial Intelligence and Data Science",
                "institution": "Stanford University",
                "location": "Stanford, CA",
                "start_date": "2021",
                "end_date": "2023",
                "current": False,
                "description": [
                    {"id": "edu_b1", "text": "Graduated with Honors; specialized in Deep Learning, NLP, and Distributed Computing"},
                    {"id": "edu_b2", "text": "Published research on scalable Transformer fine-tuning and retrieval-augmented generation"}
                ],
                "confidence": 1.0,
            },
            {
                "id": "edu2",
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of California, Berkeley",
                "location": "Berkeley, CA",
                "start_date": "2017",
                "end_date": "2021",
                "current": False,
                "description": [
                    {"id": "edu_b3", "text": "Dean's Honor List for 6 consecutive semesters; President of Data Science Society"}
                ],
                "confidence": 1.0,
            },
        ],
        "experience": [
            {
                "id": "exp1",
                "title": "Senior Data Scientist",
                "role": "Lead ML Engineer",
                "company": "Apex Analytics Inc.",
                "location": "San Francisco, CA",
                "start_date": "2023",
                "end_date": "Present",
                "current": True,
                "description": [
                    {"id": "exp_b1", "text": "Spearheaded end-to-end deployment of an enterprise RAG copilot, reducing customer query resolution time by 42%"},
                    {"id": "exp_b2", "text": "Architected real-time predictive fraud detection models processing 2M+ daily transactions with 99.4% precision"},
                    {"id": "exp_b3", "text": "Mentored a cross-functional squad of 5 junior data scientists and established team-wide CI/CD MLOps best practices"}
                ],
                "confidence": 1.0,
            },
            {
                "id": "exp2",
                "title": "Machine Learning Engineer",
                "role": "ML Engineer",
                "company": "DataVanguard Labs",
                "location": "San Jose, CA",
                "start_date": "2021",
                "end_date": "2023",
                "current": False,
                "description": [
                    {"id": "exp_b4", "text": "Engineered automated ETL pipelines utilizing Apache Spark and AWS Redshift, cutting pipeline latency by 35%"},
                    {"id": "exp_b5", "text": "Developed customer churn forecasting models yielding a 12% boost in retention rate across key subscription tiers"}
                ],
                "confidence": 1.0,
            },
        ],
        "projects": [
            {
                "id": "proj1",
                "title": "Intelligent Multimodal Search Engine",
                "role": "Lead Architect",
                "organization": "Open Source Project",
                "start_date": "2023",
                "end_date": "2024",
                "current": False,
                "description": [
                    {"id": "b1", "text": "Built a vector semantic search engine using LangChain, Qdrant, and OpenAI embeddings indexing 50k+ technical documents"},
                    {"id": "b2", "text": "Implemented hybrid BM25 and dense vector re-ranking, boosting retrieval accuracy by 28%"}
                ],
                "technologies": ["Python", "FastAPI", "Qdrant", "LangChain", "Docker"],
                "confidence": 1.0,
            },
            {
                "id": "proj2",
                "title": "Autonomous Vision Quality Inspection",
                "role": "AI Specialist",
                "organization": "Innovation Lab",
                "start_date": "2022",
                "end_date": "2023",
                "current": False,
                "description": [
                    {"id": "b3", "text": "Designed high-speed computer vision anomaly detection using YOLOv8 and PyTorch with 98.7% classification accuracy"}
                ],
                "technologies": ["PyTorch", "OpenCV", "YOLOv8", "TensorRT"],
                "confidence": 1.0,
            },
        ],
        "skills": [
            {
                "id": "s1",
                "category": "Machine Learning & AI",
                "items": ["Deep Learning", "Transformers & LLMs", "RAG & LangChain", "Computer Vision", "NLP", "Scikit-Learn", "PyTorch"]
            },
            {
                "id": "s2",
                "category": "Data Engineering & MLOps",
                "items": ["Apache Spark", "Docker", "Kubernetes", "AWS (SageMaker, S3)", "FastAPI", "PostgreSQL", "MLflow"]
            },
            {
                "id": "s3",
                "category": "Analytics & Visualization",
                "items": ["SQL", "Power BI", "Tableau", "Pandas", "Statistical Modeling", "A/B Testing"]
            },
        ],
        "languages": [
            {"id": "l1", "name": "English", "level": "Native"},
            {"id": "l2", "name": "French", "level": "Professional"},
            {"id": "l3", "name": "Spanish", "level": "Conversational"},
        ],
        "certificates": [
            {
                "id": "c1",
                "title": "AWS Certified Machine Learning - Specialty",
                "name": "AWS Certified Machine Learning - Specialty",
                "issuer": "Amazon Web Services",
                "date": "2023",
            }
        ],
        "hobbies": ["Open Source Contributing", "Marathon Running", "Astrophotography", "Chess"],
        "custom_sections": [],
        "style": {
            "template": "sidebar",
            "font": "Inter",
            "spacing": "normal",
            "photo_shape": "circle",
            "sidebar_position": "left",
            "sidebar_width_percent": 34,
            "colors": {
                "sidebar_bg": "#1A3B5C",
                "sidebar_text": "#FFFFFF",
                "heading_color": "#1A3B5C",
                "accent_color": "#1A3B5C",
                "body_text": "#222222",
                "background": "#FFFFFF",
            },
            "cv_language": "en",
            "ats_safe_mode": False,
        },
        "source_language": "en",
        "created_at": "",
        "updated_at": "",
    }


def add_skill_to_cv(category: str, skill_name: str) -> None:
    """Add a skill to the matching category (case-insensitive dedup)."""
    cv = get_cv()
    skills = cv.get("skills", [])
    skill_lower = skill_name.lower()

    # Check dedup across all categories
    for group in skills:
        if any(s.lower() == skill_lower for s in group.get("items", [])):
            return  # Already exists

    # Find matching category or create
    category_lower = category.lower()
    for group in skills:
        if group.get("category", "").lower() == category_lower:
            group["items"].append(skill_name)
            return

    # Create new category
    cv["skills"].append({
        "id": uuid.uuid4().hex[:8],
        "category": category,
        "items": [skill_name],
    })


def remove_skill_from_cv(category: str, skill_name: str) -> None:
    cv = get_cv()
    skill_lower = skill_name.lower()
    for group in cv.get("skills", []):
        if group.get("category", "").lower() == category.lower():
            group["items"] = [s for s in group["items"] if s.lower() != skill_lower]
            break


def add_language_to_cv(name: str, level: str) -> None:
    cv = get_cv()
    langs = cv.get("languages", [])
    if not any(l.get("name", "").lower() == name.lower() for l in langs):
        langs.append({"id": uuid.uuid4().hex[:8], "name": name, "level": level})


def add_education_entry() -> None:
    cv = get_cv()
    cv["education"].append({
        "id": uuid.uuid4().hex[:8],
        "degree": "",
        "institution": "",
        "location": "",
        "start_date": "",
        "end_date": "",
        "current": False,
        "description": [],
        "gpa": "",
        "confidence": 1.0,
    })


def add_project_entry() -> None:
    cv = get_cv()
    cv["projects"].append({
        "id": uuid.uuid4().hex[:8],
        "title": "",
        "role": "",
        "organization": "",
        "location": "",
        "start_date": "",
        "end_date": "",
        "current": False,
        "url": "",
        "description": [],
        "technologies": [],
        "confidence": 1.0,
    })


def add_bullet(section: str, entry_id: str, text: str) -> None:
    cv = get_cv()
    for entry in cv.get(section, []):
        if entry.get("id") == entry_id:
            entry.setdefault("description", []).append({
                "id": uuid.uuid4().hex[:8],
                "text": text,
                "improved_text": None,
            })
            break
