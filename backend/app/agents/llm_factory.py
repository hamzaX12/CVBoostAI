"""
CVBoost AI — Common LLM Factory
Returns ChatGroq or ChatGoogleGenerativeAI based on settings.
"""
from __future__ import annotations

from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_llm(temperature: float | None = None, max_tokens: int | None = None) -> BaseChatModel:
    """Return configured Chat LLM instance (Groq or Gemini)."""
    settings = get_settings()

    if settings.llm_provider == "groq" and settings.groq_api_key:
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=temperature if temperature is not None else settings.groq_temperature,
            max_tokens=max_tokens if max_tokens is not None else settings.groq_max_tokens,
        )

    # Fallback to Gemini
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=temperature if temperature is not None else settings.gemini_temperature,
        max_output_tokens=max_tokens if max_tokens is not None else settings.gemini_max_tokens,
    )

