# capex_cycle (v5.25.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **capex cycle**.

## CLI

```bash
python main.py pro capex_cycle
python main.py pro capex_cycle --action analyze --text "..."
python main.py pro capex_cycle --action add --title "..." --text "..." --symbol NVDA
python main.py pro capex_cycle --action list --symbol NVDA
```

## API

`POST /pro/capex_cycle` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/capex_cycle.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
