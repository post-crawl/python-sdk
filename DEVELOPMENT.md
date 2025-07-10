# PostCrawl Python SDK Development Guide

This guide covers development setup and contribution guidelines for the PostCrawl Python SDK.

## Prerequisites

Install [uv](https://github.com/astral-sh/uv) - a fast Python package manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick Setup

```bash
# Clone the repository
git clone https://github.com/post-crawl/python-sdk.git
cd python-sdk

# Install all dependencies (creates virtual environment automatically)
uv sync

# Run tests to verify setup
make test
```

## Development Workflow

### Makefile Commands

The SDK includes a comprehensive Makefile for common development tasks:

```bash
# Development commands
make dev          # Run development server (if applicable)
make test         # Run all tests
make format       # Format code with black and ruff
make lint         # Run linting checks
make typecheck    # Run mypy type checking
make check        # Run all checks (format, lint, tests)

# Example commands
make examples     # Run all examples
make search       # Run search example
make extract      # Run extract example
make sne          # Run search and extract example

# Build and release
make build        # Build distribution packages
make verify       # Verify package installation
make clean        # Clean build artifacts
make publish-test # Publish to TestPyPI (requires ~/.pypirc)
make publish      # Publish to PyPI (requires ~/.pypirc)

# Type generation
make generate-types # Regenerate types from TypeScript schemas
```

### Running Tests

The SDK includes a comprehensive test suite with 80+ tests covering all functionality:

```bash
# Run all tests
make test

# Run all checks (format, lint, tests)
make check

# Run specific test file
uv run pytest tests/test_client.py

# Run with coverage
uv run pytest --cov=postcrawl
```

**What's tested:**
- Client initialization and configuration
- All API endpoints (search, extract, search_and_extract)
- Async and sync method variants
- Error handling and retries
- Type validation and serialization
- Rate limiting and credit tracking
- Platform-specific types (RedditPost, TiktokPost)
- Field name conversions (camelCase API to snake_case Python)

### Code Quality

```bash
# Format code with black and ruff
make format

# Run linting and type checking
make lint

# Run everything (recommended before commits)
make check
```

### Running Examples

Test the SDK functionality with example scripts:

```bash
make search     # Run search example
make extract    # Run extract example  
make sne        # Run search & extract example
```

## Project Structure

```
python-sdk/
├── src/postcrawl/         # Main package
│   ├── __init__.py        # Package initialization
│   ├── client.py          # PostCrawlClient implementation
│   ├── types.py           # Type definitions and validation
│   ├── generated_types.py # Auto-generated types from TypeScript
│   ├── exceptions.py      # Custom exception classes
│   ├── constants.py       # API constants
│   └── py.typed           # PEP 561 type marker
├── tests/                 # Test suite
│   ├── __init__.py        # Test package initialization
│   ├── conftest.py        # Pytest configuration
│   ├── test_async.py      # Async functionality tests
│   ├── test_client.py     # Client tests
│   ├── test_exceptions.py # Exception tests
│   └── test_types.py      # Type tests
├── examples/              # Usage examples
│   ├── README.md          # Examples documentation
│   ├── extract_101.py     # Basic extraction example
│   ├── search_101.py      # Basic search example
│   ├── search_and_extract_101.py # Combined example
│   ├── .env.example       # Example environment file
│   └── .env               # Your API key (gitignored)
├── DEVELOPMENT.md         # This guide
├── README.md              # Main documentation
├── LICENSE                # MIT License
├── Makefile               # Development commands
├── pyproject.toml         # Package configuration
├── uv.lock                # Dependency lock file
└── verify_package.py      # Package verification script
```

## Managing Dependencies

```bash
# Add a dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Update all dependencies
uv sync --upgrade
```

## Building and Publishing

```bash
# Build distribution packages
make build

# Verify package (builds and tests installation)
make verify

# Publish to TestPyPI for testing
make publish-test

# Publish to PyPI (production)
make publish
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make check` to ensure code quality
5. Submit a pull request

### Guidelines

- Follow existing code style (enforced by black/ruff)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and descriptive
- Use snake_case for all Python attributes (e.g., `image_url`, not `imageUrl`)
- Ensure type annotations are modern Python 3.10+ style (lowercase `list`, `dict`, union with `|`)

## Troubleshooting

### Reset virtual environment
```bash
rm -rf .venv
uv sync
```

### Update lock file
```bash
rm uv.lock
uv sync
```

### Python version issues
```bash
# Check available Python versions
uv python list

# Install specific version
uv python install 3.12
```

## Type System

The SDK uses a sophisticated type generation system:

### Generated Types
- Types are auto-generated from TypeScript schemas in `@packages/extraction-schemas/`
- Generation is handled by `@sdks/typegen/` using `typescript-json-schema` and `datamodel-codegen`
- Generated types are in `src/postcrawl/generated_types.py`
- Uses Pydantic v2 for runtime validation

### Type Features
- **Strong typing** for `raw` field: `RedditPost | TiktokPost | None`
- **Field aliases** for API compatibility (e.g., `imageUrl` → `image_url`)
- **Modern Python syntax**: lowercase types, union with `|`
- **Platform-specific models** with full field definitions

### Regenerating Types
```bash
# From the SDK directory
make generate-types

# Or manually from typegen
cd ../typegen
python generate.py
```

## Tips

- Always use `uv run` to execute commands in the virtual environment
- Run `make check` before committing changes
- Keep dependencies minimal and well-specified
- Test with both async and sync methods
- Use snake_case for attribute access (`post.image_url`, not `post.imageUrl`)
- The API uses camelCase but the SDK automatically converts to snake_case