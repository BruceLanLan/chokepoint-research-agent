# valuation_scaffold (v5.7.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **valuation scaffold**.

## CLI

```bash
python main.py pro valuation_scaffold
python main.py pro valuation_scaffold --action analyze --text "..."
python main.py pro valuation_scaffold --action add --title "..." --text "..." --symbol NVDA
python main.py pro valuation_scaffold --action list --symbol NVDA
```

## API

`POST /pro/valuation_scaffold` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/valuation_scaffold.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
