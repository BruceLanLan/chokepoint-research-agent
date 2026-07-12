# consensus_notes (v5.3.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **consensus notes**.

## CLI

```bash
python main.py pro consensus_notes
python main.py pro consensus_notes --action analyze --text "..."
python main.py pro consensus_notes --action add --title "..." --text "..." --symbol NVDA
python main.py pro consensus_notes --action list --symbol NVDA
```

## API

`POST /pro/consensus_notes` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/consensus_notes.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
