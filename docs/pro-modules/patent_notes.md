# patent_notes (v5.20.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **patent notes**.

## CLI

```bash
python main.py pro patent_notes
python main.py pro patent_notes --action analyze --text "..."
python main.py pro patent_notes --action add --title "..." --text "..." --symbol NVDA
python main.py pro patent_notes --action list --symbol NVDA
```

## API

`POST /pro/patent_notes` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/patent_notes.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
