# related_party (v5.40.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **related party**.

## CLI

```bash
python main.py pro related_party
python main.py pro related_party --action analyze --text "..."
python main.py pro related_party --action add --title "..." --text "..." --symbol NVDA
python main.py pro related_party --action list --symbol NVDA
```

## API

`POST /pro/related_party` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/related_party.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
