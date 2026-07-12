"""Auto-split route module — register(app)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, AsyncIterator, Literal, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from src.api.deps import (
    STATIC_DIR,
    Mode,
    ResearchRequest,
    ResearchResponse,
    WatchAdd,
    ThesisAdd,
    ThesisStatus,
    _check_access,
    check_access,
    get_agent,
    log,
    clear_settings_cache,
    get_settings,
    setup_logging,
    build_investment_agent,
    extract_final_text,
    append_turn,
    new_session_id,
    session_context_block,
    run_brief,
    build_catalog,
    search_catalog,
    run_doctor,
    list_templates,
    render_template,
    theses_ops,
    watch_ops,
    extract_scorecard_table,
    validate_report_structure,
    export_report_bundle,
    list_reports,
    read_report,
    save_report_file,
    get_cost_tracker,
    reset_cost_tracker,
    __version__,
)



def register(app: FastAPI) -> None:
    """Register core routes."""
    @app.get("/", response_class=HTMLResponse)
    def index():
        p = STATIC_DIR / "index.html"
        if p.is_file():
            return FileResponse(p)
        return HTMLResponse("<h1>Chokepoint Agent</h1><a href='/docs'>/docs</a>")



    @app.get("/about")
    def api_about():
        """Public capability snapshot (no secrets)."""
        from src import __version__
        from src.ops.pro import PRO_MODULE_IDS
        from src.playbooks.registry import list_playbooks
        from src.questionnaires.registry import list_questionnaires
        from src.rubrics.registry import list_rubrics
        from src.ops.glossary_search import list_glossary_terms
        from src.ops.knowledge_maps import list_maps
        from src.skills.loader import list_skill_packs

        return {
            "name": "Chokepoint Research Agent",
            "version": __version__,
            "disclaimer": "research_only_not_investment_advice",
            "counts": {
                "pro_modules": len(PRO_MODULE_IDS),
                "playbooks": len(list_playbooks()),
                "questionnaires": len(list_questionnaires()),
                "rubrics": len(list_rubrics()),
                "glossary_terms": len(list_glossary_terms()),
                "knowledge_maps": len(list_maps()),
                "skill_packs": len(list_skill_packs()),
            },
        }



    @app.get("/health")
    def health():
        d = run_doctor()
        return {
            "status": "ok" if d["ok"] else "degraded",
            "version": __version__,
            "doctor": d,
            "disclaimer": "research/education only — not investment advice",
        }



    @app.get("/doctor")
    def doctor(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        return run_doctor()



    @app.get("/auth/plugins")
    def auth_plugins(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        # public-ish: list plugin names only (not secrets)
        from src.auth.plugins import build_auth_chain

        _check_access(x_api_key)
        return {"plugins": [p.name for p in build_auth_chain()]}



    @app.get("/metrics")
    def api_metrics(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.pipeline.postprocess import metrics_summary

        return metrics_summary()



    @app.get("/config")
    def api_config(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.config_export import sanitized_config

        return sanitized_config()


