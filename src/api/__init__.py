"""Chokepoint FastAPI package (split routes)."""
from __future__ import annotations

from src.api.factory import create_app

app = create_app()

__all__ = ["app", "create_app"]
