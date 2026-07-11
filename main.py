#!/usr/bin/env python3
"""CLI entrypoint for Chokepoint Research Agent (research workstation)."""

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

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

app = typer.Typer(
    add_completion=False,
    help=(
        "Chokepoint Research Agent — professional research workstation "
        "(Chokepoint Theory). Not investment advice."
    ),
)
watch_app = typer.Typer(help="Coverage book / watchlist")
thesis_app = typer.Typer(help="Thesis registry")
app.add_typer(watch_app, name="watch")
app.add_typer(thesis_app, name="thesis")

console = Console()
VALID_MODES = {"full", "chokepoint_fast", "risk_only", "compare"}


def _boot_env():
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    from src.config import clear_settings_cache

    clear_settings_cache()


# ── research ──────────────────────────────────────────────────────────────


@app.command()
def research(
    question: Optional[str] = typer.Argument(None, help="研究问题"),
    stream: bool = typer.Option(False, "--stream", "-s"),
    save: bool = typer.Option(True, "--save/--no-save"),
    mode: str = typer.Option("full", "--mode", "-m"),
    session: Optional[str] = typer.Option(None, "--session"),
    bilingual: bool = typer.Option(False, "--bilingual"),
    export_all: bool = typer.Option(False, "--export"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="template id"),
    var: Optional[list[str]] = typer.Option(
        None, "--var", help="template var key=value (repeatable)"
    ),
):
    """Run multi-agent research (or render --template first)."""
    vars_list = list(var) if var else []
    _run_research(
        question=question,
        stream=stream,
        save=save,
        mode=mode,
        session=session,
        bilingual=bilingual,
        export_all=export_all,
        template=template,
        var=vars_list,
    )


def _run_research(
    *,
    question: Optional[str],
    stream: bool = False,
    save: bool = True,
    mode: str = "full",
    session: Optional[str] = None,
    bilingual: bool = False,
    export_all: bool = False,
    template: Optional[str] = None,
    var: Optional[list[str]] = None,
) -> None:
    _boot_env()
    from src.config import get_settings
    from src.logging_utils import setup_logging
    from src.tools.resilience import reset_cost_tracker

    settings = get_settings()
    if bilingual:
        object.__setattr__(settings, "bilingual_memo", True)
    setup_logging(settings.log_level)
    reset_cost_tracker()

    if template:
        from src.ops.templates import render_template

        variables: dict[str, str] = {}
        for item in var or []:
            if "=" in item:
                k, v = item.split("=", 1)
                variables[k.strip()] = v.strip()
        rendered = render_template(template, variables)
        question = rendered["question"]
        mode = rendered.get("mode") or mode
        if rendered.get("bilingual"):
            object.__setattr__(settings, "bilingual_memo", True)
        console.print(f"[cyan]template={template} mode={mode}[/cyan]")

    if not question:
        question = typer.prompt("请输入研究问题")

    if mode not in VALID_MODES:
        console.print(f"[red]Unknown mode: {mode}[/red]")
        raise typer.Exit(2)

    problems = settings.validate_runtime(require_tavily=True)
    if problems:
        for p in problems:
            console.print(f"[yellow]! {p}[/yellow]")
        if any("API_KEY" in p and "TAVILY" not in p for p in problems):
            raise typer.Exit(1)

    question_for_agent = question
    if session:
        from src.memory.sessions import session_context_block

        ctx = session_context_block(session)
        if ctx:
            question_for_agent = f"{question}\n\n{ctx}"

    console.print(
        Panel.fit(
            f"[bold cyan]Chokepoint Research Agent[/bold cyan]\n"
            f"Q: {question[:200]}\nmode={mode}\n"
            f"[dim]Research only — not investment advice[/dim]",
            border_style="cyan",
        )
    )

    from src.agents.research_agent import build_investment_agent, extract_final_text
    from src.schemas.scorecard import extract_scorecard_table, validate_report_structure

    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    agent = build_investment_agent(settings, mode=mode)  # type: ignore[arg-type]
    payload = {"messages": [{"role": "user", "content": question_for_agent}]}

    if stream:
        final_text = _stream_agent(agent, payload)
    else:
        with console.status("[bold green]Researching…"):
            result = agent.invoke(payload)
        final_text = extract_final_text(result)

    quality = validate_report_structure(final_text)
    card = extract_scorecard_table(final_text)
    console.print(Panel(Markdown(final_text), title="Research memo", border_style="green"))
    console.print(
        f"[dim]quality={quality['score']} nodes={len(card.nodes)} urls={quality['url_count']}[/dim]"
    )

    from src.tools.resilience import get_cost_tracker

    cost = get_cost_tracker().summary()
    console.print(f"[dim]cost_est={cost}[/dim]")

    if save and final_text:
        from src.tools.reports import save_report_file

        path = save_report_file(
            title=question[:40], markdown_body=final_text, mode=mode, quality=quality
        )
        console.print(f"[green]Saved: {path}[/green]")
        if export_all or settings.export_html_json:
            from src.tools.export import export_report_bundle

            paths = export_report_bundle(
                title=question[:40], markdown_body=final_text, mode=mode, extra={"cost": cost}
            )
            console.print(f"[green]Export: {paths}[/green]")

    if session and final_text:
        from src.memory.sessions import append_turn

        append_turn(
            session, question=question, report=final_text, mode=mode, meta={"quality": quality}
        )


