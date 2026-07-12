# filing_alerts (v5.4.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **filing alerts**.

## CLI

```bash
python main.py pro filing_alerts
python main.py pro filing_alerts --action analyze --text "..."
python main.py pro filing_alerts --action add --title "..." --text "..." --symbol NVDA
python main.py pro filing_alerts --action list --symbol NVDA
```

## API

`POST /pro/filing_alerts` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/filing_alerts.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
