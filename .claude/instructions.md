# Claude AI Instructions for Dave Project

## Code Style and Standards

### Python Code Style
- Follow PEP 8 conventions
- **Maximum line length: 100 characters** (strictly enforced)
- Use type hints for all function parameters and return types
- Use docstrings for all public functions, classes, and modules
- Import sorting: standard library, third-party, local (enforced by ruff)

### Linting Rules
This project uses **Ruff** for linting and formatting with the following rules enabled:
- E: pycodestyle errors
- F: Pyflakes errors
- I: isort (import sorting)
- N: pep8-naming
- W: pycodestyle warnings
- UP: pyupgrade (modern Python syntax)

**Configuration location:** `backend/pyproject.toml`

### Formatting Standards
- Use double quotes for strings
- Indent with 4 spaces (no tabs)
- Add trailing commas in multi-line structures
- Always include final newline in files
- Remove trailing whitespace

### Testing
- Use pytest for all tests
- Aim for high test coverage
- Use async/await patterns for async code
- Mock external dependencies

### Architecture
This project follows **Clean Architecture** principles:
- **routes/** - API endpoints (FastAPI routes)
- **use_cases/** - Application business logic
- **domain/** - Core business entities
- **infrastructure/** - External dependencies (DB, vector store, LLMs)
- **tools/** - Utility functions for agents

### Common Patterns

#### Type Hints
```python
from typing import Any

def process_data(input_data: str, limit: int = 10) -> dict[str, Any]:
    """Process input data and return results.

    Args:
        input_data: The data to process
        limit: Maximum number of results

    Returns:
        Dictionary containing processed results
    """
    pass
```

#### Import Ordering
```python
# Standard library (alphabetically sorted)
import os
from datetime import datetime

# Third-party packages (alphabetically sorted)
import httpx
from fastapi import APIRouter

# Local imports (alphabetically sorted)
from src.domain.entities import User
```

#### Breaking Long Lines
```python
# ❌ BAD - Over 100 characters
result = some_function(parameter1, parameter2, parameter3, parameter4, parameter5, parameter6)

# ✅ GOOD - Split across multiple lines
result = some_function(
    parameter1, parameter2, parameter3, parameter4, parameter5, parameter6
)

# ✅ GOOD - For very long strings
message = (
    "This is a very long message that needs to be split "
    "across multiple lines to stay under 100 characters"
)
```

## AI Agent Workflow

When writing or modifying code, follow these steps:

### 1. Before Writing Code
- Read and understand the existing code structure
- Check similar implementations in the codebase
- Understand the dependency flow (domain → use cases → routes)

### 2. While Writing Code
- Add type hints to ALL functions
- Keep lines under 100 characters
- Use meaningful variable names
- Add docstrings for public functions
- Follow existing patterns in the codebase

### 3. After Writing Code
**ALWAYS run these checks before considering the task complete:**

```bash
# Check for linting errors
make lint

# Auto-fix linting errors if found
make lint-fix

# Run tests
make test
```

### 4. Common Mistakes to Avoid
- ❌ Lines longer than 100 characters
- ❌ Unsorted imports
- ❌ Missing type hints
- ❌ Unused imports
- ❌ Missing final newline in files
- ❌ Trailing whitespace
- ❌ Using single quotes instead of double quotes
- ❌ Missing docstrings for public functions

## Project-Specific Guidelines

### Vector Store Operations
- Use `MemoryRepository` for conversation memories
- Use `DocumentRepository` for vault documents
- Use `UploadedDocumentRepository` for user-uploaded documents
- Always use proper filters with `FieldCondition`

### LLM Interactions
- Use OpenRouter via `src/infrastructure/openrouter.py`
- Structure prompts clearly with system/user messages
- Handle rate limits and errors gracefully
- Log LLM interactions with structlog

### API Routes
- Use proper HTTP status codes
- Validate input with Pydantic schemas
- Handle errors with HTTPException
- Add proper response models
- Include docstrings describing the endpoint

### Database Models
- Defined in `src/core/models.py`
- Use SQLAlchemy ORM
- Include proper relationships
- Use UUID for primary keys

## Commands Reference

```bash
# Linting
make lint          # Check for errors
make lint-fix      # Auto-fix errors
make format        # Format code only

# Testing
make test          # Run all tests

# Development
make dev           # Start dev environment
make install       # Install dependencies
```

## Tools Available

When you need to verify linting or run tests, use these commands:
- `cd backend && poetry run ruff check src tests` - Check linting
- `cd backend && poetry run ruff check --fix src tests` - Fix linting
- `cd backend && poetry run pytest` - Run tests

## Pre-commit Hooks

This project has pre-commit hooks enabled. Before any commit:
- Ruff checks and fixes code
- File endings are normalized
- Trailing whitespace is removed
- YAML/JSON/TOML files are validated

If pre-commit fails, fix the issues before committing.

## Quality Checklist

Before marking any task as complete, verify:
- [ ] Code follows the 100-character line limit
- [ ] Imports are sorted correctly (stdlib, third-party, local)
- [ ] Add type hints where feasible (not required for all functions)
- [ ] Public functions have docstrings
- [ ] No unused imports
- [ ] File ends with a newline
- [ ] No trailing whitespace
- [ ] **`make lint` passes without errors** (ruff + mypy)
- [ ] Tests are written/updated if needed
- [ ] `make test` passes

**Note:** mypy is configured with moderate strictness. Focus on fixing ruff errors first as they are more critical for code quality.

## Additional Notes

- **Prefer `multi_replace_string_in_file`** over multiple `replace_string_in_file` calls for efficiency
- **Always read files before editing** to understand context
- **Follow existing patterns** - don't introduce new patterns without discussion
- **Ask for clarification** if requirements are unclear
- **Test your changes** - don't just assume they work
