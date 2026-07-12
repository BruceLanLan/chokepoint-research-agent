# sector_taxonomy (v5.5.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **sector taxonomy**.

## CLI

```bash
python main.py pro sector_taxonomy
python main.py pro sector_taxonomy --action analyze --text "..."
python main.py pro sector_taxonomy --action add --title "..." --text "..." --symbol NVDA
python main.py pro sector_taxonomy --action list --symbol NVDA
```

## API

`POST /pro/sector_taxonomy` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/sector_taxonomy.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
