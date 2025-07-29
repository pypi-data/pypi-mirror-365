.DEFAULT_GOAL := help

# Read Python version from .python-version file
PYTHON_VERSION := $(shell cat .python-version 2>/dev/null || echo "3.12")
PACKAGE_NAME := frostbound
TEST_DIR := tests
SOURCES := frostbound

# Color codes for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: .uv
.uv:
	@uv -V || echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'

.PHONY: install
install: .uv
	@./scripts/install.sh

.PHONY: install-dev
install-dev: install
	@echo "$(GREEN)🛠️  Setting up development environment...$(NC)"
	@echo "$(GREEN)✅ Development environment ready!$(NC)"

.PHONY: format
format: .uv
	@echo "$(GREEN)🎨 Formatting code...$(NC)"
	uv run ruff check --fix --exit-zero $(SOURCES)
	uv run ruff format $(SOURCES)
	@echo "$(GREEN)✅ Formatting complete!$(NC)"

.PHONY: lint
lint: .uv
	@echo "$(YELLOW)🔍 Running linting checks...$(NC)"
	uv run ruff check $(SOURCES)
	uv run ruff format --check $(SOURCES)

.PHONY: typecheck
typecheck: .uv
	@echo "$(YELLOW)🔍 Running type checks...$(NC)"
	@echo "Running mypy..."
	uv run mypy $(SOURCES)
	@echo "Running pyright..."
	uv run pyright $(SOURCES)

.PHONY: typecheck-strict
typecheck-strict: typecheck
	@echo "$(YELLOW)🔍 Running experimental type checkers...$(NC)"
	@echo "Running ty (experimental)..."
	uv run ty check $(SOURCES) || echo "ty check failed (expected for pre-release)"

.PHONY: test
test: .uv
	@echo "$(GREEN)🧪 Running tests...$(NC)"
	uv run pytest $(TEST_DIR) -xvs

.PHONY: test-fast
test-fast: .uv
	@echo "$(GREEN)⚡ Running tests in parallel...$(NC)"
	uv run pytest $(TEST_DIR) -n auto

.PHONY: coverage
coverage: .uv
	@echo "$(GREEN)📊 Running tests with coverage...$(NC)"
	uv run pytest --cov=frostbound --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=80 $(TEST_DIR)
	@echo "$(GREEN)📊 Coverage report generated in htmlcov/$(NC)"

.PHONY: security
security: .uv
	@./scripts/security.sh

.PHONY: docs
docs: .uv
	@echo "$(GREEN)📚 Building documentation...$(NC)"
	cd docs && uv run make html
	@echo "$(GREEN)📚 Documentation built in docs/_build/html/$(NC)"

.PHONY: docs-serve
docs-serve: docs
	@echo "$(GREEN)🌐 Serving documentation at http://localhost:8000$(NC)"
	cd docs/_build/html && python -m http.server


.PHONY: pre-commit
pre-commit: .uv
	@echo "$(GREEN)🪝 Running pre-commit hooks...$(NC)"
	uv run pre-commit run --all-files

.PHONY: pre-commit-update
pre-commit-update: .uv
	@echo "$(GREEN)🔄 Updating pre-commit hooks...$(NC)"
	uv run pre-commit autoupdate

.PHONY: ci
ci: format lint typecheck test coverage security
	@echo "$(GREEN)✅ All CI checks passed!$(NC)"

.PHONY: all
all: ci
	@echo "$(GREEN)🚀 Complete quality check pipeline finished!$(NC)"

.PHONY: lock
lock: .uv
	@echo "$(GREEN)🔒 Updating lock files...$(NC)"
	uv lock --upgrade

.PHONY: clean
clean:
	@./scripts/clean.sh

.PHONY: build
build: .uv clean
	@echo "$(GREEN)🏗️  Building package...$(NC)"
	uv build --no-sources
	@echo "$(GREEN)✅ Build complete! Artifacts in dist/$(NC)"

.PHONY: publish-test
publish-test: ci build
	@echo "$(GREEN)🚀 Publishing to TestPyPI...$(NC)"
	@if [ -z "$(UV_PUBLISH_TOKEN)" ] && [ -z "$(TESTPYPI_TOKEN)" ]; then \
		echo "$(RED)❌ Error: UV_PUBLISH_TOKEN or TESTPYPI_TOKEN environment variable not set$(NC)"; \
		echo "Get your token from: https://test.pypi.org/account/api-tokens/"; \
		exit 1; \
	fi
	@if [ -n "$(UV_PUBLISH_TOKEN)" ]; then \
		UV_PUBLISH_TOKEN=$(UV_PUBLISH_TOKEN) uv publish --publish-url https://test.pypi.org/legacy/; \
	else \
		uv publish --publish-url https://test.pypi.org/legacy/ --token $(TESTPYPI_TOKEN); \
	fi
	@echo "$(GREEN)✅ Published to TestPyPI successfully!$(NC)"
	@echo "$(YELLOW)📦 Install from TestPyPI with:$(NC)"
	@echo "  uv pip install --index https://test.pypi.org/simple/ $(PACKAGE_NAME)"

