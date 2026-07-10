"""FastAPI surface for the chokepoint research agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncIterator, Literal, Optional

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
from src.schemas.scorecard import extract_scorecard_table, validate_report_structure  # noqa: E402
from src.tools.export import export_report_bundle  # noqa: E402
from src.tools.reports import list_reports, read_report, save_report_file  # noqa: E402
from src.tools.resilience import get_cost_tracker, reset_cost_tracker  # noqa: E402

log = get_logger("chokepoint.api")
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Chokepoint Research Agent",
    description=(
        "Multi-agent investment research system powered by Chokepoint Theory. "
        "For research/education only — not investment advice."
    ),
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

_agents: dict[str, object] = {}
Mode = Literal["full", "chokepoint_fast", "risk_only", "compare"]


def _check_access(x_api_key: str | None) -> None:
    expected = get_settings().api_access_key
    if not expected:
        return
    if not x_api_key or x_api_key != expected:
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


@app.on_event("startup")
def _startup():
    clear_settings_cache()
    setup_logging(get_settings().log_level)
    log.info("API starting v%s", __version__)


@app.get("/", response_class=HTMLResponse)
def index():
    index_path = STATIC_DIR / "index.html"
    if index_path.is_file():
        return FileResponse(index_path)
    return HTMLResponse("<h1>Chokepoint Research Agent</h1><a href='/docs'>/docs</a>")


@app.get("/health")
def health():
    settings = get_settings()
    problems = settings.validate_runtime(require_tavily=True)
    return {
        "status": "ok"
        if not any("API_KEY" in p and "TAVILY" not in p for p in problems)
        else "degraded",
        "service": "chokepoint-research-agent",
        "version": __version__,
        "config_warnings": problems,
        "disclaimer": "research/education only — not investment advice",
    }


@app.post("/sessions")
def create_session(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    _check_access(x_api_key)
    return {"session_id": new_session_id()}


@app.get("/reports")
def reports(
    limit: int = 20,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)
    return {"items": list_reports(limit=limit)}


@app.get("/reports/{name}")
def report_detail(
    name: str,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)
    body = read_report(name)
    if body is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"name": Path(name).name, "content": body}


@app.post("/research", response_model=ResearchResponse)
def research(
    req: ResearchRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)
    try:
        reset_cost_tracker()
        settings = get_settings()
        if req.bilingual:
            object.__setattr__(settings, "bilingual_memo", True)
        agent = get_agent(req.mode)
        q = req.question
        if req.session_id:
            ctx = session_context_block(req.session_id)
            if ctx:
                q = f"{req.question}\n\n{ctx}"
        log.info("research mode=%s q=%s", req.mode, req.question[:80])
        result = agent.invoke({"messages": [{"role": "user", "content": q}]})
        report = extract_final_text(result)
        quality = validate_report_structure(report)
        card = extract_scorecard_table(report)
        cost = get_cost_tracker().summary()
        saved = None
        exports = None
        if req.save_report:
            saved = save_report_file(
                title=req.question[:40],
                markdown_body=report,
                mode=req.mode,
                quality=quality,
            )
        if req.export:
            exports = export_report_bundle(
                title=req.question[:40],
                markdown_body=report,
                mode=req.mode,
                extra={"cost": cost},
            )
        if req.session_id:
            append_turn(
                req.session_id,
                question=req.question,
                report=report,
                mode=req.mode,
                meta={"quality": quality, "cost": cost},
            )
        return ResearchResponse(
            question=req.question,
            report=report,
            mode=req.mode,
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
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/research/stream")
async def research_stream(
    req: ResearchRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _check_access(x_api_key)

    async def event_gen() -> AsyncIterator[dict]:
        try:
            reset_cost_tracker()
            agent = get_agent(req.mode)
            q = req.question
            if req.session_id:
                ctx = session_context_block(req.session_id)
                if ctx:
                    q = f"{req.question}\n\n{ctx}"
            payload = {"messages": [{"role": "user", "content": q}]}
            yield {
                "event": "start",
                "data": json.dumps(
                    {"question": req.question, "mode": req.mode, "session_id": req.session_id},
                    ensure_ascii=False,
                ),
            }

            final_text = ""
            for event in agent.stream(payload, stream_mode="updates"):
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
                                if getattr(last, "type", "") == "ai" or "model" in str(node):
                                    final_text = content
                    yield {
                        "event": "update",
                        "data": json.dumps(
                            {"node": str(node), "preview": preview},
                            ensure_ascii=False,
                        ),
                    }

            quality = validate_report_structure(final_text)
            cost = get_cost_tracker().summary()
            path = None
            exports = None
            if req.save_report and final_text:
                path = save_report_file(
                    title=req.question[:40],
                    markdown_body=final_text,
                    mode=req.mode,
                    quality=quality,
                )
            if req.export and final_text:
                exports = export_report_bundle(
                    title=req.question[:40],
                    markdown_body=final_text,
                    mode=req.mode,
                    extra={"cost": cost},
                )
            if req.session_id and final_text:
                append_turn(
                    req.session_id,
                    question=req.question,
                    report=final_text,
                    mode=req.mode,
                    meta={"quality": quality},
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
            yield {
                "event": "error",
                "data": json.dumps({"error": str(exc)}, ensure_ascii=False),
            }

    return EventSourceResponse(event_gen())