def _stream_agent(agent, payload: dict) -> str:
    final_chunks: list[str] = []
    try:
        for event in agent.stream(payload, stream_mode="updates"):
            if not isinstance(event, dict):
                continue
            for node, update in event.items():
                if not isinstance(update, dict):
                    continue
                for msg in update.get("messages") or []:
                    content = getattr(msg, "content", None)
                    if isinstance(content, str) and content.strip():
                        console.print(f"[blue]{node}[/blue]: {content[:300]}…\n")
                        final_chunks.append(content)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[yellow]stream failed: {exc}[/yellow]")
        from src.agents.research_agent import extract_final_text

        return extract_final_text(agent.invoke(payload))
    return final_chunks[-1] if final_chunks else "(empty)"


# ── doctor / catalog / templates / brief ───────────────────────────────────


@app.command()
def doctor():
    """Health-check environment, deps, and config."""
    _boot_env()
    from src.ops.doctor import run_doctor

    result = run_doctor()
    table = Table(title="Doctor")
    table.add_column("Check")
    table.add_column("OK")
    table.add_column("Detail")
    for c in result["checks"]:
        mark = "[green]yes[/green]" if c["ok"] else f"[red]{c['level']}[/red]"
        table.add_row(c["name"], mark, str(c["detail"])[:80])
    console.print(table)
    console.print(
        f"ok={result['ok']} errors={result['errors']} warnings={result['warnings']}"
    )
    if not result["ok"]:
        raise typer.Exit(1)


@app.command("list-reports")
def list_reports_cmd(limit: int = typer.Option(20, "-n"), q: str = typer.Option("", "--q")):
    """List / search report catalog."""
    _boot_env()
    from src.ops.catalog import search_catalog

    items = search_catalog(q, limit=limit)
    if not items:
        console.print("[dim]No reports.[/dim]")
        return
    table = Table(title="Report catalog")
    table.add_column("Name")
    table.add_column("Mode")
    table.add_column("Q")
    table.add_column("Modified")
    for it in items:
        table.add_row(it["name"][:40], it.get("mode") or "-", str(it.get("quality_score") or "-"), it["modified"])
    console.print(table)


@app.command("templates")
def templates_cmd():
    """List research templates."""
    from src.ops.templates import list_templates

    for t in list_templates():
        console.print(f"[cyan]{t['id']}[/cyan]  {t['name']}  mode={t['mode']}\n  {t['description']}")


@app.command()
def brief(
    limit: int = typer.Option(3, "--limit", "-n", help="max watchlist items"),
    dry_run: bool = typer.Option(False, "--dry-run", help="only print questions"),
):
    """Batch chokepoint_fast brief over watchlist (expensive if not dry-run)."""
    _boot_env()
    from src.ops.brief import build_brief_questions, run_brief

    jobs = build_brief_questions(limit=limit)
    if not jobs:
        console.print("[yellow]Watchlist empty. Add with: python main.py watch add SYMBOL[/yellow]")
        raise typer.Exit(1)
    for j in jobs:
        console.print(f"- {j['item'].get('symbol')}: {j['question'][:100]}…")
    if dry_run:
        return

    from src.agents.research_agent import build_investment_agent, extract_final_text
    from src.config import get_settings

    settings = get_settings()
    cache: dict = {}

    def invoke_fn(question: str, mode: str) -> str:
        if mode not in cache:
            cache[mode] = build_investment_agent(settings, mode=mode)  # type: ignore[arg-type]
        agent = cache[mode]
        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        return extract_final_text(result)

    with console.status("[bold green]Running watchlist brief…"):
        out = run_brief(invoke_fn=invoke_fn, limit=limit, save=True)
    console.print(f"[green]Brief saved: {out.get('saved_path')}[/green]")
    console.print(out.get("results"))


