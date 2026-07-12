# audit_quality (v5.41.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **audit quality**.

## CLI

```bash
python main.py pro audit_quality
python main.py pro audit_quality --action analyze --text "..."
python main.py pro audit_quality --action add --title "..." --text "..." --symbol NVDA
python main.py pro audit_quality --action list --symbol NVDA
```

## API

`POST /pro/audit_quality` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/audit_quality.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
