.PHONY: install run test coverage check fix clean

install:
	uv sync

run:
	uv run python extract_graphics.py

test:
	uv run coverage run -m pytest
	uv run coverage report -m

coverage: test

check:
	uv run ruff check .

fix:
	uv run ruff check --fix .

clean:
	rm -rf .venv .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
