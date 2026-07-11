"""Environment and dependency health checks."""

from __future__ import annotations

import importlib
import sys
from typing import Any

from src.config import clear_settings_cache, get_settings


def run_doctor() -> dict[str, Any]:
    clear_settings_cache()
    settings = get_settings()
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str, level: str = "error") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail, "level": level if not ok else "ok"})

    # Python
    py_ok = sys.version_info >= (3, 11)
    add(
        "python_version",
        py_ok,
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} (need >= 3.11)",
    )

    # Packages
    for pkg, import_name in [
        ("deepagents", "deepagents"),
        ("langchain", "langchain"),
        ("httpx", "httpx"),
        ("yaml", "yaml"),
        ("yfinance", "yfinance"),
        ("fastapi", "fastapi"),
        ("tavily", "tavily"),
    ]:
        try:
            importlib.import_module(import_name)
            add(f"pkg:{pkg}", True, "installed")
        except Exception as exc:  # noqa: BLE001
            add(f"pkg:{pkg}", False, str(exc), level="warn" if pkg in {"deepagents", "yfinance"} else "error")

    # Config
    problems = settings.validate_runtime(require_tavily=True)
    add("model_api_key", not any("API_KEY" in p and "TAVILY" not in p for p in problems), "; ".join(problems) or "ok")
    add("tavily_api_key", bool(settings.tavily_api_key), "set" if settings.tavily_api_key else "missing (search will fail)", "error")
    add(
        "model_provider",
        True,
        f"{settings.model_provider} / {settings.model_name}",
    )
    add("reports_dir", True, str(settings.reports_dir.resolve()))

    # deep agent build (no network call)
    try:
        from src.agents.research_agent import build_investment_agent

        if not any(c["name"] == "model_api_key" and not c["ok"] for c in checks):
            agent = build_investment_agent(settings, mode="chokepoint_fast")
            add("agent_build", True, type(agent).__name__)
        else:
            add("agent_build", False, "skipped — no model key", "warn")
    except Exception as exc:  # noqa: BLE001
        add("agent_build", False, str(exc), "warn")

    # Ops surface (v4)
    try:
        from src.ops.kill_monitor import kill_criteria_dashboard
        from src.plugins.loader import list_plugin_files
        from src.skills.loader import list_skill_packs

        km = kill_criteria_dashboard()
        add(
            "kill_monitor",
            True,
            f"high_process_risk={km.get('high_risk_count', 0)} theses={len(km.get('items') or [])}",
            "warn" if km.get("high_risk_count") else "ok",
        )
        packs = list_skill_packs()
        add("skill_packs", bool(packs), f"{len(packs)} packs", "warn" if not packs else "ok")
        plugs = list_plugin_files()
        add("plugins_dir", True, f"{len(plugs)} files under ./plugins/")
    except Exception as exc:  # noqa: BLE001
        add("ops_surface", False, str(exc), "warn")

    errors = sum(1 for c in checks if not c["ok"] and c["level"] == "error")
    warns = sum(1 for c in checks if not c["ok"] and c["level"] == "warn")
    return {
        "ok": errors == 0,
        "errors": errors,
        "warnings": warns,
        "checks": checks,
        "disclaimer": "research_only_not_investment_advice",
    }
