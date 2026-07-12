.PHONY: help install check test smoke ui-smoke live-smoke server clean eval

help:
	@echo "Targets:"
	@echo "  make install     - create venv + install deps"
	@echo "  make check       - smoke + ui-smoke + unit tests + eval (offline)"
	@echo "  make smoke       - structure smoke check"
	@echo "  make ui-smoke    - workstation UI smoke (TestClient; no LLM)"
	@echo "  make test        - pytest (offline; live/browser markers skip)"
	@echo "  make eval        - golden structure eval harness"
	@echo "  make live-smoke  - REFUSES unless live env gates set"
	@echo "  make server      - run FastAPI on :8000"
	@echo "  make clean       - remove caches"

install:
	python3.11 -m venv .venv || python3 -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt && pip install -e ".[dev]"
	@echo "Copy .env.example → .env and fill keys"
	@echo "Optional UI browser: pip install -e '.[ui]' && playwright install chromium"

smoke:
	python scripts/smoke_check.py

ui-smoke:
	python scripts/ui_smoke.py

test:
	pytest -q

eval:
	python main.py eval

check: smoke ui-smoke test eval

live-smoke:
	python scripts/live_smoke.py

server:
	python main.py --server

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache **/__pycache__ src/**/__pycache__
	find . -name '*.pyc' -delete 2>/dev/null || true
