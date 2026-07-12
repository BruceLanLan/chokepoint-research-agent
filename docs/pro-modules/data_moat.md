# data_moat (v5.50.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **data moat**.

## CLI

```bash
python main.py pro data_moat
python main.py pro data_moat --action analyze --text "..."
python main.py pro data_moat --action add --title "..." --text "..." --symbol NVDA
python main.py pro data_moat --action list --symbol NVDA
```

## API

`POST /pro/data_moat` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/data_moat.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
