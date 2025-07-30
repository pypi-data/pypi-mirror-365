# GitHub Copilot Instructions

This file contains instructions for GitHub Copilot to understand the project structure, coding standards, and development practices for this Ray Simplify.

## Project Overview

This is Simplify use of ray, showcasing modern development practices with integrated tooling for code quality, testing, and documentation. The project follows current Python packaging best practices and emphasizes developer experience.

## Project Structure

- **Package Layout**: Uses modern `src/` layout with `src/ray_simplify/` containing the main code
- **Testing**: `tests/` directory with pytest-based unit tests
- **Configuration**: Unified tool configuration in `pyproject.toml`
- **Documentation**: Comprehensive `README.md` with usage examples and development setup
- **Automation**: Pre-commit hooks, Makefile, and setup scripts for developer workflow

## Coding Standards and Practices

### Code Style
- **Formatting**: Use Black with 88-character line length
- **Linting**: Follow Ruff rules for code quality
- **Type Hints**: Always include type hints for function parameters and return values
- **Imports**: Use absolute imports, organize with isort via Ruff

### Documentation Standards
- **Docstring Style**: Use Google-style docstrings for all public functions, classes, and methods
- **Docstring Sections**: Include Args, Returns, Raises, and Examples sections where applicable
- **Examples**: Provide doctest-compatible examples in docstrings
- **Module Documentation**: Include module-level docstrings explaining purpose and contents

### Example Docstring Format:
```python
def example_function(param1: str, param2: int = 0) -> str:
    """Brief description of the function.

    Longer description if needed, explaining the function's purpose,
    behavior, and any important details.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter with default value.

    Returns:
        Description of the return value and its type.

    Raises:
        ValueError: When and why this exception might be raised.

    Examples:
        >>> example_function("hello", 5)
        'Expected output'
        >>> example_function("world")
        'Expected output with default param2'
    """
```

### Testing Standards
- **Test Framework**: Use pytest for all testing
- **Test Structure**: Mirror source structure in `tests/` directory
- **Test Classes**: Group related tests in classes with descriptive names
- **Test Names**: Use descriptive test method names starting with `test_`
- **Coverage**: Aim for high test coverage with meaningful assertions
- **Test Data**: Use fixtures for complex test setup when needed

### Error Handling
- **Exceptions**: Raise appropriate built-in exceptions with clear messages
- **Validation**: Validate input parameters and provide helpful error messages
- **Documentation**: Document all exceptions that functions might raise

### Code Organization
- **Single Responsibility**: Each function/class should have a single, well-defined purpose
- **Imports**: Group imports in standard order (standard library, third-party, local)
- **Constants**: Define constants at module level in UPPER_CASE
- **Private Members**: Use single underscore prefix for internal methods/attributes

## Development Workflow

### Dependencies
- **Package Manager**: Use `uv` for dependency management and virtual environments
- **Development Dependencies**: Include in `[project.optional-dependencies.dev]` section
- **Version Pinning**: Pin development tools to specific versions for consistency

### Code Quality Tools
- **Pre-commit Hooks**: Automatically run formatting, linting, and basic checks
- **Black**: Automatic code formatting
- **Ruff**: Fast linting with auto-fixes where possible
- **pytest**: Test execution with coverage reporting

### Commit Standards
- **Conventional Commits**: Use conventional commit format (feat:, fix:, docs:, etc.)
- **Commitizen**: Use `cz commit` for interactive commit message creation
- **Scope**: Include scope in commits when applicable (e.g., `feat(core): add new feature`)

### Versioning and Releases
- **Semantic Versioning**: Follow semver (MAJOR.MINOR.PATCH)
- **Changelog**: Automatic changelog generation via commitizen
- **Version Management**: Version stored in `src/ray_simplify/__init__.py`

## File-Specific Guidelines

### `src/ray_simplify/__init__.py`
- Export main public API via `__all__`
- Include package metadata (`__version__`, `__author__`, etc.)
- Import key classes/functions for convenient access

### `src/ray_simplify/core.py`
- Contains main package functionality
- All public functions and classes should have comprehensive docstrings
- Include type hints for all parameters and return values
- Handle edge cases and provide clear error messages

### `tests/test_*.py`
- Mirror the structure of source files
- Test both happy path and edge cases
- Include tests for error conditions
- Use descriptive test names that explain what's being tested
- Group related tests in classes

### `pyproject.toml`
- Central configuration for all tools
- Keep tool configurations organized and well-commented
- Maintain consistent formatting and structure

## Code Generation Guidelines

When generating code for this project:

1. **Follow the existing patterns** established in the codebase
2. **Include comprehensive docstrings** with Google style
3. **Add corresponding tests** for any new functionality
4. **Use type hints** consistently throughout
5. **Handle errors gracefully** with appropriate exceptions
6. **Consider edge cases** and document them in tests
7. **Maintain backwards compatibility** when modifying existing code
8. **Update documentation** when adding new features or changing behavior

## Quality Assurance

- **Pre-commit checks**: All code should pass pre-commit hooks before committing
- **Test coverage**: New code should include tests and maintain high coverage
- **Documentation**: New features should be documented in docstrings and README
- **Conventional commits**: Use proper commit message format for automated changelog

## Integration with Build Tools

- **Make commands**: Use Makefile targets for common development tasks
- **CI/CD ready**: Structure supports easy integration with GitHub Actions
- **Automated releases**: Commitizen enables automated versioning and releases
- **Coverage reporting**: Pytest generates coverage reports for CI integration

This project serves as a template demonstrating modern Python development practices. When contributing or extending the codebase, maintain these standards to ensure consistency and quality.
