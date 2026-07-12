# switching_cost (v5.48.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **switching cost**.

## CLI

```bash
python main.py pro switching_cost
python main.py pro switching_cost --action analyze --text "..."
python main.py pro switching_cost --action add --title "..." --text "..." --symbol NVDA
python main.py pro switching_cost --action list --symbol NVDA
```

## API

`POST /pro/switching_cost` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/switching_cost.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
