# Release notes — v8.0.0

**Professional UI/UX + package hardening**

## Highlights

1. **Workstation UI** — dark professional shell, Desk-first navigation, 12 tabs, EN/ZH language toggle, report row actions (view / checklist / grade / export-pack), SSE research stream, toast feedback.
2. **API package** — `src/api/` with `factory`, `deps`, and domain route modules (`core`, `research`, `coverage`, `reports`, `pro`, `knowledge`, `ops`). Import path remains `src.api:app`.
3. **CLI package** — `src/cli/` Typer groups (`research`, `watch`, `thesis`, `ops`, `pro`, `export`, `core`); `main.py` is a thin entry.
4. **Deep vertical packs** — CPO optics, HBM packaging, power/cooling, robotics actuators, specialty materials: physical nodes, kill criteria, evidence checklists (not keyword stubs).

## Compatibility

- CLI command names unchanged.
- HTTP routes unchanged (106 paths).
- Offline pytest: 121 passed.

## Upgrade

```bash
git pull
pip install -e ".[dev]"
python main.py doctor
python main.py --server   # UI at /
```

Research / education only — not investment advice.
