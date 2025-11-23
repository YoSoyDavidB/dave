# GitHub Copilot Instructions
# This file helps configure GitHub Copilot's behavior for this project

## Code Style and Standards

### Python Code Style
- Follow PEP 8 conventions
- Maximum line length: 100 characters
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
- Follow clean architecture principles
- Separate concerns: routes, use cases, domain, infrastructure
- Use dependency injection
- Keep business logic separate from framework code

### Common Patterns
```python
# Type hints example
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

# Import ordering
import os  # standard library
from datetime import datetime

import httpx  # third-party
from fastapi import APIRouter

from src.domain.entities import User  # local
```

### AI Agent Guidelines
When generating or modifying code:
1. **Always** run ruff to check for linting errors before considering code complete
2. Follow the existing code structure and patterns in the project
3. Add appropriate type hints to all new functions
4. Include docstrings for public APIs
5. Keep functions focused and single-purpose
6. Use meaningful variable and function names
7. Avoid lines longer than 100 characters
8. Sort imports according to ruff/isort rules
9. Remove unused imports automatically
10. Add tests for new functionality

### Before Committing
- Ensure `make lint` passes without errors
- Ensure `make test` passes
- Verify type hints are complete
- Check that docstrings are present for public APIs
