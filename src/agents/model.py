"""Model factory: Anthropic Fable 5 or any OpenAI-compatible gateway."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

from src.config import Settings, get_settings


def build_model(settings: Settings | None = None) -> BaseChatModel:
    settings = settings or get_settings()
    temperature = settings.temperature

    if settings.model_provider == "anthropic":
        # Claude Fable 5 / Opus / Sonnet via official Anthropic API
        return init_chat_model(
            model=f"anthropic:{settings.model_name}",
            temperature=temperature,
            api_key=settings.resolved_api_key(),
        )

    # OpenAI-compatible: EdgeOne AI Gateway, DeepSeek, OpenAI, vLLM, etc.
    base_url = settings.resolved_base_url()
    kwargs: dict = {
        "model": f"openai:{settings.model_name}",
        "temperature": temperature,
        "api_key": settings.resolved_api_key(),
    }
    if base_url:
        kwargs["base_url"] = base_url
    return init_chat_model(**kwargs)
