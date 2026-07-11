"""Real scheduled tasks: launchd (macOS) + cron helpers + schedule config."""

from __future__ import annotations

import json
import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings

LABEL = "ai.chokepoint.research.brief"
PLIST_NAME = f"{LABEL}.plist"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _data_dir() -> Path:
    d = Path(get_settings().reports_dir).parent / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def schedule_config_path() -> Path:
    return _data_dir() / "schedule.json"


def load_schedule() -> dict[str, Any]:
    p = schedule_config_path()
    if not p.is_file():
        return {
            "enabled": False,
            "kind": "watchlist_brief",
            "limit": 3,
            "mode": "chokepoint_fast",
            "hour": 9,
            "minute": 0,
            "timezone_note": "local machine time",
            "updated_at": None,
        }
    return json.loads(p.read_text(encoding="utf-8"))


def save_schedule(cfg: dict[str, Any]) -> dict[str, Any]:
    cfg["updated_at"] = datetime.now().isoformat(timespec="seconds")
    schedule_config_path().write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return cfg


def python_bin() -> str:
    return os.environ.get("CHOKEPOINT_PYTHON") or str(
        _project_root() / ".venv" / "bin" / "python"
    )


def runner_script() -> Path:
    return _project_root() / "scripts" / "run_scheduled_brief.py"


def launchd_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / PLIST_NAME


def build_launchd_plist(hour: int, minute: int) -> str:
    root = _project_root()
    py = python_bin()
    script = runner_script()
    log_dir = _data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout = log_dir / "scheduled_brief.out.log"
    stderr = log_dir / "scheduled_brief.err.log"
    # Keep WorkingDirectory for .env discovery
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{py}</string>
    <string>{script}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>{root}</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>{int(hour)}</integer>
    <key>Minute</key>
    <integer>{int(minute)}</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>{stdout}</string>
  <key>StandardErrorPath</key>
  <string>{stderr}</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
"""


def cron_line(hour: int, minute: int) -> str:
    py = python_bin()
    script = runner_script()
    root = _project_root()
    return (
        f"{int(minute)} {int(hour)} * * * cd {root} && "
        f"{py} {script} >> data/logs/cron_brief.log 2>&1"
    )


def install_schedule(hour: int = 9, minute: int = 0) -> dict[str, Any]:
    cfg = load_schedule()
    cfg.update(
        {
            "enabled": True,
            "hour": hour,
            "minute": minute,
            "platform": platform.system(),
        }
    )
    save_schedule(cfg)
    system = platform.system()
    result: dict[str, Any] = {
        "config": cfg,
        "cron_line": cron_line(hour, minute),
        "runner": str(runner_script()),
    }
    if system == "Darwin":
        plist = launchd_plist_path()
        plist.parent.mkdir(parents=True, exist_ok=True)
        plist.write_text(build_launchd_plist(hour, minute), encoding="utf-8")
        # unload then load
        subprocess_run(["launchctl", "unload", str(plist)], check=False)
        r = subprocess_run(["launchctl", "load", str(plist)], check=False)
        result["launchd_plist"] = str(plist)
        result["launchctl"] = r
        result["installed"] = r.get("returncode") == 0
    else:
        result["installed"] = False
        result["note"] = (
            "Non-macOS: add the cron_line to `crontab -e`. "
            "launchd install skipped."
        )
    return result


def uninstall_schedule() -> dict[str, Any]:
    cfg = load_schedule()
    cfg["enabled"] = False
    save_schedule(cfg)
    out: dict[str, Any] = {"config": cfg}
    if platform.system() == "Darwin":
        plist = launchd_plist_path()
        if plist.is_file():
            r = subprocess_run(["launchctl", "unload", str(plist)], check=False)
            out["launchctl_unload"] = r
            try:
                plist.unlink()
                out["removed_plist"] = str(plist)
            except OSError as exc:
                out["remove_error"] = str(exc)
    out["cron_hint"] = "Remove matching line from crontab -e if installed via cron."
    return out


def schedule_status() -> dict[str, Any]:
    cfg = load_schedule()
    status: dict[str, Any] = {
        "config": cfg,
        "platform": platform.system(),
        "runner_exists": runner_script().is_file(),
        "python": python_bin(),
        "cron_line": cron_line(cfg.get("hour", 9), cfg.get("minute", 0)),
    }
    if platform.system() == "Darwin":
        plist = launchd_plist_path()
        status["plist_path"] = str(plist)
        status["plist_exists"] = plist.is_file()
        r = subprocess_run(["launchctl", "list", LABEL], check=False)
        status["launchctl_list"] = r
    return status


def subprocess_run(cmd: list[str], check: bool = True) -> dict[str, Any]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return {
            "cmd": cmd,
            "returncode": p.returncode,
            "stdout": (p.stdout or "")[:500],
            "stderr": (p.stderr or "")[:500],
        }
    except Exception as exc:  # noqa: BLE001
        return {"cmd": cmd, "returncode": -1, "error": str(exc)}


def run_scheduled_job_once() -> dict[str, Any]:
    """Execute configured scheduled job (watchlist brief by default)."""
    cfg = load_schedule()
    limit = int(cfg.get("limit") or 3)
    kind = cfg.get("kind") or "watchlist_brief"
    log_dir = _data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    started = datetime.now().isoformat(timespec="seconds")
    if kind != "watchlist_brief":
        return {"error": f"unsupported kind: {kind}", "started": started}

    from src.agents.research_agent import build_investment_agent, extract_final_text
    from src.ops.brief import run_brief

    settings = get_settings()
    cache: dict = {}

    def invoke_fn(question: str, mode: str) -> str:
        if mode not in cache:
            cache[mode] = build_investment_agent(settings, mode=mode)  # type: ignore[arg-type]
        result = cache[mode].invoke({"messages": [{"role": "user", "content": question}]})
        return extract_final_text(result)

    out = run_brief(invoke_fn=invoke_fn, limit=limit, save=True)
    out["started"] = started
    out["finished"] = datetime.now().isoformat(timespec="seconds")
    out["kind"] = kind
    # also write run marker
    marker = log_dir / "last_scheduled_run.json"
    marker.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return out
