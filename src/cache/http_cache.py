"""Simple file-backed HTTP GET cache for public data (SEC tickers, etc.)."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import httpx

from src.config import get_settings


def _cache_dir() -> Path:
    d = Path(get_settings().reports_dir).parent / "data" / "http_cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _key(url: str, params: dict | None) -> str:
    raw = url + "?" + json.dumps(params or {}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def cached_get_json(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    ttl_seconds: int = 3600,
    timeout: float = 20.0,
) -> Any:
    """GET JSON with disk cache. Returns parsed JSON or raises."""
    path = _cache_dir() / f"{_key(url, params)}.json"
    if path.is_file():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if time.time() - float(payload.get("_cached_at", 0)) < ttl_seconds:
                return payload.get("data")
        except Exception:  # noqa: BLE001
            pass
    with httpx.Client(timeout=timeout, headers=headers or {}) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    path.write_text(
        json.dumps({"_cached_at": time.time(), "data": data}, ensure_ascii=False),
        encoding="utf-8",
    )
    return data


def clear_http_cache() -> int:
    n = 0
    for p in _cache_dir().glob("*.json"):
        p.unlink(missing_ok=True)
        n += 1
    return n
