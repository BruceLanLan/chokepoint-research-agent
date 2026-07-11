"""Export sanitized runtime config (never secrets)."""

from __future__ import annotations

from typing import Any

from src import __version__
from src.config import get_settings


_SECRET_KEYS = {
    "anthropic_api_key",
    "openai_api_key",
    "ai_gateway_api_key",
    "minimax_api_key",
    "tavily_api_key",
    "wsa_api_key",
    "api_access_key",
    "api_bearer_token",
}


def sanitized_config() -> dict[str, Any]:
    s = get_settings()
    data = s.model_dump()
    out: dict[str, Any] = {"version": __version__}
    for k, v in data.items():
        if k in _SECRET_KEYS:
            out[k] = "set" if v else "missing"
        elif "key" in k.lower() or "token" in k.lower() or "secret" in k.lower() or "password" in k.lower():
            out[k] = "set" if v else "missing"
        else:
            # pathlib etc.
            out[k] = str(v) if not isinstance(v, (str, int, float, bool, type(None), list, dict)) else v
    out["disclaimer"] = "research_only_not_investment_advice"
    out["note"] = "Secret values are redacted to set/missing only."
    return out
