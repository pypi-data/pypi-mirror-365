# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the wattmaven-solarnetwork-tools project - a Python library for interacting with the SolarNetwork API. The library is under active development with an unstable API (breaking changes may occur in minor versions).

## Development Commands

All development commands use `make` and `uv` (modern Python package manager):

```bash
# Setup and install dependencies
make install

# Linting and formatting
make lint-check      # Check code with ruff
make lint-fix        # Fix linting issues
make format-check    # Check code formatting
make format-fix      # Fix code formatting
make fix            # Run all fixes (lint + format)

# Testing
make test           # Run all tests with pytest
uv run pytest tests/unit/                    # Run only unit tests
uv run pytest tests/integration/             # Run only integration tests
uv run pytest -k "test_name"                # Run specific test

# Pre-commit checks (run before committing)
make pre-commit-tasks    # Runs lint-check, format-check, and tests

# Cleanup
make clean          # Remove temporary files and virtual environment
```

## Code Architecture

### Main Components

1. **SolarNetworkClient** (`src/wattmaven_solarnetwork_tools/core/solarnetwork_client.py`): 
   - Main client class for API interactions
   - Supports context manager pattern
   - Handles all HTTP methods
   - Optional authentication support
   - Proxy support for SolarQuery caching proxy

2. **Authentication** (`src/wattmaven_solarnetwork_tools/core/authentication.py`):
   - Implements SNWS2-HMAC-SHA256 authentication scheme
   - Handles request signing for secure API access

### Usage Pattern

```python
from wattmaven_solarnetwork_tools.core.solarnetwork_client import (
    SolarNetworkClient,
    SolarNetworkCredentials,
)

# Authenticated usage
with SolarNetworkClient(
    host="data.solarnetwork.net",
    credentials=SolarNetworkCredentials(token="token", secret="secret")
) as client:
    response = client.request("GET", "/solarquery/api/v1/sec/nodes")

# With proxy support (e.g., for SolarQuery caching proxy)
with SolarNetworkClient(
    host="data.solarnetwork.net",
    proxy="query.solarnetwork.net",
    credentials=SolarNetworkCredentials(token="token", secret="secret")
) as client:
    response = client.request("GET", "/solarquery/api/v1/sec/nodes")
```

## Testing Guidelines

- Tests are organized into `tests/unit/` and `tests/integration/`
- Use pytest markers: `@pytest.mark.unit` for unit tests
- Tests use parametrize for multiple scenarios
- Coverage is automatically calculated (target: high coverage for core modules)

## Important Configuration

- **Python Version**: Requires >=3.10
- **Build System**: Hatchling with dynamic versioning from git tags
- **Linting**: Ruff with specific rules for imports (I) and naming (N801-N999)
- **Commit Convention**: Conventional commits enforced by commitizen
- **CI/CD**: GitHub Actions workflows for testing, linting, and releasing

## Release Process

Version bumping and releases use commitizen:

```bash
cz bump --major-version-zero    # Bump version
uv build                        # Build package
uv publish                      # Publish to PyPI
git push && git push -u origin v<version>  # Push changes and tag
```

## Environment Variables

- For running integration tests, see [./.env.example](./.env.example).
- For examples, see each example `.env.example` file.
 