#!/bin/bash
# Run security checks

set -euo pipefail

# Color codes for output
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

SOURCES="frostbound"

echo -e "${YELLOW}🔒 Running security checks...${NC}"

echo -e "${YELLOW}Running bandit...${NC}"
uv run bandit -r ${SOURCES} -ll

echo -e "${YELLOW}Running safety...${NC}"
uv run safety check --json || true

echo -e "${YELLOW}Running pip-audit...${NC}"
uv run pip-audit || true