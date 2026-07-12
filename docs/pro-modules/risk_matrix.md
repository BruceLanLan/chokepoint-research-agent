# risk_matrix (v5.8.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **risk matrix**.

## CLI

```bash
python main.py pro risk_matrix
python main.py pro risk_matrix --action analyze --text "..."
python main.py pro risk_matrix --action add --title "..." --text "..." --symbol NVDA
python main.py pro risk_matrix --action list --symbol NVDA
```

## API

`POST /pro/risk_matrix` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/risk_matrix.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
