#!/usr/bin/env python3
"""CLI entrypoint for Chokepoint Research Agent (research workstation)."""

from __future__ import annotations

from src.cli.common import build_app

app = build_app()

if __name__ == "__main__":
    app()