# ── watchlist ─────────────────────────────────────────────────────────────


@watch_app.command("list")
def watch_list():
    _boot_env()
    from src.ops.watchlist import list_items

    items = list_items()
    if not items:
        console.print("[dim]Empty watchlist.[/dim]")
        return
    table = Table(title="Watchlist / Coverage book")
    table.add_column("ID")
    table.add_column("Symbol")
    table.add_column("Name")
    table.add_column("Pri")
    table.add_column("Thesis")
    for it in items:
        table.add_row(
            it["id"],
            it.get("symbol") or "",
            (it.get("name") or "")[:16],
            it.get("priority") or "",
            (it.get("thesis") or "")[:40],
        )
    console.print(table)


@watch_app.command("add")
def watch_add(
    symbol: str = typer.Argument(...),
    name: str = typer.Option("", "--name"),
    thesis: str = typer.Option("", "--thesis"),
    priority: str = typer.Option("medium", "--priority"),
    tags: str = typer.Option("", "--tags", help="comma-separated"),
):
    _boot_env()
    from src.ops.watchlist import add_item

    item = add_item(
        symbol=symbol,
        name=name,
        thesis=thesis,
        priority=priority,
        tags=[t.strip() for t in tags.split(",") if t.strip()],
    )
    console.print(item)


@watch_app.command("rm")
def watch_rm(item_id: str = typer.Argument(...)):
    _boot_env()
    from src.ops.watchlist import remove_item

    ok = remove_item(item_id)
    console.print("removed" if ok else "not found")
    if not ok:
        raise typer.Exit(1)


@watch_app.command("research")
def watch_research(
    item_id: str = typer.Argument(...),
    mode: str = typer.Option("chokepoint_fast", "--mode", "-m"),
):
    """Research one watchlist item."""
    _boot_env()
    from src.ops.watchlist import get_item, research_question_for

    item = get_item(item_id)
    if not item:
        raise typer.Exit(1)
    _run_research(question=research_question_for(item), mode=mode, save=True)


# ── thesis ────────────────────────────────────────────────────────────────


@thesis_app.command("list")
def thesis_list(status: str = typer.Option("", "--status")):
    _boot_env()
    from src.ops.theses import list_theses

    items = list_theses(status=status or None)
    for t in items:
        console.print(
            f"[cyan]{t['id']}[/cyan] [{t['status']}] {t['title']}\n  {t['statement'][:120]}"
        )


@thesis_app.command("add")
def thesis_add(
    title: str = typer.Option(..., "--title"),
    statement: str = typer.Option(..., "--statement"),
    system: str = typer.Option("", "--system"),
    kills: str = typer.Option("", "--kills", help="semicolon-separated kill criteria"),
    symbols: str = typer.Option("", "--symbols", help="comma-separated"),
):
    _boot_env()
    from src.ops.theses import add_thesis

    item = add_thesis(
        title=title,
        statement=statement,
        system=system,
        kill_criteria=[k.strip() for k in kills.split(";") if k.strip()],
        related_symbols=[s.strip() for s in symbols.split(",") if s.strip()],
    )
    console.print(item)


@thesis_app.command("status")
def thesis_status(
    thesis_id: str = typer.Argument(...),
    status: str = typer.Argument(..., help="active|watching|invalidated|archived"),
    note: str = typer.Option("", "--note"),
):
    _boot_env()
    from src.ops.theses import set_status

    item = set_status(thesis_id, status, note=note)  # type: ignore[arg-type]
    if not item:
        raise typer.Exit(1)
    console.print(item)


@thesis_app.command("redteam")
def thesis_redteam(thesis_id: str = typer.Argument(...)):
    _boot_env()
    from src.ops.theses import get_thesis, research_question_for

    t = get_thesis(thesis_id)
    if not t:
        raise typer.Exit(1)
    _run_research(
        question=research_question_for(t, mode="risk_only"), mode="risk_only", save=True
    )


# ── misc ──────────────────────────────────────────────────────────────────


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
def analytics():
    """Print workspace analytics (reports / watchlist / theses)."""
    _boot_env()
    from src.ops.analytics import workspace_analytics

    console.print_json(json.dumps(workspace_analytics(), ensure_ascii=False))


@app.command("providers")
def providers_cmd():
    """List registered data providers."""
    from src.providers.base import get_registry

    console.print(get_registry().list_providers())


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


@app.command("version")
def show_version():
    from src import __version__

    console.print(f"chokepoint-research-agent {__version__}")


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


if __name__ == "__main__":
    app()
