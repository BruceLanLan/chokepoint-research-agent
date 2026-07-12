# geo_risk (v5.16.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **geo risk**.

## CLI

```bash
python main.py pro geo_risk
python main.py pro geo_risk --action analyze --text "..."
python main.py pro geo_risk --action add --title "..." --text "..." --symbol NVDA
python main.py pro geo_risk --action list --symbol NVDA
```

## API

`POST /pro/geo_risk` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/geo_risk.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
