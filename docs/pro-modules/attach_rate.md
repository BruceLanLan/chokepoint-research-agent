# attach_rate (v5.47.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **attach rate**.

## CLI

```bash
python main.py pro attach_rate
python main.py pro attach_rate --action analyze --text "..."
python main.py pro attach_rate --action add --title "..." --text "..." --symbol NVDA
python main.py pro attach_rate --action list --symbol NVDA
```

## API

`POST /pro/attach_rate` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/attach_rate.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
