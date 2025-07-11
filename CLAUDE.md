# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Core Development
```bash
# Run tests
make test

# Run a single test file
uv run pytest tests/test_client.py

# Run with coverage
uv run pytest --cov=postcrawl

# Format code
make format

# Lint and type check
make lint
make typecheck

# Run all checks before commit
make check
```

### Building and Publishing
```bash
# Build distribution packages
make build

# Verify package installation
make verify

# Publish to TestPyPI
make publish-test

# Publish to PyPI
make publish
```

### Type Generation
```bash
# Regenerate types from TypeScript schemas
make generate-types
```

## Architecture Overview

### Package Structure
The SDK follows a clean architecture with clear separation of concerns:

- **`src/postcrawl/client.py`**: Main `PostCrawlClient` implementation with async/sync methods
- **`src/postcrawl/types.py`**: Pydantic models for API requests/responses
- **`src/postcrawl/generated_types.py`**: Auto-generated platform-specific types from TypeScript
- **`src/postcrawl/exceptions.py`**: Custom exception hierarchy for error handling
- **`src/postcrawl/constants.py`**: API configuration constants

### Key Design Patterns

1. **Async-First with Sync Wrappers**: All methods are implemented as async, with `_sync` suffixed synchronous versions that use `asyncio.run()`

2. **Type Safety**: Uses Pydantic v2 for runtime validation and modern Python 3.10+ type hints (lowercase types, union with `|`)

3. **Field Name Conversion**: API uses camelCase, SDK automatically converts to snake_case for Pythonic access

4. **Platform-Specific Types**: Strong typing for `raw` field with `RedditPost | TiktokPost | None`

### Testing Strategy

- **Comprehensive Mock Testing**: Uses pytest-httpx for HTTP mocking
- **Async Testing**: pytest-asyncio for testing async functionality
- **Type Validation**: Dedicated tests for Pydantic models and field conversions
- **Error Scenarios**: Tests for all exception types and retry logic

### API Integration

The SDK integrates with PostCrawl's REST API:
- Base URL: `https://api.postcrawl.com/v1`
- Authentication: Bearer token in Authorization header
- Rate limiting: Tracked via response headers
- Credit system: Different endpoints consume different credit amounts

### Type Generation System

Types are auto-generated from TypeScript schemas:
1. TypeScript schemas define the source of truth (`@packages/extraction-schemas/`)
2. Generation script converts to Pydantic models (`@sdks/typegen/`)
3. Generated file placed at `src/postcrawl/generated_types.py`
4. Manual types in `types.py` extend generated types with SDK-specific functionality