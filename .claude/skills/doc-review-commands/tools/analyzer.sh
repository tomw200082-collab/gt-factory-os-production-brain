#!/bin/bash
# Documentation Analyzer Tool
# Used by /ck:doc-review command
# Purpose: Extract documentation analysis logic for reusability and testability

set -e  # Exit on error

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../commands/ck/doc-categories.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Cache configuration
CACHE_DIR="${HOME}/.cache/doc-review"
CACHE_LIFETIME_ANALYSIS=3600      # 1 hour
CACHE_LIFETIME_LINKS=14400         # 4 hours
CACHE_LIFETIME_METRICS=86400       # 24 hours

# ============================================================================
# Function: init_cache
# Purpose: Initialize cache directory
# ============================================================================
init_cache() {
    mkdir -p "$CACHE_DIR" 2>/dev/null || true
}

# ============================================================================
# Function: get_cache_file
# Purpose: Get cache file path for a given cache key
# ============================================================================
get_cache_file() {
    local cache_key="$1"
    echo "$CACHE_DIR/$cache_key.cache"
}

# ============================================================================
# Function: is_cache_valid
# Purpose: Check if cache exists and is still valid (not expired)
# ============================================================================
is_cache_valid() {
    local cache_key="$1"
    local lifetime="${2:-3600}"  # Default to 1 hour
    local cache_file=$(get_cache_file "$cache_key")

    if [ ! -f "$cache_file" ]; then
        return 1  # Cache doesn't exist
    fi

    local file_age=$(($(date +%s) - $(stat -f%m "$cache_file" 2>/dev/null || stat -c%Y "$cache_file" 2>/dev/null || echo 0)))
    if [ "$file_age" -lt "$lifetime" ]; then
        return 0  # Cache is valid
    else
        return 1  # Cache is expired
    fi
}

# ============================================================================
# Function: read_cache
# Purpose: Read and output cache content if valid
# ============================================================================
read_cache() {
    local cache_key="$1"
    local lifetime="${2:-3600}"

    if is_cache_valid "$cache_key" "$lifetime"; then
        cat "$(get_cache_file "$cache_key")"
        return 0
    fi
    return 1
}

# ============================================================================
# Function: write_cache
# Purpose: Write content to cache file
# ============================================================================
write_cache() {
    local cache_key="$1"
    local cache_file=$(get_cache_file "$cache_key")

    cat > "$cache_file" 2>/dev/null || true
}

# ============================================================================
# Function: clear_cache
# Purpose: Clear cache for a specific key or all caches
# ============================================================================
clear_cache() {
    local cache_key="${1:-all}"

    if [ "$cache_key" = "all" ]; then
        rm -rf "$CACHE_DIR" 2>/dev/null || true
        mkdir -p "$CACHE_DIR" 2>/dev/null || true
        echo -e "${GREEN}✅ Cache cleared${NC}"
    else
        rm -f "$(get_cache_file "$cache_key")" 2>/dev/null || true
        echo -e "${GREEN}✅ Cache cleared for: $cache_key${NC}"
    fi
}

# ============================================================================
# Function: check_and_install_linting_tools
# Purpose: Check if markdownlint and prettier are installed, install if needed
# ============================================================================
check_and_install_linting_tools() {
    echo "=== 🔧 Linting Tools Setup ==="
    echo ""

    local need_install=false

    # Check markdownlint
    if ! command -v markdownlint &> /dev/null; then
        echo -e "${YELLOW}⚠️  markdownlint not found${NC}"
        need_install=true
    else
        echo -e "${GREEN}✅ markdownlint${NC} - $(markdownlint --version 2>/dev/null || echo 'available')"
    fi

    # Check prettier
    if ! command -v prettier &> /dev/null; then
        echo -e "${YELLOW}⚠️  prettier not found${NC}"
        need_install=true
    else
        echo -e "${GREEN}✅ prettier${NC} - $(prettier --version 2>/dev/null || echo 'available')"
    fi

    if [ "$need_install" = true ]; then
        echo ""
        echo -e "${BLUE}📦 Installing missing tools...${NC}"
        npm install -g markdownlint-cli prettier 2>/dev/null || {
            echo -e "${RED}❌ Failed to install tools. Please install manually:${NC}"
            echo "   npm install -g markdownlint-cli prettier"
            return 1
        }
        echo -e "${GREEN}✅ Tools installed successfully${NC}"
    fi

    echo ""
}

