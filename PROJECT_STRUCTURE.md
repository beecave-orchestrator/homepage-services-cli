# Project Structure

This project has been refactored to follow modern Python best practices with a proper package structure, comprehensive testing, and linting configuration.

## Directory Layout

```
homepage-services-cli/
├── homepage_services/          # Core package
│   ├── __init__.py             # Package initialization and exports
│   ├── cli.py                  # Typer CLI commands (root, groups, services)
│   ├── models.py               # Data models (ServiceConfig, Service, Group)
│   └── utils.py                # Utility functions (YAML I/O, validation, icon download)
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Unit tests
│   │   ├── __init__.py
│   │   ├── test_models.py      # Tests for data models
│   │   └── test_utils.py       # Tests for utility functions
│   └── integration/            # Integration tests
│       ├── __init__.py
│       └── test_cli.py         # Tests for CLI commands
├── AGENTS.md                   # Agent guide (coding standards, SOLID principles)
├── TESTING.md                  # Test strategy and manual test results
├── README.md                   # User documentation
├── pyproject.toml              # Project configuration (PDM, Ruff, Pytest)
├── .pre-commit-config.yaml     # Pre-commit hooks
└── LICENSE                     # MIT License
```

## Key Changes

### 1. Package Structure
- Moved `homepage_services.py` → `homepage_services/cli.py`
- Created `models.py` for data structures
- Created `utils.py` for helper functions
- Added proper `__init__.py` for package initialization

### 2. Code Quality
- **Ruff**: Linting and formatting (100 char line length, Google-style docstrings)
- **Pytest**: Comprehensive test suite with fixtures
- **Type hints**: Full type annotations using modern Python syntax
- **Google-style docstrings**: All public functions documented

### 3. Testing
- **Unit tests**: Tests for models and utility functions
- **Integration tests**: Tests for CLI commands
- **Fixtures**: Reusable test data in `conftest.py`
- **Coverage**: Target ≥85% line coverage

### 4. Configuration Files
- **pyproject.toml**: PDM configuration, Ruff rules, Pytest settings
- **AGENTS.md**: Comprehensive agent guide with SOLID principles
- **TESTING.md**: Test strategy and manual test results
- **.pre-commit-config.yaml**: Pre-commit hooks for Ruff

## Development Workflow

### Installation
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Or using PDM
pdm install -G dev
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_models.py

# Run with coverage
pytest --cov=homepage_services --cov-report=term-missing:skip-covered
```

### Linting & Formatting
```bash
# Check and auto-fix
ruff check --fix .

# Format code
ruff format .

# Check only (no changes)
ruff check .
ruff format --check .
```

### CLI Usage
```bash
# Validate configuration
homepage-services validate

# List groups
homepage-services groups list

# Add a service
homepage-services services add \
  --href "http://example.com" \
  --group "Infrastructure" \
  --name "Example Service"
```

## Code Style Guidelines

See `AGENTS.md` for comprehensive guidelines:

1. **Google-style docstrings** with type hints in signatures
2. **PEP 8 compliance** enforced by Ruff
3. **Naming conventions**: `snake_case` for functions, `CapWords` for classes, `UPPER_CASE` for constants
4. **Import ordering**: Standard library → Third-party → First-party
5. **Type annotations**: Use modern syntax (`list[str]`, `dict[str, int]`)
6. **Future annotations**: Always include `from __future__ import annotations`

## SOLID Principles

The codebase follows SOLID design principles:

- **SRP**: Single responsibility per module/function
- **OCP**: Open for extension (CLI options), closed for modification
- **LSP**: Compatible function signatures across the codebase
- **ISP**: Minimal function parameters with optional keyword arguments
- **DIP**: Dependency injection via parameters, not globals

## Next Steps

To fully set up the development environment:

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   # or
   pip3 install -e ".[dev]" --break-system-packages
   ```

3. Run tests to verify setup:
   ```bash
   pytest
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Migration from Old Structure

If you were using the old single-file structure:

1. The old `homepage_services.py` is still present and works
2. New package structure provides better separation of concerns
3. CLI command interface remains unchanged
4. All existing functionality is preserved

See `AGENTS.md` for detailed coding standards and patterns.
