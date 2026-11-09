# SECURITY.md — CVBoost AI

## Reporting Vulnerabilities

If you discover a security vulnerability, please email **security@cvboost.ai** with subject **"[SECURITY] CVBoost AI"**. Do not open a public GitHub issue for security reports.

---

## OWASP Top 10 (2021) Mitigation Table

| OWASP Risk | Risk | Mitigation in CVBoost AI |
|---|---|---|
| A01 | Broken Access Control | JWT auth on all CV endpoints; owner-scoped DB queries; guest quotas; `DELETE /me` data purge |
| A02 | Cryptographic Failures | Argon2id (64MB, time=3) password hashing; JWT signed with HS256 + strong secret; httpOnly/Secure cookies; no secrets in logs |
| A03 | Injection | Pydantic strict validation on all inputs; Jinja2 autoescape=ON; bleach sanitization; parameterized SQLAlchemy queries; PDF renderer URL fetcher blocks external sources |
| A04 | Insecure Design | Threat-modeled: SSRF in fetch_page and PDF renderer; prompt injection in extraction agent; file upload abuse |
| A05 | Security Misconfiguration | CSP, HSTS, X-Frame-Options, Referrer-Policy headers; no debug endpoints in production; startup fails on missing secrets |
| A06 | Vulnerable Components | Pinned dependency versions in pyproject.toml; pip-audit in CI; Dependabot config |
| A07 | Auth Failures | Argon2id + no username enumeration timing; refresh token rotation + revocation; short-lived access tokens (30min) |
| A08 | Software & Data Integrity | pyproject.toml pinned versions; Docker non-root user; pre-commit hooks; bandit SAST |
| A09 | Logging & Monitoring | structlog structured logs with request IDs; audit log for auth events; no PII in logs; no stack traces to clients |
| A10 | SSRF | `validate_url_for_fetch` resolves DNS and blocks all private/loopback/link-local IPs; WeasyPrint `url_fetcher` blocks all external URLs; only local assets allowed |

---

## OWASP LLM Top 10 Mitigation Table

| LLM Risk | Risk | Mitigation in CVBoost AI |
|---|---|---|
| LLM01 | Prompt Injection | CV text isolated in `<CV_DOCUMENT>` delimiters; regex strips obvious injection patterns pre-send; schema-validated JSON-only output; system prompt instructs ignoring embedded commands |
| LLM02 | Insecure Output Handling | All LLM output validated by Pydantic schemas before use; no LLM output executed as code; bullet text sanitized with bleach before PDF rendering |
| LLM03 | Training Data Poisoning | N/A (using pre-trained Gemini API, not training custom model) |
| LLM04 | Model DoS | Per-user daily token quota (500K); per-endpoint rate limits; agent max tool call budget (10 calls); 60s agent timeout; content length caps on inputs |
| LLM05 | Supply Chain | langchain, langchain-google-genai pinned; pip-audit scans; no untrusted plugins |
| LLM06 | Sensitive Info Disclosure | CV text is marked PII; GDPR consent notice shown; no CV content in logs; "Delete my data" endpoint; users informed CV text goes to Gemini API |
| LLM07 | Insecure Plugin Design | Fetch tool: SSRF-protected, allowlist-free but IP-validated; no filesystem access from tools; tools have no access to secrets or DB |
| LLM08 | Excessive Agency | Agents cannot write files, send emails, or access the database; skill normalizer is deterministic; tool-call budget enforced |
| LLM09 | Overreliance | UI highlights low-confidence extracted fields for user review; "model_knowledge=true" flag on unsourced skill suggestions; all AI suggestions require user approval |
| LLM10 | Insecure Output Handling | Jinja2 autoescape=ON prevents LLM output from injecting HTML into PDF; bleach strips all disallowed HTML tags from rich text fields |

---

## Additional Hardening Details

### File Upload Security
- Extension + MIME type + magic byte (file signature) triple check
- 5 MB size limit enforced server-side
- UUID-based filename randomization (original name discarded)
- Files stored outside web root
- Auto-delete immediately after processing
- PDF page count limit (max 20 pages)
- Zip-bomb protection (size limit before extraction)

### PDF Renderer SSRF Protection
WeasyPrint's `url_fetcher` is replaced with a custom function that:
- Only allows `file://` URLs
- Only allows paths inside `templates/assets/` directory
- Allows `data:` URIs (for embedded photos)
- Blocks all `http://`, `https://`, and other schemes
- Raises an error for any path traversal attempt

### Data Privacy
- CV content (PII) is sent to the Gemini API — users are informed via consent notice
- No CV content written to application logs
- Retention policy: users can delete all their data via `DELETE /api/v1/auth/me`
- Uploaded files deleted immediately after AI extraction
- Sensitive DB fields can be encrypted at rest (implementation note in config)

### Authentication Details
- Refresh token rotation: old JTI revoked on each refresh
- Refresh token stored in path-scoped cookie (`/api/v1/auth/refresh` only)
- Guest sessions: signed JWT with usage quota, no DB record
- Password minimum: 8 characters (enforced in API, not just client)
- No email enumeration: consistent error messages for login failures
