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
    """Register pro routes."""
    @app.get("/pro/verticals")
    def api_pro_verticals(
        full: bool = True,
        q: str | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.pro.verticals import list_verticals, suggest_vertical

        items = list_verticals(full=full)
        if q:
            return {
                "query": q,
                "suggestions": suggest_vertical(q),
                "items": items,
                "count": len(items),
            }
        return {"items": items, "count": len(items)}

    @app.get("/pro/verticals/{vertical_id}")
    def api_pro_vertical_one(
        vertical_id: str,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.pro.verticals import load_vertical, scaffold_research_question

        data = load_vertical(vertical_id)
        if not data:
            raise HTTPException(404, f"unknown vertical: {vertical_id}")
        return {
            "vertical": data,
            "scaffold": scaffold_research_question(vertical_id),
            "disclaimer": data.get("disclaimer"),
        }

    @app.post("/pro/verticals/{vertical_id}/scaffold")
    def api_pro_vertical_scaffold(
        vertical_id: str,
        body: dict | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.pro.verticals import scaffold_research_question

        body = body or {}
        out = scaffold_research_question(
            vertical_id,
            system=str(body.get("system") or ""),
            context=str(body.get("context") or ""),
        )
        if out.get("error"):
            raise HTTPException(404, out["error"])
        return out



    class JobSubmit(BaseModel):
        question: str = Field(..., min_length=2)
        mode: Mode = "chokepoint_fast"



    @app.get("/providers")
    def providers(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.providers.base import get_registry

        return get_registry().list_providers()



    @app.get("/providers/health")
    def api_provider_health(
        live: bool = False,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.provider_health import probe_providers

        return probe_providers(live=live)



    @app.get("/pro/modules")
    def api_pro_modules(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.pro.registry import list_modules

        return {"count": len(list_modules()), "items": list_modules()}

    # Register static /pro/suite BEFORE /pro/{module_id} so "suite" is not captured.
    @app.post("/pro/suite")
    def api_pro_suite(
        body: dict | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.pro.suite import run_suite

        body = body or {}
        return run_suite(
            text=body.get("text") or "",
            symbol=body.get("symbol") or "",
            title=body.get("title") or "suite",
            vertical=body.get("vertical"),
        )

    @app.post("/pro/{module_id}")
    def api_pro_invoke(
        module_id: str,
        body: dict | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.pro.registry import invoke_module

        body = body or {}
        out = invoke_module(module_id, **body)
        if out.get("error") and out.get("known"):
            raise HTTPException(404, out["error"])
        return out



    @app.get("/pro/dashboard")
    def api_pro_dashboard(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.pro_dashboard import pro_dashboard

        return pro_dashboard()



    @app.post("/memo-pro")
    def api_memo_pro(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.memo_pro_bridge import analyze_memo_with_pro

        name = body.get("report") or ""
        mods = body.get("modules")
        out = analyze_memo_with_pro(
            name,
            modules=mods,
            persist=bool(body.get("persist")),
            symbol=body.get("symbol") or "",
        )
        if out.get("error"):
            raise HTTPException(404, out["error"])
        return out



    @app.post("/pro/export")
    def api_pro_export(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.pro_pack_export import export_pro_pack

        return export_pro_pack()



    @app.get("/questionnaires")
    def api_questionnaires(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.questionnaires.registry import list_questionnaires

        return {"items": list_questionnaires()}



    @app.get("/questionnaires/{name}")
    def api_questionnaire(
        name: str,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.questionnaires.registry import get_questionnaire

        try:
            return get_questionnaire(name)
        except ModuleNotFoundError as exc:
            raise HTTPException(404, str(name)) from exc



    @app.get("/rubrics")
    def api_rubrics(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.rubrics.registry import list_rubrics

        return {"items": list_rubrics()}



    @app.post("/rubrics/score")
    def api_rubrics_score(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.rubrics.registry import score_all

        return score_all(body.get("text") or "")



    @app.get("/playbooks")
    def api_playbooks(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.playbooks.registry import list_playbooks

        return {"items": list_playbooks()}



    @app.get("/playbooks/{name}")
    def api_playbook(
        name: str,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.playbooks.registry import get_playbook

        try:
            return get_playbook(name)
        except ModuleNotFoundError as exc:
            raise HTTPException(404, f"unknown playbook: {name}") from exc


