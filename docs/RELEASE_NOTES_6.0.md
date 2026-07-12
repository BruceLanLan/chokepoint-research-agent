# Release notes — v6.0.0

**Fifty-version maturity train** (v5.2.0–v5.51.0) + professional workstation expansion.

中文 → [zh/RELEASE_NOTES_6.0.md](./zh/RELEASE_NOTES_6.0.md)

## What shipped

| Area | Count / surface |
|------|-----------------|
| Pro modules | 50 under `src/ops/pro/` |
| Playbooks | 20 under `src/playbooks/` |
| Text metrics | 150 offline heuristics |
| Knowledge maps | +10 |
| Skill packs | +8 |
| Module docs | `docs/pro-modules/` |
| Version catalog | [VERSIONS_5.2_to_5.51.md](./VERSIONS_5.2_to_5.51.md) |

```bash
python main.py pro                 # list 50 modules
python main.py pro risk_matrix --action analyze --text "..."
python main.py pro-suite --text "system chokepoint kill https://x.com"
python main.py playbook saas_infra
python main.py metrics-run --text "..."
```

**Research only — not investment advice.**
