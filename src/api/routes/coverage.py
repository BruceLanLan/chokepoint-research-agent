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
    """Register coverage routes."""
    @app.get("/thesis-links")
    def api_thesis_links(
        thesis_id: str | None = None,
        report: str | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.thesis_links import graph_edges, links_for_report, links_for_thesis

        if thesis_id:
            return {"items": links_for_thesis(thesis_id)}
        if report:
            return {"items": links_for_report(report)}
        return graph_edges()



    @app.post("/thesis-links")
    def api_thesis_link_write(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.thesis_links import link_report_to_thesis

        out = link_report_to_thesis(
            body.get("thesis_id") or "",
            body.get("report") or "",
            rel=body.get("rel") or "supports",
        )
        if out.get("error"):
            raise HTTPException(404, out["error"])
        return out



    @app.get("/watchlist")
    def watchlist_list(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        return {"items": watch_ops.list_items()}



    @app.post("/watchlist")
    def watchlist_add(body: WatchAdd, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        return watch_ops.add_item(**body.model_dump())



    @app.delete("/watchlist/{item_id}")
    def watchlist_del(item_id: str, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        if not watch_ops.remove_item(item_id):
            raise HTTPException(404, "not found")
        return {"ok": True}


    # ── theses ────────────────────────────────────────────────────────────────



    @app.get("/theses")
    def theses_list(
        status: str = "",
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        return {"items": theses_ops.list_theses(status=status or None)}



    @app.post("/theses")
    def theses_add(body: ThesisAdd, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        return theses_ops.add_thesis(**body.model_dump())



    @app.post("/theses/{thesis_id}/status")
    def theses_status(
        thesis_id: str,
        body: ThesisStatus,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        item = theses_ops.set_status(thesis_id, body.status, note=body.note)
        if not item:
            raise HTTPException(404, "not found")
        return item


    # ── templates ─────────────────────────────────────────────────────────────



    @app.get("/graph")
    def api_graph(
        mermaid: bool = False,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.thesis_graph import build_thesis_graph, to_mermaid

        g = build_thesis_graph()
        if mermaid:
            return {"mermaid": to_mermaid(g), "stats": g.get("stats")}
        return g



    @app.get("/kill-monitor")
    def api_kill_monitor(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.kill_monitor import kill_criteria_dashboard

        return kill_criteria_dashboard()



    @app.get("/thesis-health")
    def api_thesis_health(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.thesis_health import thesis_health_report

        return thesis_health_report()



    @app.post("/watchlist/bulk")
    def api_watch_bulk(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.watchlist_bulk import bulk_add_symbols

        symbols = body.get("symbols") or body.get("symbol") or ""
        return bulk_add_symbols(symbols, priority=body.get("priority") or "medium")



    @app.get("/hypotheses")
    def api_hypotheses(
        status: str | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.hypotheses import list_hypotheses

        return {"items": list_hypotheses(status=status)}



    @app.post("/hypotheses")
    def api_hypothesis_write(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.hypotheses import add_hypothesis, promote_to_thesis

        if body.get("promote"):
            out = promote_to_thesis(body["promote"])
            if out.get("error"):
                raise HTTPException(404, out["error"])
            return out
        statement = body.get("statement") or ""
        if not statement:
            raise HTTPException(400, "statement or promote required")
        return add_hypothesis(
            statement,
            system=body.get("system") or "",
            evidence_needed=body.get("evidence_needed"),
            related_thesis_id=body.get("related_thesis_id"),
        )


