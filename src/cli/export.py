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



def register(app: typer.Typer, export_app: typer.Typer) -> None:
    @export_app.command("pack")
    def exportgrp_pack(report: str = typer.Argument(...)):
        export_pack_cmd(report)



    @export_app.command("snapshot")
    def exportgrp_snapshot():
        snapshot_cmd()



    @export_app.command("pro")
    def exportgrp_pro():
        pro_export_cmd()


