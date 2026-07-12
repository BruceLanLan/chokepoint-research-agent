# op_leverage (v5.30.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **op leverage**.

## CLI

```bash
python main.py pro op_leverage
python main.py pro op_leverage --action analyze --text "..."
python main.py pro op_leverage --action add --title "..." --text "..." --symbol NVDA
python main.py pro op_leverage --action list --symbol NVDA
```

## API

`POST /pro/op_leverage` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/op_leverage.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
