"""Search local knowledge/glossary educational terms."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GLOSSARY = ROOT / "knowledge" / "glossary"


def list_glossary_terms() -> list[str]:
    if not GLOSSARY.is_dir():
        return []
    return sorted(p.stem for p in GLOSSARY.glob("*.md"))


def get_term(term: str) -> dict[str, Any]:
    safe = Path(term).stem
    path = GLOSSARY / f"{safe}.md"
    if not path.is_file():
        return {"error": f"unknown term: {term}"}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "term": safe,
        "path": str(path.resolve()),
        "markdown": text,
        "preview": text[:400],
        "disclaimer": "research_only_not_investment_advice",
    }


def search_glossary(query: str, *, limit: int = 30) -> dict[str, Any]:
    q = (query or "").strip().lower()
    if not q:
        terms = list_glossary_terms()
        return {
            "query": query,
            "count": len(terms),
            "terms": terms[:limit],
            "disclaimer": "research_only_not_investment_advice",
        }
    hits = []
    for p in sorted(GLOSSARY.glob("*.md")) if GLOSSARY.is_dir() else []:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        blob = f"{p.stem}\n{text}".lower()
        if q in blob or re.search(re.escape(q), blob):
            hits.append(
                {
                    "term": p.stem,
                    "score": blob.count(q),
                    "preview": text[:220].replace("\n", " "),
                }
            )
    hits.sort(key=lambda x: -x["score"])
    return {
        "query": query,
        "count": len(hits),
        "hits": hits[: max(1, min(limit, 100))],
        "disclaimer": "research_only_not_investment_advice",
        "note": "Educational glossary — not investment advice.",
    }
