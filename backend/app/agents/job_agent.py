"""
CVBoost AI — Job Requirements Agent
LangGraph-based agent with web search, page fetching, and skill normalization.
Streams progress events via async generator.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
from textwrap import dedent
from typing import Any, AsyncGenerator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.language_models.chat_models import BaseChatModel

from app.agents.llm_factory import get_llm

from app.agents.tools.search_tool import get_search_tool
from app.agents.tools.fetch_tool import fetch_page_tool
from app.agents.tools.skill_normalizer import normalize_skill
from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.cv import JobAnalysisResult, SuggestedSkill, SuggestedLanguage

logger = get_logger(__name__)
settings = get_settings()

# ── Simple in-memory cache (TTL-based by normalized query) ────────────────────

_cache: dict[str, tuple[float, JobAnalysisResult]] = {}


def _cache_key(query: str, country: str, seniority: str, has_skills: bool = False) -> str:
    raw = f"{query.lower().strip()}|{country}|{seniority}|skills:{has_skills}"
    return hashlib.md5(raw.encode()).hexdigest()  # noqa: S324


def _get_cached(key: str) -> JobAnalysisResult | None:
    if key in _cache:
        ts, result = _cache[key]
        if time.time() - ts < settings.cache_ttl_seconds:
            # Only return cached item if it has skills
            if result and result.skills:
                return result
        del _cache[key]
    return None


def _set_cached(key: str, result: JobAnalysisResult) -> None:
    if result and result.skills:
        _cache[key] = (time.time(), result)


# ─────────────────────────────────────────────────────────────────────────────
# Agent
# ─────────────────────────────────────────────────────────────────────────────

JOB_AGENT_SYSTEM = dedent("""
You are an expert technical recruiter and job requirements analyst.
Your goal is to identify strictly validated, industry-standard technical tools, languages, and competencies required for a job role.

You have access to these tools:
- web_search: Search the web for job postings, role guides, and skill requirements
- fetch_page: Fetch a specific web page to read its content
- normalize_skill: Canonicalize a skill name (e.g. "PowerBI" → "Power BI")

Process:
1. Detect the target role, seniority level, and location from the query
2. Run targeted web searches to identify current tech stack requirements
3. Extract and rank strictly authentic technical tools and skills
4. Produce a structured JSON result

CRITICAL RULES FOR SKILLS & CATEGORIES:
1. MAXIMUM 4 CATEGORIES TOTAL:
   - Group ALL suggested skills into AT MOST 4 professional domain categories (e.g. 'Machine Learning & AI', 'Data Engineering', 'Programming Languages', 'MLOps & Cloud').
   - NEVER create more than 4 categories under any circumstances.
   - NEVER use generic or catch-all category names like 'Specialized Tools', 'Keywords', 'Technical Skills', or 'Other'.

2. VALIDATED TECHNICAL SKILLS ONLY (1 to 3 words max):
   - Every skill name MUST be an authentic, recognized industry tool, library, framework, or concrete technical competency.
     Examples of valid skills: 'Python', 'PyTorch', 'Apache Spark', 'Docker', 'Kubernetes', 'PostgreSQL', 'Scikit-Learn', 'FastAPI', 'CI/CD Pipelines', 'Git'.
   - FORBIDDEN: NEVER generate conversational words, verbs, fragments, or casual text (e.g. NEVER 'hands in data', 'student', 'seeking position', 'experience', 'support', 'turning', 'grow', 'predictive', 'actionable', 'my skills').
   - Do NOT suggest skills the candidate already has.

3. QUANTITY & EXTRA SKILLS:
   - Suggest AT LEAST 5 to 7 high-impact, verified technical skills FOR EACH of the 4 categories (total 20 to 28 skills). Every category MUST have at least 5 authentic industry-standard skills.
   - Focus on core essential skills. The candidate can add any extra or specialized niche skills themselves manually.

