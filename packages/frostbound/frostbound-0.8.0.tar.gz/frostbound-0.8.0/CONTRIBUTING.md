# Contributing to Frostbound

Thank you for your interest in contributing to Frostbound! This guide provides step-by-step instructions to help you contribute effectively.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+ (managed automatically by uv)
- [uv](https://docs.astral.sh/uv/) for fast Python package management
- Git

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/frostbound.git
cd frostbound

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL-OWNER/frostbound.git

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and set up environment
make install-dev
```

**What `make install-dev` does:**

1. Installs all dependencies (including development tools)
2. Sets up pre-commit hooks for code quality
3. Configures your development environment

## 🛠️ Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Follow our coding standards:

- **Line length**: 120 characters
- **String quotes**: Double quotes
- **Imports**: Absolute imports, sorted by groups
- **Type hints**: Required for all functions and variables

### 3. Run Quality Checks

```bash
# Format code automatically
make format

# Check linting and types
make lint
make typecheck

# Run tests
make test

# Run all quality checks at once
make ci
```

### 4. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Examples of good commit messages
feat(auth): add OAuth2 authentication support
fix(parser): handle empty input gracefully  
docs(readme): update installation instructions
test(utils): add unit tests for helper functions
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
# Then create a PR on GitHub
```

## 📋 Available Commands

All commands are organized in our Makefile for consistency:

### Setup Commands

```bash
make install      # Install dependencies only
make install-dev  # Full development setup
```

### Code Quality Commands

```bash
make format       # Auto-format with ruff
make lint         # Check linting with ruff
make typecheck    # Type check with mypy + pyright
make security     # Security scans (bandit, safety, pip-audit)
make pre-commit   # Run all pre-commit hooks
```

### Testing Commands

```bash
make test         # Run tests
make test-fast    # Run tests in parallel  
make coverage     # Tests with coverage report
```

### Utility Commands

```bash
make clean        # Clean all caches and build artifacts
make docs         # Build documentation  
make build        # Build package for distribution
make help         # Show all available commands
```

## 🧪 Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source code structure
- Use descriptive test names
- Aim for 80%+ code coverage

```python
# Example test structure
import pytest
from frostbound.module import MyClass

class TestMyClass:
    """Test cases for MyClass."""

    def test_initialization_with_valid_data(self):
        """Test that MyClass initializes correctly with valid data."""
        obj = MyClass(value=42)
        assert obj.value == 42

    def test_method_raises_on_invalid_input(self):
        """Test that method raises ValueError on invalid input.""" 
        obj = MyClass()
        with pytest.raises(ValueError, match="Invalid input"):
            obj.process("")
```

### Running Tests

```bash
# Basic test run
make test

# With coverage
make coverage

# Note: Multi-version testing is handled by GitHub Actions CI

# Fast parallel execution
make test-fast
```

## 📝 Code Style

### Formatting and Linting

We use **Ruff** for both linting and formatting:

```bash
# Auto-fix most issues
make format

# Check for remaining issues
make lint
```

### Type Annotations

**Required** for all public functions, classes, and variables:

```python
def calculate_sum(numbers: list[int]) -> int:
    """Calculate the sum of a list of numbers.
    
    Args:
        numbers: List of integers to sum.
        
    Returns:
        The sum of all numbers.
        
    Raises:
        ValueError: If the list is empty.
    """
    if not numbers:
        raise ValueError("Cannot sum empty list")
    return sum(numbers)
```

### Docstrings

Use Google-style docstrings with examples:

```python
def parse_config(config_path: str) -> dict[str, Any]:
    """Parse configuration file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        Parsed configuration as a dictionary.
        
    Example:
        >>> config = parse_config("config.yaml")
        >>> print(config["database"]["host"])
        localhost
    """
```

## 🔒 Security

### Security Checks

Run security scans before submitting:

```bash
make security  # Runs bandit, safety, and pip-audit
```

### Best Practices

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all user input
- Keep dependencies updated
- Follow OWASP guidelines

## 🚦 CI/CD Pipeline

Our CI runs the same checks as your local environment:

```bash
make ci  # Runs: format, lint, typecheck, test, coverage, security
```

**Before submitting a PR:**

1. Run `make ci` locally
2. Ensure all checks pass
3. Update documentation if needed
4. Add tests for new features

## 📚 Documentation

### Building Documentation

```bash
# Build docs
make docs

# Serve docs locally at http://localhost:8000
make docs-serve
```

### Documentation Requirements

- Update README.md for new features
- Add docstrings to all public APIs
- Include examples in docstrings
- Update CONTRIBUTING.md for workflow changes

## 🎯 Pull Request Process

### Before Submitting

- [ ] All tests pass (`make test`)
- [ ] Code follows style guidelines (`make lint`)
- [ ] Types are correct (`make typecheck`) 
- [ ] Security checks pass (`make security`)
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated documentation
- [ ] Followed code style guidelines
```

## 🆘 Getting Help

If you need help:

1. Check existing [documentation](README.md)
2. Search through [issues](https://github.com/OWNER/frostbound/issues)
3. Create a new issue with details
4. Join our discussions

## 🎉 Recognition  

All contributors are:

- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in commit messages

Thank you for contributing to Frostbound! 🚀

---

## Quick Reference

| Task | Command |
|------|---------|
| **Setup** | `make install-dev` |
| **Format code** | `make format` |
| **Run tests** | `make test` |
| **Quality checks** | `make ci` |
| **Clean up** | `make clean` |
| **Get help** | `make help` |
