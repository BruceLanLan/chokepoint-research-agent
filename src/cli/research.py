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




def run_research(
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
    skill: Optional[str] = None,
    vertical: Optional[str] = None,
    mock: bool = False,
    min_quality: int = 0,
    thesis_id: Optional[str] = None,
    pro_suite: bool = False,
    pro_persist: bool = False,
    auto_tag: bool = True,
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

    if vertical:
        from src.ops.pro.verticals import load_vertical, scaffold_research_question

        if not load_vertical(vertical):
            console.print(f"[red]Unknown vertical: {vertical}[/red]")
            console.print("[dim]List: python main.py progrp verticals[/dim]")
            raise typer.Exit(2)
        if not question and not template:
            sc = scaffold_research_question(vertical)
            question = sc.get("question")
            mode = sc.get("mode") or mode
            if not skill and sc.get("suggested_skill"):
                skill = sc["suggested_skill"]
            console.print(f"[cyan]vertical={vertical} mode={mode} skill={skill or '-'}[/cyan]")
        elif question:
            # Agent system prompt gets vertical via build_investment_agent(vertical=…)
            console.print(f"[cyan]vertical={vertical}[/cyan]")

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
        if mock and vertical:
            pass  # scaffold already ran above when vertical set
        elif mock:
            question = "Offline mock chokepoint memo"
        else:
            question = typer.prompt("请输入研究问题")

    if mode not in VALID_MODES:
        console.print(f"[red]Unknown mode: {mode}[/red]")
        raise typer.Exit(2)

    if not mock:
        problems = settings.validate_runtime(require_tavily=True)
        if problems:
            for p in problems:
                console.print(f"[yellow]! {p}[/yellow]")
            if any("API_KEY" in p and "TAVILY" not in p for p in problems):
                raise typer.Exit(1)

    question_for_agent = question or ""
    if session:
        from src.memory.sessions import session_context_block

        ctx = session_context_block(session)
        if ctx:
            question_for_agent = f"{question}\n\n{ctx}"

    console.print(
        Panel.fit(
            f"[bold cyan]Chokepoint Research Agent[/bold cyan]\n"
            f"Q: {(question or '')[:200]}\nmode={mode}"
            f"{' mock=True' if mock else ''}\n"
            f"[dim]Research only — not investment advice[/dim]",
            border_style="cyan",
        )
    )

    from src.agents.research_agent import build_investment_agent, extract_final_text
    from src.schemas.scorecard import extract_scorecard_table, validate_report_structure

    settings.reports_dir.mkdir(parents=True, exist_ok=True)

    if mock:
        from src.eval.mock_pipeline import MOCK_MEMO

        final_text = MOCK_MEMO
        if vertical:
            final_text = f"# Mock vertical: {vertical}\n\nQuestion: {question}\n\n" + MOCK_MEMO
        console.print("[dim]mock offline — no LLM[/dim]")
    else:
        agent = build_investment_agent(
            settings, mode=mode, skill=skill, vertical=vertical
        )  # type: ignore[arg-type]
        payload = {"messages": [{"role": "user", "content": question_for_agent}]}

        if stream:
            final_text = _stream_agent(agent, payload)
        else:
            with console.status("[bold green]Researching…"):
                result = agent.invoke(payload)
            final_text = extract_final_text(result)

    from src.pipeline.postprocess import postprocess_memo

    pp = postprocess_memo(
        question[:40], final_text, mode=mode, embed_charts=True, min_quality=min_quality
    )
    final_text = pp["markdown"]
    quality = pp["quality"]
    card_nodes = pp["scorecard_nodes"]
    console.print(Panel(Markdown(final_text), title="Research memo", border_style="green"))
    console.print(
        f"[dim]quality={quality['score']} nodes={card_nodes} "
        f"gate_ok={pp['gate_ok']} urls={quality['url_count']}[/dim]"
    )
    if min_quality and not pp["gate_ok"]:
        console.print(f"[yellow]Quality gate failed (min={min_quality})[/yellow]")

    from src.tools.resilience import get_cost_tracker

    cost = get_cost_tracker().summary()
    if settings.max_tokens_budget and get_cost_tracker().over_budget(settings.max_tokens_budget):
        console.print(
            f"[yellow]Token budget exceeded "
            f"(est={cost.get('total_tokens_est')} max={settings.max_tokens_budget})[/yellow]"
        )
    console.print(f"[dim]cost_est={cost}[/dim]")

    if save and final_text:
        from src.pipeline.save_pipeline import save_research_memo

        saved = save_research_memo(
            (question or "research")[:40],
            final_text,
            mode=mode,
            skill=skill,
            vertical=vertical,
            thesis_id=thesis_id,
            min_quality=min_quality,
            auto_tag=auto_tag,
            pro_suite=pro_suite,
            pro_persist=pro_persist,
            extra_meta={
                "cost_tokens_est": cost.get("total_tokens_est"),
                "mock": mock or None,
            },
            quality=quality,
            skip_postprocess=True,
        )
        path = saved["path"]
        console.print(f"[green]Saved: {path}[/green]")
        if vertical:
            console.print(f"[dim]vertical_id={vertical}[/dim]")
        if saved.get("tags"):
            console.print(f"[dim]tags={saved.get('tags')}[/dim]")
        if thesis_id:
            console.print(f"[dim]thesis_link={saved.get('thesis_link')}[/dim]")
        if export_all or settings.export_html_json:
            from src.tools.export import export_report_bundle

            paths = export_report_bundle(
                title=(question or "research")[:40],
                markdown_body=final_text,
                mode=mode,
                extra={
                    "cost": cost,
                    "postprocess": {"charts": pp.get("charts")},
                    "skill": skill,
                    "vertical": vertical,
                },
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



_run_research = run_research  # back-compat alias


def register(app: typer.Typer) -> None:
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
        skill: Optional[str] = typer.Option(None, "--skill", help="domain skill pack id"),
        vertical: Optional[str] = typer.Option(
            None, "--vertical", "-V", help="deep vertical pack (cpo_optics, hbm_packaging, …)"
        ),
        mock: bool = typer.Option(False, "--mock", help="offline mock memo — no LLM"),
        min_quality: int = typer.Option(0, "--min-quality", help="postprocess quality gate"),
        thesis_id: Optional[str] = typer.Option(None, "--thesis-id", help="link saved memo to thesis"),
        pro_suite: bool = typer.Option(False, "--pro-suite", help="run pro suite on saved memo"),
        pro_persist: bool = typer.Option(False, "--pro-persist", help="persist pro notes when suite passes"),
        no_auto_tag: bool = typer.Option(False, "--no-auto-tag"),
    ):
        """Run multi-agent research (or render --template first).

        Deep vertical: research --vertical cpo_optics
        Offline demo: research --mock --vertical cpo_optics
        """
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
            skill=skill,
            vertical=vertical,
            mock=mock,
            min_quality=min_quality,
            thesis_id=thesis_id,
            pro_suite=pro_suite,
            pro_persist=pro_persist,
            auto_tag=not no_auto_tag,
        )



    # ── doctor / catalog / templates / brief ───────────────────────────────────



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