# ============================================================================
# Function: run_markdown_linting
# Purpose: Run markdownlint and prettier to auto-fix markdown files
# ============================================================================
run_markdown_linting() {
    echo "=== 🎨 Markdown Linting & Auto-Fix ==="
    echo ""

    local md_files=$(find . -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

    if [ "$md_files" -eq 0 ]; then
        echo "No markdown files found"
        return 0
    fi

    echo "Processing $md_files markdown files..."
    echo ""

    # Run markdownlint with auto-fix
    echo -e "${BLUE}Running markdownlint --fix...${NC}"
    markdownlint --fix . --ignore node_modules --ignore '.git' 2>/dev/null || true
    echo -e "${GREEN}✅ markdownlint complete${NC}"
    echo ""

    # Run prettier
    echo -e "${BLUE}Running prettier...${NC}"
    prettier --write "**/*.md" 2>/dev/null || true
    echo -e "${GREEN}✅ prettier complete${NC}"
    echo ""

    # Show changed files
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local changed=$(git diff --name-only 2>/dev/null | grep "\.md$" | wc -l)
        if [ "$changed" -gt 0 ]; then
            echo "📝 Modified files:"
            git diff --name-only 2>/dev/null | grep "\.md$" | sed 's/^/   /'
            echo ""
        fi
    fi
}

# ============================================================================
# Function: analyze_principles
# Purpose: Extract and validate project-specific documentation principles
# ============================================================================
analyze_principles() {
    echo "=== 📋 Project Documentation Principles Analysis ==="
    echo ""

    local principles_found=0
    local conflicts=0

    # Extract key documentation design claims
    echo "🔍 Searching for documentation philosophy..."
    if grep -i "no.*config.*files\|zero.*setup\|interactive.*config\|self.*contained\|minimal.*docs\|single.*file\|documentation.*philosophy" README.md CLAUDE.md *.md 2>/dev/null; then
        principles_found=$((principles_found + 1))
        echo ""
    else
        echo "   No specific documentation philosophy found"
        echo ""
    fi

    # Check for explicit documentation structure preferences
    echo "🔍 Checking documentation structure preferences..."
    if grep -i "directory.*structure\|file.*organization\|docs.*folder\|keep.*root\|avoid.*dirs" README.md CLAUDE.md *.md 2>/dev/null; then
        principles_found=$((principles_found + 1))
        echo ""
    else
        echo "   No explicit structure preferences found"
        echo ""
    fi

    # Look for configuration philosophy
    echo "🔍 Analyzing configuration approach..."
    if grep -i "no.*env\|environment.*files\|configuration.*approach\|setup.*method" README.md CLAUDE.md *.md 2>/dev/null; then
        principles_found=$((principles_found + 1))
        echo ""
    else
        echo "   No specific configuration philosophy found"
        echo ""
    fi

    # Summary
    echo "📊 Summary:"
    echo "   Principles detected: $principles_found"
    echo "   Conflicts detected: $conflicts"

    if [ $principles_found -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Project has specific documentation principles${NC}"
        echo "   Ensure updates respect these principles"
    else
        echo ""
        echo -e "${GREEN}✅ No specific documentation constraints detected${NC}"
        echo "   Standard documentation updates can proceed"
    fi
}

# ============================================================================
# Function: analyze_structure
# Purpose: Analyze current documentation structure and identify issues
# ============================================================================
analyze_structure() {
    echo "=== 📁 Documentation Structure Analysis ==="
    echo ""

    # Check if config file exists
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}❌ Config file not found: $CONFIG_FILE${NC}"
        return 1
    fi

    # Count documentation files
    local total_md=$(find . -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local root_md=$(find . -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local sdd_files=$(find ./specs -name "spec.md" -o -name "plan.md" -o -name "tasks.md" 2>/dev/null | wc -l | tr -d ' ')

    echo "📊 Inventory:"
    echo "   Total .md files: $total_md"
    echo "   Root .md files: $root_md"
    echo "   SDD artifacts: $sdd_files"
    echo ""

    # Discover SDD artifacts
    if [ $sdd_files -gt 0 ]; then
        echo "📋 SDD Artifacts Found:"
        find ./specs -type f \( -name "spec.md" -o -name "plan.md" -o -name "tasks.md" \) 2>/dev/null | while read file; do
            echo "   $file"
        done
        echo ""
    fi

    # Find potential misplaced files in root
    echo "🔍 Root Directory Analysis:"
    local misplaced=$(find . -maxdepth 1 -name "*.md" | grep -E "(EXAMPLES?|GUIDE|TUTORIAL|REFERENCE|API|SPEC|MANUAL)" 2>/dev/null || true)
    if [ -n "$misplaced" ]; then
        echo -e "${YELLOW}⚠️  Potential candidates for docs/ organization:${NC}"
        echo "$misplaced" | while read file; do
            echo "   $file"
        done
    else
        echo "   ✅ No obviously misplaced files detected"
    fi
    echo ""

    # Check file sizes
    echo "📄 Large Documentation Files (>200 lines):"
    find . -maxdepth 1 -name "*.md" -exec wc -l {} \; 2>/dev/null | sort -nr | head -5 | while read lines file; do
        if [ "$lines" -gt 200 ]; then
            echo "   $file: $lines lines"
        fi
    done
    echo ""
}

# ============================================================================
# Function: categorize_files
# Purpose: Categorize documentation files by content type
# ============================================================================
categorize_files() {
    echo "=== 🏷️  Documentation File Categorization ==="
    echo ""

    # Check if config file exists
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}❌ Config file not found: $CONFIG_FILE${NC}"
        return 1
    fi

    # Get essential files list from config (simplified - just hardcode for now)
    local essential_files=("README.md" "CLAUDE.md" "GEMINI.md" "CHANGELOG.md" "CONTRIBUTING.md" "LICENSE.md")

    for file in *.md; do
        [ ! -f "$file" ] && continue

        # Check if essential root file
        local is_essential=false
        for essential in "${essential_files[@]}"; do
            if [ "$file" = "$essential" ]; then
                is_essential=true
                break
            fi
        done

        if [ "$is_essential" = true ]; then
            echo -e "${GREEN}✅ $file${NC} - Keep at root (essential)"
            continue
        fi

        # Analyze content patterns
        local category=""
        local keywords=""

        if grep -q "## API\|### Endpoints\|Request/Response\|curl.*http\|POST\|GET\|PUT" "$file" 2>/dev/null; then
            category="developer"
            keywords="API documentation"
        elif grep -q "## Installation\|### Setup\|Getting Started\|Quick Start\|## Usage\|### Examples" "$file" 2>/dev/null; then
            category="user"
            keywords="User guide"
        elif grep -q "## Architecture\|### Design\|Technical.*Spec\|## Security\|Performance\|Requirements" "$file" 2>/dev/null; then
            category="technical"
            keywords="Technical specification"
        elif grep -q "AI\|Claude\|Gemini\|Assistant\|Tool.*Usage\|Prompt" "$file" 2>/dev/null; then
            category="ai-agents"
            keywords="AI integration"
        fi

        if [ -n "$category" ]; then
            echo -e "${BLUE}📁 $file${NC} → docs/$category/ ($keywords)"
        else
            echo -e "${YELLOW}❓ $file${NC} - Manual review needed"
        fi
    done
    echo ""
}

# ============================================================================
# Function: analyze_impact
# Purpose: Determine documentation impact from recent code changes
# ============================================================================
analyze_impact() {
    echo "=== 🎯 Change Impact Analysis ==="
    echo ""

    # Get recent changes
    echo "📝 Recent Changes (last 5 commits):"
    local changed_files=$(git diff --name-only HEAD~5..HEAD 2>/dev/null || git diff --name-only HEAD~3..HEAD 2>/dev/null || git diff --name-only HEAD~1..HEAD 2>/dev/null || echo "")

    if [ -z "$changed_files" ]; then
        echo "   No recent commits to analyze"
        echo ""
        return 0
    fi

    echo "$changed_files" | while read file; do
        echo "   Changed: $file"
    done
    echo ""

    # Analyze impact areas
    local needs_readme=false
    local needs_claude=false
    local needs_sdd=false
    local needs_api=false

    echo "📊 Impact Assessment:"

    # Check if source code changed
    if echo "$changed_files" | grep -q "\.py$\|\.js$\|\.ts$\|\.go$\|\.rs$" 2>/dev/null; then
        echo "   ⚠️  Source code changed → Update README, CLAUDE, possibly API docs"
        needs_readme=true
        needs_claude=true
        needs_api=true
    fi

    # Check if specs changed
    if echo "$changed_files" | grep -q "specs/" 2>/dev/null; then
        echo "   ⚠️  Specs changed → Update SDD artifacts"
        needs_sdd=true
    fi

    # Check if tests changed
    if echo "$changed_files" | grep -q "test\|spec" 2>/dev/null; then
        echo "   ℹ️  Tests changed → Consider updating test documentation"
    fi

    # Check if config changed
    if echo "$changed_files" | grep -q "\.toml$\|\.yaml$\|\.json$\|\.env" 2>/dev/null; then
        echo "   ℹ️  Configuration changed → Update setup/config docs"
        needs_readme=true
    fi

    echo ""
    echo "🎯 Recommended Update Scope:"
    [ "$needs_readme" = true ] && echo "   - README.md (features, installation, usage)"
    [ "$needs_claude" = true ] && echo "   - CLAUDE.md (AI context, new modules)"
    [ "$needs_sdd" = true ] && echo "   - SDD artifacts (spec.md, plan.md, tasks.md)"
    [ "$needs_api" = true ] && echo "   - API/Technical documentation"
    echo ""
}

# ============================================================================
# Function: validate_links
# Purpose: Validate all markdown links point to existing files
# ============================================================================
validate_links() {
    echo "=== 🔗 Link Validation ==="
    echo ""

    local total_links=0
    local broken_links=0
    local external_links=0
    local broken_list=""

    # Find all markdown links [text](path)
    while IFS= read -r line; do
        if [[ "$line" =~ \]\(([^)]+)\) ]]; then
            local url="${BASH_REMATCH[1]}"
            total_links=$((total_links + 1))

            # Check if it's an external link
            if [[ "$url" =~ ^https?:// ]]; then
                external_links=$((external_links + 1))
            # Check if local file exists
            elif [ -f "$url" ]; then
                :  # Link is valid
            else
                broken_links=$((broken_links + 1))
                broken_list="$broken_list\n   - $url"
            fi
        fi
    done < <(find . -name "*.md" -exec cat {} \; 2>/dev/null)

    echo "📊 Link Summary:"
    echo "   ✅ Valid local links: $((total_links - broken_links - external_links))"
    echo "   ❌ Broken links: $broken_links"
    echo "   ⚠️  External links: $external_links"
    echo ""

    if [ "$broken_links" -gt 0 ]; then
        echo -e "${RED}Broken Links Found:${NC}$broken_list"
        echo ""
    fi
}

# ============================================================================
# Function: validate_references
# Purpose: Validate file:line references in documentation
# ============================================================================
validate_references() {
    echo "=== 📍 Reference Validation ==="
    echo ""

    local total_refs=0
    local valid_refs=0
    local invalid_refs=0
    local invalid_list=""

    # Find all file:line references (e.g., src/main.py:123)
    while IFS= read -r ref; do
        if [ -n "$ref" ]; then
            total_refs=$((total_refs + 1))
            local file="${ref%:*}"
            local line="${ref#*:}"

            # Check if file exists
            if [ ! -f "$file" ]; then
                invalid_refs=$((invalid_refs + 1))
                invalid_list="$invalid_list\n   - $ref (file not found)"
            else
                valid_refs=$((valid_refs + 1))
            fi
        fi
    done < <(grep -oh '[a-zA-Z0-9_/.-]*\.[a-z]*:[0-9]*' $(find . -name "*.md" 2>/dev/null) 2>/dev/null | sort -u)

    echo "📊 Reference Summary:"
    echo "   ✅ Valid references: $valid_refs"
    echo "   ❌ Invalid references: $invalid_refs"
    echo "   📝 Total references: $total_refs"
    echo ""

    if [ "$invalid_refs" -gt 0 ]; then
        echo -e "${RED}Invalid References Found:${NC}$invalid_list"
        echo ""
    fi
}

# ============================================================================
# Function: validate_versions
# Purpose: Check version consistency across documentation files
# ============================================================================
validate_versions() {
    echo "=== 📌 Version Consistency Check ==="
    echo ""

    local version_count=0
    declare -A versions

    # Find all version patterns
    while IFS= read -r version; do
        if [ -n "$version" ]; then
            version_count=$((version_count + 1))
            versions["$version"]=$((${versions["$version"]:-0} + 1))
        fi
    done < <(grep -h "v[0-9]\+\.[0-9]\+\.[0-9]\+" $(find . -name "*.md" 2>/dev/null) 2>/dev/null | grep -oh "v[0-9]\+\.[0-9]\+\.[0-9]\+" | sort -u)

    echo "📊 Found Versions:"
    for version in "${!versions[@]}"; do
        echo "   - $version (${versions[$version]} occurrences)"
    done

    if [ ${#versions[@]} -gt 1 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Multiple versions found - consider standardizing${NC}"
    else
        echo ""
        echo -e "${GREEN}✅ All versions are consistent${NC}"
    fi
    echo ""
}

# ============================================================================
# Function: generate_metrics
# Purpose: Generate documentation metrics for reporting
# ============================================================================
generate_metrics() {
    echo "=== 📊 Documentation Metrics ==="
    echo ""

    local total_md=$(find . -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local root_md=$(find . -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local docs_md=$(find ./docs -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local specs_md=$(find ./specs -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

    echo "Total documentation files: $total_md"
    echo "  - Root directory: $root_md"
    echo "  - docs/ directory: $docs_md"
    echo "  - specs/ directory: $specs_md"
    echo ""

    # Total line counts
    local total_lines=$(find . -name "*.md" -exec wc -l {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}')
    echo "Total documentation lines: ${total_lines:-0}"
    echo ""

    # Git stats if available
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local last_commit=$(git log -1 --format="%h - %s" 2>/dev/null || echo "N/A")
        local last_doc_commit=$(git log -1 --format="%h - %s" -- "*.md" 2>/dev/null || echo "No doc commits found")

        echo "Git Information:"
        echo "  Last commit: $last_commit"
        echo "  Last doc update: $last_doc_commit"
    fi
    echo ""
}

# ============================================================================
# Main execution
# ============================================================================
main() {
    # Initialize cache directory
    init_cache

    local command=${1:-help}

    case "$command" in
        lint)
            check_and_install_linting_tools && run_markdown_linting
            ;;
        principles)
            # Try cache first
            if read_cache "principles" "$CACHE_LIFETIME_ANALYSIS"; then
                echo -e "${YELLOW}(from cache)${NC}"
            else
                analyze_principles | tee >(write_cache "principles")
            fi
            ;;
        structure)
            # Try cache first
            if read_cache "structure" "$CACHE_LIFETIME_ANALYSIS"; then
                echo -e "${YELLOW}(from cache)${NC}"
            else
                analyze_structure | tee >(write_cache "structure")
            fi
            ;;
        categorize)
            categorize_files
            ;;
        validate|validate-all)
            validate_links
            validate_references
            validate_versions
            ;;
        validate-links)
            validate_links
            ;;
        validate-references)
            validate_references
            ;;
        validate-versions)
            validate_versions
            ;;
        impact)
            # Try cache first (shorter TTL since code changes)
            if read_cache "impact" 1800; then
                echo -e "${YELLOW}(from cache)${NC}"
            else
                analyze_impact | tee >(write_cache "impact")
            fi
            ;;
        metrics)
            # Try cache first
            if read_cache "metrics" "$CACHE_LIFETIME_METRICS"; then
                echo -e "${YELLOW}(from cache)${NC}"
            else
                generate_metrics | tee >(write_cache "metrics")
            fi
            ;;
        all)
            check_and_install_linting_tools
            echo ""
            run_markdown_linting
            echo ""
            if read_cache "principles" "$CACHE_LIFETIME_ANALYSIS"; then
                echo -e "${YELLOW}(from cache)${NC}"
            else
                analyze_principles | tee >(write_cache "principles")
            fi
            echo ""
            if read_cache "structure" "$CACHE_LIFETIME_ANALYSIS"; then
                echo -e "${YELLOW}(from cache)${NC}"
            else
                analyze_structure | tee >(write_cache "structure")
            fi
            echo ""
            categorize_files
            echo ""
            if read_cache "impact" 1800; then
                echo -e "${YELLOW}(from cache)${NC}"
            else
                analyze_impact | tee >(write_cache "impact")
            fi
            echo ""
            if read_cache "metrics" "$CACHE_LIFETIME_METRICS"; then
                echo -e "${YELLOW}(from cache)${NC}"
            else
                generate_metrics | tee >(write_cache "metrics")
            fi
            echo ""
            validate_links
            echo ""
            validate_references
            echo ""
            validate_versions
            ;;
        cache)
            echo "=== 📦 Cache Status ==="
            echo "Cache directory: $CACHE_DIR"
            echo "Cache contents:"
            if [ -d "$CACHE_DIR" ]; then
                ls -lh "$CACHE_DIR" 2>/dev/null | tail -n +2 | while read line; do
                    echo "  $line"
                done
                echo ""
                echo "Cache sizes:"
                du -sh "$CACHE_DIR" 2>/dev/null | sed 's/^/  /'
            else
                echo "  (no cache directory yet)"
            fi
            echo ""
            ;;
        clear-cache|clear)
            local cache_key="${2:-all}"
            clear_cache "$cache_key"
            ;;
        help|--help|-h)
            echo "Documentation Analyzer Tool"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  lint              - Check/install linting tools and auto-fix markdown"
            echo "  principles        - Extract project documentation principles (cached)"
            echo "  structure         - Analyze documentation structure (cached)"
            echo "  categorize        - Categorize files by content type"
            echo "  impact            - Analyze change impact from git history (cached)"
            echo "  metrics           - Generate documentation metrics (cached)"
            echo "  validate          - Run all validation checks (link, reference, version)"
            echo "  validate-links    - Check all markdown links point to existing files"
            echo "  validate-references - Check file:line references are valid"
            echo "  validate-versions - Check version consistency across docs"
            echo "  all               - Run all analyses including linting (uses cache)"
            echo "  cache             - Show cache status"
            echo "  clear-cache       - Clear all caches (or 'clear-cache <key>' for specific)"
            echo "  help              - Show this help message"
            echo ""
            echo "Caching:"
            echo "  - Analysis results cached for 1 hour"
            echo "  - Impact analysis cached for 30 minutes"
            echo "  - Metrics cached for 24 hours"
            echo "  - Cache location: $CACHE_DIR"
            echo ""
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
