"""Shared API dependencies and models."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, AsyncIterator, Literal, Optional

from dotenv import load_dotenv
from fastapi import Header, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

from src import __version__  # noqa: E402
from src.agents.research_agent import build_investment_agent, extract_final_text  # noqa: E402
from src.config import clear_settings_cache, get_settings  # noqa: E402
from src.logging_utils import get_logger, setup_logging  # noqa: E402
from src.memory.sessions import append_turn, new_session_id, session_context_block  # noqa: E402
from src.ops.brief import run_brief  # noqa: E402
from src.ops.catalog import build_catalog, search_catalog  # noqa: E402
from src.ops.doctor import run_doctor  # noqa: E402
from src.ops.templates import list_templates, render_template  # noqa: E402
from src.ops import theses as theses_ops  # noqa: E402
from src.ops import watchlist as watch_ops  # noqa: E402
from src.schemas.scorecard import extract_scorecard_table, validate_report_structure  # noqa: E402
from src.tools.export import export_report_bundle  # noqa: E402
from src.tools.reports import list_reports, read_report, save_report_file  # noqa: E402
from src.tools.resilience import get_cost_tracker, reset_cost_tracker  # noqa: E402

log = get_logger("chokepoint.api")
# static lives next to package parent (src/static)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

_agents: dict[str, object] = {}
Mode = Literal["full", "chokepoint_fast", "risk_only", "compare"]


def check_access(
    x_api_key: str | None = None,
    authorization: str | None = None,
) -> None:
    from src.auth.base import AuthError
    from src.auth.plugins import authenticate_request

    try:
        authenticate_request(authorization, x_api_key)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


_check_access = check_access


def get_agent(mode: str = "full", skill: str | None = None, vertical: str | None = None):
    """Return a (possibly cached) agent. Skill/vertical bypass mode-only cache."""
    if skill or vertical:
        setup_logging(get_settings().log_level)
        return build_investment_agent(
            get_settings(), mode=mode, skill=skill, vertical=vertical  # type: ignore[arg-type]
        )
    if mode not in _agents:
        setup_logging(get_settings().log_level)
        _agents[mode] = build_investment_agent(get_settings(), mode=mode)  # type: ignore[arg-type]
    return _agents[mode]


class ResearchRequest(BaseModel):
    question: str = Field("", min_length=0)
    save_report: bool = True
    mode: Mode = "full"
    session_id: Optional[str] = None
    bilingual: bool = False
    export: bool = True
    template_id: Optional[str] = None
    template_vars: Optional[dict[str, str]] = None
    skill: Optional[str] = None
    vertical: Optional[str] = None
    min_quality: int = 0
    pro_suite: bool = False
    mock: bool = False  # offline mock memo — no LLM


class ResearchResponse(BaseModel):
    question: str
    report: str
    mode: str
    saved_path: Optional[str] = None
    exports: Optional[dict] = None
    quality: dict
    scorecard_nodes: int = 0
    session_id: Optional[str] = None
    cost: dict


class WatchAdd(BaseModel):
    symbol: str
    name: str = ""
    thesis: str = ""
    priority: str = "medium"
    tags: list[str] = Field(default_factory=list)
    notes: str = ""


class ThesisAdd(BaseModel):
    title: str
    statement: str
    system: str = ""
    chokepoints: list[str] = Field(default_factory=list)
    kill_criteria: list[str] = Field(default_factory=list)
    related_symbols: list[str] = Field(default_factory=list)


class ThesisStatus(BaseModel):
    status: Literal["active", "watching", "invalidated", "archived"]
    note: str = ""
