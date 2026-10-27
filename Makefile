.PHONY: install run test coverage clean

install:
	uv sync

run:
	uv run python extract_graphics.py

test:
	uv run pytest

coverage:
	uv run coverage run -m pytest
	uv run coverage report -m

clean:
	rm -rf .venv .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
