# factor_checklist (v5.6.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **factor checklist**.

## CLI

```bash
python main.py pro factor_checklist
python main.py pro factor_checklist --action analyze --text "..."
python main.py pro factor_checklist --action add --title "..." --text "..." --symbol NVDA
python main.py pro factor_checklist --action list --symbol NVDA
```

## API

`POST /pro/factor_checklist` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/factor_checklist.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
