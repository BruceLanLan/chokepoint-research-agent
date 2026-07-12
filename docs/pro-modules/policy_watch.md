# policy_watch (v5.15.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **policy watch**.

## CLI

```bash
python main.py pro policy_watch
python main.py pro policy_watch --action analyze --text "..."
python main.py pro policy_watch --action add --title "..." --text "..." --symbol NVDA
python main.py pro policy_watch --action list --symbol NVDA
```

## API

`POST /pro/policy_watch` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/policy_watch.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
