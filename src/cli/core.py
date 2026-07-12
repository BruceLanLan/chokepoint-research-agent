"""CLI domain module."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from src.cli.common import (
    ROOT,
    VALID_MODES,
    console,
    _boot_env,
)

from src.cli.research import run_research as _run_research



def register(app: typer.Typer) -> None:
    @app.command()
    def doctor(
        ops_only: bool = typer.Option(
            False, "--ops-only", help="Ignore missing model/search keys (ops surface only)"
        ),
    ):
        """Health-check environment, deps, and config."""
        _boot_env()
        from src.ops.doctor import run_doctor
        from src.ops.store_migrate import migrate_data_stores

        mig = migrate_data_stores()
        result = run_doctor()
        table = Table(title="Doctor")
        table.add_column("Bucket")
        table.add_column("Check")
        table.add_column("OK")
        table.add_column("Detail")
        key_checks = {"model_api_key", "tavily_api_key", "model_provider"}
        for c in result["checks"]:
            if ops_only and c.get("bucket") == "config" and c["name"] in key_checks:
                mark = "[yellow]skip[/yellow]"
            elif c["ok"]:
                mark = "[green]yes[/green]"
            else:
                mark = f"[red]{c['level']}[/red]"
            table.add_row(c.get("bucket") or "-", c["name"], mark, str(c["detail"])[:72])
        console.print(table)
        cfg = result.get("config") or {}
        ops = result.get("ops") or {}
        console.print(
            f"ok={result['ok']} live_ready={result.get('live_ready')} "
            f"ops_ok={result.get('ops_ok')} errors={result['errors']} warnings={result['warnings']}"
        )
        console.print(
            f"[cyan]config[/cyan] {cfg.get('grade')}({cfg.get('score')})  "
            f"[cyan]ops[/cyan] {ops.get('grade')}({ops.get('score')})"
        )
        if result.get("hint"):
            console.print(f"[dim]{result['hint']}[/dim]")
        if mig.get("actions"):
            console.print(f"[dim]migrate: {mig['actions']}[/dim]")
        console.print(
            "[dim]Golden path: about → desk → research --mock -V cpo_optics → "
            "checklist → weekly-ops · demo-journey[/dim]"
        )
        if ops_only:
            console.print("[dim]--ops-only: config key failures do not exit non-zero[/dim]")
            if not result.get("ops_ok", True):
                raise typer.Exit(1)
            return
        # Fail only on hard config errors (model key / packages), not missing Tavily warn
        if not result["ok"]:
            raise typer.Exit(1)

    @app.command("demo-journey")
    def demo_journey_cmd(
        vertical: str = typer.Option("cpo_optics", "--vertical", "-V"),
        save: bool = typer.Option(True, "--save/--no-save"),
    ):
        """Offline end-to-end demo: desk → plan → mock memo → vertical suite."""
        _boot_env()
        from src.ops.demo_journey import run_demo_journey

        out = run_demo_journey(vertical=vertical, save=save)
        console.print(out)
        console.print("[green]demo-journey complete (offline)[/green]")



    @app.command("eval")
    def eval_cmd():
        from src.eval.harness import run_all

        result = run_all()
        console.print_json(json.dumps(result, ensure_ascii=False))
        if result["failed"]:
            raise typer.Exit(1)



    @app.command("new-session")
    def new_session_cmd():
        from src.memory.sessions import new_session_id

        console.print(new_session_id())



    @app.command()
    def server(
        host: str = typer.Option("0.0.0.0", "--host"),
        port: int = typer.Option(8000, "--port"),
    ):
        _boot_env()
        import uvicorn

        from src.config import get_settings
        from src.logging_utils import setup_logging

        setup_logging(get_settings().log_level)
        console.print(f"[cyan]Workstation → http://{host}:{port}/[/cyan]")
        console.print("[dim]Research only — not investment advice.[/dim]")
        uvicorn.run("src.api:app", host=host, port=port, reload=False)



    @app.command()
    def analytics(as_json: bool = typer.Option(False, "--json", help="machine-readable")):
        """Print workspace analytics (reports / watchlist / theses)."""
        _boot_env()
        from src.ops.analytics import workspace_analytics

        data = workspace_analytics()
        if as_json:
            print(json.dumps(data, ensure_ascii=False))
        else:
            console.print_json(json.dumps(data, ensure_ascii=False))



    @app.command("diff-reports")
    def diff_reports_cmd(
        a: str = typer.Argument(..., help="report filename A"),
        b: str = typer.Argument(..., help="report filename B"),
    ):
        """Unified diff two saved memos."""
        _boot_env()
        from src.ops.report_diff import diff_reports

        d = diff_reports(a, b)
        if d.get("error"):
            console.print(f"[red]{d['error']}[/red]")
            raise typer.Exit(1)
        console.print(f"similarity ratio={d['ratio']}")
        for line in d.get("udiff") or []:
            console.print(line)



    @app.command()
    def backup(dest: str = typer.Option("", "--dest", help="output directory")):
        """Zip backup of data/ (watchlist, theses, jobs, sessions)."""
        _boot_env()
        from pathlib import Path

        from src.ops.backup import create_backup

        out = create_backup(Path(dest) if dest else None)
        console.print(out)



    @app.command()
    def restore(zip_path: str = typer.Argument(..., help="backup zip path")):
        """Restore data/ from backup zip."""
        _boot_env()
        from src.ops.backup import restore_backup

        console.print(restore_backup(zip_path))



    @app.command("export-theses")
    def export_theses_cmd(path: str = typer.Option("", "--path")):
        """Export thesis registry to markdown."""
        _boot_env()
        from src.ops.thesis_export import export_theses_markdown

        p = export_theses_markdown(path or None)
        console.print(f"[green]{p}[/green]")



    @app.command("peer-review")
    def peer_review_cmd(
        text: str = typer.Option("", "--text", help="inline text"),
        file: str = typer.Option("", "--file", help="path to memo md"),
        mode: str = typer.Option("risk_only", "--mode"),
    ):
        """Second-pass devil's advocate on a memo or thesis text."""
        _boot_env()
        from pathlib import Path

        from src.ops.peer_review import peer_review_question

        body = text
        if file:
            body = Path(file).read_text(encoding="utf-8")
        if not body.strip():
            console.print("[red]provide --text or --file[/red]")
            raise typer.Exit(1)
        _run_research(question=peer_review_question(body), mode=mode, save=True)



    @app.command()
    def job(
        question: str = typer.Argument(..., help="research question"),
        mode: str = typer.Option("chokepoint_fast", "--mode", "-m"),
        wait: bool = typer.Option(False, "--wait", help="poll until done"),
    ):
        """Submit async research job."""
        _boot_env()
        import time

        from src.agents.research_agent import build_investment_agent, extract_final_text
        from src.config import get_settings
        from src.ops.jobs import get_job, submit_research_job
        from src.schemas.scorecard import validate_report_structure
        from src.tools.reports import save_report_file
        from src.tools.resilience import get_cost_tracker, reset_cost_tracker

        settings = get_settings()

        def run_fn(q: str, m: str) -> dict:
            reset_cost_tracker()
            agent = build_investment_agent(settings, mode=m)  # type: ignore[arg-type]
            result = agent.invoke({"messages": [{"role": "user", "content": q}]})
            report = extract_final_text(result)
            quality = validate_report_structure(report)
            saved = save_report_file(title=q[:40], markdown_body=report, mode=m, quality=quality)
            return {
                "report_preview": report[:2000],
                "quality": quality,
                "saved_path": saved,
                "cost": get_cost_tracker().summary(),
            }

        j = submit_research_job(question=question, mode=mode, run_fn=run_fn)
        console.print(j)
        if not wait:
            return
        while True:
            cur = get_job(j["id"])
            if not cur:
                break
            console.print(f"status={cur.get('status')}")
            if cur.get("status") in {"completed", "failed"}:
                console.print(cur)
                break
            time.sleep(2)


    # ── schedule (launchd / cron) ─────────────────────────────────────────────

    schedule_app = typer.Typer(help="Real scheduled tasks (launchd on macOS / cron elsewhere)")
    app.add_typer(schedule_app, name="schedule")


    @schedule_app.command("install")

    @app.command()
    def pdf(
        file: str = typer.Option("", "--file", help="markdown report path"),
        title: str = typer.Option("Research Memo", "--title"),
        text: str = typer.Option("", "--text", help="inline markdown"),
    ):
        """Generate a pretty PDF from markdown memo."""
        _boot_env()
        from pathlib import Path

        from src.tools.pdf_report import markdown_to_pdf

        body = text
        if file:
            body = Path(file).read_text(encoding="utf-8")
        if not body.strip():
            console.print("[red]provide --file or --text[/red]")
            raise typer.Exit(1)
        out = markdown_to_pdf(title, body)
        console.print(out)
        if out.get("error"):
            raise typer.Exit(1)



    @app.command("search-memos")
    def search_memos_cmd(
        query: str = typer.Argument(..., help="search query"),
        limit: int = typer.Option(10, "--limit", "-n"),
    ):
        """Local TF-IDF search over past memos in reports/."""
        _boot_env()
        from src.ops.memo_search import search_memos

        hits = search_memos(query, limit=limit)
        if not hits:
            console.print("[dim]No hits.[/dim]")
            return
        for h in hits:
            console.print(f"[cyan]{h['score']:.3f}[/cyan] {h['name']}\n  {h['preview'][:120]}…")



    @app.command()
    def chart(
        kind: str = typer.Argument("scorecard", help="scorecard|price"),
        report: str = typer.Option("", "--report", help="report filename for scorecard"),
        symbol: str = typer.Option("", "--symbol", help="ticker for price chart"),
        period: str = typer.Option("6mo", "--period"),
    ):
        """Render SVG charts into reports/charts/."""
        _boot_env()
        from pathlib import Path

        from src.charts.scorecard import charts_from_memo, fetch_price_points, price_line_chart_svg
        from src.config import get_settings
        from src.tools.reports import read_report

        out_dir = Path(get_settings().reports_dir) / "charts"
        out_dir.mkdir(parents=True, exist_ok=True)
        if kind == "scorecard":
            if not report:
                console.print("[red]--report required[/red]")
                raise typer.Exit(1)
            body = read_report(report)
            if not body:
                raise typer.Exit(1)
            svg = charts_from_memo(body)["scorecard_svg"]
            path = out_dir / f"scorecard_{Path(report).stem}.svg"
            path.write_text(svg, encoding="utf-8")
            console.print(f"[green]{path}[/green]")
        elif kind == "price":
            if not symbol:
                console.print("[red]--symbol required[/red]")
                raise typer.Exit(1)
            pts = fetch_price_points(symbol, period=period)
            svg = price_line_chart_svg(pts, title=f"{symbol} {period}")
            path = out_dir / f"price_{symbol.replace('.', '_')}.svg"
            path.write_text(svg, encoding="utf-8")
            console.print(f"[green]{path}[/green] points={len(pts)}")
        else:
            console.print("[red]kind must be scorecard|price[/red]")
            raise typer.Exit(2)



    @app.command()
    def skills():
        """List domain skill packs."""
        from src.skills.loader import list_skill_packs

        for s in list_skill_packs():
            console.print(f"[cyan]{s['id']}[/cyan]  {s['name']}\n  {s['description']}")



    @app.command("mock-eval")
    def mock_eval_cmd():
        """Run offline mock research pipeline (no LLM)."""
        from src.eval.mock_pipeline import run_mock_pipeline

        r = run_mock_pipeline()
        console.print(r)
        if not r.get("ok"):
            raise typer.Exit(1)



    @app.command()
    def metrics():
        """Show postprocess metrics.jsonl summary."""
        _boot_env()
        from src.pipeline.postprocess import metrics_summary

        console.print(metrics_summary())



    @app.command("clear-cache")
    def clear_cache_cmd():
        """Clear HTTP disk cache (SEC tickers etc.)."""
        _boot_env()
        from src.cache.http_cache import clear_http_cache

        n = clear_http_cache()
        console.print(f"cleared {n} cache files")



    @app.command("evidence")
    def evidence_cmd(
        report: Optional[str] = typer.Option(None, "--report", help="Extract from saved report name"),
        summary: bool = typer.Option(False, "--summary", help="Ledger summary only"),
    ):
        """Evidence ledger — extract URLs/claims or show summary."""
        _boot_env()
        from src.ops.evidence import evidence_summary, extract_and_store, list_evidence
        from src.tools.reports import read_report

        if summary or not report:
            console.print(evidence_summary() if summary else {"recent": list_evidence(limit=10)})
            if not report:
                return
        body = read_report(report)
        if not body:
            console.print(f"[red]not found: {report}[/red]")
            raise typer.Exit(1)
        row = extract_and_store(body, report_name=report)
        console.print(row)



    @app.command("graph")
    def graph_cmd(
        mermaid: bool = typer.Option(False, "--mermaid", help="Emit Mermaid flowchart"),
        links: bool = typer.Option(False, "--links", help="Include thesis↔report hard links"),
    ):
        """Thesis / chokepoint / symbol graph."""
        _boot_env()
        from src.ops.thesis_graph import build_thesis_graph, to_mermaid

        g = build_thesis_graph()
        if links:
            from src.ops.thesis_links import graph_edges

            g["report_links"] = graph_edges()
        if mermaid:
            console.print(to_mermaid(g))
        else:
            console.print(g)



    @app.command("compare-memos")
    def compare_memos_cmd(
        names: list[str] = typer.Argument(..., help="Two or more report filenames"),
    ):
        """Structured comparison of saved research memos."""
        _boot_env()
        from src.ops.compare_memos import compare_memos

        if len(names) < 2:
            console.print("[red]need at least 2 report names[/red]")
            raise typer.Exit(2)
        console.print(compare_memos(names))

    @app.command("compare-vertical")
    def compare_vertical_cmd(
        vertical_id: Optional[str] = typer.Argument(
            None, help="Deep vertical id (cpo_optics, …); omit if passing --a/--b"
        ),
        a: Optional[str] = typer.Option(None, "--a", help="Report filename A (older)"),
        b: Optional[str] = typer.Option(None, "--b", help="Report filename B (newer)"),
        no_udiff: bool = typer.Option(False, "--no-udiff", help="Skip unified diff lines"),
        list_only: bool = typer.Option(
            False, "--list", help="Only list memos for vertical_id"
        ),
    ):
        """Compare two memos in a vertical pack (or latest two)."""
        _boot_env()
        from src.ops.vertical_compare import compare_vertical, list_vertical_reports

        if list_only:
            if not vertical_id:
                console.print("[red]vertical_id required with --list[/red]")
                raise typer.Exit(2)
            rows = list_vertical_reports(vertical_id)
            for r in rows:
                console.print(
                    f"[cyan]{r.get('name')}[/cyan]  q={r.get('quality_score')}  "
                    f"{r.get('modified')}"
                )
            console.print(f"[dim]{len(rows)} reports · vertical={vertical_id}[/dim]")
            return
        out = compare_vertical(
            vertical_id,
            name_a=a,
            name_b=b,
            include_udiff=not no_udiff,
        )
        if out.get("error"):
            console.print(f"[red]{out['error']}[/red]")
            if out.get("hint"):
                console.print(f"[dim]{out['hint']}[/dim]")
            raise typer.Exit(1)
        console.print(
            f"[bold]similarity[/bold]={out.get('similarity_ratio')}  "
            f"same_vertical={out.get('same_vertical')}  "
            f"Δquality(B−A)={out.get('quality_delta_b_minus_a')}"
        )
        sc = out.get("scorecard") or {}
        console.print(f"shared nodes: {sc.get('shared_nodes')}")
        console.print(f"only A: {sc.get('only_in_a')}")
        console.print(f"only B: {sc.get('only_in_b')}")
        for act in out.get("next_actions") or []:
            console.print(f"[yellow]→[/yellow] {act}")
        if not no_udiff:
            for line in (out.get("udiff") or [])[:80]:
                console.print(line)
        console.print(f"[dim]{out.get('a', {}).get('name')}  vs  {out.get('b', {}).get('name')}[/dim]")



    @app.command("tag")
    def tag_cmd(
        report: str = typer.Argument(..., help="Report filename"),
        tags: str = typer.Option(..., "--tags", help="Comma-separated tags"),
    ):
        """Tag a report for collections / filtering."""
        _boot_env()
        from src.ops.tags import tag_report

        console.print(tag_report(report, [t.strip() for t in tags.split(",") if t.strip()]))



    @app.command("collections")
    def collections_cmd(
        create: Optional[str] = typer.Option(None, "--create", help="Create collection name"),
        add: Optional[str] = typer.Option(None, "--add", help="Add report to collection id"),
        collection: Optional[str] = typer.Option(None, "--collection", help="Collection id for --add"),
    ):
        """List or manage report collections."""
        _boot_env()
        from src.ops.tags import add_to_collection, create_collection, list_collections

        if create:
            console.print(create_collection(create))
            return
        if add:
            if not collection:
                console.print("[red]--collection required with --add[/red]")
                raise typer.Exit(2)
            row = add_to_collection(collection, add)
            if not row:
                console.print("[red]collection not found[/red]")
                raise typer.Exit(1)
            console.print(row)
            return
        console.print(list_collections())



    @app.command("kill-monitor")
    def kill_monitor_cmd():
        """Dashboard: active theses missing kill criteria / reviews."""
        _boot_env()
        from src.ops.kill_monitor import kill_criteria_dashboard

        console.print(kill_criteria_dashboard())



    @app.command("coverage")
    def coverage_cmd():
        """Coverage heat map (watchlist × theses × reports)."""
        _boot_env()
        from src.ops.coverage_heat import coverage_heatmap

        console.print(coverage_heatmap())



    @app.command("audit")
    def audit_cmd(
        limit: int = typer.Option(20, "--limit"),
        summary: bool = typer.Option(False, "--summary"),
    ):
        """Research audit trail."""
        _boot_env()
        from src.ops.audit import audit_summary, list_events

        console.print(audit_summary() if summary else list_events(limit=limit))



    @app.command("snapshot")
    def snapshot_cmd():
        """Zip workspace data + recent reports (never includes .env)."""
        _boot_env()
        from src.ops.snapshot import create_snapshot

        console.print(create_snapshot())



    @app.command("docx")
    def docx_cmd(
        report: str = typer.Argument(..., help="Saved report .md name"),
    ):
        """Export a saved memo to DOCX."""
        _boot_env()
        from src.tools.docx_report import markdown_to_docx
        from src.tools.reports import read_report

        body = read_report(report)
        if not body:
            console.print(f"[red]not found: {report}[/red]")
            raise typer.Exit(1)
        meta = markdown_to_docx(Path(report).stem, body)
        console.print(meta)



    @app.command("plugins")
    def plugins_cmd(
        load: Optional[str] = typer.Option(None, "--load", help="Load plugin by name"),
        install: Optional[str] = typer.Option(
            None, "--install", help="HTTPS manifest URL (hash-pinned; needs PLUGIN_ALLOW_HOSTS)"
        ),
        dry_run: bool = typer.Option(False, "--dry-run"),
    ):
        """List / load plugins under ./plugins/; optional remote install."""
        from src.plugins.loader import list_plugin_files, load_all_plugins, load_plugin

        if install:
            from src.plugins.remote_install import install_from_manifest

            out = install_from_manifest(install, dry_run=dry_run)
            console.print(out)
            if not out.get("ok"):
                raise typer.Exit(1)
            return
        if load:
            console.print(load_plugin(load))
            return
        console.print({"files": list_plugin_files(), "loaded": load_all_plugins()})



    @app.command("citations")
    def citations_cmd(
        mermaid: bool = typer.Option(False, "--mermaid"),
        limit: int = typer.Option(60, "--limit"),
    ):
        """Citation / domain co-occurrence network across memos."""
        _boot_env()
        from src.ops.citation_network import build_citation_network, citation_mermaid

        if mermaid:
            console.print(citation_mermaid(limit_reports=limit))
        else:
            console.print(build_citation_network(limit_reports=limit))



    @app.command("lineage")
    def lineage_cmd(
        parent: Optional[str] = typer.Option(None, "--parent"),
        child: Optional[str] = typer.Option(None, "--child"),
        chain: Optional[str] = typer.Option(None, "--chain", help="Create chain name"),
        reports: Optional[str] = typer.Option(None, "--reports", help="Comma report names for chain"),
        report: Optional[str] = typer.Option(None, "--report", help="Show lineage for one report"),
    ):
        """Report research lineage / chains."""
        _boot_env()
        from src.ops.lineage import create_chain, lineage_for, link_reports, list_lineage

        if parent and child:
            console.print(link_reports(parent, child))
            return
        if chain:
            reps = [r.strip() for r in (reports or "").split(",") if r.strip()]
            console.print(create_chain(chain, reps))
            return
        if report:
            console.print(lineage_for(report))
            return
        console.print(list_lineage())



    @app.command("plan")
    def plan_cmd(
        topic: str = typer.Argument(..., help="Research topic / system"),
        skill: Optional[str] = typer.Option(None, "--skill"),
        template: str = typer.Option("chokepoint_map", "--template"),
    ):
        """Offline research plan (no LLM)."""
        _boot_env()
        from src.ops.research_plan import build_research_plan

        console.print(build_research_plan(topic, skill=skill, template_id=template))



    @app.command("maps")
    def maps_cmd(
        map_id: Optional[str] = typer.Argument(None, help="Map id under knowledge/maps"),
        mermaid: bool = typer.Option(False, "--mermaid"),
        seed: bool = typer.Option(False, "--seed", help="Emit research seed question"),
    ):
        """Educational knowledge maps (YAML) → graph / seed question."""
        from src.ops.knowledge_maps import list_maps, map_research_seed, map_to_graph, map_to_mermaid

        if not map_id:
            console.print(list_maps())
            return
        if seed:
            console.print(map_research_seed(map_id))
            return
        if mermaid:
            console.print(map_to_mermaid(map_id))
            return
        console.print(map_to_graph(map_id))



    @app.command("dashboard")
    def dashboard_cmd():
        """Cost / quality / audit dashboard (local metrics)."""
        _boot_env()
        from src.ops.cost_dashboard import cost_quality_dashboard

        console.print(cost_quality_dashboard())



    @app.command("index-memos")
    def index_memos_cmd(
        rebuild: bool = typer.Option(True, "--rebuild/--no-rebuild"),
        q: Optional[str] = typer.Option(None, "--q", help="Search after index"),
    ):
        """Build/search local SQLite FTS index over memos."""
        _boot_env()
        from src.ops.memo_index import rebuild_index, search_index

        if rebuild or not q:
            console.print(rebuild_index())
        if q:
            console.print(search_index(q))



    @app.command("queue")
    def queue_cmd(
        add: Optional[str] = typer.Option(None, "--add", help="Enqueue a question"),
        mode: str = typer.Option("chokepoint_fast", "--mode"),
        skill: Optional[str] = typer.Option(None, "--skill"),
        from_watchlist: bool = typer.Option(False, "--from-watchlist"),
        from_map: Optional[str] = typer.Option(None, "--from-map"),
        summary: bool = typer.Option(False, "--summary"),
        limit: int = typer.Option(10, "--limit"),
        run: int = typer.Option(0, "--run", help="Process N items (uses mock unless --live)"),
        live: bool = typer.Option(False, "--live", help="With --run: call real LLM (costs tokens)"),
        i_accept_live_costs: bool = typer.Option(
            False,
            "--i-accept-live-costs",
            help="Required with --live (or set CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1)",
        ),
        estimate_live: bool = typer.Option(
            False, "--estimate-live", help="Show heuristic live cost banner and exit"
        ),
        cancel: Optional[str] = typer.Option(None, "--cancel", help="Cancel item id"),
        cancel_queued: bool = typer.Option(False, "--cancel-queued"),
    ):
        """Research queue — plan, then --run (mock) or --run --live (LLM)."""
        _boot_env()
        from src.ops.research_queue import (
            cancel_all_queued,
            cancel_item,
            enqueue,
            enqueue_from_map,
            enqueue_from_watchlist,
            list_queue,
            queue_summary,
        )

        if cancel:
            console.print(cancel_item(cancel) or {"error": "not found"})
            return
        if cancel_queued:
            console.print({"cancelled": cancel_all_queued()})
            return
        if estimate_live:
            from src.ops.live_safety import estimate_queue_live_cost

            console.print(estimate_queue_live_cost(n=max(run, 1)))
            return
        if run and run > 0:
            from src.ops.queue_worker import process_batch

            run_fn = None
            if live:
                from src.ops.live_safety import assert_live_allowed, estimate_queue_live_cost

                try:
                    gate = assert_live_allowed(flag=i_accept_live_costs)
                except ValueError as exc:
                    console.print(f"[red]{exc}[/red]")
                    console.print(estimate_queue_live_cost(n=run))
                    raise typer.Exit(2) from exc
                console.print(f"[yellow]Live LLM accepted. estimate={gate.get('estimate')}[/yellow]")

                from src.agents.research_agent import build_investment_agent, extract_final_text
                from src.config import get_settings

                settings = get_settings()
                cache: dict = {}

                def run_fn(question: str, mode_s: str, skill_s: str | None = None) -> dict:
                    key = f"{mode_s}:{skill_s or ''}"
                    if key not in cache:
                        cache[key] = build_investment_agent(
                            settings, mode=mode_s, skill=skill_s
                        )  # type: ignore[arg-type]
                    agent = cache[key]
                    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
                    return {"report": extract_final_text(result)}

            console.print(process_batch(n=run, run_fn=run_fn, dry_run=not live))
            return
        if add:
            console.print(enqueue(add, mode=mode, skill=skill))
            return
        if from_watchlist:
            console.print(enqueue_from_watchlist(limit=limit))
            return
        if from_map:
            console.print(enqueue_from_map(from_map))
            return
        if summary:
            console.print(queue_summary())
            return
        console.print(list_queue())



    @app.command("export-pack")
    def export_pack_cmd(report: str = typer.Argument(..., help="Report .md filename")):
        """Zip memo + evidence + tags + lineage into a portable pack."""
        _boot_env()
        from src.ops.export_pack import build_export_pack

        out = build_export_pack(report)
        if out.get("error"):
            console.print(f"[red]{out['error']}[/red]")
            raise typer.Exit(1)
        console.print(out)



    @app.command("auto-tag")
    def auto_tag_cmd(report: str = typer.Argument(..., help="Report filename")):
        """Heuristic tags from memo content."""
        _boot_env()
        from src.ops.auto_tag import auto_tag_report

        console.print(auto_tag_report(report))



    @app.command("thesis-health")
    def thesis_health_cmd():
        """Process-quality scores for thesis registry (not investment merit)."""
        _boot_env()
        from src.ops.thesis_health import thesis_health_report

        console.print(thesis_health_report())



    @app.command("config-show")
    def config_show_cmd():
        """Sanitized config (secrets → set/missing only)."""
        _boot_env()
        from src.ops.config_export import sanitized_config

        console.print(sanitized_config())



    @app.command("notion-export")
    def notion_export_cmd(report: str = typer.Argument(...)):
        """Notion-friendly blocks/plain text for a saved memo."""
        _boot_env()
        from src.ops.notion_export import export_report_for_notion

        out = export_report_for_notion(report)
        if out.get("error"):
            console.print(f"[red]{out['error']}[/red]")
            raise typer.Exit(1)
        console.print(out)



    @app.command("plugin-catalog")
    def plugin_catalog_cmd():
        """Local plugin / provider / skill catalog."""
        from src.ops.plugin_catalog import plugin_catalog

        console.print(plugin_catalog())



    @app.command("marketplace")
    def marketplace_cmd(
        q: Optional[str] = typer.Option(None, "--q", help="Search listings"),
    ):
        """Local extension marketplace index (plugins/skills/templates/maps)."""
        from src.ops.marketplace import marketplace_index, marketplace_search

        console.print(marketplace_search(q) if q else marketplace_index())



    @app.command("workspace-health")
    def workspace_health_cmd():
        """Composite research-ops health score (process hygiene, not alpha)."""
        _boot_env()
        from src.ops.workspace_health import workspace_health_score

        console.print(workspace_health_score())



    @app.command("runbook")
    def runbook_cmd(
        system: str = typer.Option("", "--system", help="System boundary text"),
        md: bool = typer.Option(False, "--md", help="Print markdown SOP"),
    ):
        """Professional Chokepoint research runbook / SOP (offline)."""
        _boot_env()
        from src.ops.runbook import professional_runbook, runbook_markdown

        if md:
            console.print(runbook_markdown(system=system))
        else:
            console.print(professional_runbook(system=system))



    @app.command("batch-review")
    def batch_review_cmd(limit: int = typer.Option(20, "--limit")):
        """Batch structure checklist over recent memos (no LLM)."""
        _boot_env()
        from src.ops.batch_review import batch_structure_review

        console.print(batch_structure_review(limit=limit))



    @app.command("weekly-ops")
    def weekly_ops_cmd(
        save: bool = typer.Option(True, "--save/--no-save"),
        enqueue: int = typer.Option(0, "--enqueue", help="Also enqueue N watchlist items"),
    ):
        """Weekly ops pack: digest + health + batch review (+ optional queue)."""
        _boot_env()
        from src.ops.weekly_ops import run_weekly_ops

        out = run_weekly_ops(save=save, enqueue_watchlist=enqueue)
        console.print(out.get("markdown") if not save else out)
        if out.get("saved_path"):
            console.print(f"[green]Saved: {out['saved_path']}[/green]")



    @app.command("quotes-cache")
    def quotes_cache_cmd(
        symbols: Optional[str] = typer.Option(None, "--symbols", help="Comma symbols to refresh"),
        history: Optional[str] = typer.Option(None, "--history", help="Symbol for history"),
        summary: bool = typer.Option(False, "--summary"),
        from_watchlist: bool = typer.Option(False, "--from-watchlist"),
    ):
        """Local multi-symbol quote snapshot cache (research utility)."""
        _boot_env()
        from src.ops.quote_cache import history_summary, load_history, refresh_symbols

        if from_watchlist:
            from src.ops.coverage_refresh import refresh_watchlist_quotes

            console.print(refresh_watchlist_quotes())
            return
        if symbols:
            syms = [s.strip() for s in symbols.split(",") if s.strip()]
            console.print(refresh_symbols(syms))
            return
        if history:
            console.print(load_history(history, limit=50))
            return
        console.print(history_summary())



    @app.command("grade-memo")
    def grade_memo_cmd(report: str = typer.Argument(...)):
        """Professional structure/evidence grade for one memo (not investment merit)."""
        _boot_env()
        from src.ops.memo_grade import grade_memo

        out = grade_memo(report)
        if out.get("error"):
            console.print(f"[red]{out['error']}[/red]")
            raise typer.Exit(1)
        console.print(out)



    @app.command("memo-pro")
    def memo_pro_cmd(
        report: str = typer.Argument(..., help="Saved memo filename"),
        persist: bool = typer.Option(False, "--persist", help="Write notes into modules that pass gate"),
        symbol: str = typer.Option("", "--symbol"),
        modules: str = typer.Option("", "--modules", help="Comma subset; empty=full suite"),
    ):
        """Analyze a saved memo through pro modules / suite."""
        _boot_env()
        from src.ops.memo_pro_bridge import analyze_memo_with_pro

        mods = [m.strip() for m in modules.split(",") if m.strip()] or None
        out = analyze_memo_with_pro(report, modules=mods, persist=persist, symbol=symbol)
        if out.get("error"):
            console.print(f"[red]{out['error']}[/red]")
            raise typer.Exit(1)
        console.print(out)



    @app.command("desk")
    def desk_cmd(md: bool = typer.Option(False, "--md")):
        """Unified research desk status (health + pro + queue + catalog)."""
        _boot_env()
        from src.ops.research_desk import research_desk_markdown, research_desk_status

        console.print(research_desk_markdown() if md else research_desk_status())



    @app.command("glossary")
    def glossary_cmd(
        q: Optional[str] = typer.Argument(None, help="Search query or exact term"),
        get: Optional[str] = typer.Option(None, "--get", help="Fetch exact term markdown"),
    ):
        """Search educational glossary under knowledge/glossary/."""
        from src.ops.glossary_search import get_term, list_glossary_terms, search_glossary

        if get:
            console.print(get_term(get))
            return
        if not q:
            terms = list_glossary_terms()
            console.print({"count": len(terms), "sample": terms[:30]})
            return
        # if exact term file exists, prefer get
        exact = get_term(q)
        if not exact.get("error") and q.replace(" ", "_") == exact.get("term"):
            console.print(exact)
            return
        console.print(search_glossary(q))



    @app.command("quote-chart")
    def quote_chart_cmd(
        symbol: str = typer.Argument(...),
        out: Optional[str] = typer.Option(None, "--out", help="Write SVG path"),
    ):
        """SVG from local quote_cache history (research utility)."""
        _boot_env()
        from pathlib import Path

        from src.charts.quote_history import quote_history_svg
        from src.config import get_settings

        svg = quote_history_svg(symbol)
        if out:
            path = Path(out)
        else:
            d = Path(get_settings().reports_dir) / "charts"
            d.mkdir(parents=True, exist_ok=True)
            path = d / f"quote_hist_{symbol.replace('.', '_')}.svg"
        path.write_text(svg, encoding="utf-8")
        console.print(f"[green]{path}[/green]")



    @app.command("multi-quotes")
    def multi_quotes_cmd(
        symbols: str = typer.Argument(..., help="Comma-separated symbols"),
    ):
        """Batch refresh + table of quote snapshots (research utility)."""
        _boot_env()
        from src.ops.multi_quotes import multi_quote_snapshot

        console.print(multi_quote_snapshot(symbols))



    @app.command("playbook")
    def playbook_cmd(
        name: Optional[str] = typer.Argument(None, help="Playbook id; omit to list"),
    ):
        """Research process playbooks (IPO, cyclical, SaaS, hardware, …)."""
        from src.playbooks.registry import get_playbook, list_playbooks

        if not name:
            for p in list_playbooks():
                console.print(f"[cyan]{p}[/cyan]")
            return
        try:
            console.print(get_playbook(name))
        except ModuleNotFoundError:
            console.print(f"[red]unknown playbook: {name}[/red]")
            raise typer.Exit(1)



    @app.command("metrics-run")
    def metrics_run_cmd(
        text: str = typer.Option(..., "--text", help="Text to score with metric battery"),
    ):
        """Run offline text metric battery (80 heuristics)."""
        from src.analysis.text_metrics import run_all_metrics

        console.print(run_all_metrics(text))





    @app.command("questionnaire")
    def questionnaire_cmd(name: Optional[str] = typer.Argument(None)):
        """List/run structured research questionnaires."""
        from src.questionnaires.registry import get_questionnaire, list_questionnaires
        if not name:
            for q in list_questionnaires():
                console.print(f"[cyan]{q}[/cyan]")
            return
        try:
            console.print(get_questionnaire(name))
        except ModuleNotFoundError:
            raise typer.Exit(1)



    @app.command("rubric")
    def rubric_cmd(
        name: Optional[str] = typer.Argument(None),
        text: str = typer.Option("", "--text"),
        all_rubrics: bool = typer.Option(False, "--all"),
    ):
        """Process quality rubrics (not investment scores)."""
        from src.rubrics.registry import list_rubrics, score_all
        import importlib
        if all_rubrics or (not name and text):
            console.print(score_all(text or "system kill criteria https://x.com"))
            return
        if not name:
            for r in list_rubrics():
                console.print(f"[cyan]{r}[/cyan]")
            return
        mod = importlib.import_module(f"src.rubrics.{name}")
        console.print(mod.score(text))



    @app.command("quality-board")
    def quality_board_cmd(limit: int = typer.Option(30, "--limit")):
        """Structure-quality leaderboard for recent memos."""
        _boot_env()
        from src.ops.quality_board import quality_leaderboard

        console.print(quality_leaderboard(limit=limit))



    @app.command("digest")
    def digest_cmd(
        save: bool = typer.Option(True, "--save/--no-save"),
    ):
        """Offline workspace digest (no LLM)."""
        _boot_env()
        from src.ops.digest import build_workspace_digest

        out = build_workspace_digest(save=save)
        console.print(out.get("markdown"))
        if out.get("saved_path"):
            console.print(f"[green]Saved: {out['saved_path']}[/green]")



    @app.command("compare-maps")
    def compare_maps_cmd(
        a: str = typer.Argument(..., help="Map id A"),
        b: str = typer.Argument(..., help="Map id B"),
    ):
        """Compare two knowledge maps (label overlap)."""
        from src.ops.map_compare import compare_maps

        out = compare_maps(a, b)
        if out.get("error"):
            console.print(f"[red]{out['error']}[/red]")
            raise typer.Exit(1)
        console.print(out)



    @app.command("hypothesis")
    def hypothesis_cmd(
        add: Optional[str] = typer.Option(None, "--add", help="Hypothesis statement"),
        system: str = typer.Option("", "--system"),
        list_all: bool = typer.Option(False, "--list"),
        promote: Optional[str] = typer.Option(None, "--promote", help="Hypothesis id → thesis"),
        status: Optional[str] = typer.Option(None, "--status", help="Filter list by status"),
    ):
        """Research hypotheses scratchpad (pre-thesis)."""
        _boot_env()
        from src.ops.hypotheses import (
            add_hypothesis,
            list_hypotheses,
            promote_to_thesis,
        )

        if add:
            console.print(add_hypothesis(add, system=system))
            return
        if promote:
            console.print(promote_to_thesis(promote))
            return
        console.print(list_hypotheses(status=status) if list_all or status or True else [])



    @app.command("enrich-report")
    def enrich_report_cmd(report: str = typer.Argument(...)):
        """Rewrite frontmatter with quality + auto tags."""
        _boot_env()
        from src.ops.report_frontmatter import enrich_report_frontmatter

        out = enrich_report_frontmatter(report)
        if out.get("error"):
            console.print(f"[red]{out['error']}[/red]")
            raise typer.Exit(1)
        console.print(out)



    @app.command("checklist")
    def checklist_cmd(report: str = typer.Argument(..., help="Saved report name")):
        """Publish gate checklist for a memo (structure, not factuality)."""
        _boot_env()
        from src.ops.checklist import run_checklist

        out = run_checklist(report_name=report)
        if out.get("error"):
            console.print(f"[red]{out['error']}[/red]")
            raise typer.Exit(1)
        console.print(out)
        if not out.get("gate_ok"):
            raise typer.Exit(2)



    @app.command("eval-record")
    def eval_record_cmd():
        """Run golden eval and append to eval history."""
        _boot_env()
        from src.ops.eval_history import record_eval_run

        console.print(record_eval_run())



    @app.command("eval-trend")
    def eval_trend_cmd():
        """Show offline eval pass-rate history."""
        _boot_env()
        from src.ops.eval_history import eval_trend

        console.print(eval_trend())



    @app.command("version")
    def show_version():
        from src import __version__
        from src.prompts.version import PROMPT_PACK_VERSION

        console.print(f"chokepoint-research-agent {__version__} (prompts {PROMPT_PACK_VERSION})")



    @app.command("about")
    def about_cmd():
        """Professional capability snapshot (offline)."""
        from src import __version__
        from src.ops.pro import PRO_MODULE_IDS
        from src.playbooks.registry import list_playbooks
        from src.questionnaires.registry import list_questionnaires
        from src.rubrics.registry import list_rubrics
        from src.ops.glossary_search import list_glossary_terms
        from src.ops.knowledge_maps import list_maps
        from src.skills.loader import list_skill_packs
        from src.ops.marketplace import marketplace_index

        mkt = marketplace_index()
        console.print(
            {
                "name": "Chokepoint Research Agent",
                "version": __version__,
                "positioning": "Professional research workstation — not a trading bot",
                "disclaimer": "research_only_not_investment_advice",
                "counts": {
                    "pro_modules": len(PRO_MODULE_IDS),
                    "playbooks": len(list_playbooks()),
                    "questionnaires": len(list_questionnaires()),
                    "rubrics": len(list_rubrics()),
                    "glossary_terms": len(list_glossary_terms()),
                    "knowledge_maps": len(list_maps()),
                    "skill_packs": len(list_skill_packs()),
                    "marketplace_listings": (mkt.get("counts") or {}).get("listings"),
                },
                "docs": {
                    "readme": "README.md / README.zh-CN.md",
                    "workstation": "docs/PROFESSIONAL_WORKSTATION.md",
                    "pro_train": "docs/VERSIONS_5.2_to_5.51.md",
                },
                "entrypoints": [
                    "python main.py doctor",
                    "python main.py desk --md",
                    "python main.py research \"…\" --mode chokepoint_fast",
                    "python main.py --server",
                ],
            }
        )



    @app.callback(invoke_without_command=True)
    def default(
        ctx: typer.Context,
        server_mode: bool = typer.Option(False, "--server", help="start API/UI server"),
        host: str = typer.Option("0.0.0.0", "--host"),
        port: int = typer.Option(8000, "--port"),
    ):
        """Root callback. Prefer subcommands: research / doctor / watch / thesis / server."""
        if ctx.invoked_subcommand is not None:
            return
        if server_mode:
            server(host=host, port=port)
            return
        console.print(ctx.get_help())
        console.print(
            "\n[dim]Tip: python main.py research \"your question\"\n"
            "     python main.py doctor\n"
            "     python main.py --server[/dim]"
        )


