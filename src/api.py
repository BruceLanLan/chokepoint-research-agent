"""FastAPI research workstation API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, AsyncIterator, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

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
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Chokepoint Research Agent",
    description=(
        "Professional multi-agent research workstation powered by Chokepoint Theory. "
        "Research/education only — not investment advice."
    ),
    version=__version__,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# rate limit + request id (order: last added runs first)
from src.api_middleware import RequestIdMiddleware, SimpleRateLimitMiddleware  # noqa: E402
from src.config import get_settings as _gs  # noqa: E402

_s0 = _gs()
app.add_middleware(
    SimpleRateLimitMiddleware,
    max_requests=_s0.api_rate_limit,
    window_seconds=_s0.api_rate_window_seconds,
)
app.add_middleware(RequestIdMiddleware)
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

_agents: dict[str, object] = {}
Mode = Literal["full", "chokepoint_fast", "risk_only", "compare"]


def _check_access(
    x_api_key: str | None = None,
    authorization: str | None = None,
) -> None:
    """Pluggable auth: API key / bearer / OIDC (see src/auth)."""
    from src.auth.base import AuthError
    from src.auth.plugins import authenticate_request

    try:
        authenticate_request(authorization, x_api_key)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


def get_agent(mode: str = "full"):
    if mode not in _agents:
        setup_logging(get_settings().log_level)
        _agents[mode] = build_investment_agent(get_settings(), mode=mode)  # type: ignore[arg-type]
    return _agents[mode]


class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=2)
    save_report: bool = True
    mode: Mode = "full"
    session_id: Optional[str] = None
    bilingual: bool = False
    export: bool = True
    template_id: Optional[str] = None
    template_vars: Optional[dict[str, str]] = None


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


@app.on_event("startup")
def _startup():
    clear_settings_cache()
    setup_logging(get_settings().log_level)
    log.info("API v%s starting", __version__)


@app.get("/", response_class=HTMLResponse)
def index():
    p = STATIC_DIR / "index.html"
    if p.is_file():
        return FileResponse(p)
    return HTMLResponse("<h1>Chokepoint Agent</h1><a href='/docs'>/docs</a>")


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


@app.post("/sessions")
def create_session(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    return {"session_id": new_session_id()}


# ── reports / catalog ─────────────────────────────────────────────────────


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


def _resolve_question(req: ResearchRequest) -> tuple[str, str]:
    mode = req.mode
    question = req.question
    if req.template_id:
        rendered = render_template(req.template_id, req.template_vars or {})
        question = rendered["question"]
        mode = rendered.get("mode") or mode  # type: ignore[assignment]
    if req.session_id:
        ctx = session_context_block(req.session_id)
        if ctx:
            question = f"{question}\n\n{ctx}"
    return question, mode  # type: ignore[return-value]


@app.post("/research", response_model=ResearchResponse)
def research(req: ResearchRequest, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    try:
        reset_cost_tracker()
        settings = get_settings()
        if req.bilingual:
            object.__setattr__(settings, "bilingual_memo", True)
        q, mode = _resolve_question(req)
        agent = get_agent(mode)
        result = agent.invoke({"messages": [{"role": "user", "content": q}]})
        report = extract_final_text(result)
        quality = validate_report_structure(report)
        card = extract_scorecard_table(report)
        cost = get_cost_tracker().summary()
        saved = None
        exports = None
        if req.save_report:
            saved = save_report_file(
                title=req.question[:40], markdown_body=report, mode=mode, quality=quality
            )
        if req.export:
            exports = export_report_bundle(
                title=req.question[:40], markdown_body=report, mode=mode, extra={"cost": cost}
            )
        if req.session_id:
            append_turn(
                req.session_id,
                question=req.question,
                report=report,
                mode=mode,
                meta={"quality": quality, "cost": cost},
            )
        return ResearchResponse(
            question=req.question,
            report=report,
            mode=mode,
            saved_path=saved,
            exports=exports,
            quality=quality,
            scorecard_nodes=len(card.nodes),
            session_id=req.session_id,
            cost=cost,
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        log.exception("research failed")
        raise HTTPException(500, str(exc)) from exc


@app.post("/research/stream")
async def research_stream(
    req: ResearchRequest, x_api_key: str | None = Header(default=None, alias="X-API-Key")
):
    _check_access(x_api_key)

    async def event_gen() -> AsyncIterator[dict]:
        try:
            reset_cost_tracker()
            q, mode = _resolve_question(req)
            agent = get_agent(mode)
            yield {
                "event": "start",
                "data": json.dumps({"question": req.question, "mode": mode}, ensure_ascii=False),
            }
            final_text = ""
            for event in agent.stream(
                {"messages": [{"role": "user", "content": q}]}, stream_mode="updates"
            ):
                if not isinstance(event, dict):
                    continue
                for node, update in event.items():
                    preview = ""
                    if isinstance(update, dict):
                        messages = update.get("messages") or []
                        if messages:
                            last = messages[-1]
                            content = getattr(last, "content", "")
                            if isinstance(content, str):
                                preview = content[:800]
                                final_text = content
                    yield {
                        "event": "update",
                        "data": json.dumps({"node": str(node), "preview": preview}, ensure_ascii=False),
                    }
            quality = validate_report_structure(final_text)
            cost = get_cost_tracker().summary()
            path = None
            exports = None
            if req.save_report and final_text:
                path = save_report_file(
                    title=req.question[:40], markdown_body=final_text, mode=mode, quality=quality
                )
            if req.export and final_text:
                exports = export_report_bundle(
                    title=req.question[:40], markdown_body=final_text, mode=mode, extra={"cost": cost}
                )
            yield {
                "event": "final",
                "data": json.dumps(
                    {
                        "report": final_text,
                        "saved_path": path,
                        "exports": exports,
                        "quality": quality,
                        "cost": cost,
                    },
                    ensure_ascii=False,
                ),
            }
            yield {"event": "done", "data": "[DONE]"}
        except Exception as exc:  # noqa: BLE001
            yield {"event": "error", "data": json.dumps({"error": str(exc)}, ensure_ascii=False)}

    return EventSourceResponse(event_gen())


@app.post("/brief")
def brief(
    limit: int = 3,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    """Run watchlist brief (synchronous, can be slow)."""
    _check_access(x_api_key)
    settings = get_settings()
    cache: dict[str, Any] = {}

    def invoke_fn(question: str, mode: str) -> str:
        if mode not in cache:
            cache[mode] = build_investment_agent(settings, mode=mode)  # type: ignore[arg-type]
        result = cache[mode].invoke({"messages": [{"role": "user", "content": question}]})
        return extract_final_text(result)

    return run_brief(invoke_fn=invoke_fn, limit=limit, save=True)


# ── analytics / providers / async jobs ────────────────────────────────────


@app.get("/analytics")
def analytics(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.ops.analytics import workspace_analytics

    return workspace_analytics()


@app.get("/providers")
def providers(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.providers.base import get_registry

    return get_registry().list_providers()


class JobSubmit(BaseModel):
    question: str = Field(..., min_length=2)
    mode: Mode = "chokepoint_fast"


@app.post("/jobs")
def jobs_submit(body: JobSubmit, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    """Submit async research job (poll GET /jobs/{id})."""
    _check_access(x_api_key)
    from src.ops.jobs import submit_research_job

    settings = get_settings()

    def run_fn(question: str, mode: str) -> dict[str, Any]:
        reset_cost_tracker()
        agent = build_investment_agent(settings, mode=mode)  # type: ignore[arg-type]
        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        report = extract_final_text(result)
        quality = validate_report_structure(report)
        saved = save_report_file(
            title=question[:40], markdown_body=report, mode=mode, quality=quality
        )
        return {
            "report_preview": (report or "")[:3000],
            "report_chars": len(report or ""),
            "quality": quality,
            "saved_path": saved,
            "cost": get_cost_tracker().summary(),
        }

    return submit_research_job(question=body.question, mode=body.mode, run_fn=run_fn)


@app.get("/jobs")
def jobs_list(
    limit: int = 20,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)
    from src.ops.jobs import list_jobs

    return {"items": list_jobs(limit=limit)}


@app.get("/jobs/{job_id}")
def jobs_get(job_id: str, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.ops.jobs import get_job

    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return job


class PdfRequest(BaseModel):
    title: str = "Research Memo"
    markdown: str = Field(..., min_length=2)


@app.post("/export/pdf")
def export_pdf(body: PdfRequest, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.tools.pdf_report import markdown_to_pdf

    out = markdown_to_pdf(body.title, body.markdown)
    if out.get("error") and not out.get("path"):
        raise HTTPException(500, out)
    return out


@app.get("/schedule/status")
def api_schedule_status(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.ops.scheduler import schedule_status

    return schedule_status()


class ScheduleInstall(BaseModel):
    hour: int = 9
    minute: int = 0
    limit: int = 3


@app.post("/schedule/install")
def api_schedule_install(
    body: ScheduleInstall, x_api_key: str | None = Header(default=None, alias="X-API-Key")
):
    _check_access(x_api_key)
    from src.ops.scheduler import install_schedule, load_schedule, save_schedule

    cfg = load_schedule()
    cfg["limit"] = body.limit
    save_schedule(cfg)
    return install_schedule(hour=body.hour, minute=body.minute)


@app.post("/schedule/uninstall")
def api_schedule_uninstall(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.ops.scheduler import uninstall_schedule

    return uninstall_schedule()


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


@app.get("/auth/plugins")
def auth_plugins(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    # public-ish: list plugin names only (not secrets)
    from src.auth.plugins import build_auth_chain

    _check_access(x_api_key)
    return {"plugins": [p.name for p in build_auth_chain()]}


@app.get("/skills")
def api_skills(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.skills.loader import list_skill_packs

    return {"items": list_skill_packs()}


@app.get("/metrics")
def api_metrics(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.pipeline.postprocess import metrics_summary

    return metrics_summary()


@app.post("/pipeline/postprocess")
def api_postprocess(
    body: dict,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    """Post-process markdown without LLM (charts + quality)."""
    _check_access(x_api_key)
    from src.pipeline.postprocess import postprocess_memo

    md = body.get("markdown") or ""
    title = body.get("title") or "memo"
    mode = body.get("mode") or "full"
    return postprocess_memo(title, md, mode=mode, embed_charts=True)


@app.get("/charts/scorecard")
def chart_scorecard(
    name: str,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    """SVG scorecard from a saved report name."""
    _check_access(x_api_key)
    from src.charts.scorecard import charts_from_memo
    from src.tools.reports import read_report
    from fastapi.responses import Response

    body = read_report(name)
    if not body:
        raise HTTPException(404, "report not found")
    svg = charts_from_memo(body).get("scorecard_svg") or ""
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/quotes/stream")
async def quotes_stream(
    symbol: str,
    interval: float = 5.0,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    """SSE polling quote stream (best-effort, not a full market data terminal)."""
    _check_access(x_api_key)
    import asyncio
    import json as _json

    from src.tools.research_tools import get_market_snapshot

    interval = max(2.0, min(float(interval or 5), 60.0))

    async def gen():
        for _ in range(30):  # cap ~ few minutes
            try:
                raw = get_market_snapshot.invoke({"symbol": symbol})
                yield {"event": "quote", "data": raw if isinstance(raw, str) else _json.dumps(raw)}
            except Exception as exc:  # noqa: BLE001
                yield {"event": "error", "data": _json.dumps({"error": str(exc)})}
            await asyncio.sleep(interval)
        yield {"event": "done", "data": "[DONE]"}

    return EventSourceResponse(gen())


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


@app.post("/compare-memos")
def api_compare_memos(
    body: dict,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)
    from src.ops.compare_memos import compare_memos

    names = body.get("names") or body.get("reports") or []
    if len(names) < 2:
        raise HTTPException(400, "need at least 2 report names")
    return compare_memos(list(names))


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


@app.get("/kill-monitor")
def api_kill_monitor(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.ops.kill_monitor import kill_criteria_dashboard

    return kill_criteria_dashboard()


@app.get("/coverage")
def api_coverage(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.ops.coverage_heat import coverage_heatmap

    return coverage_heatmap()


@app.get("/audit")
def api_audit(
    limit: int = 30,
    summary: bool = False,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)
    from src.ops.audit import audit_summary, list_events

    if summary:
        return audit_summary()
    return {"items": list_events(limit=limit)}


@app.post("/snapshot")
def api_snapshot(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.ops.snapshot import create_snapshot

    return create_snapshot()


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


@app.get("/providers/health")
def api_provider_health(
    live: bool = False,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)
    from src.ops.provider_health import probe_providers

    return probe_providers(live=live)


@app.post("/plan")
def api_plan(
    body: dict,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)
    from src.ops.research_plan import build_research_plan

    topic = body.get("topic") or body.get("system") or ""
    if not topic:
        raise HTTPException(400, "topic required")
    return build_research_plan(
        topic,
        skill=body.get("skill"),
        template_id=body.get("template_id") or "chokepoint_map",
        mode=body.get("mode"),
    )


@app.get("/charts/coverage")
def chart_coverage(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from fastapi.responses import Response

    from src.charts.coverage import coverage_heat_svg

    return Response(content=coverage_heat_svg(), media_type="image/svg+xml")


@app.get("/maps")
def api_maps(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.ops.knowledge_maps import list_maps

    return {"items": list_maps()}


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


@app.get("/dashboard")
def api_dashboard(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    from src.ops.cost_dashboard import cost_quality_dashboard

    return cost_quality_dashboard()


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


@app.get("/queue")
def api_queue(
    summary: bool = False,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)
    from src.ops.research_queue import list_queue, queue_summary

    if summary:
        return queue_summary()
    return {"items": list_queue()}


@app.post("/queue")
def api_queue_add(
    body: dict,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)
    from src.ops.research_queue import enqueue, enqueue_from_map, enqueue_from_watchlist

    if body.get("from_watchlist"):
        return {"items": enqueue_from_watchlist(limit=int(body.get("limit") or 10))}
    if body.get("from_map"):
        return enqueue_from_map(body["from_map"])
    q = body.get("question") or ""
    if not q:
        raise HTTPException(400, "question or from_watchlist/from_map required")
    return enqueue(
        q,
        mode=body.get("mode") or "chokepoint_fast",
        skill=body.get("skill"),
        priority=int(body.get("priority") or 50),
    )


@app.websocket("/ws/quotes")
async def ws_quotes(websocket):  # type: ignore[no-untyped-def]
    """WebSocket quote stream (polling under the hood; research utility only)."""
    await websocket.accept()
    try:
        import asyncio
        import json as _json

        from src.tools.research_tools import get_market_snapshot

        # first message may be {"symbol":"AAPL","interval":5}
        init = await websocket.receive_text()
        try:
            cfg = _json.loads(init)
        except Exception:  # noqa: BLE001
            cfg = {"symbol": init.strip()}
        symbol = str(cfg.get("symbol") or "AAPL")
        interval = max(2.0, min(float(cfg.get("interval") or 5), 60.0))
        for _ in range(40):
            try:
                raw = get_market_snapshot.invoke({"symbol": symbol})
                await websocket.send_text(raw if isinstance(raw, str) else _json.dumps(raw))
            except Exception as exc:  # noqa: BLE001
                await websocket.send_text(_json.dumps({"error": str(exc)}))
            await asyncio.sleep(interval)
        await websocket.send_text(_json.dumps({"event": "done"}))
    except Exception:  # noqa: BLE001
        pass
    finally:
        try:
            await websocket.close()
        except Exception:  # noqa: BLE001
            pass
