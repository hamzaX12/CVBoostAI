"""
CVBoost AI — API Client for Streamlit Frontend
Handles all communication with the FastAPI backend.
"""
from __future__ import annotations

import os
import time
from typing import Any, Generator

import httpx
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 60.0


def _get_headers() -> dict[str, str]:
    """Get auth headers from session state."""
    token = st.session_state.get("access_token", "")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _client() -> httpx.Client:
    return httpx.Client(base_url=API_BASE, timeout=TIMEOUT, headers=_get_headers())


# ── Auth ──────────────────────────────────────────────────────────────────────

def register(email: str, password: str, full_name: str = "") -> dict | None:
    try:
        with _client() as c:
            r = c.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": full_name})
            if r.is_success:
                data = r.json()
                st.session_state["access_token"] = data["access_token"]
                st.session_state["user"] = data["user"]
                return data
            st.error(r.json().get("detail", "Registration failed"))
    except (httpx.ConnectError, httpx.NetworkError):
        st.error("Backend is not running. Please start it with: python run.py")
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None


def login(email: str, password: str) -> dict | None:
    try:
        with _client() as c:
            r = c.post("/api/v1/auth/login", json={"email": email, "password": password})
            if r.is_success:
                data = r.json()
                st.session_state["access_token"] = data["access_token"]
                st.session_state["user"] = data["user"]
                return data
            st.error(r.json().get("detail", "Login failed"))
    except (httpx.ConnectError, httpx.NetworkError):
        st.error("Backend is not running. Please start it with: python run.py")
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None


def guest_session() -> dict | None:
    try:
        with _client() as c:
            r = c.post("/api/v1/auth/guest")
            if r.is_success:
                data = r.json()
                st.session_state["access_token"] = data["access_token"]
                st.session_state["user"] = data["user"]
                st.session_state["backend_offline"] = False
                return data
    except Exception:
        st.session_state["backend_offline"] = True
    return None


# ── CV operations ─────────────────────────────────────────────────────────────

def extract_cv(file_bytes: bytes, filename: str, content_type: str) -> dict | None:
    try:
        with _client() as c:
            r = c.post(
                "/api/v1/cv/extract",
                files={"file": (filename, file_bytes, content_type)},
                timeout=120.0,
            )
            if r.is_success:
                return r.json()
            st.error(r.json().get("detail", "Extraction failed"))
    except Exception as e:
        st.error(f"Extraction error: {e}")
    return None


def generate_pdf(cv_data: dict) -> bytes | None:
    try:
        with _client() as c:
            r = c.post("/api/v1/cv/pdf", json=cv_data, timeout=60.0)
            if r.is_success:
                return r.content
            st.error(r.json().get("detail", "PDF generation failed"))
    except Exception as e:
        st.error(f"PDF error: {e}")
    return None


def check_ats(file_bytes: bytes, filename: str = "cv.pdf") -> dict | None:
    """Send generated or uploaded PDF to backend ATS compliance checker."""
    try:
        with _client() as c:
            r = c.post(
                "/api/v1/cv/ats-check",
                files={"file": (filename, file_bytes, "application/pdf")},
                timeout=45.0,
            )
            if r.is_success:
                return r.json()
            st.error(r.json().get("detail", "ATS check failed"))
    except Exception as e:
        st.error(f"ATS check error: {e}")
    return None


def improve_bullet(bullet: str, context: str = "") -> dict | None:
    try:
        with _client() as c:
            r = c.post(
                "/api/v1/cv/improve-bullet",
                json={"bullet": bullet, "context": context},
                timeout=30.0,
            )
            if r.is_success:
                return r.json()
            st.error("Improvement failed")
    except Exception as e:
        st.error(f"AI error: {e}")
    return None


def save_cv(cv_data: dict, cv_id: str | None = None) -> str | None:
    try:
        with _client() as c:
            if cv_id:
                r = c.put(f"/api/v1/cv/{cv_id}", json=cv_data)
            else:
                r = c.post("/api/v1/cv/", json=cv_data)
            if r.is_success:
                return r.json().get("id")
            st.error("Save failed")
    except Exception as e:
        st.error(f"Save error: {e}")
    return None


def submit_contact(name: str, email: str, message: str) -> bool:
    try:
        with httpx.Client(base_url=API_BASE, timeout=15.0) as c:
            r = c.post(
                "/api/v1/contact/",
                json={"name": name, "email": email, "message": message, "honeypot": ""},
            )
            return r.is_success
    except Exception:
        return False


# ── Job analysis (SSE streaming) ──────────────────────────────────────────────

def stream_job_analysis(
    query: str,
    country: str = "",
    seniority: str = "",
    current_skills: list[str] | None = None,
) -> Generator[dict[str, Any], None, None]:
    """Yields dicts: {"type": "progress"|"result"|"error", ...}"""
    payload = {
        "query": query,
        "country": country,
        "seniority": seniority,
        "current_skills": current_skills or [],
    }
    headers = {**_get_headers(), "Accept": "text/event-stream"}
    try:
        with httpx.Client(base_url=API_BASE, timeout=90.0, headers=headers) as c:
            with c.stream("POST", "/api/v1/jobs/analyze", json=payload) as response:
                import json as _json
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            yield _json.loads(data_str)
                        except _json.JSONDecodeError:
                            continue
    except Exception as e:
        yield {"type": "error", "message": str(e)}
