"""Example third-party provider plugin.

Register at runtime:
  from plugins.example_provider import ExampleStaticProvider
  from src.providers.base import get_registry
  get_registry().register_filings(ExampleStaticProvider())
"""

from __future__ import annotations

from typing import Any


class ExampleStaticProvider:
    """Demo filings provider returning static educational rows."""

    name = "example_static"

    def search_company(self, query: str) -> list[dict[str, Any]]:
        return [
            {
                "ticker": "DEMO",
                "name": f"Example match for {query}",
                "source": "example_static",
                "note": "Replace with real vendor API",
            }
        ]

    def recent_filings(
        self, cik: str, form: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        return [
            {
                "form": form or "DEMO",
                "title": f"Static demo filing for {cik}",
                "url": "https://example.com/demo-filing",
                "source": "example_static",
            }
        ][:limit]
