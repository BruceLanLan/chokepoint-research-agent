# inventory_signal (v5.26.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **inventory signal**.

## CLI

```bash
python main.py pro inventory_signal
python main.py pro inventory_signal --action analyze --text "..."
python main.py pro inventory_signal --action add --title "..." --text "..." --symbol NVDA
python main.py pro inventory_signal --action list --symbol NVDA
```

## API

`POST /pro/inventory_signal` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/inventory_signal.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