4. Importance: 5=always required, 4=very common, 3=common, 2=nice-to-have, 1=rare.
5. Max {max_calls} tool calls total.
""").strip().format(max_calls=settings.agent_max_tool_calls)


async def run_job_agent(
    query: str,
    country: str = "",
    seniority: str = "",
    current_skills: list[str] | None = None,
    existing_categories: list[dict] | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Async generator that yields:
      {"type": "progress", "message": "..."}
      {"type": "result", "data": {...JobAnalysisResult...}}
    """
    # Check cache
    has_skills = bool(current_skills and len(current_skills) > 0)
    cache_key = _cache_key(query, country, seniority, has_skills)
    cached = _get_cached(cache_key)
    if cached and cached.skills:
        yield {"type": "progress", "message": "Using cached analysis..."}
        yield {"type": "result", "data": cached.model_dump(mode="json")}
        return

    # Build LLM with tools
    llm = get_llm(temperature=0.1)
    tools = [get_search_tool(), fetch_page_tool, normalize_skill]
    llm_with_tools = llm.bind_tools(tools)
    tool_map = {t.name: t for t in tools}

    # Build initial message
    context_parts = [f"Job query: {query}"]
    if country:
        context_parts.append(f"Country: {country}")
    if seniority:
        context_parts.append(f"Seniority: {seniority}")
    if current_skills:
        context_parts.append(f"Candidate already has these skills (do NOT suggest duplicates): {', '.join(current_skills[:50])}")
    else:
        context_parts.append(
            "CRITICAL: The candidate's CV currently has NO skills. "
            "You MUST generate AT LEAST 5 verified, essential industry-standard skills FOR EACH category, "
            "divided across MAXIMUM 4 distinct professional categories (total 20-25 skills). "
            "Every category must have at least 5 recognized tools or frameworks (e.g. PyTorch, Spark, SQL, Docker, FastAPI). "
            "Never exceed 4 categories. NEVER create categories named 'Specialized Tools' or 'Keywords'."
        )
    if existing_categories:
        cat_lines = []
        for cat in existing_categories:
            cname = cat.get("name") or cat.get("category") or ""
            cskills = cat.get("skills") or cat.get("items") or []
            if cname:
                s_str = ", ".join(str(s) for s in cskills[:8]) if cskills else "none"
                cat_lines.append(f"  * {cname} (current skills: {s_str})")
        if cat_lines:
            context_parts.append("Candidate's CURRENT skill categories on their CV (match new skills here if they fit):\n" + "\n".join(cat_lines))

    messages = [
        SystemMessage(content=JOB_AGENT_SYSTEM),
        HumanMessage(content="\n".join(context_parts)),
    ]

    tool_calls_made = 0
    sources: list[str] = []
    search_queries: list[str] = []

    try:
        yield {"type": "progress", "message": "Detecting role and searching the web..."}

        # Agentic loop
        async with asyncio.timeout(settings.agent_timeout_seconds):
            while tool_calls_made < settings.agent_max_tool_calls:
                response: AIMessage = await llm_with_tools.ainvoke(messages)
                messages.append(response)

                if not response.tool_calls:
                    # Final response — extract structured result
                    break

                # Execute tool calls
                for tc in response.tool_calls:
                    if tool_calls_made >= settings.agent_max_tool_calls:
                        break

                    tool_name = tc["name"]
                    tool_args = tc["args"]
                    tool_calls_made += 1

                    progress_msg = _progress_for_tool(tool_name, tool_args)
                    yield {"type": "progress", "message": progress_msg}

                    try:
                        tool_fn = tool_map[tool_name]
                        if asyncio.iscoroutinefunction(tool_fn.func if hasattr(tool_fn, 'func') else tool_fn):
                            result = await tool_fn.ainvoke(tool_args)
                        else:
                            result = tool_fn.invoke(tool_args)

                        # Collect sources
                        if tool_name == "web_search" and isinstance(result, list):
                            for r in result:
                                if isinstance(r, dict) and r.get("url"):
                                    sources.append(r["url"])
                            if "query" in tool_args:
                                search_queries.append(tool_args["query"])
                        elif tool_name == "fetch_page" and isinstance(tool_args, dict):
                            if tool_args.get("url"):
                                sources.append(tool_args["url"])

                        messages.append(ToolMessage(
                            content=json.dumps(result, ensure_ascii=False)[:8000],
                            tool_call_id=tc["id"],
                        ))
                    except Exception as exc:
                        logger.warning("tool_call_failed", tool=tool_name, error=str(exc))
                        messages.append(ToolMessage(
                            content=f"Error: {str(exc)[:200]}",
                            tool_call_id=tc["id"],
                        ))

        # Now extract structured result from final message
        yield {"type": "progress", "message": "Structuring requirements and mapping to your skills categories..."}
        result = await _extract_structured_result(
            llm, messages, sources, search_queries, current_skills or [], existing_categories or []
        )

        _set_cached(cache_key, result)
        yield {"type": "result", "data": result.model_dump(mode="json")}

    except TimeoutError:
        logger.warning("job_agent_timeout", query=query)
        # Return partial result from whatever we have
        result = await _extract_structured_result(llm, messages, sources, search_queries, current_skills or [], existing_categories or [])
        yield {"type": "result", "data": result.model_dump(mode="json")}
    except Exception as exc:
        logger.error("job_agent_error", error=str(exc))
        raise


