#!/bin/bash
# Setup script for pre-commit hooks

echo "🔧 Setting up pre-commit hooks for code formatting..."

# Install pre-commit if in virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✓ Virtual environment detected"
else
    echo "⚠️  No virtual environment detected. It's recommended to use one."
    echo "   Run: python3 -m venv .venv && source .venv/bin/activate"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install dev dependencies
echo "📦 Installing development dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Run against all files for the first time (optional)
echo "🧹 Running formatters on all files..."
pre-commit run --all-files || true

echo "✅ Setup complete!"
echo ""
echo "Now ruff will automatically:"
echo "  - Format your code on every commit"
echo "  - Fix common linting issues"
echo "  - Ensure consistent code style"
echo ""
echo "To manually run formatters: pre-commit run --all-files"
