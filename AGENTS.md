# AGENTS.md — Chokepoint Research Agent

Persistent instructions for Grok (and other coding agents) working in this repo.
These apply every session without the user re-stating them.

## Product identity

- **Professional research workstation**, not a chat toy and **not a trading bot**.
- Framework: **Chokepoint Theory** (bottom-up supply-chain reverse engineering).
- **Research / education only — not investment advice.** Never add brokerage, OMS, auto-trade, or “buy/sell now” product surfaces.

## Autonomous operating mode (default when user says “继续 / 自主 / 用额度”)

When the user grants free rein or overnight autonomy:

1. **Do not wait for confirmation** on local, reversible work: edit files, run tests, commit, tag, push `main`, create GitHub Releases for this public repo.
2. Prefer **high-value ops / research-workflow** features over cosmetic churn.
3. After each meaningful batch: **pytest green → version bump → CHANGELOG → bilingual release notes (if ship) → tag → push → `gh release`**.
4. Keep **docs bilingual** (EN + `docs/zh/`) for user-facing CLI/API changes.
5. Update **`docs/AUTONOMOUS_LOG.md`** every ship or when blocked (so the next session can resume without the user).
6. If stuck after repeated failures: write **`docs/BLOCKERS.md`**, pick the next ROADMAP item, continue — do not idle waiting for the user.

### Explicitly allowed (this project)

- `git commit`, annotated tags, `git push origin main`, `git push origin v*`, `gh release create`
- Adding CLI/API/UI features, tests, skills packs, docs under `docs/`
- Refactors that improve clarity without breaking the public CLI

### Explicitly forbidden

- Commit or print **secrets** (`.env`, API keys, tokens). Never put full keys in chat or git.
- `git push --force` to `main` / rewrite published history without an explicit user request
- Destructive mass deletes (`rm -rf` outside the project’s own temp/cache paths)
- Brokerage / order execution / portfolio P&L “advice” products
- **Live LLM research burns** (real `research` / `queue --run --live` / Tavily-heavy demos) unless the user explicitly asks — prefer mock, offline eval, fixtures
- Leaking MiniMax / DeepSeek / gateway keys from local `.env`

## Engineering standards

- Python **≥ 3.11**; use project `.venv` when present: `.venv/bin/python -m pytest`
- Prefer small, focused modules under `src/ops/`, `src/tools/`, `src/providers/`
- Every new capability: **CLI + tests**; API/UI when it is a workstation surface
- Offline tests must stay green; do not require network for `pytest`
- Version is dual-homed: `pyproject.toml` + `src/__init__.py` (`__version__`)
- Public repo: `BruceLanLan/chokepoint-research-agent`

## Commands agents should know

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python main.py doctor
.venv/bin/python main.py mock-eval
.venv/bin/python main.py digest --no-save
.venv/bin/python main.py queue --run 1          # mock, safe
# .venv/bin/python main.py queue --run 1 --live  # costs tokens — only if user asked
```

## Roadmap pointer

- Current product roadmap: `docs/ROADMAP.md` / `docs/zh/ROADMAP.md`
- Next future themes (as of v4.6): remote plugin marketplace, heavier realtime market data — only if they stay research-ops scoped
- Overnight / long-run progress: `docs/AUTONOMOUS_LOG.md`
- One-shot overnight launcher: `scripts/autonomous_overnight.sh`

## Session resume contract

On a **new** session that should continue autonomous work:

1. Read `AGENTS.md`, `docs/AUTONOMOUS_LOG.md`, `docs/ROADMAP.md`, `git log -5`, `git status`
2. Run tests; fix regressions first
3. Pick the next high-value item; implement; ship if batch is complete
4. Append to `docs/AUTONOMOUS_LOG.md`

## Disclaimer (product)

All outputs remain **research only — not investment advice**. Surface that disclaimer on new CLI/API/export paths.
