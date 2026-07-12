# esg_process (v5.38.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **esg process**.

## CLI

```bash
python main.py pro esg_process
python main.py pro esg_process --action analyze --text "..."
python main.py pro esg_process --action add --title "..." --text "..." --symbol NVDA
python main.py pro esg_process --action list --symbol NVDA
```

## API

`POST /pro/esg_process` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/esg_process.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
