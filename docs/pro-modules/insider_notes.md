# insider_notes (v5.32.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **insider notes**.

## CLI

```bash
python main.py pro insider_notes
python main.py pro insider_notes --action analyze --text "..."
python main.py pro insider_notes --action add --title "..." --text "..." --symbol NVDA
python main.py pro insider_notes --action list --symbol NVDA
```

## API

`POST /pro/insider_notes` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/insider_notes.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
