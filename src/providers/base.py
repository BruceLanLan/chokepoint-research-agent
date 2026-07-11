"""Data provider protocol — pluggable market/filings sources."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MarketDataProvider(Protocol):
    name: str

    def quote(self, symbol: str) -> dict[str, Any]:
        """Return a best-effort quote snapshot."""
        ...


@runtime_checkable
class FilingsProvider(Protocol):
    name: str

    def search_company(self, query: str) -> list[dict[str, Any]]:
        ...

    def recent_filings(self, cik: str, form: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        ...


class ProviderRegistry:
    def __init__(self) -> None:
        self._market: dict[str, MarketDataProvider] = {}
        self._filings: dict[str, FilingsProvider] = {}

    def register_market(self, provider: MarketDataProvider) -> None:
        self._market[provider.name] = provider

    def register_filings(self, provider: FilingsProvider) -> None:
        self._filings[provider.name] = provider

    def market(self, name: str | None = None) -> MarketDataProvider | None:
        if name:
            return self._market.get(name)
        return next(iter(self._market.values()), None)

    def filings(self, name: str | None = None) -> FilingsProvider | None:
        if name:
            return self._filings.get(name)
        return next(iter(self._filings.values()), None)

    def list_providers(self) -> dict[str, list[str]]:
        return {
            "market": list(self._market.keys()),
            "filings": list(self._filings.keys()),
        }


_REGISTRY: ProviderRegistry | None = None


def get_registry() -> ProviderRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = ProviderRegistry()
        # lazy default registrations
        from src.providers.cn_announcements import CnAnnouncementProvider
        from src.providers.hkex_news import HkexNewsProvider
        from src.providers.sec_edgar import SecEdgarProvider
        from src.providers.yahoo_market import YahooMarketProvider

        _REGISTRY.register_filings(SecEdgarProvider())
        _REGISTRY.register_filings(CnAnnouncementProvider())
        _REGISTRY.register_filings(HkexNewsProvider())
        _REGISTRY.register_market(YahooMarketProvider())
    return _REGISTRY
