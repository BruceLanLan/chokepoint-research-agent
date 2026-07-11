"""Export thesis registry to markdown notebook."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.config import get_settings
from src.ops.theses import list_theses


def export_theses_markdown(path: str | Path | None = None) -> str:
    items = list_theses()
    lines = [
        "# Thesis Registry / 论点台账",
        "",
        f"exported_at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "> Research only — not investment advice. 仅供研究学习，不构成投资建议。",
        "",
    ]
    for t in items:
        lines.append(f"## {t.get('title')} (`{t.get('id')}`)")
        lines.append(f"- status: **{t.get('status')}**")
        lines.append(f"- system: {t.get('system') or '—'}")
        lines.append(f"- symbols: {', '.join(t.get('related_symbols') or []) or '—'}")
        lines.append("")
        lines.append("### Statement")
        lines.append(t.get("statement") or "")
        lines.append("")
        lines.append("### Chokepoints")
        for c in t.get("chokepoints") or []:
            lines.append(f"- {c}")
        if not t.get("chokepoints"):
            lines.append("- —")
        lines.append("")
        lines.append("### Kill criteria")
        for k in t.get("kill_criteria") or []:
            lines.append(f"- {k}")
        if not t.get("kill_criteria"):
            lines.append("- —")
        lines.append("")
        lines.append("---")
        lines.append("")
    text = "\n".join(lines)
    if path is None:
        out = Path(get_settings().reports_dir) / f"theses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    else:
        out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return str(out.resolve())
