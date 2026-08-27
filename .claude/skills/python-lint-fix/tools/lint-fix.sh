#!/usr/bin/env bash
# lint-fix: environment health check + pre-commit setup guide.
# Lint/format/test are handled automatically by pre-commit on every git commit.
# This script verifies tools are present and pre-commit hooks are installed.
# Reference: https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ISSUES=0

echo -e "${BLUE}=== Environment Health Check ===${NC}"

# ── 1. uv ─────────────────────────────────────────────────────────────────────
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✓ uv found:${NC} $(uv --version)"
else
    echo -e "${RED}✗ uv not found.${NC}"
    echo -e "   Install: ${BLUE}brew install uv${NC} or ${BLUE}curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    ISSUES=$((ISSUES + 1))
fi

# ── 2. pre-commit ─────────────────────────────────────────────────────────────
if command -v uv &> /dev/null && uvx pre-commit --version &> /dev/null; then
    echo -e "${GREEN}✓ pre-commit available via uvx${NC}"
elif command -v pre-commit &> /dev/null; then
    echo -e "${GREEN}✓ pre-commit found:${NC} $(pre-commit --version)"
else
    echo -e "${RED}✗ pre-commit not found.${NC}"
    echo -e "   Install: ${BLUE}uv tool install pre-commit${NC} or ${BLUE}pipx install pre-commit${NC}"
    ISSUES=$((ISSUES + 1))
fi

# ── 3. pre-commit hook installed ──────────────────────────────────────────────
if [ -f ".git/hooks/pre-commit" ]; then
    echo -e "${GREEN}✓ pre-commit git hook is installed${NC}"
else
    echo -e "${YELLOW}⚠️  pre-commit git hook is NOT installed.${NC}"
    echo -e "   Linting will NOT run automatically on commit."
    echo -e "   Fix: ${BLUE}uv run pre-commit install${NC}"
    ISSUES=$((ISSUES + 1))
fi

# ── 4. .pre-commit-config.yaml present ────────────────────────────────────────
if [ -f ".pre-commit-config.yaml" ]; then
    echo -e "${GREEN}✓ .pre-commit-config.yaml found${NC}"
else
    echo -e "${RED}✗ .pre-commit-config.yaml not found.${NC}"
    echo -e "   This project requires a pre-commit config to enforce lint/format."
    ISSUES=$((ISSUES + 1))
fi

# ── 5. markdownlint-cli version ───────────────────────────────────────────────
if command -v markdownlint &> /dev/null; then
    current_version=$(markdownlint --version 2>&1 | head -n 1)
    version_ge() { printf '%s\n%s' "$2" "$1" | sort -V -C; }
    if version_ge "$current_version" "0.45.0"; then
        echo -e "${GREEN}✓ markdownlint-cli ${current_version} (meets 0.45.0+ requirement)${NC}"
    else
        echo -e "${YELLOW}⚠️  markdownlint-cli ${current_version} is too old (need 0.45.0+ for MD060).${NC}"
        echo -e "   Update: ${BLUE}npm install -g markdownlint-cli@latest${NC}"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo -e "${YELLOW}⚠️  markdownlint-cli not found (used by pre-commit hook).${NC}"
    echo -e "   Install: ${BLUE}npm install -g markdownlint-cli@latest${NC}"
    ISSUES=$((ISSUES + 1))
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
if [ "$ISSUES" -eq 0 ]; then
    echo -e "${GREEN}=== Environment ready. pre-commit will lint/format/test on every git commit. ===${NC}"
else
    echo -e "${YELLOW}=== ${ISSUES} issue(s) found. Resolve the above before committing. ===${NC}"
    echo ""
    echo -e "Quick setup:"
    echo -e "  ${BLUE}uv tool install pre-commit${NC}   # install pre-commit"
    echo -e "  ${BLUE}uv run pre-commit install${NC}    # install git hook (once per clone)"
    echo -e "  ${BLUE}uvx pre-commit run --all-files${NC}  # run all hooks manually"
    exit 1
fi
