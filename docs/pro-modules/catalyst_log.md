# catalyst_log (v5.12.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **catalyst log**.

## CLI

```bash
python main.py pro catalyst_log
python main.py pro catalyst_log --action analyze --text "..."
python main.py pro catalyst_log --action add --title "..." --text "..." --symbol NVDA
python main.py pro catalyst_log --action list --symbol NVDA
```

## API

`POST /pro/catalyst_log` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/catalyst_log.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
