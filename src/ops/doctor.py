"""Environment and dependency health checks.

Reports both **config** score (keys / packages / agent build) and **ops** score
(workspace process surface). Missing search keys should not look like the ops
product is broken.
"""

from __future__ import annotations

import importlib
import sys
from typing import Any

from src.config import clear_settings_cache, get_settings

# Check name prefixes / exact names for scoring buckets
_CONFIG_NAMES = {
    "python_version",
    "model_api_key",
    "tavily_api_key",
    "model_provider",
    "reports_dir",
    "agent_build",
}
_CONFIG_PREFIXES = ("pkg:",)
_OPS_NAMES = {
    "kill_monitor",
    "skill_packs",
    "plugins_dir",
    "research_queue",
    "ops_surface",
    "verticals",
    "pro_specs",
}


def run_doctor() -> dict[str, Any]:
    clear_settings_cache()
    settings = get_settings()
    checks: list[dict[str, Any]] = []

    def add(
        name: str,
        ok: bool,
        detail: str,
        level: str = "error",
        *,
        bucket: str = "config",
    ) -> None:
        checks.append(
            {
                "name": name,
                "ok": ok,
                "detail": detail,
                "level": level if not ok else "ok",
                "bucket": bucket,
            }
        )

    # Python
    py_ok = sys.version_info >= (3, 11)
    add(
        "python_version",
        py_ok,
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} (need >= 3.11)",
        bucket="config",
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
            add(f"pkg:{pkg}", True, "installed", bucket="config")
        except Exception as exc:  # noqa: BLE001
            add(
                f"pkg:{pkg}",
                False,
                str(exc),
                level="warn" if pkg in {"deepagents", "yfinance"} else "error",
                bucket="config",
            )

    # Config keys — tavily missing is warn for product ops, error for full live research
    problems = settings.validate_runtime(require_tavily=True)
    model_key_ok = not any("API_KEY" in p and "TAVILY" not in p for p in problems)
    add(
        "model_api_key",
        model_key_ok,
        "; ".join(problems) or "ok",
        level="error" if not model_key_ok else "ok",
        bucket="config",
    )
    tavily_ok = bool(settings.tavily_api_key)
    add(
        "tavily_api_key",
        tavily_ok,
        "set" if tavily_ok else "missing — web_search soft-fails; use --mock or set TAVILY_API_KEY",
        level="warn",  # no longer hard-fail product health
        bucket="config",
    )
    add(
        "model_provider",
        True,
        f"{settings.model_provider} / {settings.model_name}",
        bucket="config",
    )
    add("reports_dir", True, str(settings.reports_dir.resolve()), bucket="config")

    # deep agent build (no network call)
    try:
        from src.agents.research_agent import build_investment_agent

        if model_key_ok:
            agent = build_investment_agent(settings, mode="chokepoint_fast")
            add("agent_build", True, type(agent).__name__, bucket="config")
        else:
            add("agent_build", False, "skipped — no model key", "warn", bucket="config")
    except Exception as exc:  # noqa: BLE001
        add("agent_build", False, str(exc), "warn", bucket="config")

    # Ops surface (v4+)
    try:
        from src.ops.kill_monitor import kill_criteria_dashboard
        from src.ops.pro.verticals import list_verticals
        from src.ops.research_queue import queue_summary
        from src.ops.pro import PRO_MODULE_IDS
        from src.plugins.loader import list_plugin_files
        from src.skills.loader import list_skill_packs

        km = kill_criteria_dashboard()
        high = int(km.get("high_risk_count") or 0)
        add(
            "kill_monitor",
            True,
            f"high_process_risk={high} theses={len(km.get('items') or [])}",
            level="warn" if high else "ok",
            bucket="ops",
        )
        packs = list_skill_packs()
        add(
            "skill_packs",
            bool(packs),
            f"{len(packs)} packs",
            "warn" if not packs else "ok",
            bucket="ops",
        )
        plugs = list_plugin_files()
        add("plugins_dir", True, f"{len(plugs)} files under ./plugins/", bucket="ops")
        qs = queue_summary()
        add(
            "research_queue",
            True,
            f"total={qs.get('total')} by_status={qs.get('by_status')}",
            bucket="ops",
        )
        verts = list_verticals()
        add(
            "verticals",
            len(verts) >= 5,
            f"{len(verts)} deep packs",
            "warn" if len(verts) < 5 else "ok",
            bucket="ops",
        )
        add(
            "pro_specs",
            len(PRO_MODULE_IDS) >= 40,
            f"{len(PRO_MODULE_IDS)} pro module ids",
            bucket="ops",
        )
    except Exception as exc:  # noqa: BLE001
        add("ops_surface", False, str(exc), "warn", bucket="ops")

    def _score(bucket: str) -> dict[str, Any]:
        rows = [c for c in checks if c.get("bucket") == bucket]
        if not rows:
            return {"score": 100, "grade": "A", "errors": 0, "warnings": 0, "count": 0}
        errors = sum(1 for c in rows if not c["ok"] and c["level"] == "error")
        warns = sum(1 for c in rows if not c["ok"] and c["level"] == "warn")
        # start 100; -15 error, -5 warn
        score = max(0, 100 - 15 * errors - 5 * warns)
        if score >= 90:
            grade = "A"
        elif score >= 75:
            grade = "B"
        elif score >= 60:
            grade = "C"
        elif score >= 40:
            grade = "D"
        else:
            grade = "F"
        return {
            "score": score,
            "grade": grade,
            "errors": errors,
            "warnings": warns,
            "count": len(rows),
        }

    config = _score("config")
    ops = _score("ops")
    # Overall product "ok" for live research still needs model key; ops can be healthy alone
    live_ready = config["errors"] == 0 and bool(settings.tavily_api_key) and model_key_ok
    ops_ok = ops["errors"] == 0
    errors = sum(1 for c in checks if not c["ok"] and c["level"] == "error")
    warns = sum(1 for c in checks if not c["ok"] and c["level"] == "warn")

    return {
        "ok": errors == 0,  # soft: tavily is warn so often True without Tavily
        "live_ready": live_ready,
        "ops_ok": ops_ok,
        "errors": errors,
        "warnings": warns,
        "config": config,
        "ops": ops,
        "checks": checks,
        "hint": (
            "Use doctor --ops-only for process surface; "
            "research --mock without keys; set MODEL + TAVILY for live research."
        ),
        "disclaimer": "research_only_not_investment_advice",
    }
