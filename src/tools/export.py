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
    chart_svg = ""
    try:
        from src.charts.scorecard import charts_from_memo

        chart_svg = charts_from_memo(markdown_body).get("scorecard_svg") or ""
    except Exception:  # noqa: BLE001
        chart_svg = ""
    html_path.write_text(
        _to_html(title, markdown_body, quality, chart_svg=chart_svg), encoding="utf-8"
    )

    pdf_meta: dict[str, Any] = {}
    try:
        from src.tools.pdf_report import markdown_to_pdf

        pdf_meta = markdown_to_pdf(
            title, markdown_body, out_path=base.with_suffix(".pdf"), mode=mode
        )
    except Exception as exc:  # noqa: BLE001
        pdf_meta = {"error": str(exc)}

    result = {
        "md": str(md_path.resolve()),
        "json": str(json_path.resolve()),
        "html": str(html_path.resolve()),
    }
    if pdf_meta.get("path"):
        result["pdf"] = pdf_meta["path"]
    if pdf_meta.get("error"):
        result["pdf_error"] = pdf_meta["error"]
    return result


def _to_html(
    title: str,
    markdown_body: str,
    quality: dict[str, Any],
    chart_svg: str = "",
) -> str:
    """Print-optimized HTML (use browser Print → PDF)."""
    escaped = html.escape(markdown_body)
    # light markdown: headings & bullets
    lines = []
    for raw in escaped.splitlines():
        line = raw.rstrip()
        if line.startswith("### "):
            lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("- "):
            lines.append(f"<li>{line[2:]}</li>")
        elif line.strip() == "":
            lines.append("<br/>")
        else:
            lines.append(f"<p>{line}</p>")
    body = "\n".join(lines)
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
:root {{ --fg:#111; --muted:#555; --line:#ddd; }}
body {{ font-family: "Segoe UI", "PingFang SC", "Noto Sans SC", system-ui, sans-serif;
  max-width: 820px; margin: 0 auto; padding: 1.5rem; line-height: 1.6; color: var(--fg); }}
.banner {{ background:#fff8e1; border:1px solid #ffe082; padding:.75rem 1rem; border-radius:8px; margin-bottom:1rem; font-size:.92rem; }}
.meta {{ color:var(--muted); font-size:.9rem; margin-bottom:1.25rem; border-bottom:1px solid var(--line); padding-bottom:.75rem; }}
h1,h2,h3 {{ line-height:1.25; }}
h1 {{ font-size:1.5rem; }} h2 {{ font-size:1.2rem; margin-top:1.4rem; }} h3 {{ font-size:1.05rem; }}
p {{ margin:.35rem 0; }} li {{ margin-left:1.1rem; }}
footer {{ margin-top:2rem; padding-top:1rem; border-top:1px solid var(--line); color:var(--muted); font-size:.85rem; }}
@media print {{
  body {{ max-width:100%; padding:0; }}
  .banner {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  a {{ color:inherit; text-decoration:none; }}
}}
</style></head><body>
<div class="banner"><strong>免责声明 / Disclaimer</strong>：仅供研究学习，不构成投资建议。 Research only — not investment advice.</div>
<h1>{html.escape(title)}</h1>
<div class="meta">quality_score={quality.get("score")} · pass={quality.get("pass")} · generator=chokepoint-research-agent</div>
{f'<section class="chart">{chart_svg}</section>' if chart_svg else ""}
<article>{body}</article>
<footer>Print this page to PDF from your browser. Do not treat as investment advice.</footer>
</body></html>
"""
