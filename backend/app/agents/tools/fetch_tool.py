"""
CVBoost AI — SSRF-Safe Page Fetch Tool
Validates URL against SSRF rules before fetching.
"""
from __future__ import annotations

from langchain_core.tools import tool

from app.core.config import get_settings
from app.core.security import validate_url_for_fetch

settings = get_settings()

MAX_CONTENT_BYTES = 500_000  # 500 KB
REQUEST_TIMEOUT = 15.0


@tool
async def fetch_page_tool(url: str) -> str:
    """
    Fetch the text content of a web page (SSRF-safe).
    Only fetches http/https URLs that resolve to public IPs.
    Returns plain text content (HTML stripped).
    """
    import httpx
    import html2text

    # SSRF protection
    try:
        validate_url_for_fetch(url)
    except ValueError as e:
        return f"Error: URL blocked for security reasons — {e}"

    headers = {
        "User-Agent": "CVBoostAI/1.0 (job requirements research bot)",
        "Accept": "text/html,application/xhtml+xml,text/plain",
    }

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            max_redirects=3,
            timeout=REQUEST_TIMEOUT,
            limits=httpx.Limits(max_connections=5),
        ) as client:
            response = await client.get(url, headers=headers)

        # Check content type
        ct = response.headers.get("content-type", "")
        if "text" not in ct and "html" not in ct:
            return f"Error: Unsupported content type: {ct}"

        # Size limit
        content = response.text[:MAX_CONTENT_BYTES]

        # Convert HTML → plain text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0
        plain = h.handle(content)
        return plain[:20_000]  # Cap output to 20K chars

    except httpx.TimeoutException:
        return "Error: Request timed out"
    except httpx.TooManyRedirects:
        return "Error: Too many redirects"
    except Exception as exc:
        return f"Error: {str(exc)[:200]}"
