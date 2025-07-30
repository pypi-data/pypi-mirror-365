.PHONY: help install test lint format clean docs release

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install package in development mode
	uv pip install -e ".[dev]"

install-hooks: ## Install pre-commit hooks
	pre-commit install
	pre-commit install --hook-type commit-msg

test: ## Run tests
	pytest --maxfail=1 --disable-warnings -v ./tests --override-ini="addopts="


test-cov: ## Run tests with coverage report
	pytest --cov=ray_simplify --cov-report=html --cov-report=term ./tests --override-ini="addopts="

lint: ## Run all linting and formatting checks
	black --check src tests
	ruff check src tests

safety: ## Run safety check for vulnerabilities
	safety check --ignore 65189

format: ## Format code with black and fix ruff issues
	black src tests
	ruff check --fix src tests

clean: ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs: ## Generate documentation (placeholder)
	@echo "Documentation generation not yet configured"

release: ## Create a new release with commitizen
	cz bump --changelog

build: ## Build the package
	python -m build

check: ## Run all checks (lint, safety, test)
	make lint
	make safety
	make test

dev-setup: ## Complete development environment setup
	uv venv
	@echo "Virtual environment created. Activate with:"
	@echo "source .venv/bin/activate"
	@echo "Then run: make install && make install-hooks"
