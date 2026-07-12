"""CLI ops group — desk / digest / health / weekly / migrate."""
from __future__ import annotations

import typer

from src.cli.common import console, _boot_env


def register(app: typer.Typer, ops_app: typer.Typer) -> None:
    @ops_app.command("desk")
    def ops_desk(md: bool = typer.Option(False, "--md")):
        """Alias: research desk status."""
        _boot_env()
        from src.ops.research_desk import research_desk_markdown, research_desk_status

        console.print(research_desk_markdown() if md else research_desk_status())

    @ops_app.command("digest")
    def ops_digest(save: bool = typer.Option(True, "--save/--no-save")):
        """Offline workspace digest (no LLM)."""
        _boot_env()
        from src.ops.digest import build_workspace_digest

        out = build_workspace_digest(save=save)
        console.print(out.get("markdown"))
        if out.get("saved_path"):
            console.print(f"[green]Saved: {out['saved_path']}[/green]")

    @ops_app.command("health")
    def ops_health():
        """Composite research-ops health score (process hygiene, not alpha)."""
        _boot_env()
        from src.ops.workspace_health import workspace_health_score

        console.print(workspace_health_score())

    @ops_app.command("weekly")
    def ops_weekly(
        save: bool = typer.Option(True, "--save/--no-save"),
        enqueue: int = typer.Option(0, "--enqueue"),
    ):
        """Weekly ops pack: digest + health + batch review (+ optional queue)."""
        _boot_env()
        from src.ops.weekly_ops import run_weekly_ops

        out = run_weekly_ops(save=save, enqueue_watchlist=enqueue)
        console.print(out.get("markdown") if not save else out)
        if out.get("saved_path"):
            console.print(f"[green]Saved: {out['saved_path']}[/green]")

    @ops_app.command("migrate")
    def ops_migrate():
        """Run data store schema migration / backup."""
        _boot_env()
        from src.ops.store_migrate import migrate_data_stores

        console.print(migrate_data_stores())
