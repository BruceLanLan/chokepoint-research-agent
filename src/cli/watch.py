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



def register(app: typer.Typer, watch_app: typer.Typer) -> None:
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



    @watch_app.command("bulk")
    def watch_bulk(
        symbols: str = typer.Argument(..., help="Comma-separated symbols e.g. NVDA,AAPL,600519"),
        priority: str = typer.Option("medium", "--priority"),
    ):
        """Bulk-add symbols to coverage book."""
        _boot_env()
        from src.ops.watchlist_bulk import bulk_add_symbols

        console.print(bulk_add_symbols(symbols, priority=priority))



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



    @watch_app.command("export-csv")
    def watch_export_csv(path: str = typer.Option("watchlist.csv", "--path")):
        _boot_env()
        from src.ops.io_csv import export_watchlist_csv

        export_watchlist_csv(path)
        console.print(f"[green]exported {path}[/green]")



    @watch_app.command("import-csv")
    def watch_import_csv(path: str = typer.Argument(...)):
        _boot_env()
        from src.ops.io_csv import import_watchlist_csv

        console.print(import_watchlist_csv(path))


    # ── thesis ────────────────────────────────────────────────────────────────


