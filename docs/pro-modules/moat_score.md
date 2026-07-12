# moat_score (v5.22.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **moat score**.

## CLI

```bash
python main.py pro moat_score
python main.py pro moat_score --action analyze --text "..."
python main.py pro moat_score --action add --title "..." --text "..." --symbol NVDA
python main.py pro moat_score --action list --symbol NVDA
```

## API

`POST /pro/moat_score` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/moat_score.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
