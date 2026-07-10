#!/usr/bin/env python3
"""CLI entrypoint for Chokepoint Research Agent."""

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
        "Chokepoint Research Agent — multi-specialist investment research "
        "(Bottom-up supply-chain / 卡脖子框架). Not investment advice."
    ),
)
console = Console()

VALID_MODES = {"full", "chokepoint_fast", "risk_only", "compare"}


@app.command()
def research(
    question: Optional[str] = typer.Argument(None, help="研究问题"),
    stream: bool = typer.Option(False, "--stream", "-s", help="流式打印中间过程"),
    save: bool = typer.Option(True, "--save/--no-save", help="是否落盘最终答案"),
    mode: str = typer.Option(
        "full",
        "--mode",
        "-m",
        help="full | chokepoint_fast | risk_only | compare",
    ),
    session: Optional[str] = typer.Option(None, "--session", help="session id for memory"),
    bilingual: bool = typer.Option(False, "--bilingual", help="append English one-pager"),
    export_all: bool = typer.Option(False, "--export", help="also write JSON+HTML"),
):
    """对一个投研问题跑完整研究流程。"""
    if not question:
        question = typer.prompt("请输入研究问题")

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    from src.config import clear_settings_cache, get_settings
    from src.logging_utils import setup_logging
    from src.tools.resilience import reset_cost_tracker

    clear_settings_cache()
    settings = get_settings()
    if bilingual:
        # mutate cached settings instance
        object.__setattr__(settings, "bilingual_memo", True)
    setup_logging(settings.log_level)
    reset_cost_tracker()

    if mode not in VALID_MODES:
        console.print(f"[red]Unknown mode: {mode}[/red]")
        raise typer.Exit(2)

    problems = settings.validate_runtime(require_tavily=True)
    if problems:
        for p in problems:
            console.print(f"[yellow]! {p}[/yellow]")
        if any("API_KEY" in p and "TAVILY" not in p for p in problems):
            console.print("[red]模型 Key 缺失，无法继续。[/red]")
            raise typer.Exit(1)

    session_id = session
    context = ""
    if session_id:
        from src.memory.sessions import session_context_block

        context = session_context_block(session_id)
        if context:
            question_for_agent = f"{question}\n\n{context}"
        else:
            question_for_agent = question
    else:
        question_for_agent = question

    console.print(
        Panel.fit(
            f"[bold cyan]Chokepoint Research Agent[/bold cyan]\n"
            f"问题：{question}\n"
            f"模式：{mode}"
            + (f"\nsession：{session_id}" if session_id else "")
            + "\n[dim]研究学习用途 · 不构成投资建议[/dim]",
            border_style="cyan",
        )
    )

    from src.agents.research_agent import build_investment_agent, extract_final_text
    from src.schemas.scorecard import extract_scorecard_table, validate_report_structure

    settings.reports_dir.mkdir(parents=True, exist_ok=True)

    try:
        agent = build_investment_agent(settings, mode=mode)  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Agent 初始化失败：{exc}[/red]")
        raise typer.Exit(1) from exc

    payload = {"messages": [{"role": "user", "content": question_for_agent}]}

    if stream:
        console.print("[dim]Streaming events…[/dim]\n")
        final_text = _stream_agent(agent, payload)
    else:
        with console.status("[bold green]多专家研究中（可能需要 1–10 分钟）…"):
            result = agent.invoke(payload)
        final_text = extract_final_text(result)

    quality = validate_report_structure(final_text)
    card = extract_scorecard_table(final_text)

    console.print("\n")
    console.print(Panel(Markdown(final_text), title="投研简报", border_style="green"))
    console.print(
        f"[dim]quality_score={quality['score']} pass={quality['pass']} "
        f"scorecard_nodes={len(card.nodes)} urls={quality['url_count']}[/dim]"
    )

    from src.tools.resilience import get_cost_tracker

    cost = get_cost_tracker().summary()
    console.print(f"[dim]cost_est={cost}[/dim]")

    if save and final_text:
        from src.tools.reports import save_report_file

        path = save_report_file(
            title=question[:40],
            markdown_body=final_text,
            mode=mode,
            quality=quality,
        )
        console.print(f"[green]Report saved: {path}[/green]")
        if export_all or settings.export_html_json:
            from src.tools.export import export_report_bundle

            paths = export_report_bundle(
                title=question[:40],
                markdown_body=final_text,
                mode=mode,
                extra={"cost": cost},
            )
            console.print(f"[green]Export: {paths}[/green]")

    if session_id and final_text:
        from src.memory.sessions import append_turn

        append_turn(
            session_id,
            question=question,
            report=final_text,
            mode=mode,
            meta={"quality": quality, "cost": cost},
        )
        console.print(f"[cyan]Session updated: {session_id}[/cyan]")


