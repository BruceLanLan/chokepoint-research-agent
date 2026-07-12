# 20-round review / debug / user-sim / fix / iterate log

Product: Chokepoint Research Workstation · Session culminating in **v8.2.0**.

| Round | User simulation | Finding | Fix / feature |
|------:|-----------------|---------|---------------|
| 1 | Smoke API `/`, `/desk`, `/pro/verticals` | Baseline healthy (133 tests) | Establish journey harness |
| 2 | `POST /watchlist` NVDA | Works | — |
| 3 | `POST /theses` without kills | Silent; kill-monitor flags risk | `process_warning` on create |
| 4 | UI template `{"vars":{}}` | **422** body schema wrong | Accept `vars` / `variables` / flat map |
| 5 | Live `POST /research` no Tavily | **500** RuntimeError crash | Soft-fail `web_search`; 503 guidance |
| 6 | Vertical placeholder research | Scaffold OK then live fail | `mock:true` offline path |
| 7 | Empty question | Ambiguous error | 422 with scaffold hint |
| 8 | Vertical-only research | Need empty question + vertical | Scaffold when empty + vertical |
| 9 | SSE stream without keys | Risky live cost | Stream respects `mock` |
| 10 | Desk next actions static text | Not actionable | Clickable vertical / tab links |
| 11 | Watchlist UI | No delete | Row delete button |
| 12 | Thesis UI | No status transitions | Watching / Invalidate / Archive |
| 13 | Plan for “CPO…” | No vertical hint | Auto-suggest + seed from pack |
| 14 | FastAPI startup | Deprecation warning | Lifespan handler |
| 15 | Doctor missing Tavily | Looks “product broken” | `doctor --ops-only` |
| 16 | New-user golden path | Too many commands | `demo-journey` CLI + `POST /demo-journey` |
| 17 | CLI research without keys | Blocked | `research --mock -V …` |
| 18 | UI Research tab | Live by default burns keys | Mock offline checked by default |
| 19 | Vertical dropdown hard-coded | Stale if packs change | Load from `/pro/verticals` |
| 20 | Regression | Need journey suite | `tests/test_v82_journeys.py` + ship |

## Optimization backlog (not all shipped)

1. Split doctor into config-doctor vs ops-doctor scores in one payload  
2. Per-report vertical_id in frontmatter when research uses `--vertical`  
3. Rate-limit friendly mock in OpenAPI examples  
4. E2E Playwright smoke for static UI  
5. Add vertical only when real coverage book demands a 6th pack  

## Golden path after v8.2

```bash
python main.py doctor --ops-only
python main.py desk
python main.py demo-journey -V cpo_optics
python main.py research --mock -V cpo_optics
python main.py pro-suite --vertical cpo_optics --text "…"
python main.py --server   # UI: Desk → Demo journey / Research mock
```

Research only — not investment advice.
