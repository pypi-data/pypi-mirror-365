# Publishing Guide for Frostbound

This guide covers the complete process for publishing the Frostbound package to PyPI using `uv`, following industry best practices for 2024-2025.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Authentication Methods](#authentication-methods)
- [Local Publishing](#local-publishing)
- [GitHub Actions Publishing](#github-actions-publishing)
- [Version Management](#version-management)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)
- [Pre-Release Checklist](#pre-release-checklist)

## Overview

Frostbound uses [uv](https://docs.astral.sh/uv/) for package management and publishing. This modern tool provides:

- Fast, reliable package building
- Native PyPI publishing support
- Trusted publishing (OIDC) integration
- Comprehensive dependency resolution

## Prerequisites

1. **uv installed**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **PyPI account**: Register at [pypi.org](https://pypi.org)
3. **API token**: Generate at [pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
4. **Git tags**: Ensure your repository uses semantic versioning tags

## Authentication Methods

### 1. API Token (Recommended for Local Publishing)

Generate a PyPI API token:
1. Go to [pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
2. Create a token (prefer project-scoped tokens for security)
3. Store securely (never commit to version control)

### 2. Environment Variables

uv supports multiple environment variables for authentication:

```bash
# Preferred method
export UV_PUBLISH_TOKEN="pypi-YOUR_TOKEN_HERE"

# Alternative (if UV_PUBLISH_TOKEN not set)
export PYPI_TOKEN="pypi-YOUR_TOKEN_HERE"

# Legacy method (not recommended)
export UV_PUBLISH_USERNAME="__token__"
export UV_PUBLISH_PASSWORD="pypi-YOUR_TOKEN_HERE"
```

### 3. Trusted Publishing (GitHub Actions)

Trusted publishing uses OpenID Connect (OIDC) to authenticate directly with PyPI without storing tokens. This is the most secure method for CI/CD.

## Local Publishing

### Quick Publish

Using the Makefile (recommended):

```bash
# Set your PyPI token
export PYPI_TOKEN="pypi-YOUR_TOKEN_HERE"

# Publish to PyPI
make publish-prod
```

### Manual Steps

1. **Ensure all tests pass**:
   ```bash
   make ci
   ```

2. **Build the package**:
   ```bash
   uv build --no-sources
   ```
   
   The `--no-sources` flag is recommended for better compatibility across different systems.

3. **Verify the build**:
   ```bash
   ls -la dist/
   # Should show .whl and .tar.gz files
   ```

4. **Publish to PyPI**:
   ```bash
   # Using environment variable
   UV_PUBLISH_TOKEN="pypi-YOUR_TOKEN_HERE" uv publish
   
   # Or if token is already exported
   uv publish
   ```

### Publishing to TestPyPI

Test your package on TestPyPI before the official release:

```bash
# Set TestPyPI token
export TESTPYPI_TOKEN="pypi-YOUR_TEST_TOKEN_HERE"

# Publish to TestPyPI
make publish-test

# Or manually
uv publish --publish-url https://test.pypi.org/legacy/
```

## GitHub Actions Publishing

### Setup Trusted Publishing

1. **Configure PyPI**:
   - Go to your project on PyPI: `https://pypi.org/project/frostbound/`
   - Navigate to "Settings" → "Publishing"
   - Add a new publisher:
     - Owner: `YOUR_GITHUB_USERNAME`
     - Repository: `frost`
     - Workflow name: `publish.yml`
     - Environment: `pypi` (optional but recommended)

2. **Create GitHub Environment** (optional but recommended):
   - Go to Settings → Environments in your GitHub repo
   - Create a new environment called `pypi`
   - Add protection rules:
     - Required reviewers
     - Restrict to specific branches/tags

### Workflow Configuration

The GitHub Actions workflow (`.github/workflows/publish.yml`) handles:

- Automatic publishing on version tags (e.g., `v1.0.0`)
- Manual publishing via workflow dispatch
- Comprehensive testing before release
- Digital attestations for security

Key features:
- Uses trusted publishing (no token storage)
- Builds once, publishes to multiple indexes
- Generates attestations for supply chain security
- Creates GitHub releases automatically

### Triggering a Release

1. **Automatic Release** (Recommended):
   ```bash
   # Create and push a version tag
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **Manual Release**:
   - Go to Actions → Publish to PyPI
   - Click "Run workflow"
   - Select branch and confirm

## Version Management

### Semantic Versioning

Frostbound follows [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Sources

The version is defined in:
1. `pyproject.toml` - Single source of truth
2. Git tags - Must match pyproject.toml version

### Pre-release Versions

For alpha/beta releases:
```bash
# Alpha release
git tag v1.0.0a1

# Beta release
git tag v1.0.0b1

# Release candidate
git tag v1.0.0rc1
```

## Security Best Practices

### 1. Token Management

**DO**:
- Use project-scoped tokens when possible
- Store tokens in password managers
- Rotate tokens regularly
- Use different tokens for different projects

**DON'T**:
- Commit tokens to version control
- Share tokens between projects
- Use account-wide tokens for automation
- Store tokens in plain text files

### 2. Local Security

For local publishing:
```bash
# Use a .env file (git-ignored)
echo 'PYPI_TOKEN="pypi-YOUR_TOKEN_HERE"' > .env
source .env

# Or use a password manager
export PYPI_TOKEN=$(op read "op://Personal/PyPI/token")
```

### 3. Verification

Always verify published packages:
```bash
# Wait a few minutes after publishing, then:
uv pip install --no-cache frostbound==[VERSION]
python -c "import frostbound; print(frostbound.__version__)"
```

## Troubleshooting

### Common Issues

1. **"Invalid or non-existent authentication"**
   - Verify token starts with `pypi-`
   - Check token isn't expired
   - Ensure token has upload permissions

2. **"Package already exists"**
   - Version already published (can't overwrite)
   - Increment version number
   - Delete the version on PyPI (if within 72 hours)

3. **"No module named 'frostbound'"**
   - Package structure issue
   - Check `pyproject.toml` configuration
   - Verify `__init__.py` exists

4. **Build failures**
   ```bash
   # Clean and rebuild
   make clean
   uv build --no-sources
   ```

5. **Upload timeouts**
   ```bash
   # Retry with explicit timeout
   uv publish --timeout 300
   ```

### Validation Commands

```bash
# Check package metadata
uv build --no-sources
tar -tzf dist/*.tar.gz | head -20

# Test installation in isolated environment
uv run --isolated --with frostbound python -c "import frostbound"

# Verify wheel contents
unzip -l dist/*.whl | head -20
```

## Pre-Release Checklist

Before publishing a new release, ensure:

### Code Quality
- [ ] All tests pass: `make test`
- [ ] Type checking passes: `make typecheck`
- [ ] Linting passes: `make lint`
- [ ] Security scan passes: `make security`
- [ ] Coverage meets threshold: `make coverage`

### Version Management
- [ ] Version bumped in `pyproject.toml`
- [ ] Changelog updated with release notes
- [ ] Git tag matches package version
- [ ] No uncommitted changes

### Documentation
- [ ] README.md is up to date
- [ ] API documentation is current
- [ ] Migration guide (if breaking changes)
- [ ] Example code works

### Final Checks
- [ ] Test on Python 3.11, 3.12, 3.13
- [ ] Verify on macOS, Linux, Windows
- [ ] Check package size is reasonable
- [ ] Dependencies are properly specified

### Release Commands

```bash
# Full release process
git checkout main
git pull origin main
make ci  # Run all checks

# Update version in pyproject.toml
# Update CHANGELOG.md

git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to X.Y.Z"
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin main --tags

# Publishing happens automatically via GitHub Actions
# Or manually:
make publish-prod
```

## Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Python Packaging User Guide](https://packaging.python.org/)