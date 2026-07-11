# Professional research workstation (v5)

How this open-source agent maps to a **research ops** workflow (Bloomberg/FactSet *process*, not a data terminal clone).

**中文要点：** 这是投研**流程工作台**（覆盖、论点、证据、杀逻辑、质检、归档），不是行情终端，也**不是投资建议**。

## Analyst loop

| Step | Capability |
|------|------------|
| Frame system | templates, skill packs, `maps --seed`, `plan`, `runbook` |
| Coverage book | `watch`, bulk add, coverage heat |
| Thesis & kills | `thesis`, kill-monitor, thesis-health, hypotheses |
| Research | multi-agent modes, queue (mock default), jobs |
| Evidence | evidence ledger, citations network, filings providers |
| Quality gate | checklist, min-quality, batch-review, quality-board |
| Ops hygiene | digest, workspace-health, weekly-ops, audit, snapshot |
| Archive | export-pack, docx/pdf/html, lineage, tags, FTS index |

## Daily / weekly commands

```bash
python main.py doctor
python main.py workspace-health
python main.py digest
python main.py runbook --system "AI CPO" --md
python main.py weekly-ops
python main.py batch-review
python main.py queue --from-watchlist --limit 5
python main.py queue --run 3          # mock
python main.py checklist <memo.md>
```

## Explicit non-goals

- Brokerage / auto-trade / “buy now”
- Guaranteed alpha or regulatory-grade market data
- Silent live LLM burns (need `--i-accept-live-costs`)

**Research only — not investment advice.**
