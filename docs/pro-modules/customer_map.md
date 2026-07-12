# customer_map (v5.17.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **customer map**.

## CLI

```bash
python main.py pro customer_map
python main.py pro customer_map --action analyze --text "..."
python main.py pro customer_map --action add --title "..." --text "..." --symbol NVDA
python main.py pro customer_map --action list --symbol NVDA
```

## API

`POST /pro/customer_map` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/customer_map.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
