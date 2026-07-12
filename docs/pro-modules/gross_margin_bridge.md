# gross_margin_bridge (v5.29.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **gross margin bridge**.

## CLI

```bash
python main.py pro gross_margin_bridge
python main.py pro gross_margin_bridge --action analyze --text "..."
python main.py pro gross_margin_bridge --action add --title "..." --text "..." --symbol NVDA
python main.py pro gross_margin_bridge --action list --symbol NVDA
```

## API

`POST /pro/gross_margin_bridge` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/gross_margin_bridge.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
