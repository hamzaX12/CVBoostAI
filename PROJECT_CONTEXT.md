# SYSTEM / CONTEXT PROMPT: CVBoost AI

## 1. Project Overview & Mission
- **Project Name:** CVBoost AI
- **Tagline:** "Enhance your CV for better job chances"
- **Purpose:** A modern, AI-powered web platform where job seekers create, optimize, and export ATS-compliant resumes (CVs).
- **Core Value Proposition:**
  1. Split-screen interactive CV builder with instant real-time live preview.
  2. Multi-template rendering: **Simple** (clean ATS-focused, single column), **Classic Navy** (modern sidebar), and **Executive Slate**.
  3. AI-powered CV extraction from existing PDF/DOCX files using Google Gemini.
  4. Real-time web agent for target job market analysis & ranked skill recommendations (via Tavily / DuckDuckGo).
  5. One-click bullet point rewriting using actionable, high-impact phrasing.
  6. ATS compliance checker providing a heuristic audit score (0–100) and actionable improvement feedback.
  7. Client-side and server-side PDF generation producing searchable, ATS-friendly text layers (not flattened images).

---

## 2. Technical Stack & Architecture

### Backend (FastAPI — Port 8000)
- **Framework:** FastAPI (Python 3.11+) with asynchronous routes (`async def`).
- **Data Validation & Schemas:** Pydantic v2. `CVSchema` (`backend/app/schemas/cv.py`) serves as the single source of truth for the CV JSON schema.
- **Database & ORM:** SQLAlchemy (Async Engine) with a SQLite database (`cvboost.db`) by default, fully PostgreSQL-compatible via `DATABASE_URL`.
- **Security & Auth:** Argon2 password hashing, JWT bearer tokens, HTTP-only refresh tokens, SSRF protection (`fetch_tool.py`), magic-byte upload validation, HTML sanitization via `bleach`, and rate limiting via `slowapi`.
- **AI Integration:** Google Gemini (`gemini-2.5-flash` via LangChain / Google Generative AI SDK) for structured CV extraction and bullet improvements.
- **Job Search Agent:** ReAct/tool loop utilizing Tavily Search API (with DuckDuckGo fallback) and SSRF-safe page fetching.
- **PDF Generation:** WeasyPrint + Jinja2 HTML templates (`backend/app/templates/pdf/`) for server-side generation, plus HTML5/Canvas client-side generation.

### Frontend (Streamlit — Port 8501)
- **Framework:** Streamlit (Multi-page app router using `st.navigation` & `st.Page`).
- **Entry Points:** `frontend/app.py` & `frontend/app/app.py` routing between:
  - `1_Landing.py`: High-converting marketing landing page with glassmorphism UI.
  - `2_Builder.py`: Full-viewport split-screen CV builder (collapsible form editor on the left, responsive 1:1 live A4 preview sheet on the right).
- **Styling:** Tailwind CSS CDN injected directly inside iframe components, with Streamlit chrome hidden (`HIDE_STREAMLIT`) to give a native web application feel.
- **State Management:** In-memory session state (`st.session_state["cv"]`) coupled with `cv_state.py` for state initialization, manipulation, and safe fallback templates.

---

## 3. Directory Map & Core Files

```
CVBoost AI/
├── run.py                       # CLI entry point to start backend/frontend
├── to_run.txt                   # Execution commands
├── cvboost.db                   # Local SQLite database
├── PROJECT_CONTEXT.md           # This project architecture & context prompt
├── PROJECT_EXPLANATION.txt      # Detailed technical deep-dive
├── backend/
│   ├── pyproject.toml           # Backend dependencies
│   └── app/
│       ├── main.py              # FastAPI app instance, CORS, routers, health
│       ├── api/v1/              # Endpoints (auth, cv, jobs, contact)
│       ├── core/                # config.py (Settings), security.py, limits.py
│       ├── models/              # db.py (SQLAlchemy ORM), database.py (Session)
│       ├── schemas/cv.py        # Pydantic CVSchema (source of truth)
│       ├── agents/              # extraction_agent.py, job_agent.py, tools/
│       ├── services/            # pdf.py, parsers.py, ats_checker.py
│       ├── templates/pdf/       # Jinja2 PDF templates
│       └── tests/test_all.py    # Unit & integration test suite
└── frontend/
    ├── app.py                   # Streamlit multi-page router & URL normalizer
    └── app/
        ├── components/          # cv_state.py (State), api_client.py (httpx client)
        ├── pages/
        │   ├── 1_Landing.py     # Marketing landing page
        │   └── 2_Builder.py     # Split-screen CV builder & preview engine
        └── styles/theme.py      # Streamlit hiding rules & theme variables
```

---

## 4. Key Workflows & Design Rules

1. **Routing & URL Navigation:**
   - Root URL `http://localhost:8501/` routes to the **Landing Page**.
   - Path `http://localhost:8501/builder` (case-insensitive) routes to the **Builder**.
   - Back button ("CVs") in builder dynamically redirects to `/`.
2. **Preview & PDF Alignment:**
   - Any layout change made to a preview template in `2_Builder.py` (Simple, Classic Navy, Executive Slate) must have matching CSS/structure in the backend PDF generation templates (`backend/app/templates/pdf/`) and client-side PDF export.
   - The Simple template is clean, monochrome/neutral, single-column, and ATS-optimized without photos.
   - The Classic Navy template features a `#1A3B5C` navy left column with contact info, skills, and profile photo, with white background main content.
3. **Data Privacy & Fallback Safety:**
   - No user-specific personal data must be hardcoded in repository files. Default placeholder data is always the inspiring general profile: **Alex Morgan — Senior Data Scientist**.
4. **ATS Priority:**
   - All exported documents must retain selectable text, standard section headings (Profile, Experience, Education, Skills, Projects, Languages, Certifications), and clean semantic structures.

---

## 5. Local Execution Commands
- **Frontend:**
  `python -m streamlit run frontend/app.py --server.port 8501`
- **Backend:**
  `python run.py backend`
- **Testing:**
  `python -m pytest backend/app/tests/test_all.py`

