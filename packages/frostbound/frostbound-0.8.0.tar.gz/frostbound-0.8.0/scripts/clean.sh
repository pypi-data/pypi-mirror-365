#!/bin/bash
# Clean up build artifacts and caches

set -euo pipefail

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧹 Cleaning Python cache files and directories...${NC}"

# Define patterns to clean
patterns=(
    "__pycache__"
    "*.pyc"
    "*.pyo"
    ".cache"
    ".pytest_cache"
    ".ruff_cache"
    ".mypy_cache"
    ".nox"
    ".tox"
    "htmlcov"
    "coverage.xml"
    ".coverage"
    ".dmypy.json"
    "*.egg-info"
    "build"
    "dist"
    "_build"
    "_static"
)

# Clean each pattern
for pattern in "${patterns[@]}"; do
    echo -e "${YELLOW}Removing ${pattern}...${NC}"
    find . -type d -name "${pattern}" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "${pattern}" -delete 2>/dev/null || true
done

echo -e "${GREEN}✅ Cleanup complete!${NC}"