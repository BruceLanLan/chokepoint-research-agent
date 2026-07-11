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


def _check_access(x_api_key: str | None) -> None:
    expected = get_settings().api_access_key
    if expected and (not x_api_key or x_api_key != expected):
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


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
