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
        vertical_id: str = "",
        skill: str = "",
        mode: str = "",
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.catalog import catalog_facets, filter_catalog

        items = filter_catalog(
            q=q,
            vertical_id=vertical_id,
            skill=skill,
            mode=mode,
            limit=limit,
        )
        return {
            "items": items,
            "count": len(items),
            "filters": {
                "q": q or None,
                "vertical_id": vertical_id or None,
                "skill": skill or None,
                "mode": mode or None,
            },
            "facets": catalog_facets(),
        }

    @app.get("/reports/facets")
    def reports_facets(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.catalog import catalog_facets

        return catalog_facets()

    @app.get("/reports/compare")
    def reports_compare_get(
        vertical_id: str = "",
        a: str = "",
        b: str = "",
        udiff: bool = True,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        """Compare two memos or the latest pair for a vertical."""
        _check_access(x_api_key)
        from src.ops.vertical_compare import compare_vertical

        out = compare_vertical(
            vertical_id or None,
            name_a=a or None,
            name_b=b or None,
            include_udiff=udiff,
        )
        if out.get("error") and "need at least 2" in str(out.get("error")):
            raise HTTPException(404, out)
        if out.get("error") and "not found" in str(out.get("error")):
            raise HTTPException(404, out)
        if out.get("error") and "provide vertical" in str(out.get("error")):
            raise HTTPException(400, out)
        return out

    @app.post("/reports/compare")
    def reports_compare_post(
        body: dict | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.vertical_compare import compare_vertical

        body = body or {}
        out = compare_vertical(
            body.get("vertical_id"),
            name_a=body.get("a") or body.get("name_a"),
            name_b=body.get("b") or body.get("name_b"),
            include_udiff=bool(body.get("udiff", True)),
        )
        if out.get("error"):
            code = 400
            err = str(out.get("error"))
            if "not found" in err or "need at least 2" in err:
                code = 404
            raise HTTPException(code, out)
        return out

    @app.get("/reports/by-vertical/{vertical_id}")
    def reports_by_vertical(
        vertical_id: str,
        limit: int = 20,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.vertical_compare import list_vertical_reports

        items = list_vertical_reports(vertical_id, limit=limit)
        return {
            "vertical_id": vertical_id,
            "count": len(items),
            "items": items,
            "disclaimer": "research_only_not_investment_advice",
        }

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
        body: dict | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        """Render a research template.

        Accepts either ``{"vars": {...}}``, ``{"variables": {...}}``, or a flat
        string map of template variables (UI-friendly).
        """
        _check_access(x_api_key)
        body = body or {}
        variables: dict[str, str] = {}
        raw = body.get("vars") if "vars" in body else body.get("variables")
        if raw is None and body and all(isinstance(v, (str, int, float)) for v in body.values()):
            raw = body
        if isinstance(raw, dict):
            variables = {str(k): str(v) for k, v in raw.items()}
        try:
            return render_template(template_id, variables)
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


