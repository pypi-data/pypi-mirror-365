# Ray Simplify

Simplify use of ray

## Features

- 🏗️ **Modern Project Structure**: `src/` layout for clean package organization
- 📦 **uv Integration**: Fast dependency management and virtual environment handling
- 🔧 **Code Quality Tools**: Pre-configured Black, Ruff, and pre-commit hooks
- 🧪 **Testing Setup**: pytest with coverage reporting and test discovery
- 📝 **Documentation**: Google-style docstrings throughout
- 🔄 **Semantic Versioning**: Commitizen for conventional commits and automated changelog
- ⚡ **Development Automation**: Makefile for common development tasks

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/DINHDUY/ray_simplify
   cd ray_simplify
   ```

2. **Set up development environment:**

   ```bash
   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks:**

   ```bash
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=ray_simplify --cov-report=html

# Run specific test file
pytest tests/test_core.py
```

### Code Quality

```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Run all quality checks
make lint
```

### Making Changes

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Commit using conventional commits:**

   ```bash
   git add .
   cz commit  # Interactive commit message helper
   # or manually: git commit -m "feat: add new feature"
   ```

4. **Push and create a pull request**

### Available Make Commands

```bash
make help          # Show available commands
make install       # Install package in development mode
make test          # Run tests
make lint          # Run all linting and formatting
make clean         # Clean build artifacts
make docs          # Generate documentation (if configured)
make release       # Create a new release with commitizen
```

## Package Usage

```python
from ray_simplify import Calculator, greet

# Simple greeting
message = greet("World")
print(message)  # "Hello, World!"

# Use the calculator
calc = Calculator()
result = calc.add(10, 5)
print(f"10 + 5 = {result}")

# Check calculation history
history = calc.get_history()
print(f"Operations performed: {len(history)}")
```

## Project Structure

```
ray_simplify/
├── .github/
│   └── copilot-instructions.md  # GitHub Copilot development guidelines
├── src/
│   └── ray_simplify/
│       ├── __init__.py          # Package initialization
│       └── core.py              # Core functionality
├── tests/
│   ├── __init__.py
│   └── test_core.py             # Unit tests
├── .pre-commit-config.yaml      # Pre-commit hooks configuration
├── pyproject.toml               # Project configuration and dependencies
├── README.md                    # This file
├── Makefile                     # Development automation
└── CHANGELOG.md                 # Auto-generated changelog
```

## Configuration

All tool configurations are centralized in `pyproject.toml`:

- **Black**: Code formatting (88 character line length)
- **Ruff**: Fast linting with sensible defaults
- **pytest**: Test discovery and coverage reporting
- **Commitizen**: Conventional commits and semantic versioning

## AI-Assisted Development

This project includes GitHub Copilot instructions to help with AI-assisted development:

- **Copilot Instructions**: See `.github/copilot-instructions.md` for detailed guidelines
- **Code Standards**: AI assistance follows project's coding standards and practices
- **Documentation**: Copilot understands the Google-style docstring requirements
- **Testing**: AI can help generate tests following the established patterns

The instructions help ensure consistent code generation that matches the project's architecture and quality standards.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the code style (see `.github/copilot-instructions.md` for details)
4. Add tests for new functionality
5. Commit your changes using conventional commits (`cz commit`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes to this project.
