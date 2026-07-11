# Release notes — v2.0.0

## Theme

**Mature research agent v2**: real OS scheduling, print-quality PDF, multi-source A-share announcements.

中文 → [zh/RELEASE_NOTES_2.0.md](./zh/RELEASE_NOTES_2.0.md)

---

## 1. Real scheduled tasks

| Command | Meaning |
|---------|---------|
| `python main.py schedule install --hour 9 --minute 0` | macOS **launchd** daily job + always prints **cron** line |
| `python main.py schedule status` | Config + launchctl list / cron hint |
| `python main.py schedule uninstall` | Unload launchd plist |
| `python main.py schedule run` | Run once now (uses model keys) |
| `scripts/run_scheduled_brief.py` | Entry for launchd/cron |

Default job: **watchlist brief** (`chokepoint_fast`, configurable `limit` in `data/schedule.json`).

Logs: `data/logs/scheduled_brief.*.log`, `last_scheduled_run.json`.

API: `GET /schedule/status`, `POST /schedule/install`, `POST /schedule/uninstall`.

---

## 2. Pretty PDF reports

- `fpdf2` generator with CJK system font discovery (PingFang / Noto / YaHei…)
- `python main.py pdf --file reports/xxx.md --title "..."`
- Auto PDF when using export bundle (`--export` / API export)
- `POST /export/pdf`
- Disclaimer banner + print-friendly layout

---

## 3. More A-share announcement sources

Provider `cn_announcements` multi-source:

1. Eastmoney stock announcements (6-digit code)
2. Eastmoney CMS / suggest search
3. Eastmoney news column
4. Sina finance roll headlines

Tools:

- `cn_search_announcements`
- `cn_company_suggest`

---

## 4. v2.0 maturity bar

Includes entire 1.x train (ops workstation, SEC, jobs, analytics) plus scheduling + PDF + CN depth.

### Upgrade

```bash
git pull
pip install -r requirements.txt   # includes fpdf2
python main.py doctor
python main.py schedule status
python main.py schedule install --hour 9 --minute 0
```

### Non-goals

Still **not** investment advice. No brokerage. Kill-criteria culture remains.

---

## macOS launchd notes

```bash
python main.py schedule install --hour 9 --minute 0 --limit 3
launchctl list | grep chokepoint
# logs
tail -f data/logs/scheduled_brief.out.log
```

Ensure `.venv` python path is valid (or set `CHOKEPOINT_PYTHON`).

## Linux cron

```bash
python main.py schedule status   # copy cron_line
crontab -e
```
