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



def register(app: typer.Typer, pro_app: typer.Typer) -> None:
    @pro_app.command("list")
    def progrp_list():
        pro_cmd(module=None)



    @pro_app.command("suite")
    def progrp_suite(
        text: str = typer.Option(
            "System boundary defined with chokepoint nodes, kill criteria, and https://example.com source",
            "--text",
        ),
        symbol: str = typer.Option("", "--symbol"),
    ):
        pro_suite_cmd(text=text, symbol=symbol)



    @pro_app.command("dashboard")
    def progrp_dashboard():
        pro_dashboard_cmd()



    @pro_app.command("verticals")
    def progrp_verticals(
        show: Optional[str] = typer.Option(None, "--show", help="Print one pack in detail"),
        scaffold: Optional[str] = typer.Option(
            None, "--scaffold", help="Print research question scaffold for pack id"
        ),
        suggest: Optional[str] = typer.Option(
            None, "--suggest", help="Suggest vertical from free text"
        ),
    ):
        """List / show / scaffold deep vertical packs (skills/pro_verticals/)."""
        from src.ops.pro.verticals import (
            list_verticals,
            load_vertical,
            scaffold_research_question,
            suggest_vertical,
        )

        if suggest:
            console.print(suggest_vertical(suggest))
            return
        if scaffold:
            console.print(scaffold_research_question(scaffold))
            return
        if show:
            data = load_vertical(show)
            if not data:
                console.print(f"[red]unknown vertical: {show}[/red]")
                raise typer.Exit(1)
            console.print(data)
            return
        for v in list_verticals():
            console.print(
                f"[cyan]{v['id']}[/cyan]  {v.get('title')}  "
                f"nodes={v.get('node_count')} kills={v.get('kill_count')}  "
                f"modules={v.get('modules')}"
            )
        console.print(
            "[dim]research --vertical cpo_optics · pro-suite --vertical cpo_optics · "
            "progrp verticals --show cpo_optics[/dim]"
        )



    @app.command("providers")
    def providers_cmd():
        """List registered data providers."""
        from src.providers.base import get_registry

        console.print(get_registry().list_providers())



    @app.command("provider-health")
    def provider_health_cmd(
        live: bool = typer.Option(False, "--live", help="Hit network probes (slow)"),
    ):
        """Probe registered data providers."""
        _boot_env()
        from src.ops.provider_health import probe_providers

        console.print(probe_providers(live=live))



    @app.command("pro")
    def pro_cmd(
        module: Optional[str] = typer.Argument(None, help="Module id (omit to list)"),
        action: str = typer.Option("summarize", "--action", "-a"),
        title: str = typer.Option("", "--title"),
        text: str = typer.Option("", "--text", help="Body / text for analyze or add"),
        symbol: str = typer.Option("", "--symbol"),
        limit: int = typer.Option(50, "--limit"),
    ):
        """Professional maturity-train modules (v5.2–v5.51). Research ops only."""
        _boot_env()
        from src.ops.pro.registry import invoke_module, list_modules

        if not module:
            for m in list_modules():
                console.print(f"[cyan]{m['id']}[/cyan]  {m['version_theme']}  {m['title']}")
            console.print(f"[dim]{len(list_modules())} modules — research only, not advice[/dim]")
            return
        kwargs: dict = {"action": action, "limit": limit}
        if title:
            kwargs["title"] = title
        if text:
            kwargs["text"] = text
            kwargs["body"] = text
        if symbol:
            kwargs["symbol"] = symbol
        console.print(invoke_module(module, **kwargs))



    @app.command("pro-suite")
    def pro_suite_cmd(
        text: str = typer.Option(
            "System boundary defined with chokepoint nodes, kill criteria, and https://example.com source",
            "--text",
        ),
        symbol: str = typer.Option("", "--symbol"),
        vertical: Optional[str] = typer.Option(
            None, "--vertical", "-V", help="Scope suite to vertical pack modules only"
        ),
    ):
        """Run analyze across all 50 pro modules (or --vertical scoped subset)."""
        _boot_env()
        from src.ops.pro.suite import run_suite

        console.print(run_suite(text=text, symbol=symbol, vertical=vertical))



    @app.command("pro-dashboard")
    def pro_dashboard_cmd():
        """Aggregate activity across all pro modules."""
        _boot_env()
        from src.ops.pro_dashboard import pro_dashboard

        console.print(pro_dashboard())



    @app.command("pro-export")
    def pro_export_cmd():
        """Zip all pro-module summaries + local data/pro stores."""
        _boot_env()
        from src.ops.pro_pack_export import export_pro_pack

        console.print(export_pro_pack())


