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
    """Register reports routes."""
    @app.get("/reports")
    def reports(
        limit: int = 20,
        q: str = "",
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        if q:
            return {"items": search_catalog(q, limit=limit)}
        return {"items": build_catalog(limit=limit)}



    @app.get("/reports/{name}")
    def report_detail(name: str, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        body = read_report(name)
        if body is None:
            raise HTTPException(404, "Report not found")
        return {"name": Path(name).name, "content": body}


    # ── watchlist ─────────────────────────────────────────────────────────────



    @app.get("/templates")
    def templates(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        return {"items": list_templates()}



    @app.post("/templates/{template_id}/render")
    def template_render(
        template_id: str,
        variables: dict[str, str] | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        try:
            return render_template(template_id, variables or {})
        except KeyError as exc:
            raise HTTPException(404, str(exc)) from exc


    # ── research ──────────────────────────────────────────────────────────────



    @app.post("/export/pdf")
    def export_pdf(body: PdfRequest, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.tools.pdf_report import markdown_to_pdf

        out = markdown_to_pdf(body.title, body.markdown)
        if out.get("error") and not out.get("path"):
            raise HTTPException(500, out)
        return out



    @app.post("/export/docx")
    def api_export_docx(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.tools.docx_report import markdown_to_docx
        from src.tools.reports import read_report

        name = body.get("report") or ""
        md = body.get("markdown") or ""
        title = body.get("title") or name or "memo"
        if name and not md:
            md = read_report(name) or ""
        if not md:
            raise HTTPException(400, "markdown or report required")
        return markdown_to_docx(title, md, mode=body.get("mode") or "full")



    @app.post("/export-pack")
    def api_export_pack(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.export_pack import build_export_pack

        name = body.get("report") or ""
        out = build_export_pack(name)
        if out.get("error"):
            raise HTTPException(404, out["error"])
        return out



    @app.get("/notion-export/{report_name}")
    def api_notion_export(
        report_name: str,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.notion_export import export_report_for_notion

        out = export_report_for_notion(report_name)
        if out.get("error"):
            raise HTTPException(404, out["error"])
        return out



    @app.get("/grade/{name}")
    def api_grade_memo(
        name: str,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.memo_grade import grade_memo

        out = grade_memo(name)
        if out.get("error"):
            raise HTTPException(404, out["error"])
        return out



    @app.post("/reports/{name}/enrich")
    def api_enrich_report(
        name: str,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.report_frontmatter import enrich_report_frontmatter

        out = enrich_report_frontmatter(name)
        if out.get("error"):
            raise HTTPException(404, out["error"])
        return out



    @app.get("/checklist/{name}")
    def api_checklist(
        name: str,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.checklist import run_checklist

        out = run_checklist(report_name=name)
        if out.get("error"):
            raise HTTPException(404, out["error"])
        return out


