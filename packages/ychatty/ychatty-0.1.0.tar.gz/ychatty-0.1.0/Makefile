# ychatty Makefile - using uv for all Python operations

.PHONY: help install dev-install test lint format type-check build clean upload upload-test

help:  ## Show this help message
	@echo "ychatty Development Commands (using uv)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "\033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install:  ## Install package dependencies
	uv sync

dev-install:  ## Install package with development dependencies
	uv sync --all-extras

test:  ## Run tests
	uv run pytest

test-cov:  ## Run tests with coverage
	uv run pytest --cov=ychatty --cov-report=html --cov-report=term

lint:  ## Run linting (ruff)
	uv run ruff check src/ tests/

format:  ## Format code (black + ruff)
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

type-check:  ## Run type checking (mypy)
	uv run mypy src/

check: lint type-check test  ## Run all quality checks

build:  ## Build package for distribution
	uv build

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete

upload-test:  ## Upload to TestPyPI
	uv run twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	uv run twine upload dist/*

example:  ## Run the example application
	uv run python example.py

example-help:  ## Show example application help
	uv run python example.py --help

example-list:  ## List functions in example application  
	uv run python example.py list

example-server:  ## Start example application server
	uv run python example.py server