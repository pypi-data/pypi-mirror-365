#!/bin/bash
# Development environment setup script

set -e

echo "🚀 Setting up Ray Simplify development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install package in development mode
echo "⚙️  Installing package and dependencies..."
uv pip install -e ".[dev]"

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Run initial tests to verify setup
echo "🧪 Running initial tests..."
pytest

echo ""
echo "✅ Setup complete! Your development environment is ready."
echo ""
echo "To activate the virtual environment in future sessions:"
echo "   source .venv/bin/activate"
echo ""
echo "Available commands:"
echo "   make help     - Show all available commands"
echo "   make test     - Run tests"
echo "   make lint     - Run linting and formatting"
echo "   cz commit     - Commit with conventional commits"
echo ""
