# Release notes — v5.0.0

**Professional research workstation** maturity cut: health score, runbook, batch review, weekly ops, quote cache.

中文 → [zh/RELEASE_NOTES_5.0.md](./zh/RELEASE_NOTES_5.0.md)

## Why v5

The agent is no longer “a multi-agent memo writer.” It is a **research ops stack**:

coverage → thesis/kills → evidence → quality gate → archive → weekly hygiene.

Still **research only — not investment advice.** Not a Bloomberg data terminal.

## Commands

```bash
python main.py workspace-health
python main.py runbook --system "AI CPO racks" --md
python main.py batch-review
python main.py weekly-ops
python main.py quotes-cache --symbols NVDA,AVGO --summary
python main.py doctor
python main.py digest
```

Guide: [PROFESSIONAL_WORKSTATION.md](./PROFESSIONAL_WORKSTATION.md)

**Research only — not investment advice.**
