# asp_tracker (v5.28.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **asp tracker**.

## CLI

```bash
python main.py pro asp_tracker
python main.py pro asp_tracker --action analyze --text "..."
python main.py pro asp_tracker --action add --title "..." --text "..." --symbol NVDA
python main.py pro asp_tracker --action list --symbol NVDA
```

## API

`POST /pro/asp_tracker` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/asp_tracker.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
