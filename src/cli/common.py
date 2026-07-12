"""Shared CLI bootstrap."""
from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

console = Console()
VALID_MODES = {"full", "chokepoint_fast", "risk_only", "compare"}


def _boot_env():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    from src.config import clear_settings_cache
    clear_settings_cache()


def build_app() -> typer.Typer:
    """Construct the root Typer app with sub-apps and all commands."""
    app = typer.Typer(
        add_completion=False,
        help=(
            "Chokepoint Research Agent — professional research workstation "
            "(Chokepoint Theory). Not investment advice.\n\n"
            "Golden path: doctor → about → desk → research → checklist → weekly-ops"
        ),
    )
    watch_app = typer.Typer(help="Coverage book / watchlist")
    thesis_app = typer.Typer(help="Thesis registry")
    ops_app = typer.Typer(help="Research ops hygiene (desk, digest, health, weekly)")
    pro_app = typer.Typer(help="Professional modules (50-module train + suite)")
    export_app = typer.Typer(help="Export / backup / snapshot")
    app.add_typer(watch_app, name="watch")
    app.add_typer(thesis_app, name="thesis")
    app.add_typer(ops_app, name="ops")
    app.add_typer(pro_app, name="progrp")
    app.add_typer(export_app, name="export")

    from src.cli import research as research_mod
    from src.cli import watch as watch_mod
    from src.cli import thesis as thesis_mod
    from src.cli import ops as ops_mod
    from src.cli import pro as pro_mod
    from src.cli import export as export_mod
    from src.cli import core as core_mod

    research_mod.register(app)
    watch_mod.register(app, watch_app)
    thesis_mod.register(app, thesis_app)
    ops_mod.register(app, ops_app)
    pro_mod.register(app, pro_app)
    export_mod.register(app, export_app)
    core_mod.register(app)

    return app
