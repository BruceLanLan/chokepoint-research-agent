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
    """Register knowledge routes."""
    @app.post("/plugins/install")
    def api_plugin_install(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.plugins.remote_install import install_from_manifest

        out = install_from_manifest(
            body.get("manifest_url") or "",
            dry_run=bool(body.get("dry_run")),
        )
        if not out.get("ok"):
            raise HTTPException(400, out.get("error") or "install failed")
        return out



    @app.get("/search/memos")
    def search_memos_api(
        q: str,
        limit: int = 10,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
        authorization: str | None = Header(default=None),
    ):
        _check_access(x_api_key, authorization)
        from src.ops.memo_search import search_memos

        return {"query": q, "items": search_memos(q, limit=limit)}



    @app.get("/skills")
    def api_skills(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.skills.loader import list_skill_packs

        return {"items": list_skill_packs()}



    @app.get("/evidence")
    def api_evidence(
        summary: bool = False,
        limit: int = 30,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.evidence import evidence_summary, list_evidence

        if summary:
            return evidence_summary()
        return {"items": list_evidence(limit=limit)}



    @app.post("/evidence/extract")
    def api_evidence_extract(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.evidence import extract_and_store
        from src.tools.reports import read_report

        name = body.get("report") or ""
        md = body.get("markdown") or ""
        if name and not md:
            md = read_report(name) or ""
        if not md:
            raise HTTPException(400, "markdown or report required")
        return extract_and_store(md, report_name=name, title=body.get("title") or name)



    @app.get("/tags")
    def api_tags(
        report: str | None = None,
        tag: str | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.tags import find_by_tag, get_tags

        if tag:
            return {"tag": tag, "reports": find_by_tag(tag)}
        return get_tags(report)



    @app.post("/tags")
    def api_tag_report(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.tags import tag_report

        name = body.get("report") or ""
        tags = body.get("tags") or []
        if not name:
            raise HTTPException(400, "report required")
        return tag_report(name, list(tags))



    @app.get("/collections")
    def api_collections(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.tags import list_collections

        return {"items": list_collections()}



    @app.post("/collections")
    def api_create_collection(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.tags import add_to_collection, create_collection

        if body.get("add") and body.get("collection"):
            row = add_to_collection(body["collection"], body["add"])
            if not row:
                raise HTTPException(404, "collection not found")
            return row
        name = body.get("name") or ""
        if not name:
            raise HTTPException(400, "name required")
        return create_collection(name, body.get("reports"), body.get("note") or "")



    @app.get("/plugins")
    def api_plugins(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.plugins.loader import list_plugin_files, load_all_plugins

        return {"files": list_plugin_files(), "loaded": load_all_plugins()}



    @app.get("/citations")
    def api_citations(
        mermaid: bool = False,
        limit: int = 60,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.citation_network import build_citation_network, citation_mermaid

        if mermaid:
            return {"mermaid": citation_mermaid(limit_reports=limit)}
        return build_citation_network(limit_reports=limit)



    @app.get("/lineage")
    def api_lineage(
        report: str | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.lineage import lineage_for, list_lineage

        if report:
            return lineage_for(report)
        return list_lineage()



    @app.post("/lineage")
    def api_lineage_write(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.lineage import create_chain, link_reports

        if body.get("chain"):
            return create_chain(body["chain"], body.get("reports") or [], body.get("note") or "")
        parent, child = body.get("parent"), body.get("child")
        if not parent or not child:
            raise HTTPException(400, "parent+child or chain required")
        return link_reports(parent, child, rel=body.get("rel") or "follows", note=body.get("note") or "")



    @app.get("/maps")
    def api_maps(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.knowledge_maps import list_maps

        return {"items": list_maps()}



    @app.get("/maps/compare")
    def api_compare_maps(
        a: str,
        b: str,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        """Static path must be registered before /maps/{map_id}."""
        _check_access(x_api_key)
        from src.ops.map_compare import compare_maps

        out = compare_maps(a, b)
        if out.get("error"):
            raise HTTPException(404, out["error"])
        return out



    @app.get("/maps/{map_id}")
    def api_map_detail(
        map_id: str,
        mermaid: bool = False,
        seed: bool = False,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.knowledge_maps import map_research_seed, map_to_graph, map_to_mermaid

        if seed:
            return map_research_seed(map_id)
        if mermaid:
            return {"mermaid": map_to_mermaid(map_id)}
        g = map_to_graph(map_id)
        if g.get("error"):
            raise HTTPException(404, g["error"])
        return g



    @app.post("/index/memos")
    def api_index_memos(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.memo_index import rebuild_index

        return rebuild_index()



    @app.get("/index/search")
    def api_index_search(
        q: str,
        limit: int = 15,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.memo_index import search_index

        return {"query": q, "items": search_index(q, limit=limit)}



    @app.get("/plugin-catalog")
    def api_plugin_catalog(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.plugin_catalog import plugin_catalog

        return plugin_catalog()



    @app.get("/marketplace")
    def api_marketplace(
        q: str | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.marketplace import marketplace_index, marketplace_search

        return marketplace_search(q) if q else marketplace_index()



    @app.get("/glossary")
    def api_glossary(
        q: str | None = None,
        term: str | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.glossary_search import get_term, list_glossary_terms, search_glossary

        if term:
            out = get_term(term)
            if out.get("error"):
                raise HTTPException(404, out["error"])
            return out
        if q:
            return search_glossary(q)
        terms = list_glossary_terms()
        return {"count": len(terms), "terms": terms[:100]}


