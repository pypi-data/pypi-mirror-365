#!/bin/bash
# Install dependencies and pre-commit hooks

set -euo pipefail

# Color codes for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Please install uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo -e "${GREEN}📦 Installing dependencies...${NC}"
uv sync --frozen --group all --all-extras

echo -e "${GREEN}🔧 Installing pre-commit hooks...${NC}"
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

echo -e "${GREEN}✅ Installation complete!${NC}"