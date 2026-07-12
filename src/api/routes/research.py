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
    """Register research routes."""
    @app.post("/sessions")
    def create_session(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        return {"session_id": new_session_id()}


    # ── reports / catalog ─────────────────────────────────────────────────────



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



    class PdfRequest(BaseModel):
        title: str = "Research Memo"
        markdown: str = Field(..., min_length=2)



    @app.get("/jobs/{job_id}")
    def jobs_get(job_id: str, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.jobs import get_job

        job = get_job(job_id)
        if not job:
            raise HTTPException(404, "job not found")
        return job



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


