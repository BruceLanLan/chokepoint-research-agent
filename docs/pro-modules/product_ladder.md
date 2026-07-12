# product_ladder (v5.46.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **product ladder**.

## CLI

```bash
python main.py pro product_ladder
python main.py pro product_ladder --action analyze --text "..."
python main.py pro product_ladder --action add --title "..." --text "..." --symbol NVDA
python main.py pro product_ladder --action list --symbol NVDA
```

## API

`POST /pro/product_ladder` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/product_ladder.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
