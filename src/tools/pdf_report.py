"""Pretty PDF research memo generator (fpdf2, optional Chinese system fonts)."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings
from src.schemas.scorecard import validate_report_structure


def _find_cjk_font() -> str | None:
    candidates = [
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        # Linux common
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        # Windows
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for p in candidates:
        if Path(p).is_file():
            return p
    return None


def markdown_to_pdf(
    title: str,
    markdown_body: str,
    *,
    out_path: str | Path | None = None,
    mode: str = "full",
) -> dict[str, Any]:
    """Render a research memo to PDF. Returns path + meta."""
    try:
        from fpdf import FPDF
    except ImportError as exc:
        return {
            "error": "fpdf2 not installed. Run: pip install fpdf2",
            "detail": str(exc),
        }

    quality = validate_report_structure(markdown_body)
    settings = get_settings()
    out_dir = Path(settings.reports_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w\u4e00-\u9fff\-]+", "_", title.strip())[:60] or "report"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(out_path) if out_path else out_dir / f"{ts}_{safe}.pdf"

    font_path = _find_cjk_font()
    pdf = FPDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_margins(16, 16, 16)

    font_name = "Helvetica"
    unicode_ok = False
    if font_path:
        try:
            # TTC may need uni=True / specific font index depending on fpdf2 version
            pdf.add_font("CJK", "", font_path)
            pdf.add_font("CJK", "B", font_path)
            font_name = "CJK"
            unicode_ok = True
        except Exception:  # noqa: BLE001
            font_name = "Helvetica"
            unicode_ok = False

    def set_font(bold: bool = False, size: int = 11) -> None:
        style = "B" if bold and font_name == "Helvetica" else ""
        if font_name == "CJK":
            pdf.set_font("CJK", size=size)
        else:
            pdf.set_font("Helvetica", style=style, size=size)

    def write_line(text: str, size: int = 11, bold: bool = False, gap: float = 1.5) -> None:
        set_font(bold=bold, size=size)
        # fpdf multi_cell for wrapping
        safe_text = text if unicode_ok else _ascii_fallback(text)
        pdf.multi_cell(0, size * 0.45 + 2, safe_text)
        pdf.ln(gap)

    # Banner
    pdf.set_fill_color(255, 248, 225)
    pdf.set_draw_color(255, 224, 130)
    set_font(size=9)
    banner = (
        "DISCLAIMER / 免责声明: Research only — not investment advice. "
        "仅供研究学习，不构成投资建议。"
    )
    pdf.multi_cell(0, 5, banner if unicode_ok else _ascii_fallback(banner), border=1, fill=True)
    pdf.ln(4)

    # Title
    write_line(title, size=16, bold=True, gap=2)
    meta = (
        f"mode={mode}  quality={quality.get('score')}  "
        f"generated={datetime.now().isoformat(timespec='seconds')}  "
        f"generator=chokepoint-research-agent"
    )
    pdf.set_text_color(90, 90, 90)
    write_line(meta, size=8, gap=3)
    pdf.set_text_color(0, 0, 0)

    # Horizontal rule
    pdf.set_draw_color(200, 200, 200)
    y = pdf.get_y()
    pdf.line(16, y, 194, y)
    pdf.ln(4)

    # Body
    for raw in (markdown_body or "").splitlines():
        line = raw.rstrip()
        if not line.strip():
            pdf.ln(2)
            continue
        if line.startswith("### "):
            write_line(line[4:], size=12, bold=True, gap=2)
        elif line.startswith("## "):
            write_line(line[3:], size=13, bold=True, gap=2)
        elif line.startswith("# "):
            write_line(line[2:], size=14, bold=True, gap=2)
        elif line.startswith("- ") or line.startswith("* "):
            write_line("• " + line[2:], size=10, gap=1)
        elif re.match(r"^\|.+\|$", line):
            # simple table row as monospace-ish text
            cells = [c.strip() for c in line.strip("|").split("|")]
            write_line(" | ".join(cells), size=8, gap=1)
        else:
            write_line(line, size=10, gap=1)

    # Footer on last page
    pdf.ln(6)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(16, pdf.get_y(), 194, pdf.get_y())
    pdf.ln(3)
    pdf.set_text_color(120, 120, 120)
    write_line(
        "End of report · Do not treat as investment advice · 报告结束",
        size=8,
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(path))
    return {
        "path": str(path.resolve()),
        "quality": quality,
        "font": font_path or "Helvetica",
        "unicode_font": unicode_ok,
        "pages": pdf.page_no(),
    }


def _ascii_fallback(text: str) -> str:
    """Best-effort strip non-latin when CJK font unavailable (CI)."""
    try:
        text.encode("latin-1")
        return text
    except UnicodeEncodeError:
        return text.encode("ascii", errors="replace").decode("ascii")
