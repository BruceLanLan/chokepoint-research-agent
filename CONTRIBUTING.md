# Contributing

Thanks for helping improve **Chokepoint Research Agent**.

## Development setup

```bash
git clone https://github.com/BruceLanLan/chokepoint-research-agent.git
cd chokepoint-research-agent

python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
pip install -e ".[dev]"
cp .env.example .env
```

Run structure checks (no API keys required):

```bash
make check
# or
python scripts/smoke_check.py
pytest -q
```

## What to contribute

| Area | Examples |
|------|----------|
| Tools | Better A-share / HK data sources, filing parsers, SEC 10-K helpers |
| Agents | New specialist roles, better prompts, language packs |
| Knowledge | Editable supply-chain YAML maps (CPO, robots, rare earths) |
| UX | Web UI, better streaming, report templates |
| Docs | Tutorials, architecture diagrams, translations |
| Reliability | Tests, eval harness, cost controls |

## Guidelines

1. **No investment recommendations in docs or code comments.** Teach frameworks, not tickers-to-buy.
2. Keep secrets out of git (use `.env`; never commit API keys).
3. Prefer small, focused PRs with a clear description.
4. Match existing style: type hints, complete sentences in docs, Chinese + English where helpful.
5. New tools must have clear `description` strings so the agent knows when to call them.
6. Run `make check` before opening a PR.
7. **Docs:** user-facing changes should update `README.md` and/or `README.zh-CN.md`, plus `docs/zh/` when relevant.

## Chinese documentation

Primary Chinese entry: [`README.zh-CN.md`](README.zh-CN.md)  
Chinese docs index: [`docs/zh/README.md`](docs/zh/README.md)

## Pull request checklist

- [ ] `make check` passes
- [ ] Docs updated if behavior changed
- [ ] No secrets in the diff
- [ ] Disclaimer still accurate for any new “research output” surface

## Code of conduct

Be respectful. No harassment, no spam, no market-manipulation guidance.

## License

By contributing, you agree your contributions are licensed under the MIT License.
