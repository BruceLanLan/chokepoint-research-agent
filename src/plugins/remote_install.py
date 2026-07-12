"""Hash-pinned remote plugin install (fail-closed)."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from src.ops.audit import log_event
from src.plugins.loader import plugins_dir

DISCLAIMER = "research_only_not_investment_advice"


def _allowed_hosts() -> set[str]:
    raw = os.environ.get("PLUGIN_ALLOW_HOSTS") or ""
    hosts = {h.strip().lower() for h in raw.split(",") if h.strip()}
    # default empty = deny all remote unless host allowlisted
    return hosts


def install_from_manifest(manifest_url: str, *, dry_run: bool = False) -> dict[str, Any]:
    """
    Download manifest JSON then entry file if sha256 matches.
    Requires PLUGIN_ALLOW_HOSTS to include manifest host.
    """
    parsed = urlparse(manifest_url)
    if parsed.scheme != "https":
        return {"ok": False, "error": "manifest_url must be https"}
    host = (parsed.hostname or "").lower()
    allow = _allowed_hosts()
    if not allow or host not in allow:
        return {
            "ok": False,
            "error": "host not in PLUGIN_ALLOW_HOSTS",
            "host": host,
            "allow": sorted(allow),
            "note": "Set PLUGIN_ALLOW_HOSTS=example.com to allow",
        }
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(manifest_url)
            r.raise_for_status()
            manifest = r.json()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"manifest fetch failed: {exc}"}

    pid = str(manifest.get("id") or "").strip()
    sha = str(manifest.get("sha256") or "").strip().lower()
    entry = str(manifest.get("entry") or "provider.py").strip()
    entry_url = str(manifest.get("entry_url") or "").strip()
    if not pid or not sha or not entry_url:
        return {"ok": False, "error": "manifest requires id, sha256, entry_url"}
    if urlparse(entry_url).scheme != "https":
        return {"ok": False, "error": "entry_url must be https"}
    ehost = (urlparse(entry_url).hostname or "").lower()
    if ehost not in allow:
        return {"ok": False, "error": "entry host not allowlisted", "host": ehost}

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "manifest": {k: manifest.get(k) for k in ("id", "version", "entry", "permissions")},
            "disclaimer": DISCLAIMER,
        }

    try:
        with httpx.Client(timeout=60.0) as client:
            er = client.get(entry_url)
            er.raise_for_status()
            content = er.content
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"entry fetch failed: {exc}"}

    digest = hashlib.sha256(content).hexdigest()
    if digest != sha:
        log_event("plugin_install_hash_mismatch", detail={"id": pid, "expected": sha, "got": digest})
        return {"ok": False, "error": "sha256 mismatch", "expected": sha, "got": digest}

    # write under plugins/ as sanitized name
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in pid)[:60]
    dest = plugins_dir() / f"{safe}.py"
    dest.write_bytes(content)
    log_event(
        "plugin_installed",
        detail={"id": pid, "path": str(dest), "sha256": digest, "version": manifest.get("version")},
    )
    return {
        "ok": True,
        "id": pid,
        "path": str(dest.resolve()),
        "sha256": digest,
        "version": manifest.get("version"),
        "permissions": manifest.get("permissions") or [],
        "disclaimer": DISCLAIMER,
        "note": "Installed locally. Load with: python main.py plugins --load " + safe,
    }
