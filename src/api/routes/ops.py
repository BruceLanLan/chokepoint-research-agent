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
    """Register ops routes."""
    @app.post("/migrate")
    def api_migrate(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.store_migrate import migrate_data_stores

        return migrate_data_stores()



    @app.get("/analytics")
    def analytics(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.analytics import workspace_analytics

        return workspace_analytics()



    class ScheduleInstall(BaseModel):
        hour: int = 9
        minute: int = 0
        limit: int = 3



    @app.get("/schedule/status")
    def api_schedule_status(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.scheduler import schedule_status

        return schedule_status()



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



    @app.get("/charts/coverage")
    def chart_coverage(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from fastapi.responses import Response

        from src.charts.coverage import coverage_heat_svg

        return Response(content=coverage_heat_svg(), media_type="image/svg+xml")



    @app.get("/dashboard")
    def api_dashboard(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.cost_dashboard import cost_quality_dashboard

        return cost_quality_dashboard()



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
        if body.get("vertical") or body.get("vertical_id"):
            from src.ops.research_queue import enqueue_vertical

            return enqueue_vertical(
                str(body.get("vertical") or body.get("vertical_id")),
                system=str(body.get("system") or ""),
                context=str(body.get("context") or ""),
                priority=int(body.get("priority") or 30),
            )
        q = body.get("question") or ""
        if not q:
            raise HTTPException(400, "question or from_watchlist/from_map/vertical required")
        return enqueue(
            q,
            mode=body.get("mode") or "chokepoint_fast",
            skill=body.get("skill"),
            vertical=body.get("vertical") or body.get("vertical_id"),
            priority=int(body.get("priority") or 50),
        )



    @app.post("/queue/run")
    def api_queue_run(
        body: dict | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        """Process queue with mock runner by default. Set live=true to use LLM (costs tokens)."""
        _check_access(x_api_key)
        body = body or {}
        n = int(body.get("n") or 1)
        live = bool(body.get("live"))
        from src.ops.queue_worker import process_batch

        run_fn = None
        if live:
            from src.ops.live_safety import assert_live_allowed

            accept = bool(body.get("i_accept_live_costs") or body.get("accept_live_costs"))
            try:
                assert_live_allowed(flag=accept)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            from src.agents.research_agent import build_investment_agent, extract_final_text

            settings = get_settings()
            cache: dict = {}

            def run_fn(question: str, mode_s: str, skill_s: str | None = None) -> dict:
                key = f"{mode_s}:{skill_s or ''}"
                if key not in cache:
                    cache[key] = build_investment_agent(settings, mode=mode_s, skill=skill_s)  # type: ignore[arg-type]
                agent = cache[key]
                result = agent.invoke({"messages": [{"role": "user", "content": question}]})
                return {"report": extract_final_text(result)}

        return process_batch(n=n, run_fn=run_fn, dry_run=not live)



    @app.get("/queue/estimate-live")
    def api_queue_estimate_live(
        n: int = 1,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.live_safety import estimate_queue_live_cost

        return estimate_queue_live_cost(n=n)



    @app.post("/auto-tag")
    def api_auto_tag(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.auto_tag import auto_tag_report

        name = body.get("report") or ""
        out = auto_tag_report(name)
        if out.get("error"):
            raise HTTPException(404, out["error"])
        return out



    @app.get("/quotes/capabilities")
    def api_quotes_capabilities(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.quotes_meta import quotes_capabilities

        return quotes_capabilities()



    @app.get("/workspace-health")
    def api_workspace_health(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.workspace_health import workspace_health_score

        return workspace_health_score()



    @app.get("/runbook")
    def api_runbook(
        system: str = "",
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.runbook import professional_runbook

        return professional_runbook(system=system)



    @app.get("/batch-review")
    def api_batch_review(
        limit: int = 20,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.batch_review import batch_structure_review

        return batch_structure_review(limit=limit)



    @app.post("/weekly-ops")
    def api_weekly_ops(
        body: dict | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        body = body or {}
        from src.ops.weekly_ops import run_weekly_ops

        return run_weekly_ops(
            save=bool(body.get("save", True)),
            enqueue_watchlist=int(body.get("enqueue") or 0),
        )



    @app.get("/quotes/cache")
    def api_quotes_cache(
        symbol: str | None = None,
        summary: bool = False,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.quote_cache import history_summary, load_history

        if summary or not symbol:
            return history_summary(symbol)
        return {"items": load_history(symbol, limit=100)}



    @app.post("/quotes/cache/refresh")
    def api_quotes_cache_refresh(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.quote_cache import refresh_symbols

        if body.get("from_watchlist"):
            from src.ops.coverage_refresh import refresh_watchlist_quotes

            return refresh_watchlist_quotes(limit=int(body.get("limit") or 50))
        symbols = body.get("symbols") or []
        if isinstance(symbols, str):
            symbols = [s.strip() for s in symbols.split(",") if s.strip()]
        if not symbols:
            raise HTTPException(400, "symbols or from_watchlist required")
        return refresh_symbols(list(symbols))



    @app.get("/desk")
    def api_desk(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.research_desk import research_desk_status

        return research_desk_status()

    @app.post("/demo-journey")
    def api_demo_journey(
        body: dict | None = None,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        """Offline golden-path demo for new users (no LLM)."""
        _check_access(x_api_key)
        from src.ops.demo_journey import run_demo_journey

        body = body or {}
        return run_demo_journey(
            vertical=str(body.get("vertical") or "cpo_optics"),
            save=bool(body.get("save", True)),
        )



    @app.get("/charts/quote-history")
    def api_quote_history_chart(
        symbol: str,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from fastapi.responses import Response

        from src.charts.quote_history import quote_history_svg

        return Response(content=quote_history_svg(symbol), media_type="image/svg+xml")



    @app.post("/quotes/multi")
    def api_multi_quotes(
        body: dict,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.multi_quotes import multi_quote_snapshot

        return multi_quote_snapshot(body.get("symbols") or [])



    @app.get("/quality-board")
    def api_quality_board(
        limit: int = 30,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.quality_board import quality_leaderboard

        return quality_leaderboard(limit=limit)



    @app.get("/digest")
    def api_digest(
        save: bool = False,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ):
        _check_access(x_api_key)
        from src.ops.digest import build_workspace_digest

        return build_workspace_digest(save=save)



    @app.post("/eval/record")
    def api_eval_record(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.eval_history import record_eval_run

        return record_eval_run()



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

    @app.get("/eval/trend")
    def api_eval_trend(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
        _check_access(x_api_key)
        from src.ops.eval_history import eval_trend

        return eval_trend()


