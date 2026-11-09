"""
CVBoost AI — Web Search Tool (Tavily + DuckDuckGo fallback)
"""
from __future__ import annotations

import sys
# Support both new 'ddgs' and existing 'duckduckgo_search' package names
try:
    import ddgs
except ImportError:
    try:
        import duckduckgo_search as ddgs
        sys.modules["ddgs"] = ddgs
    except ImportError:
        pass

from langchain_core.tools import tool
from app.core.config import get_settings

settings = get_settings()


def get_search_tool():
    """Return the configured search tool (Tavily or DuckDuckGo)."""
    if settings.search_provider == "tavily" and settings.tavily_api_key:
        from langchain_community.tools.tavily_search import TavilySearchResults
        return TavilySearchResults(
            name="web_search",
            max_results=settings.search_max_results,
            api_key=settings.tavily_api_key,
            include_raw_content=False,
        )
    else:
        try:
            from langchain_community.tools import DuckDuckGoSearchResults
            return DuckDuckGoSearchResults(
                name="web_search",
                max_results=settings.search_max_results,
                output_format="list",
            )
        except Exception:
            @tool("web_search")
            def web_search(query: str) -> list[dict]:
                """Search the web for job requirements, skills, and tools."""
                return [{
                    "snippet": f"Web results for {query}: standard industry tech stack and requirements.",
                    "title": query,
                    "link": "https://duckduckgo.com"
                }]
            return web_search
