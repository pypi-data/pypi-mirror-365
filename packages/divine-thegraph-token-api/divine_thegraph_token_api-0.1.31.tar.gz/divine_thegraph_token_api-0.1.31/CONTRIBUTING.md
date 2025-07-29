# Contributing to divine-thegraph-token-api

## Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/divinescreener/thegraph-token-api.git
cd token-api
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install development dependencies
```bash
pip install -e ".[dev]"
```

### 4. Set up pre-commit hooks
```bash
# Run the setup script
./scripts/setup-hooks.sh

# Or manually:
pre-commit install
```

## Code Style

This project uses automated code formatting and linting:

- **ruff**: For code formatting and linting
- **mypy**: For type checking
- **pre-commit**: Automatically runs formatters before each commit

### Manual formatting
```bash
# Format all files
pre-commit run --all-files

# Or just ruff
ruff format .
ruff check --fix .
```

### Commit hooks
When you commit, pre-commit will automatically:
1. Format your code with `ruff format`
2. Fix linting issues with `ruff check --fix`
3. Remove trailing whitespace
4. Ensure files end with a newline
5. Check YAML/JSON/TOML syntax
6. Run mypy type checking

If any files are modified by the hooks, the commit will fail and you'll need to:
1. Review the changes
2. Stage them with `git add`
3. Commit again

### Bypassing hooks (not recommended)
```bash
git commit --no-verify
```

## Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_evm_api.py

# Run with verbose output
pytest -v
```

## Making Changes

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Ensure tests pass: `pytest`
4. Commit your changes (pre-commit will format automatically)
5. Push and create a pull request

## Code Quality Standards

- Maintain >90% test coverage
- All functions should have type hints
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed
