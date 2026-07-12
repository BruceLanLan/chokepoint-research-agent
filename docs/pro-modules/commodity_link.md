# commodity_link (v5.37.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **commodity link**.

## CLI

```bash
python main.py pro commodity_link
python main.py pro commodity_link --action analyze --text "..."
python main.py pro commodity_link --action add --title "..." --text "..." --symbol NVDA
python main.py pro commodity_link --action list --symbol NVDA
```

## API

`POST /pro/commodity_link` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/commodity_link.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
