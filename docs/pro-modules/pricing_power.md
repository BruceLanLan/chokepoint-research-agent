# pricing_power (v5.21.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **pricing power**.

## CLI

```bash
python main.py pro pricing_power
python main.py pro pricing_power --action analyze --text "..."
python main.py pro pricing_power --action add --title "..." --text "..." --symbol NVDA
python main.py pro pricing_power --action list --symbol NVDA
```

## API

`POST /pro/pricing_power` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/pricing_power.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
