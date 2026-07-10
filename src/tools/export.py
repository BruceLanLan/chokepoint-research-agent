"""Export research memos to HTML / JSON."""

from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings
from src.schemas.scorecard import extract_scorecard_table, validate_report_structure


def export_report_bundle(
    title: str,
    markdown_body: str,
    *,
    mode: str = "full",
    extra: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Write .md companion .json and .html under reports/. Returns paths."""
    settings = get_settings()
    out_dir = Path(settings.reports_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w\u4e00-\u9fff\-]+", "_", title.strip())[:80] or "report"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = out_dir / f"{ts}_{safe}"

    quality = validate_report_structure(markdown_body)
    card = extract_scorecard_table(markdown_body)
    payload = {
        "title": title,
        "mode": mode,
        "generated_at": datetime.now().isoformat(),
        "quality": quality,
        "scorecard": card.model_dump(),
        "markdown": markdown_body,
        "extra": extra or {},
        "disclaimer": "research_only_not_investment_advice",
    }
    json_path = base.with_suffix(".json")
    html_path = base.with_suffix(".html")
    md_path = base.with_suffix(".md")

    md_path.write_text(markdown_body.strip() + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(_to_html(title, markdown_body, quality), encoding="utf-8")

    return {
        "md": str(md_path.resolve()),
        "json": str(json_path.resolve()),
        "html": str(html_path.resolve()),
    }


def _to_html(title: str, markdown_body: str, quality: dict[str, Any]) -> str:
    # Minimal, dependency-free markdown-ish rendering
    escaped = html.escape(markdown_body)
    # preserve newlines
    body = escaped.replace("\n", "<br>\n")
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;line-height:1.55;color:#111}}
.banner{{background:#fff3cd;border:1px solid #ffecb5;padding:.75rem 1rem;border-radius:8px;margin-bottom:1rem}}
.meta{{color:#555;font-size:.9rem;margin-bottom:1.5rem}}
</style></head><body>
<div class="banner"><strong>免责声明</strong>：仅供研究学习，不构成投资建议。 / Research only — not investment advice.</div>
<h1>{html.escape(title)}</h1>
<div class="meta">quality_score={quality.get("score")} · pass={quality.get("pass")}</div>
<article>{body}</article>
</body></html>
"""
