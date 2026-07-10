"""Lightweight tests for market snapshot helpers (network optional)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_a_share_symbol_normalization_logic():
    from src.tools.research_tools import normalize_symbol

    assert normalize_symbol("600519") == "600519.SS"
    assert normalize_symbol("000001") == "000001.SZ"
    assert normalize_symbol("AAPL") == "AAPL"
    assert normalize_symbol("0700.HK") == "0700.HK"


def test_fetch_url_rejects_non_http():
    from src.tools.research_tools import fetch_url

    out = fetch_url.invoke({"url": "file:///etc/passwd"})
    assert "Invalid URL" in out
