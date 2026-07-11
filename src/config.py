"""Runtime configuration loaded from environment / .env."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ResearchMode = Literal["full", "chokepoint_fast", "risk_only", "compare"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Model
    model_provider: Literal["anthropic", "openai_compatible"] = "openai_compatible"
    model_name: str = "deepseek-chat"
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    ai_gateway_api_key: str | None = None
    ai_gateway_base_url: str | None = None
    # Alias for MiniMax OpenAI-compatible API (https://api.minimax.io/v1)
    minimax_api_key: str | None = None

    # Search
    tavily_api_key: str | None = None
    wsa_api_key: str | None = None

    # Runtime
    research_mode: ResearchMode = "full"
    max_concurrent_subagents: int = Field(default=3, ge=1, le=6)
    max_searches_per_subagent: int = Field(default=5, ge=1, le=10)
    reports_dir: Path = Path("./reports")
    temperature: float = 0.2
    log_level: str = "INFO"
    # Optional API gate (empty = disabled, for local demos)
    api_access_key: str | None = None
    request_timeout_seconds: int = Field(default=600, ge=60, le=3600)
    export_html_json: bool = True
    bilingual_memo: bool = False
    max_tool_retries: int = Field(default=3, ge=1, le=6)
    # Soft cost budget (estimated tokens); 0 = disabled
    max_tokens_budget: int = Field(default=0, ge=0)
    # Optional webhook for async job completion
    webhook_url: str | None = None
    # API rate limit
    api_rate_limit: int = Field(default=120, ge=10, le=10000)
    api_rate_window_seconds: int = Field(default=60, ge=10, le=3600)
    # Report default language preference for prompts
    report_language: Literal["zh", "en", "bilingual"] = "zh"
    # Auth plugins
    api_bearer_token: str | None = None
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    oidc_jwks_url: str | None = None

    def resolved_api_key(self) -> str:
        if self.model_provider == "anthropic":
            key = self.anthropic_api_key
            if not key:
                raise ValueError("ANTHROPIC_API_KEY is required for model_provider=anthropic")
            return key

        key = self.ai_gateway_api_key or self.openai_api_key or self.minimax_api_key
        if not key:
            raise ValueError(
                "AI_GATEWAY_API_KEY / OPENAI_API_KEY / MINIMAX_API_KEY is required "
                "for openai_compatible provider"
            )
        return key

    def resolved_base_url(self) -> str | None:
        if self.model_provider == "anthropic":
            return None
        url = self.ai_gateway_base_url or self.openai_base_url
        # Default MiniMax OpenAI-compatible endpoint when using MiniMax models
        if not url and (
            self.minimax_api_key
            or (self.model_name or "").lower().startswith("minimax")
        ):
            return "https://api.minimax.io/v1"
        return url

    def validate_runtime(self, *, require_tavily: bool = True) -> list[str]:
        """Return human-readable problems; empty list means OK to run research."""
        problems: list[str] = []
        try:
            self.resolved_api_key()
        except ValueError as exc:
            problems.append(str(exc))
        if require_tavily and not self.tavily_api_key:
            problems.append(
                "TAVILY_API_KEY is missing (https://tavily.com). Web search will fail."
            )
        if self.model_provider == "openai_compatible" and not self.resolved_base_url():
            problems.append(
                "OPENAI_BASE_URL or AI_GATEWAY_BASE_URL recommended for openai_compatible provider."
            )
        return problems


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    """Clear cached settings (call after env changes in tests)."""
    get_settings.cache_clear()
