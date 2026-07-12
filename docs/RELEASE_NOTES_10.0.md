# Release notes — v10.0.0

**Research workstation 1.0 milestone** (train v8.7 → v10.0)

Offline-first Chokepoint research ops: vertical coverage, compare packs, golden path, gated live research.

## Train summary

| Ver | Theme |
|-----|--------|
| **8.7** | Compare pack export (md + json) |
| **8.8** | Compare → thesis review trail |
| **8.9** | Vertical coverage dashboard |
| **9.0** | `golden-path` offline ritual |
| **9.1** | Queue enqueue by vertical scaffold |
| **9.2** | Weekly-ops includes vertical coverage |
| **9.3** | Desk surfaces coverage + golden actions |
| **9.4** | `/capabilities` + richer `/about` |
| **9.5** | UI: golden path, coverage, compare export, Alt+hotkeys |
| **10.0** | Milestone cut — docs, tests, product surface freeze for 10.x |

## Golden path (offline)

```bash
python main.py golden-path -V cpo_optics
python main.py vertical-coverage
python main.py compare-vertical cpo_optics --export
python main.py --server
```

API highlights: `/golden-path`, `/verticals/coverage`, `/reports/compare`, `/reports/compare/export`, `/capabilities`.

167 offline tests (+2 skipped opt-in).  
Research / education only — **not investment advice**.
