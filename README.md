# CVBoost AI 🚀

> **"Enhance your CV for better job chances"**

AI-powered, ATS-optimized CV builder built with FastAPI, Streamlit, LangChain, Gemini, and WeasyPrint.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI CV Extraction** | Upload PDF/DOCX → Gemini extracts all data with confidence scores |
| 🎯 **Job Targeting** | Type a job → agent searches web, suggests ranked skills with sources |
| ✏️ **Interactive CV Editor** | Side-by-side editor with live preview, drag-and-drop sections |
| 📄 **ATS-Optimized PDF** | WeasyPrint PDF with real text layer, 3 templates, multilingual |
| ✅ **ATS Checker** | Score 0-100, section detection, email/phone parsing, garbled text |
| ✨ **Improve Bullet** | AI rewrites bullets with action verbs — shows diff, you accept/reject |
| 🔒 **Production Security** | Argon2, JWT, SSRF protection, file hardening, rate limiting, CORS |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CVBoost AI                                  │
│                                                                   │
│  ┌──────────────────┐          ┌────────────────────────────┐    │
│  │  Streamlit       │ HTTP/SSE │      FastAPI Backend        │    │
│  │  Frontend        │◄────────►│  /api/v1/...               │    │
│  │  (Port 8501)     │          │  (Port 8000)               │    │
│  │                  │          │                            │    │
│  │  • Landing Page  │          │  ┌──────────────────────┐  │    │
│  │  • CV Builder    │          │  │  AI Agents           │  │    │
│  │  • Live Preview  │          │  │  • Job Agent (SSE)   │  │    │
│  └──────────────────┘          │  │  • CV Extraction     │  │    │
│                                │  │  • Bullet Improver   │  │    │
│                                │  └──────────────────────┘  │    │
│                                │  ┌──────────────────────┐  │    │
│                                │  │  Services            │  │    │
│                                │  │  • PDF (WeasyPrint)  │  │    │
│                                │  │  • ATS Checker       │  │    │
│                                │  │  • File Parsers      │  │    │
│                                │  └──────────────────────┘  │    │
│                                │  ┌──────────────────────┐  │    │
│                                │  │  SQLite / PostgreSQL  │  │    │
│                                │  └──────────────────────┘  │    │
│                                └────────────────────────────┘    │
│                                                                   │
│  External: Gemini API, Tavily Search, DuckDuckGo               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/cvboost-ai/cvboost-ai
cd cvboost-ai
cp .env.example .env
# Edit .env with your API keys
```

### 2. With Docker (recommended)

```bash
docker compose up --build
```

- Frontend: http://localhost:8501  
- Backend API: http://localhost:8000/api/docs

### 3. Manual (development)

```bash
# Backend
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
pip install -r requirements-frontend.txt
streamlit run app/app.py --server.port 8501
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key |
| `TAVILY_API_KEY` | ⚠️ | Tavily search key (falls back to DuckDuckGo) |
| `JWT_SECRET_KEY` | ✅ | 64+ char random string for JWT signing |
| `APP_SECRET_KEY` | ✅ | 32+ char app secret key |
| `DATABASE_URL` | ⚡ | SQLite (default) or PostgreSQL URL |
| `GEMINI_MODEL` | ⚡ | Default: `gemini-3.5-flash` |
| `SMTP_HOST/USER/PASS` | 📧 | For contact form email sending |
| `REDIS_URL` | 🔄 | Redis for rate limiting (falls back to in-memory) |

Get your Gemini API key: https://aistudio.google.com/app/apikey

---

## 🧪 Tests

```bash
# All tests
cd backend && pytest app/tests/ -v

# Fast (no PDF generation)
cd backend && pytest app/tests/ -v -k "not pdf"

# Security scan
cd backend && bandit -r app/ -ll
cd backend && pip-audit

# Lint
cd backend && ruff check app/ --fix
```

---

## 📁 Project Structure

```
cvboost-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── api/v1/              # Endpoints: auth, cv, jobs, contact
│   │   ├── core/                # config, security, limits, logging
│   │   ├── agents/              # Job agent, CV extraction agent
│   │   │   └── tools/           # search, fetch_page, skill_normalizer
│   │   ├── services/            # pdf, ats_checker, parsers
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic CV schema (source of truth)
│   │   ├── templates/pdf/       # Jinja2 HTML→PDF templates
│   │   └── tests/               # Full test suite
│   └── pyproject.toml
├── frontend/
│   ├── app/
│   │   ├── pages/
│   │   │   ├── 1_Landing.py    # Tailwind landing page
│   │   │   └── 2_Builder.py    # CV editor + live preview
│   │   ├── components/
│   │   │   ├── api_client.py   # Backend API calls
│   │   │   └── cv_state.py     # Session state management
│   │   └── styles/theme.py     # Shared CSS
│   └── app.py                   # Streamlit entry point
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .env.example
├── Makefile
├── README.md
└── SECURITY.md
```

---

## 🎨 Design System

| Token | Hex | Use |
|---|---|---|
| `primary-dark` | `#09637E` | Headers, PDF sidebar, hover |
| `primary` | `#088395` | Buttons, CTAs, links |
| `accent` | `#7AB2B2` | Borders, chips, timeline dots |
| `surface` | `#EBF4F6` | Page background, cards |

Font: Inter (UI + PDF). Templates: Sidebar, Classic, Minimal.

---

## 🤖 AI Agents

### Agent 1 — Job Requirements Agent
- Input: job title or description
- Tools: web_search (Tavily/DDG), fetch_page (SSRF-safe), skill_normalizer
- Output: ranked skills by category with evidence URLs, streamed via SSE
- Guardrails: max 10 tool calls, 60s timeout, response caching (1h TTL)

### Agent 2 — CV Extraction Agent
- Input: raw text from uploaded CV
- Output: full CVSchema with per-field confidence scores
- Security: prompt injection defense via delimiters + schema validation

### Improve Bullet Chain
- Rewrites individual bullets with strong action verbs
- Never invents facts — shows diff, user accepts or rejects

---

## 🛡️ Security Highlights

- **Auth**: Argon2id password hashing, JWT access + refresh tokens in httpOnly cookies
- **File uploads**: extension + MIME + magic byte checks, UUID filenames, auto-delete after processing
- **SSRF**: DNS resolution checks, private IP blocks, no external fetching in PDF renderer
- **Prompt injection**: CV content isolated in delimiters, schema-validated output only
- **Rate limiting**: per-IP, per-user, stricter on AI endpoints
- **Headers**: HSTS, CSP, X-Frame-Options, Referrer-Policy in production

See [SECURITY.md](SECURITY.md) for the full OWASP Top 10 + LLM Top 10 mapping.

---

## 📋 Known Limits & Next Steps

### Known Limits
- Photo in PDF stored as base64 data URI — large photos increase PDF size
- Guest sessions don't persist CV across page refresh
- ATS score uses heuristic text extraction (not a real ATS engine)
- WeasyPrint requires Linux system libraries (docker handles this)

### Roadmap
1. **Job-Tailoring Score** — compute match % between CV and job description
2. **Cover Letter Generator** — one-click AI cover letter from CV + JD
3. **Multi-CV Versions** — maintain multiple CV variants for different roles
4. **LinkedIn OAuth Import** — direct profile sync (when API permits)
5. **CV Collaboration** — share CV with mentor for review/comments

---

## 👨‍💻 Project & Support

**CVBoost AI Team**  
📧 support@cvboost.ai  
🌐 [cvboost.ai](https://cvboost.ai)  
🔒 [SECURITY.md](SECURITY.md)
