# Release notes — v0.8 → v0.10 (autonomous pro-workstation cycle)

## Summary

Brought the agent closer to a **professional research workstation** (coverage book, thesis registry, templates, catalog, multi-panel UI, watchlist brief) while keeping **research-only / non-advice** boundaries.

中文见 [zh/RELEASE_NOTES_0.10.md](./zh/RELEASE_NOTES_0.10.md).

## v0.8 — Research operations

- `python main.py doctor` — env/deps/config health
- Watchlist / coverage book (`watch list|add|rm|research`)
- Thesis registry (`thesis list|add|status|redteam`)
- Report catalog with search (`list-reports --q`)
- Builtin research templates under `templates/research/`

## v0.9 — Workstation UI & API

- Multi-panel web UI: Research / Watchlist / Theses / Reports / Templates / Doctor
- REST: `/watchlist`, `/theses`, `/templates`, `/doctor`, enhanced `/reports?q=`
- Template render + fill research flow

## v0.10 — Automation & polish

- `python main.py brief` — batch watchlist digest (`chokepoint_fast`)
- Print-optimized HTML export (browser Print → PDF)
- Expanded tests for ops layer
- Roadmap docs EN/ZH

## Upgrade notes

```bash
git pull
pip install -r requirements.txt
python main.py doctor
python main.py --server
```

Data files live under `data/` (gitignored): `watchlist.json`, `theses.json`, `sessions/`.
