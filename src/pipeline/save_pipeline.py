"""Unified research save path: postprocess → evidence → audit → auto-tag → optional pro."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.pipeline.postprocess import postprocess_memo
from src.tools.reports import save_report_file


def save_research_memo(
    title: str,
    markdown: str,
    *,
    mode: str = "full",
    skill: str | None = None,
    thesis_id: str | None = None,
    watch_ids: list[str] | None = None,
    min_quality: int = 0,
    embed_charts: bool = True,
    auto_tag: bool = True,
    pro_suite: bool = False,
    pro_persist: bool = False,
    extra_meta: dict[str, Any] | None = None,
    quality: dict[str, Any] | None = None,
    skip_postprocess: bool = False,
) -> dict[str, Any]:
    """Canonical save pipeline for research memos."""
    if skip_postprocess and quality is not None:
        body = markdown
        pp = {
            "markdown": body,
            "quality": quality,
            "gate_ok": True,
            "charts": {},
            "evidence": {},
        }
    else:
        pp = postprocess_memo(
            title, markdown, mode=mode, embed_charts=embed_charts, min_quality=min_quality
        )
        body = pp["markdown"]
        quality = pp.get("quality") or {}
    meta = dict(extra_meta or {})
    if pp.get("evidence"):
        meta["evidence_urls"] = (pp.get("evidence") or {}).get("url_count")
    path = save_report_file(
        title=title,
        markdown_body=body,
        mode=mode,
        quality=quality,
        skill=skill,
        thesis_id=thesis_id,
        watch_ids=watch_ids,
        extra_meta=meta,
    )
    name = Path(path).name
    result: dict[str, Any] = {
        "path": path,
        "name": name,
        "quality": quality,
        "postprocess": {
            "gate_ok": pp.get("gate_ok"),
            "charts": pp.get("charts"),
            "evidence": pp.get("evidence"),
        },
        "disclaimer": "research_only_not_investment_advice",
    }
    try:
        from src.ops.audit import log_event
        from src.ops.evidence import extract_and_store

        extract_and_store(body, report_name=name, title=title)
        log_event(
            "research_saved",
            detail={
                "path": path,
                "mode": mode,
                "quality": quality.get("score"),
                "skill": skill,
                "thesis_id": thesis_id,
            },
        )
        result["evidence_stored"] = True
    except Exception as exc:  # noqa: BLE001
        result["evidence_error"] = str(exc)[:200]

    if auto_tag:
        try:
            from src.ops.auto_tag import auto_tag_report

            result["tags"] = auto_tag_report(name)
        except Exception as exc:  # noqa: BLE001
            result["tags_error"] = str(exc)[:200]

    if pro_suite:
        try:
            from src.ops.memo_pro_bridge import analyze_memo_with_pro

            result["pro"] = analyze_memo_with_pro(
                name, persist=pro_persist, symbol=(watch_ids or [""])[0] if watch_ids else ""
            )
        except Exception as exc:  # noqa: BLE001
            result["pro_error"] = str(exc)[:200]

    if thesis_id:
        try:
            from src.ops.thesis_links import link_report_to_thesis

            result["thesis_link"] = link_report_to_thesis(thesis_id, name)
        except Exception as exc:  # noqa: BLE001
            result["thesis_link_error"] = str(exc)[:200]

    return result
