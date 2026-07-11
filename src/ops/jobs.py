"""Simple async research job queue (in-process + JSON persistence)."""

from __future__ import annotations

import json
import threading
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from src.config import get_settings
from src.logging_utils import get_logger

log = get_logger("chokepoint.jobs")

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="research-job")
_lock = threading.Lock()


def _jobs_path() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "jobs.json"


def _load() -> dict[str, Any]:
    p = _jobs_path()
    if not p.is_file():
        return {"jobs": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def _save(data: dict[str, Any]) -> None:
    _jobs_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_jobs(limit: int = 30) -> list[dict[str, Any]]:
    data = _load()
    jobs = list((data.get("jobs") or {}).values())
    jobs.sort(key=lambda j: j.get("created_at") or "", reverse=True)
    return jobs[: max(1, min(limit, 100))]


def get_job(job_id: str) -> dict[str, Any] | None:
    return (_load().get("jobs") or {}).get(job_id)


def _update(job_id: str, **fields: Any) -> None:
    with _lock:
        data = _load()
        job = (data.get("jobs") or {}).get(job_id)
        if not job:
            return
        job.update(fields)
        job["updated_at"] = datetime.now().isoformat(timespec="seconds")
        data["jobs"][job_id] = job
        # prune old finished jobs beyond 100
        if len(data["jobs"]) > 120:
            ordered = sorted(data["jobs"].values(), key=lambda j: j.get("created_at") or "")
            for old in ordered[:-100]:
                data["jobs"].pop(old["id"], None)
        _save(data)


def submit_research_job(
    *,
    question: str,
    mode: str = "full",
    run_fn: Callable[[str, str], dict[str, Any]],
) -> dict[str, Any]:
    """run_fn(question, mode) -> {report, quality, saved_path, ...}"""
    job_id = uuid.uuid4().hex[:12]
    job = {
        "id": job_id,
        "question": question,
        "mode": mode,
        "status": "queued",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "result": None,
        "error": None,
    }
    with _lock:
        data = _load()
        data.setdefault("jobs", {})[job_id] = job
        _save(data)

    def _work() -> None:
        _update(job_id, status="running")
        try:
            result = run_fn(question, mode)
            _update(job_id, status="completed", result=result)
            log.info("job %s completed", job_id)
        except Exception as exc:  # noqa: BLE001
            log.exception("job %s failed", job_id)
            _update(
                job_id,
                status="failed",
                error=str(exc),
                traceback=traceback.format_exc()[-2000:],
            )

    _executor.submit(_work)
    return job
