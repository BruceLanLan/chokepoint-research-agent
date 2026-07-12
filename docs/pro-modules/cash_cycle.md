# cash_cycle (v5.24.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **cash cycle**.

## CLI

```bash
python main.py pro cash_cycle
python main.py pro cash_cycle --action analyze --text "..."
python main.py pro cash_cycle --action add --title "..." --text "..." --symbol NVDA
python main.py pro cash_cycle --action list --symbol NVDA
```

## API

`POST /pro/cash_cycle` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/cash_cycle.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
