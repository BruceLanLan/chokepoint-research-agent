"""Optional SQLite FTS5 index over research memos (stdlib sqlite3)."""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings

_TOKEN = re.compile(r"[\w\u4e00-\u9fff]{2,}", re.UNICODE)


def _db_path() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "memo_index.sqlite"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def rebuild_index(limit: int = 500) -> dict[str, Any]:
    out_dir = Path(get_settings().reports_dir)
    conn = _connect()
    try:
        conn.execute("DROP TABLE IF EXISTS memos_fts")
        conn.execute("DROP TABLE IF EXISTS memos_meta")
        # FTS5 may be unavailable on some builds — fall back to LIKE table
        fts_ok = True
        try:
            conn.execute(
                "CREATE VIRTUAL TABLE memos_fts USING fts5(name, title, body, tokenize='unicode61')"
            )
        except sqlite3.OperationalError:
            fts_ok = False
            conn.execute(
                "CREATE TABLE memos_fts (name TEXT, title TEXT, body TEXT)"
            )
        conn.execute(
            "CREATE TABLE memos_meta (name TEXT PRIMARY KEY, mtime REAL, chars INTEGER)"
        )
        if not out_dir.is_dir():
            conn.commit()
            return {"indexed": 0, "fts5": fts_ok}
        files = sorted(
            [p for p in out_dir.glob("*.md") if p.name != "SAMPLE_REPORT_FORMAT.md"],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[: max(1, min(limit, 2000))]
        n = 0
        for p in files:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            title = p.stem
            for line in text.splitlines()[:20]:
                if line.startswith("# "):
                    title = line[2:].strip()[:120]
                    break
            conn.execute(
                "INSERT INTO memos_fts(name, title, body) VALUES (?,?,?)",
                (p.name, title, text),
            )
            conn.execute(
                "INSERT OR REPLACE INTO memos_meta(name, mtime, chars) VALUES (?,?,?)",
                (p.name, p.stat().st_mtime, len(text)),
            )
            n += 1
        conn.commit()
        return {
            "indexed": n,
            "fts5": fts_ok,
            "path": str(_db_path().resolve()),
            "at": datetime.now().isoformat(timespec="seconds"),
        }
    finally:
        conn.close()


def search_index(query: str, limit: int = 15) -> list[dict[str, Any]]:
    q = (query or "").strip()
    if not q:
        return []
    if not _db_path().is_file():
        rebuild_index()
    conn = _connect()
    try:
        # detect fts5
        row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE name='memos_fts'"
        ).fetchone()
        is_fts = bool(row and row[0] and "fts5" in (row[0] or "").lower())
        results: list[dict[str, Any]] = []
        if is_fts:
            # escape double quotes for FTS
            safe = q.replace('"', " ")
            try:
                cur = conn.execute(
                    "SELECT name, title, snippet(memos_fts, 2, '[', ']', '…', 16) AS snip "
                    "FROM memos_fts WHERE memos_fts MATCH ? LIMIT ?",
                    (safe, limit),
                )
            except sqlite3.OperationalError:
                # fallback LIKE
                is_fts = False
        if not is_fts:
            like = f"%{q}%"
            cur = conn.execute(
                "SELECT name, title, substr(body, 1, 200) AS snip FROM memos_fts "
                "WHERE body LIKE ? OR title LIKE ? LIMIT ?",
                (like, like, limit),
            )
        for r in cur.fetchall():
            results.append(
                {
                    "name": r["name"],
                    "title": r["title"],
                    "snippet": r["snip"],
                    "engine": "fts5" if is_fts else "like",
                }
            )
        return results
    finally:
        conn.close()
