# Release notes — v2.6 → v3.0.0

Autonomous optimization wave: **cache, post-process pipeline, skill packs, metrics, plugin SDK, CI hardening**.

中文 → [zh/RELEASE_NOTES_3.0.md](./zh/RELEASE_NOTES_3.0.md)

---

## v2.6 — HTTP cache

- Disk cache for expensive public GETs (SEC company tickers, 24h TTL)
- `python main.py clear-cache`

## v2.7 — Memo post-process pipeline

- Auto scorecard SVG + quality/citation metrics on research save path
- `POST /pipeline/postprocess`
- `python main.py metrics` → `data/metrics.jsonl` summary
- `--min-quality` gate on `research`

## v2.8 — Domain skill packs

- `skills/packs/`: semiconductor, robotics, energy_power
- `python main.py skills`
- `python main.py research "..." --skill semiconductor`

## v2.9 — Offline mock eval + CI

- `python main.py mock-eval` (no LLM)
- CI runs mock pipeline + golden `eval`

## v3.0.0 — Plugin SDK + maturity cut

- Documented provider/auth/skill plugin surfaces (`docs/PLUGIN_SDK.md`)
- Example plugin: `plugins/example_provider.py`
- Version **3.0.0**, bilingual docs, full regression suite

---

## Upgrade

```bash
git pull
pip install -r requirements.txt
python main.py doctor
python main.py mock-eval
python main.py skills
python main.py research "CPO 卡点" --skill semiconductor --mode chokepoint_fast
```

**Research only — not investment advice.**