def _stream_agent(agent, payload: dict) -> str:
    final_chunks: list[str] = []
    try:
        for event in agent.stream(payload, stream_mode="updates"):
            if not isinstance(event, dict):
                continue
            for node, update in event.items():
                if not isinstance(update, dict):
                    continue
                messages = update.get("messages") or []
                for msg in messages:
                    content = getattr(msg, "content", None)
                    role = getattr(msg, "type", getattr(msg, "role", node))
                    if not content:
                        tool_calls = getattr(msg, "tool_calls", None)
                        if tool_calls:
                            for tc in tool_calls:
                                name = (
                                    tc.get("name")
                                    if isinstance(tc, dict)
                                    else getattr(tc, "name", "?")
                                )
                                console.print(f"[yellow]→ tool[/yellow] {name}")
                        continue
                    text = content if isinstance(content, str) else str(content)
                    preview = text[:400] + ("…" if len(text) > 400 else "")
                    console.print(f"[blue]{role}/{node}[/blue]: {preview}\n")
                    if role in {"ai", "AIMessage"} or "model" in str(node):
                        final_chunks.append(text)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[yellow]stream 失败，回退 invoke：{exc}[/yellow]")
        result = agent.invoke(payload)
        from src.agents.research_agent import extract_final_text

        return extract_final_text(result)

    return final_chunks[-1] if final_chunks else "(empty stream)"


@app.command("list-reports")
def list_reports_cmd(limit: int = typer.Option(20, "--limit", "-n")):
    """List saved research reports."""
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    from src.tools.reports import list_reports

    items = list_reports(limit=limit)
    if not items:
        console.print("[dim]No reports yet.[/dim]")
        return
    table = Table(title="Saved reports")
    table.add_column("Name")
    table.add_column("KB", justify="right")
    table.add_column("Modified")
    for it in items:
        table.add_row(it["name"], str(it["size_kb"]), it["modified"])
    console.print(table)


@app.command("eval")
def eval_cmd():
    """Run offline golden-structure eval harness."""
    from src.eval.harness import run_all

    result = run_all()
    console.print_json(json.dumps(result, ensure_ascii=False))
    if result["failed"]:
        raise typer.Exit(1)


@app.command("new-session")
def new_session_cmd():
    """Create a new research session id."""
    from src.memory.sessions import new_session_id

    sid = new_session_id()
    console.print(sid)


@app.command()
def server(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8000, "--port"),
):
    """启动 FastAPI（UI + API）。"""
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    import uvicorn

    from src.config import clear_settings_cache, get_settings
    from src.logging_utils import setup_logging

    clear_settings_cache()
    setup_logging(get_settings().log_level)
    console.print(f"[cyan]API/UI → http://{host}:{port}/[/cyan]")
    console.print("[dim]Research only — not investment advice.[/dim]")
    uvicorn.run("src.api:app", host=host, port=port, reload=False)


@app.command("version")
def show_version():
    from src import __version__

    console.print(f"chokepoint-research-agent {__version__}")


@app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    question: Optional[str] = typer.Argument(None),
    stream: bool = typer.Option(False, "--stream", "-s"),
    server_mode: bool = typer.Option(False, "--server"),
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8000, "--port"),
    mode: str = typer.Option("full", "--mode", "-m"),
    session: Optional[str] = typer.Option(None, "--session"),
    bilingual: bool = typer.Option(False, "--bilingual"),
):
    if ctx.invoked_subcommand is not None:
        return
    if server_mode:
        server(host=host, port=port)
        return
    if question:
        research(
            question=question,
            stream=stream,
            save=True,
            mode=mode,
            session=session,
            bilingual=bilingual,
        )
    else:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
