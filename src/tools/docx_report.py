"""Minimal DOCX export for research memos (pure stdlib OOXML)."""

from __future__ import annotations

import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from src.config import get_settings

_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

_DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>
"""


def _p(text: str, *, bold: bool = False, size: int = 22) -> str:
    run_props = f'<w:rPr><w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    if bold:
        run_props += "<w:b/>"
    run_props += "</w:rPr>"
    safe = escape(text).replace("\n", "</w:t><w:br/><w:t>")
    return (
        f'<w:p><w:r>{run_props}<w:t xml:space="preserve">{safe}</w:t></w:r></w:p>'
    )


def _md_to_paragraphs(markdown: str) -> str:
    parts: list[str] = []
    parts.append(
        _p(
            "Research only — not investment advice / 仅供研究学习，不构成投资建议",
            bold=True,
            size=18,
        )
    )
    for raw in (markdown or "").splitlines():
        line = raw.rstrip()
        if not line.strip():
            parts.append("<w:p/>")
            continue
        if line.startswith("# "):
            parts.append(_p(line[2:].strip(), bold=True, size=32))
        elif line.startswith("## "):
            parts.append(_p(line[3:].strip(), bold=True, size=28))
        elif line.startswith("### "):
            parts.append(_p(line[4:].strip(), bold=True, size=24))
        elif line.startswith(("- ", "* ")):
            parts.append(_p("• " + line[2:].strip(), size=20))
        else:
            # strip simple markdown bold/italic markers for readability
            clean = re.sub(r"[*_`]+", "", line)
            parts.append(_p(clean, size=20))
    return "".join(parts)


def markdown_to_docx(
    title: str,
    markdown_body: str,
    *,
    out_path: Path | None = None,
    mode: str = "full",
) -> dict[str, Any]:
    settings = get_settings()
    out_dir = Path(settings.reports_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w\u4e00-\u9fff\-]+", "_", title.strip())[:60] or "report"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_path or (out_dir / f"{ts}_{safe}.docx")

    body = _md_to_paragraphs(markdown_body)
    title_p = _p(title, bold=True, size=36)
    meta_p = _p(f"mode={mode} · generated={datetime.now().isoformat(timespec='seconds')}", size=16)
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {title_p}
    {meta_p}
    {body}
    <w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>
  </w:body>
</w:document>
"""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _CONTENT_TYPES)
        zf.writestr("_rels/.rels", _RELS)
        zf.writestr("word/document.xml", document)
        zf.writestr("word/_rels/document.xml.rels", _DOC_RELS)

    return {
        "path": str(path.resolve()),
        "size_kb": round(path.stat().st_size / 1024, 1),
        "format": "docx",
    }
