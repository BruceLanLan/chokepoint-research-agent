# event_calendar (v5.2.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **event calendar**.

## CLI

```bash
python main.py pro event_calendar
python main.py pro event_calendar --action analyze --text "..."
python main.py pro event_calendar --action add --title "..." --text "..." --symbol NVDA
python main.py pro event_calendar --action list --symbol NVDA
```

## API

`POST /pro/event_calendar` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/event_calendar.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
