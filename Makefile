.PHONY: help install check test smoke server clean eval

help:
	@echo "Targets:"
	@echo "  make install  - create venv + install deps"
	@echo "  make check    - smoke + unit tests (no live API required)"
	@echo "  make smoke    - structure smoke check"
	@echo "  make test     - pytest"
	@echo "  make eval     - golden structure eval harness"
	@echo "  make server   - run FastAPI on :8000"
	@echo "  make clean    - remove caches"

install:
	python3.11 -m venv .venv || python3 -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt && pip install -e ".[dev]"
	@echo "Copy .env.example → .env and fill keys"

smoke:
	python scripts/smoke_check.py

test:
	pytest -q

eval:
	python main.py eval

check: smoke test eval

server:
	python main.py --server

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache **/__pycache__ src/**/__pycache__
	find . -name '*.pyc' -delete 2>/dev/null || true
