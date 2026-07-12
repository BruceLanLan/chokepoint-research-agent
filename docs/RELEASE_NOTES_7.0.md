# Release notes — v7.0.0

**Consolidation sprint** implementing the review plan (Phases 0–3).

## Highlights

- YAML-backed **ProEngine** (50 module IDs, less clone code)
- **Save pipeline**: evidence + audit + auto-tag + thesis links + optional `--pro-suite`
- CLI groups: `ops`, `progrp`, `export`
- Schedule: `--kind weekly_ops|queue_mock|watchlist_brief`
- Remote plugins: `plugins --install <https-manifest>` with `PLUGIN_ALLOW_HOSTS` + sha256
- UI Desk tab + report checklist/grade/pack actions
- Golden evals: 16 · `docs/PROVIDERS.md`

```bash
python main.py doctor
python main.py ops desk --md
python main.py research "…" --skill semiconductor --thesis-id <id> --pro-suite
python main.py progrp verticals
python main.py schedule install --kind weekly_ops --hour 8
```

**Research only — not investment advice.**
