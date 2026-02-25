# AGENTS.md — Homepage Services CLI Agent Guide

This guide documents how to work effectively in the **homepage-services-cli** codebase. It covers setup, architecture, and the required coding rules enforced by Ruff + Pytest. When in doubt, prefer **correctness → clarity → consistency → brevity** (in that order).

## Table of Contents

- [Setup & Commands](#setup--commands)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Architecture & Patterns](#architecture--patterns)
- [Code Style & Patterns](#code-style--patterns)
  - [1) Correctness (Ruff F - Pyflakes)](#1-correctness-ruff-f---pyflakes)
  - [2) PEP 8 surface rules (Ruff E, W - pycodestyle)](#2-pep-8-surface-ruff-e-w---pycodestyle)
  - [3) Naming conventions (Ruff N - pep8-naming)](#3-naming-conventions-ruff-n---pep8-naming)
  - [4) Imports: order & style (Ruff I - isort rules)](#4-imports-order--style-ruff-i---isort-rules)
  - [5) Docstrings — content & style (Ruff D + DOC)](#5-docstrings--content--style-ruff-d--doc)
  - [6) Import hygiene (Ruff TID - flake8-tidy-imports)](#6-import-hygiene-ruff-tid---flake8-tidy-imports)
  - [7) Modern Python upgrades (Ruff UP - pyupgrade)](#7-modern-python-upgrades-ruff-up---pyupgrade)
  - [8) Future annotations (Ruff FA - flake8-future-annotations)](#8-future-annotations-ruff-fa---flake8-future-annotations)
  - [9) Tests & examples (Pytest + Coverage)](#9-tests--examples-pytest--coverage)
  - [10) Commit discipline](#10-commit-discipline)
  - [11) Quick DO / DON'T](#11-quick-do--dont)
  - [12) Pre-commit (recommended)](#12-pre-commit-recommended)
  - [13) CI expectations](#13-ci-expectations)
  - [14) SOLID design principles — Explanation & Integration](#14-solid-design-principles--explanation--integration)
  - [Final note (code style)](#final-note-code-style)
- [Git / PR Workflow](#git--pr-workflow)
- [Boundaries](#boundaries)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

______________________________________________________________________

## Setup & Commands

### Install

**Install with pip:**

```bash
pip install -e ".[dev]"
```

**Or using PDM (recommended):**

```bash
pdm install -G dev
```

### Run / Dev

```bash
homepage-services --help
homepage-services validate
homepage-services groups list
homepage-services services list --group "Infrastructure"
```

### Tests

```bash
# Fast unit tests only
pytest tests/unit/

# Full suite
pytest

# Coverage
pytest --cov=homepage_services --cov-report=term-missing:skip-covered --cov-report=xml
```

### Lint / Format

```bash
ruff check --fix .
ruff format .
```

### Build

```bash
pdm build
```

______________________________________________________________________

## Project Structure

```text
homepage-services-cli/
├── homepage_services/       # Core package (CLI, models, utils)
│   ├── __init__.py
│   ├── cli.py              # Typer CLI entrypoint and command wiring
│   ├── models.py           # Data models and types
│   └── utils.py            # YAML I/O, icon download, validation
├── tests/                  # Unit, integration, and e2e tests
│   ├── conftest.py         # Pytest fixtures
│   ├── unit/               # Unit tests for core logic
│   └── integration/        # Integration tests for CLI commands
├── AGENTS.md               # This guide
├── TESTING.md              # Test strategy and manual test results
├── README.md               # User documentation
├── LICENSE                 # MIT License
└── pyproject.toml          # Dependencies, scripts, Ruff, Pytest config
```

**Key package areas:**

- `homepage_services/cli.py`: Typer CLI entrypoint and command wiring.
- `homepage_services/models.py`: Data models, types, and domain objects.
- `homepage_services/utils.py`: YAML I/O, icon download, validation helpers.

**Path aliases:** None. Use absolute imports from `homepage_services`.

______________________________________________________________________

## Tech Stack

### Core

- Python 3.10+ (runtime and typing target)
- PDM (dependency management and scripts)
- Hatchling (build backend)

### CLI & UX

- Typer for CLI commands and help output
- Rich for progress and formatted output (optional)

### YAML & Data

- ruamel.yaml for YAML parsing with formatting preservation

### Networking

- requests for HTTP icon downloads

### Dev Tooling

- Ruff for linting/formatting
- Pytest + pytest-cov for tests and coverage

______________________________________________________________________

## Architecture & Patterns

The project uses a clean architecture that separates CLI orchestration from domain logic and I/O operations. Key patterns include:

- **Separation of concerns**: CLI layer in `cli.py`, business logic in `utils.py` and `models.py`
- **Path-based configuration**: Default paths can be overridden via CLI options
- **Safe I/O**: Atomic writes with temporary files and automatic backups
- **Validation**: Structure validation for YAML files and PNG icon signatures

### Required approach when extending functionality

When adding features, agents **must follow these principles**:

1. **Respect layer boundaries**

   - Keep `cli.py` as a thin orchestration layer.
   - Put domain logic in `utils.py` (YAML I/O, validation, file operations).
   - Define data structures in `models.py`.

2. **Prefer pure functions**

   - Business logic should be testable without CLI infrastructure.
   - Use dependency injection for file paths and configuration.

3. **Centralize defaults**

   - Default paths and constants are defined at module level.
   - CLI options override defaults without changing global state.

4. **Keep dependencies injectable and testable**

   - Pass file paths as parameters, not globals.
   - Add unit tests for core logic (YAML parsing, validation).
   - Add integration tests for CLI commands.

5. **Make changes coherent with existing architecture docs**

   - Update `README.md` and `TESTING.md` for new features.
   - Add docstrings to all public functions following Google style.

### Extension anti-patterns (must avoid)

- Adding business logic directly in CLI command functions.
- Hard-coding file paths in utility functions.
- Duplicating validation logic across modules.
- Adding I/O operations without proper error handling.

______________________________________________________________________

## Code Style & Patterns

This repository uses **Ruff** as the single source of truth for linting/formatting and **Pytest** (with **pytest-cov**) for tests & coverage. CI fails when these rules are violated.

Run locally before committing:

```bash
# Lint & format (Ruff)
ruff check --fix .
ruff format .

# Tests & coverage
pytest --maxfail=1 -q
pytest --cov=homepage_services --cov-report=term-missing:skip-covered --cov-report=xml
```

When in doubt, prefer **correctness → clarity → consistency → brevity** (in that order).

______________________________________________________________________

## 1) Correctness (Ruff F - Pyflakes)

### What It Enforces — Correctness

- No undefined names/variables.
- No unused imports/variables/arguments.
- No duplicate arguments in function definitions.
- No `import *`.

### Agent Checklist — Correctness

- Remove dead code and unused symbols.
- Keep imports minimal and explicit.
- Use local scopes (comprehensions, context managers) where appropriate.

______________________________________________________________________

### 2) PEP 8 surface rules (Ruff E, W - pycodestyle)

### What It Enforces — PEP 8 Surface

- Spacing/blank-line/indentation hygiene.
- No trailing whitespace.
- Reasonable line breaks; respect the configured line length (100 chars).

### Agent Checklist — PEP 8 Surface

- Let the formatter handle whitespace.
- Break long expressions cleanly (after operators, around commas).
- End files with exactly one trailing newline.

______________________________________________________________________

### 3) Naming conventions (Ruff N - pep8-naming)

### What It Enforces — Naming

- `snake_case` for functions, methods, and non-constant variables.
- `CapWords` (PascalCase) for classes.
- `UPPER_CASE` for module-level constants.
- Exceptions end with `Error` and subclass `Exception`.
- Private/internal functions prefixed with `_`.

### Agent Checklist — Naming

- Avoid camelCase unless mirroring a third-party API.
- Use `_` prefix for private/internal functions.

______________________________________________________________________

### 4) Imports: order & style (Ruff I - isort rules)

### What It Enforces — Imports

- Group imports: 1) Standard library, 2) Third-party, 3) First-party/local.
- Alphabetical within groups; one blank line between groups.
- Prefer one import per line for clarity.

### Agent Checklist — Imports

- Keep imports at module scope (top of file).
- Only alias when it adds clarity (e.g., `import pathlib as Path`).

### Canonical example — Imports

```python
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import typer
from ruamel.yaml import YAML

from homepage_services.models import Service, ServiceConfig
from homepage_services.utils import read_services_file, write_services_file
```

______________________________________________________________________

### 5) Docstrings — content & style (Ruff D + DOC)

Public modules, classes, functions, and methods **must have docstrings**. Ruff enforces **pydocstyle** (`D…`) and **pydoclint** (`DOC…`).

**Single-source style**: **Google-style** docstrings with type hints in signatures.

### Rules of Thumb — Docstrings

- Triple double quotes.
- First line: one-sentence summary, capitalized, ends with a period.
- Blank line after summary, then details.
- Keep `Args/Returns/Raises` in sync with the signature.
- Use imperative mood ("Return…", "Validate…"). Don't repeat obvious types (use type hints).

### Function Template — Docstrings

```python
def add_service(
    href: str,
    group: str,
    name: Optional[str] = None,
    icon: Optional[str] = None,
) -> str:
    """Add a new service to the configuration.

    If no name is provided, it is inferred from the href hostname.

    Args:
        href: Service URL.
        group: Group name to add the service to.
        name: Service display name. Defaults to inferred from href.
        icon: Icon reference (Material Design Icons or local path).

    Returns:
        The service name that was added.

    Raises:
        ValueError: If service name already exists.
        FileNotFoundError: If services.yaml does not exist.
    """
```

### Class Template — Docstrings

```python
class ServicesManager:
    """Manage Homepage services.yaml configuration.

    Provides methods for CRUD operations on groups and services.

    Notes:
        All write operations create automatic .bak backups.
    """
```

______________________________________________________________________

### 6) Import hygiene (Ruff TID - flake8-tidy-imports)

### What It Enforces — Import Hygiene

- Prefer absolute imports over deep relative imports.
- Avoid circular imports; import inside functions only for performance or to break a cycle.
- Avoid broad implicit re-exports; if you re-export, do it explicitly via `__all__`.

### Agent Checklist — Import Hygiene

- Use absolute imports from `homepage_services`.
- Avoid circular dependencies between `cli.py` and `utils.py`.

______________________________________________________________________

### 7) Modern Python upgrades (Ruff UP - pyupgrade)

### What It Prefers — Modernization

- f-strings over `format()` / `%`.
- PEP 585 generics (`list[str]`, `dict[str, int]`) over `typing.List`, `typing.Dict`, etc.
- Context managers where appropriate.
- Remove legacy constructs.

### Agent Checklist — Modernization

- Use `pathlib.Path` for filesystem paths.
- Use assignment expressions (`:=`) sparingly and only when clearer.
- Prefer `is None`/`is not None`.

______________________________________________________________________

### 8) Future annotations (Ruff FA - flake8-future-annotations)

### Guidance — Future Annotations

- Place at the top of every module:

  ```python
  from __future__ import annotations
  ```

This enables postponed evaluation of annotations and is required for Python 3.10+.

______________________________________________________________________

### 9) Tests & examples (Pytest + Coverage)

### Expectations — Tests

- Tests follow the same rules as production code.
- Naming: `test_<unit_under_test>__<expected_behavior>()`.
- Keep tests deterministic; avoid hidden network/filesystem dependencies without fixtures.

### Minimal Example — Tests

```python
def add_service(href: str, group: str, name: str) -> str:
    """Add a new service to the configuration.

    Args:
        href: Service URL.
        group: Group name.
        name: Service name.

    Returns:
        The service name that was added.

    Examples:
        >>> add_service("http://example.com", "Test", "Example")
        'Example'
    """
```

### Running — Tests & Coverage

```bash
# Quick
pytest -q

# Coverage
pytest --cov=homepage_services --cov-report=term-missing:skip-covered --cov-report=xml
```

### Coverage Policy — Threshold

- Guideline: **≥ 85%** line coverage, with critical paths covered.
- Make CI fail below the threshold (see "CI expectations").

______________________________________________________________________

### 10) Commit discipline

### Expectations — Commits

Run Ruff and tests **before** committing. Keep commits small and focused.

Use conventional commit format (see MEMORY.md):
- `feat ✨:` for new features
- `fix 🐛:` for bug fixes
- `docs 📝:` for documentation
- `style 💎:` for code style
- `refactor ♻️:` for refactoring
- `test 🧪:` for tests
- `chore 📦:` for maintenance

______________________________________________________________________

### 11) Quick DO / DON'T

### DO — Practices

- Google-style docstrings that match signatures.
- Absolute imports and sorted import blocks.
- f-strings and modern type syntax (`list[str]`).
- Remove unused code promptly.
- Use Pytest fixtures for reusable setup; prefer `tmp_path` for temp files.

### DON'T — Anti-patterns

- Introduce camelCase (except when mirroring external APIs).
- Use `import *` or deep relative imports.
- Leave parameters undocumented in public functions.
- Add broad `noqa`—always keep ignores narrow and justified.
- Add business logic to CLI command functions.

______________________________________________________________________

### 12) Pre-commit (recommended)

### Configuration — Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9  # keep in sync with pyproject.toml
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

______________________________________________________________________

### 13) CI expectations

### Commands — CI

```bash
# Lint & format
ruff check .
ruff format --check .

# Tests & coverage
pytest --cov=homepage_services --cov-report=term-missing:skip-covered --cov-report=xml --maxfail=1
```

### Policy — CI Coverage

Enforce a minimum coverage threshold (example: 85%). Fail the pipeline if below.

______________________________________________________________________

### 14) SOLID design principles — Explanation & Integration

The **SOLID** principles help you design maintainable, testable, and extensible Python code. This section explains each principle concisely and shows how it maps to our codebase.

### S — Single Responsibility Principle (SRP)

- **Definition**: A module/class should have **one reason to change** (one cohesive responsibility).
- **Pythonic approach**:
  - Keep functions small; factor out I/O, parsing, and domain logic into distinct units.
  - Prefer composition over "god classes".
- **In practice**:
  - `utils.py`: File I/O and YAML operations
  - `models.py`: Data structures and types
  - `cli.py`: CLI orchestration only
- **How we enforce/integrate**:
  - **Docs**: Each function docstring states its single responsibility.
  - **Tests**: Unit tests focus on one behavior per test.
  - **Lint**: Small functions with clear purpose.

### O — Open/Closed Principle (OCP)

- **Definition**: Software entities should be **open for extension, closed for modification**.
- **Pythonic approach**:
  - Rely on configuration over hard-coding.
  - Allow extension via CLI options, not code modification.
- **In practice**:
  - File paths and defaults can be overridden via CLI options.
  - Validation rules are configurable.
- **How we enforce/integrate**:
  - **Docs**: Document CLI options and their defaults.
  - **Tests**: Parametrize tests across different configurations.

### L — Liskov Substitution Principle (LSP)

- **Definition**: Subtypes must be **substitutable** for their base types without breaking expectations.
- **Pythonic approach**:
  - Use duck typing and protocols where appropriate.
  - Keep function signatures compatible (types/return values/raised errors).
- **In practice**:
  - File operations work with any `PathLike` object.
- **How we enforce/integrate**:
  - **Docs**: State behavioral contracts and possible exceptions in docstrings.
  - **Tests**: Run tests with different file paths and configurations.

### I — Interface Segregation Principle (ISP)

- **Definition**: Prefer **small, role-specific interfaces** over fat interfaces.
- **Pythonic approach**:
  - Keep functions with minimal required parameters.
  - Use keyword arguments for optional parameters.
- **In practice**:
  - Functions only require what they need (e.g., `read_services_file` takes a path).
- **How we enforce/integrate**:
  - **Docs**: Clarify the minimal interface needed by a function (in the Args section).
  - **Tests**: Provide minimal test data, not complex fixtures.

### D — Dependency Inversion Principle (DIP)

- **Definition**: High-level modules **depend on abstractions**, not concrete details.
- **Pythonic approach**:
  - Use constructor or function parameters for dependencies.
  - Keep configuration and file paths as parameters, not globals.
- **In practice**:
  - All file operations accept `Path` parameters.
  - CLI options are passed down to utility functions.
- **How we enforce/integrate**:
  - **Docs**: Document file path and configuration parameters.
  - **Tests**: Replace real files with `tmp_path` fixtures.

### SOLID — Minimal example

```python
from pathlib import Path
from typing import List, Dict, Any


def read_services_file(path: Path) -> List[Dict[str, Any]]:
    """Read and parse a services.yaml file.

    Args:
        path: Path to the services.yaml file.

    Returns:
        Parsed YAML data as a list of group dictionaries.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML structure is invalid.
    """
    if not path.exists():
        raise FileNotFoundError(f"Services file not found: {path}")

    yaml = YAML()
    yaml.preserve_quotes = True

    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)

    if data is None:
        return []

    if not isinstance(data, list):
        raise ValueError("YAML must be a list (top-level array of groups).")

    return data
```

### SOLID — Agent Checklist

- **SRP**: One responsibility per function; split I/O from domain logic.
- **OCP**: Use CLI options and parameters for extension, not code modification.
- **LSP**: Keep function behavior compatible; document exceptions.
- **ISP**: Prefer functions with minimal required parameters.
- **DIP**: Pass dependencies as parameters, not globals.

______________________________________________________________________

## Git / PR Workflow

- Run `ruff check --fix .`, `ruff format .`, and relevant pytest suites before opening a PR.
- Keep commits small and focused; follow the conventional commit format.
- For major changes, open an issue or discussion first.

______________________________________________________________________

## Boundaries

### ✅ Always

- Use `pathlib.Path` for all filesystem operations.
- Validate inputs before file I/O to avoid path traversal risks.
- Keep CLI options in sync with README.md and TESTING.md.
- Add or update tests alongside behavior changes; prefer unit tests for core logic.
- Create `.bak` backups before modifying services.yaml.

### ⚠️ Ask First

- Changing default file paths or icons directory.
- Modifying YAML structure validation rules.
- Adding new dependencies to pyproject.toml.

### 🚫 Never

- Hard-code file paths in utility functions.
- Remove safety features (backups, validation).
- Add network dependencies without proper error handling.
- Skip tests without marking as `@pytest.mark.skip`.

______________________________________________________________________

## Common Tasks

### Run a command locally

```bash
homepage-services validate
homepage-services groups list
homepage-services services add --href "http://example.com" --group "Test"
```

### Add a new command

1. Add the command function in `homepage_services/cli.py`.
2. Implement business logic in `homepage_services/utils.py` if needed.
3. Add tests in `tests/unit/` and `tests/integration/`.
4. Update README.md with usage examples.

### Add a new helper function

1. Add the function in `homepage_services/utils.py` or `homepage_services/models.py`.
2. Add Google-style docstring with type hints.
3. Add unit tests in `tests/unit/`.
4. Run `ruff check --fix .` and `pytest`.

### Run a targeted test suite

```bash
pytest tests/unit/test_utils.py::test_read_services_file
pytest tests/integration/test_cli.py::test_validate_command
```

______________________________________________________________________

## Troubleshooting

### Ruff errors

- Fix automatically with `ruff check --fix .`
- Check pyproject.toml for rule configuration
- Use targeted ignores only when necessary with inline comments

### Tests failing

- Check if test fixtures are properly defined in `tests/conftest.py`
- Verify test data files exist in `tests/fixtures/`
- Run with `-v` flag for verbose output: `pytest -v`

### YAML formatting issues

- Ensure ruamel.yaml is configured correctly
- Check that original formatting is preserved after modifications
- Use the backup (.bak) file to compare before/after states

______________________________________________________________________

## Final note (code style)

If you must deviate (e.g., third-party naming or unavoidable import patterns), add a **short comment** explaining why and keep the ignore as narrow as possible.