.PHONY: publish-prod
publish-prod: build
	@echo "$(GREEN)🚀 Publishing to PyPI...$(NC)"
	@if [ -z "$(UV_PUBLISH_TOKEN)" ] && [ -z "$(PYPI_TOKEN)" ]; then \
		echo "$(RED)❌ Error: UV_PUBLISH_TOKEN or PYPI_TOKEN environment variable not set$(NC)"; \
		echo "Get your token from: https://pypi.org/account/api-tokens/"; \
		exit 1; \
	fi
	@if [ -n "$(UV_PUBLISH_TOKEN)" ]; then \
		UV_PUBLISH_TOKEN=$(UV_PUBLISH_TOKEN) uv publish; \
	else \
		uv publish --token $(PYPI_TOKEN); \
	fi
	@echo "$(GREEN)✅ Published to PyPI successfully!$(NC)"

.PHONY: verify-install
verify-install: .uv
	@echo "$(GREEN)🔍 Verifying package installation...$(NC)"
	uv run --with $(PACKAGE_NAME) --no-project -- python -c "import $(PACKAGE_NAME); print('✅ Package $(PACKAGE_NAME) installed and importable!')"

.PHONY: verify-publish
verify-publish: .uv
	@echo "$(GREEN)🔍 Verifying published package from PyPI...$(NC)"
	@echo "Waiting for package to be available on PyPI..."
	@sleep 30
	uv pip install --no-cache $(PACKAGE_NAME) --python 3.12
	uv run --no-project python -c "import $(PACKAGE_NAME); print(f'✅ $(PACKAGE_NAME) {$(PACKAGE_NAME).__version__} successfully installed from PyPI!')"

.PHONY: build-check
build-check: build
	@echo "$(GREEN)🔍 Checking package metadata...$(NC)"
	uv run python -m twine check --strict dist/*
	@echo "$(GREEN)📦 Package contents:$(NC)"
	@unzip -l dist/*.whl | head -20

.PHONY: version
version:
	@echo "$(GREEN)🏷️  Python version: $(PYTHON_VERSION)$(NC)"
	@echo "$(GREEN)🏷️  Package: $(PACKAGE_NAME)$(NC)"

.PHONY: help
help:
	@echo "$(GREEN)🛠️  Frostbound Development Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)📦 Setup Commands:$(NC)"
	@echo "  $(GREEN)install$(NC)             Install dependencies and pre-commit hooks"
	@echo "  $(GREEN)install-dev$(NC)         Complete development environment setup"
	@echo ""
	@echo "$(YELLOW)🎨 Code Quality Commands:$(NC)"
	@echo "  $(GREEN)format$(NC)              Auto-format code with ruff"
	@echo "  $(GREEN)lint$(NC)                Lint code with ruff"
	@echo "  $(GREEN)typecheck$(NC)           Type check with mypy and pyright"
	@echo "  $(GREEN)typecheck-strict$(NC)    Include experimental type checkers"
	@echo "  $(GREEN)security$(NC)            Run security scans (bandit, safety, pip-audit)"
	@echo "  $(GREEN)pre-commit$(NC)          Run all pre-commit hooks"
	@echo "  $(GREEN)pre-commit-update$(NC)   Update pre-commit hooks to latest versions"
	@echo ""
	@echo "$(YELLOW)🧪 Testing Commands:$(NC)"
	@echo "  $(GREEN)test$(NC)                Run tests with pytest"
	@echo "  $(GREEN)test-fast$(NC)           Run tests in parallel"
	@echo "  $(GREEN)coverage$(NC)            Run tests with coverage reporting"
	@echo ""
	@echo "$(YELLOW)📚 Documentation Commands:$(NC)"
	@echo "  $(GREEN)docs$(NC)                Build documentation"
	@echo "  $(GREEN)docs-serve$(NC)          Build and serve docs at http://localhost:8000"
	@echo ""
	@echo "$(YELLOW)🚀 CI/CD Commands:$(NC)"
	@echo "  $(GREEN)ci$(NC)                  Run full CI pipeline"
	@echo "  $(GREEN)all$(NC)                 Run complete quality checks (ci + all)"
	@echo ""
	@echo "$(YELLOW)📦 Publishing Commands:$(NC)"
	@echo "  $(GREEN)build$(NC)               Build package for distribution"
	@echo "  $(GREEN)build-check$(NC)         Build and validate package metadata"
	@echo "  $(GREEN)publish-test$(NC)        Publish to TestPyPI (requires UV_PUBLISH_TOKEN or TESTPYPI_TOKEN)"
	@echo "  $(GREEN)publish-prod$(NC)        Publish to PyPI (requires UV_PUBLISH_TOKEN or PYPI_TOKEN)"
	@echo "  $(GREEN)verify-install$(NC)      Verify package can be installed locally"
	@echo "  $(GREEN)verify-publish$(NC)      Verify package from PyPI after publishing"
	@echo ""
	@echo "$(YELLOW)🔧 Utility Commands:$(NC)"
	@echo "  $(GREEN)lock$(NC)                Update dependency lock files"
	@echo "  $(GREEN)clean$(NC)               Clean all build artifacts and caches"
	@echo "  $(GREEN)version$(NC)             Show Python and package versions"
	@echo "  $(GREEN)help$(NC)                Show this help message"
	@echo ""
	@echo "$(YELLOW)📝 Current Configuration:$(NC)"
	@echo "  Python Version: $(PYTHON_VERSION)"
	@echo "  Package Name: $(PACKAGE_NAME)"
