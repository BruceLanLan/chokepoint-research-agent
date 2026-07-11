"""Local search over past research memos (lightweight TF-IDF, no heavy deps)."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.config import get_settings

_TOKEN = re.compile(r"[\w\u4e00-\u9fff]{2,}", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text or "")]


def _load_docs(limit: int = 200) -> list[dict[str, Any]]:
    out_dir = Path(get_settings().reports_dir)
    if not out_dir.is_dir():
        return []
    files = sorted(
        [p for p in out_dir.glob("*.md") if p.name != "SAMPLE_REPORT_FORMAT.md"],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:limit]
    docs = []
    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        docs.append({"name": p.name, "path": str(p.resolve()), "text": text})
    return docs


def search_memos(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """TF-IDF cosine-ish ranking over local markdown reports."""
    q = (query or "").strip()
    if not q:
        return []
    docs = _load_docs()
    if not docs:
        return []

    doc_tokens = [_tokenize(d["text"]) for d in docs]
    df: Counter[str] = Counter()
    for toks in doc_tokens:
        for t in set(toks):
            df[t] += 1
    n = len(docs)
    idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in df}

    def vec(toks: list[str]) -> dict[str, float]:
        tf = Counter(toks)
        if not tf:
            return {}
        max_tf = max(tf.values())
        return {t: (c / max_tf) * idf.get(t, 0.0) for t, c in tf.items()}

    def cos(a: dict[str, float], b: dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        keys = set(a) & set(b)
        num = sum(a[k] * b[k] for k in keys)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        if na == 0 or nb == 0:
            return 0.0
        return num / (na * nb)

    qv = vec(_tokenize(q))
    scored = []
    for d, toks in zip(docs, doc_tokens, strict=False):
        score = cos(qv, vec(toks))
        if score <= 0:
            continue
        # preview
        preview = re.sub(r"\s+", " ", d["text"])[:200]
        scored.append(
            {
                "name": d["name"],
                "path": d["path"],
                "score": round(score, 4),
                "preview": preview,
            }
        )
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[: max(1, min(limit, 50))]
