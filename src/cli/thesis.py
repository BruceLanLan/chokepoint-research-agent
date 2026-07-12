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



def register(app: typer.Typer, thesis_app: typer.Typer) -> None:
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


