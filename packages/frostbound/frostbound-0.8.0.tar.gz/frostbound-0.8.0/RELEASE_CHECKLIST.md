# Release Checklist

Use this checklist for every release of Frostbound. Copy this template and check off items as you complete them.

**Release Version**: `_____`  
**Release Date**: `_____`  
**Release Manager**: `_____`

## Pre-Release Verification

### 🔍 Code Quality
- [ ] All CI checks pass: `make ci`
  - [ ] Linting: `make lint`
  - [ ] Type checking: `make typecheck`
  - [ ] Tests: `make test`
  - [ ] Security: `make security`
  - [ ] Coverage > 80%: `make coverage`
- [ ] No unresolved GitHub issues targeted for this release
- [ ] All PRs for this release have been merged

### 📋 Version Management
- [ ] Version updated in `pyproject.toml`
- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)
- [ ] CHANGELOG.md updated with:
  - [ ] Release date
  - [ ] Summary of changes
  - [ ] Breaking changes (if any)
  - [ ] Migration guide (if breaking changes)

### 📚 Documentation
- [ ] README.md reflects any new features
- [ ] API documentation is current
- [ ] All code examples in docs have been tested
- [ ] PUBLISHING.md is up to date

### 🧪 Final Testing
- [ ] Clean install test: `make clean && make install && make test`
- [ ] Import test: `python -c "import frostbound; print(frostbound.__version__)"`
- [ ] Example scripts run successfully
- [ ] Package builds without warnings: `make build-check`

## Release Process

### 📦 Local Release (if not using GitHub Actions)
- [ ] Export PyPI token: `export PYPI_TOKEN="pypi-..."`
- [ ] Run release: `make publish-prod`
- [ ] Verify on PyPI: https://pypi.org/project/frostbound/

### 🚀 GitHub Release
- [ ] Commit all changes: `git add -A && git commit -m "Release version X.Y.Z"`
- [ ] Create git tag: `git tag -a vX.Y.Z -m "Release version X.Y.Z"`
- [ ] Push changes: `git push origin main --tags`
- [ ] Monitor GitHub Actions: Check workflow success
- [ ] Verify GitHub release was created with artifacts

## Post-Release Verification

### ✅ Package Availability
- [ ] Package visible on PyPI: https://pypi.org/project/frostbound/
- [ ] Version number correct on PyPI
- [ ] Package metadata displays correctly
- [ ] Installation works: `uv pip install --no-cache frostbound==X.Y.Z`

### 📊 Installation Testing
Test on clean environments:
- [ ] Python 3.11: `uv run --python 3.11 --with frostbound python -c "import frostbound"`
- [ ] Python 3.12: `uv run --python 3.12 --with frostbound python -c "import frostbound"`
- [ ] Python 3.13: `uv run --python 3.13 --with frostbound python -c "import frostbound"`

### 🔔 Announcements
- [ ] GitHub release notes published
- [ ] Team notified via Slack/Discord/Email
- [ ] Social media announcement (if applicable)
- [ ] Update project roadmap/milestones

## Rollback Plan

If issues are discovered:
1. **Within 72 hours**: Can delete/yank release from PyPI
2. **After 72 hours**: Must release patch version
3. **Emergency contacts**: 
   - PyPI admin: _____
   - GitHub admin: _____

## Notes

_Add any release-specific notes here:_

---

**Sign-off**:  
Released by: _______________  
Date: _______________  
Verified by: _______________