async def _extract_structured_result(
    llm: BaseChatModel,
    messages: list,
    sources: list[str],
    search_queries: list[str],
    current_skills: list[str],
    existing_categories: list[dict] | None = None,
) -> JobAnalysisResult:
    """Ask LLM to produce structured output from the conversation history."""
    structured_llm = llm.with_structured_output(JobAnalysisResult)

    existing_lower = {s.lower() for s in current_skills}
    dedup_note = (
        f"\nIMPORTANT: The candidate already has these skills — do NOT include duplicates of them: {current_skills[:40]}"
        if current_skills else ""
    )

    cat_names = []
    if existing_categories:
        cat_names = [c.get("name") or c.get("category") or "" for c in existing_categories]
        cat_names = [c.strip() for c in cat_names if c and c.strip()]

    cat_note = (
        f"\nSTRICT CATEGORIZATION & SKILL NAME RULES: "
        f"1. MAXIMUM 4 CATEGORIES TOTAL: All skills must be grouped into at most 4 clean professional categories. "
        f"If candidate has existing categories ({cat_names[:4]}), prioritize mapping into them. "
        f"2. AT LEAST 5 TO 7 VERIFIED SKILLS PER CATEGORY: Every single category MUST contain at least 5 authentic, industry-standard skills (total 20 to 28 skills across the 4 categories). Do NOT leave any category with only 1 or 2 skills. "
        f"3. AUTHENTIC TECHNICAL SKILLS ONLY: Every skill name MUST be a real, recognized tool, language, or technical standard (1 to 3 words, e.g. 'PyTorch', 'Docker', 'SQL', 'Apache Spark'). "
        f"4. NEVER generate fragments, casual text, verbs, or non-technical words like 'hands in data', 'support', 'student', 'into', 'turning', 'my skills'. "
        f"5. Focus on essential core skills only. Any extra or specialized niche skills will be added manually by the candidate. "
        f"6. NEVER create categories named 'Specialized Tools', 'Keywords', or 'Other'."
    )

    final_prompt = HumanMessage(content=dedent(f"""
        Based on your research above, produce the final structured job requirements analysis.
        Sources found: {sources[:10]}
        Search queries used: {search_queries}
        {dedup_note}
        {cat_note}

        Return a complete JobAnalysisResult with all skills grouped into at most 4 professional categories,
        with AT LEAST 5 validated technical skills per category (1-3 words max), importance scores, and evidence URLs.
    """).strip())

    try:
        result: JobAnalysisResult = await structured_llm.ainvoke(messages + [final_prompt])
        result.sources = list(set(sources))[:10]
        result.search_queries_used = search_queries
        if result.skills:
            return result
    except Exception as exc:
        logger.error("structured_extraction_failed", error=str(exc))

    # Resilient fallback if structured extraction returned empty
    fallback_skills = []
    user_query = ""
    for m in messages:
        if isinstance(m, HumanMessage):
            user_query += " " + str(m.content)

    import re
    buzzwords = [
        ("PyTorch", "Machine Learning & AI"),
        ("TensorFlow", "Machine Learning & AI"),
        ("LLMs", "Machine Learning & AI"),
        ("Transformers", "Machine Learning & AI"),
        ("NLP", "Machine Learning & AI"),
        ("Deep Learning", "Machine Learning & AI"),
        ("Scikit-Learn", "Machine Learning & AI"),
        ("Spark", "Data Engineering"),
        ("Apache Spark", "Data Engineering"),
        ("SQL", "Data Engineering"),
        ("ETL", "Data Engineering"),
        ("Data Pipelines", "Data Engineering"),
        ("Kafka", "Data Engineering"),
        ("MLOps", "MLOps & Deployment"),
        ("Docker", "MLOps & Deployment"),
        ("Kubernetes", "MLOps & Deployment"),
        ("Model Deployment", "MLOps & Deployment"),
        ("CI/CD for ML", "MLOps & Deployment"),
        ("Model Serving", "MLOps & Deployment"),
        ("Vector DB", "Machine Learning & AI"),
        ("Hugging Face", "Machine Learning & AI"),
        ("Power BI", "Analytics & BI"),
        ("Python", "Programming Languages"),
    ]
    for term, cat in buzzwords:
        if re.search(rf"\b{re.escape(term)}\b", user_query, re.IGNORECASE):
            fallback_skills.append(SuggestedSkill(name=term, category=cat, importance=5, model_knowledge=True))

    if not fallback_skills:
        fallback_skills = [
            # Machine Learning & AI (5 skills)
            SuggestedSkill(name="PyTorch", category="Machine Learning & AI", importance=5, model_knowledge=True),
            SuggestedSkill(name="TensorFlow", category="Machine Learning & AI", importance=5, model_knowledge=True),
            SuggestedSkill(name="Scikit-Learn", category="Machine Learning & AI", importance=5, model_knowledge=True),
            SuggestedSkill(name="Deep Learning", category="Machine Learning & AI", importance=5, model_knowledge=True),
            SuggestedSkill(name="NLP", category="Machine Learning & AI", importance=4, model_knowledge=True),
            # Data Engineering (5 skills)
            SuggestedSkill(name="SQL", category="Data Engineering", importance=5, model_knowledge=True),
            SuggestedSkill(name="Apache Spark", category="Data Engineering", importance=5, model_knowledge=True),
            SuggestedSkill(name="PySpark", category="Data Engineering", importance=4, model_knowledge=True),
            SuggestedSkill(name="Data Pipelines", category="Data Engineering", importance=4, model_knowledge=True),
            SuggestedSkill(name="ETL", category="Data Engineering", importance=4, model_knowledge=True),
            # MLOps & Deployment (5 skills)
            SuggestedSkill(name="Docker", category="MLOps & Deployment", importance=5, model_knowledge=True),
            SuggestedSkill(name="Kubernetes", category="MLOps & Deployment", importance=4, model_knowledge=True),
            SuggestedSkill(name="MLOps", category="MLOps & Deployment", importance=5, model_knowledge=True),
            SuggestedSkill(name="CI/CD Pipelines", category="MLOps & Deployment", importance=4, model_knowledge=True),
            SuggestedSkill(name="Model Serving", category="MLOps & Deployment", importance=4, model_knowledge=True),
            # Analytics & BI (5 skills)
            SuggestedSkill(name="Power BI", category="Analytics & BI", importance=5, model_knowledge=True),
            SuggestedSkill(name="Tableau", category="Analytics & BI", importance=4, model_knowledge=True),
            SuggestedSkill(name="Data Analysis", category="Analytics & BI", importance=5, model_knowledge=True),
            SuggestedSkill(name="Pandas", category="Analytics & BI", importance=5, model_knowledge=True),
            SuggestedSkill(name="KPI Dashboards", category="Analytics & BI", importance=4, model_knowledge=True),
        ]

    return JobAnalysisResult(
        role_detected="Data Scientist" if "data scientist" in user_query.lower() else "Specialist",
        skills=fallback_skills,
        keywords=[s.name for s in fallback_skills],
        sources=sources,
        search_queries_used=search_queries,
    )


def _progress_for_tool(tool_name: str, args: dict) -> str:
    if tool_name == "web_search":
        q = args.get("query", "")[:60]
        return f'Searching: "{q}"'
    elif tool_name == "fetch_page":
        url = args.get("url", "")[:60]
        return f"Reading: {url}"
    elif tool_name == "normalize_skill":
        return f"Normalizing skill: {args.get('skill', '')}"
    return f"Using tool: {tool_name}"
