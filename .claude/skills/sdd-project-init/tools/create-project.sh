#!/bin/bash
#
# create-project.sh — SDD project creator
# Called by Claude Code after the interview to generate the project.
#
# Usage:
#   create-project.sh \
#     --name "my-tool" \
#     --purpose "Does X so that Y" \
#     --stack "Python/uv" \
#     --runtime "CLI" \
#     --integrations "Apstra REST API" \
#     --path "/Users/ckim/Projects/my-tool"
#
# --integrations is optional; omit or pass "" to skip
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ── Parse arguments ────────────────────────────────────────────────────────────
PROJECT_NAME=""
PROJECT_PURPOSE=""
LANGUAGE_STACK=""
RUNTIME_TARGET=""
INTEGRATIONS=""
REPO_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)         PROJECT_NAME="$2";    shift 2 ;;
        --purpose)      PROJECT_PURPOSE="$2"; shift 2 ;;
        --stack)        LANGUAGE_STACK="$2";  shift 2 ;;
        --runtime)      RUNTIME_TARGET="$2";  shift 2 ;;
        --integrations) INTEGRATIONS="$2";    shift 2 ;;
        --path)         REPO_PATH="$2";       shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

# ── Validate required args ─────────────────────────────────────────────────────
if [[ -z "$PROJECT_NAME" || -z "$PROJECT_PURPOSE" || -z "$REPO_PATH" ]]; then
    echo -e "${RED}Error: --name, --purpose, and --path are required.${NC}"
    exit 1
fi

# ── Derived values ─────────────────────────────────────────────────────────────
PACKAGE_NAME="${PROJECT_NAME//-/_}"   # my-tool → my_tool
DATE="$(date +%Y-%m-%d)"
TEMPLATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../template" && pwd)"

# Setup hint based on stack
SETUP_HINT="fill in setup commands for ${LANGUAGE_STACK}"
if [[ "$LANGUAGE_STACK" == *"Python"* ]] || [[ "$LANGUAGE_STACK" == *"python"* ]]; then
    SETUP_HINT="uv sync && uv run ${PACKAGE_NAME} --help"
fi

# Integrations line
if [[ -n "$INTEGRATIONS" ]]; then
    INTEGRATIONS_LINE="- **Integrations**: ${INTEGRATIONS}"
else
    INTEGRATIONS_LINE=""
fi

# ── Create project directory ───────────────────────────────────────────────────
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   SDD Project Init                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

if [ -d "$REPO_PATH" ] && [ "$(ls -A "$REPO_PATH" 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  Directory $REPO_PATH already exists and is not empty.${NC}"
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
fi

mkdir -p "$REPO_PATH"
mkdir -p "$REPO_PATH/docs"
mkdir -p "$REPO_PATH/specs/features"

echo -e "${BLUE}📁 Created directory structure${NC}"

# ── Substitution helper ────────────────────────────────────────────────────────
# Escape sed replacement special characters (& and \)
sed_escape() { printf '%s\n' "$1" | sed 's/[&\\/]/\\&/g'; }

substitute() {
    local src="$1"
    local dst="$2"
    sed \
        -e "s|{{PROJECT_NAME}}|$(sed_escape "$PROJECT_NAME")|g" \
        -e "s|{{PROJECT_PURPOSE}}|$(sed_escape "$PROJECT_PURPOSE")|g" \
        -e "s|{{LANGUAGE_STACK}}|$(sed_escape "$LANGUAGE_STACK")|g" \
        -e "s|{{RUNTIME_TARGET}}|$(sed_escape "$RUNTIME_TARGET")|g" \
        -e "s|{{PACKAGE_NAME}}|$(sed_escape "$PACKAGE_NAME")|g" \
        -e "s|{{INTEGRATIONS_LINE}}|$(sed_escape "$INTEGRATIONS_LINE")|g" \
        -e "s|{{SETUP_HINT}}|$(sed_escape "$SETUP_HINT")|g" \
        -e "s|{{DATE}}|$(sed_escape "$DATE")|g" \
        "$src" > "$dst"
}

# ── Copy core files ────────────────────────────────────────────────────────────
echo -e "${BLUE}📝 Generating files...${NC}"

substitute "$TEMPLATE_DIR/AGENTS.md"                        "$REPO_PATH/AGENTS.md"
substitute "$TEMPLATE_DIR/README.md"                        "$REPO_PATH/README.md"
substitute "$TEMPLATE_DIR/specs/requirements.md"            "$REPO_PATH/specs/requirements.md"
substitute "$TEMPLATE_DIR/specs/design.md"                  "$REPO_PATH/specs/design.md"
substitute "$TEMPLATE_DIR/specs/tasks.md"                   "$REPO_PATH/specs/tasks.md"
substitute "$TEMPLATE_DIR/specs/features/_template.md"      "$REPO_PATH/specs/features/_template.md"
substitute "$TEMPLATE_DIR/docs/sdd-how-to-apply.md"         "$REPO_PATH/docs/sdd-how-to-apply.md"
cp         "$TEMPLATE_DIR/.gitignore"                       "$REPO_PATH/.gitignore"
cp         "$TEMPLATE_DIR/.markdownlint.json"              "$REPO_PATH/.markdownlint.json"

echo -e "${GREEN}   ✓ AGENTS.md${NC}"
echo -e "${GREEN}   ✓ README.md${NC}"
echo -e "${GREEN}   ✓ .gitignore${NC}"
echo -e "${GREEN}   ✓ .markdownlint.json${NC}"
echo -e "${GREEN}   ✓ specs/requirements.md${NC}"
echo -e "${GREEN}   ✓ specs/design.md${NC}"
echo -e "${GREEN}   ✓ specs/tasks.md${NC}"
echo -e "${GREEN}   ✓ specs/features/_template.md${NC}"
echo -e "${GREEN}   ✓ docs/sdd-how-to-apply.md${NC}"

# ── Git init ───────────────────────────────────────────────────────────────────
if command -v git &>/dev/null; then
    cd "$REPO_PATH"
    git init -q
    git add .
    git commit -q -m "chore: init SDD project structure"
    echo -e "${GREEN}   ✓ git init + initial commit${NC}"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✓ ${PROJECT_NAME} initialized!${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📦 Location:${NC} $REPO_PATH"
echo ""
echo -e "${BLUE}🚀 Next step:${NC}"
echo -e "   Open ${YELLOW}specs/requirements.md${NC} and describe what you're building."
echo -e "   Then ask Claude: ${YELLOW}\"Help me complete requirements for [first feature]\"${NC}"
echo ""
