# PostCrawl Python SDK Makefile

.PHONY: help install test test-types clean format lint typecheck dev check examples search extract sne build verify publish-test version version-patch version-minor version-major

# Default target - show help
.DEFAULT_GOAL := help

# Show available commands
help:
	@echo "PostCrawl Python SDK - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev          Install all dependencies"
	@echo "  make test         Run all tests"
	@echo "  make format       Format code with black and ruff"
	@echo "  make lint         Run linting checks"
	@echo "  make typecheck    Run mypy type checking"
	@echo "  make check        Run all checks (format, lint, tests)"
	@echo ""
	@echo "Examples:"
	@echo "  make examples     Run all examples"
	@echo "  make search       Run search example"
	@echo "  make extract      Run extract example"
	@echo "  make sne          Run search and extract example"
	@echo ""
	@echo "Build & Release:"
	@echo "  make build        Build distribution packages"
	@echo "  make verify       Verify package installation"
	@echo "  make clean        Clean build artifacts"
	@echo "  make publish-test Publish to TestPyPI"
	@echo "  make publish      Publish to PyPI"
	@echo ""
	@echo "Version Management:"
	@echo "  make version      Show current version"
	@echo "  make version-patch Bump patch version (e.g., 1.0.0 → 1.0.1)"
	@echo "  make version-minor Bump minor version (e.g., 1.0.0 → 1.1.0)"
	@echo "  make version-major Bump major version (e.g., 1.0.0 → 2.0.0)"
	@echo ""
	@echo "Type Generation:"
	@echo "  make generate-types Regenerate types from TypeScript"

# Install dependencies
install:
	uv sync

# Install dev dependencies
dev:
	uv sync

# Run all tests
test:
	uv run pytest tests/ -v

# Run only type tests
test-types:
	uv run pytest tests/test_types.py -v

# Run only client tests
test-client:
	uv run pytest tests/test_client.py -v

# Run tests with coverage
test-coverage:
	uv run pytest tests/ --cov=postcrawl --cov-report=html --cov-report=term

# Format code
format:
	uv run ruff format .
	uv run ruff check --fix .

# Lint code
lint:
	uv run ruff check .

# Type check
typecheck:
	uv run mypy src/postcrawl

# Run all quality checks (format, lint, tests)
check: format lint test

# Clean up
clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Generate types from TypeScript
generate-types:
	cd ../typegen && python generate.py

# Quick test after changes
quick-test: test-types

# Full CI-like check
ci: check

# Run all examples
examples: search extract sne

# Run search example
search:
	cd examples && uv run python search_101.py

# Run extract example
extract:
	cd examples && uv run python extract_101.py

# Run search and extract example
sne:
	cd examples && uv run python search_and_extract_101.py

# Build distribution packages
build: clean
	uv build

# Verify package installation
verify: build
	@echo "Verifying package installation..."
	uv run --with postcrawl --no-project --refresh-package postcrawl -- python -c "import postcrawl; print('✓ Package import successful')"
	uv run --with postcrawl --no-project -- python -c "from postcrawl import PostCrawlClient; print('✓ Client import successful')"

# Publish to TestPyPI
publish-test: build
	@echo "Publishing to TestPyPI..."
	uv publish --index testpypi

# Publish to PyPI (production)
publish: build
	@echo "Publishing to PyPI..."
	uv publish

# Version management commands
version:
	@echo "Current version:"
	@uv version

version-patch:
	uv version --bump patch

version-minor:
	uv version --bump minor

version-major:
	uv version --bump major
