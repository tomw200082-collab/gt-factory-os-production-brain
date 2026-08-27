---
description: Quality validation - auto-fix linting, check links, consistency, completeness
allowed-tools: Bash(find:*), Bash(grep:*), Bash(git:*), Bash(npm:*), Read(*), Grep(*), Glob(*), Edit(*), Write(*)
---

# Quality Assurance Validation Command

## Context

- All markdown files: !`find . -name "*.md" | wc -l`
- Recent doc changes:
  !`git log -5 --oneline -- "*.md" 2>/dev/null || echo "No recent doc commits"`

## Task

**Quality validation and auto-fix** - Automatically fixes formatting issues with
linting tools, then performs validation checks for links, consistency, and
completeness.

---

## Linting & Auto-Fix Phase

### Step 1: Check for Linting Tools

```bash
# Check if markdownlint is available
which markdownlint || npm list -g markdownlint || echo "markdownlint not found"

# Check if prettier is available
which prettier || npm list -g prettier || echo "prettier not found"
```

### Step 2: Install Tools if Missing

If tools are not available:

```bash
npm install -g markdownlint-cli prettier
```

### Step 3: Auto-Fix Markdown Files

**Run markdownlint with auto-fix enabled:**

```bash
markdownlint --fix . --ignore node_modules --ignore '.git'
```

This automatically fixes:

- MD032: Lists surrounded by blank lines
- MD034: Bare URLs wrapped in links
- MD036: Emphasis used instead of headings
- MD040: Fenced code blocks with language specified
- MD059: Link text descriptive

**Run prettier for consistent formatting:**

```bash
prettier --write "**/*.md"
```

This formats:

- Line length consistency
- Indentation
- List formatting
- Code block formatting

### Step 4: Verify Changes

```bash
# Show what was changed
git diff --name-only 2>/dev/null || echo "Not a git repo"

# Count auto-fixed issues
echo "✅ Auto-fix complete"
```

______________________________________________________________________

## QA Check 1: Link Validation

### Find All Markdown Links

Search for markdown links in all .md files:

```bash
# Find all links
find . -name "*.md" -exec grep -o '\[.*\](.*\.md)' {} +

# Find relative links
find . -name "*.md" -exec grep -o '](\.\.*/.*\.md)' {} +
```

### Validate Links

For each link found:

- Check if target file exists
- Note broken links
- Note external links (for manual review)

**Report Format:**

```text
✅ Valid links: [count]
❌ Broken links: [count]
⚠️  External links: [count] (manual review needed)

Broken Links Found:
- file.md:123 → links to missing-file.md
- [...]
```

______________________________________________________________________

## QA Check 2: Cross-Reference Consistency

### File:Line References

Find all code references (e.g., `path/to/file.py:123`):

```bash
find . -name "*.md" -exec grep -o '[a-zA-Z0-9_/.-]*\.[a-z]*:[0-9]*' {} +
```

### Validate References

For each reference:

- Check if file exists
- Optionally check if line number is reasonable (file has that many lines)

**Report Format:**

```text
✅ Valid references: [count]
❌ Invalid file references: [count]
⚠️  Questionable line numbers: [count]

Issues Found:
- README.md mentions deleted_file.py:50
- CLAUDE.md references file.py:999 (file only has 200 lines)
```

______________________________________________________________________

## QA Check 3: Terminology Consistency

### Extract Key Terms

Find variations of important terms:

```bash
# Example: Find all variations of "apstra"
grep -i "apstra\|APSTRA\|Apstra" . -r --include="*.md"

# Check for inconsistent capitalization
# Check for inconsistent naming (e.g., "doc review" vs "doc-review")
```

### Common Inconsistencies to Check

- Product names (capitalization)
- Feature names (hyphenation)
- Technical terms (spelling variations)
- Version numbers (consistency)

**Report Format:**

```text
📝 Terminology Review:

Consistent:
- ✅ "Apstra" used consistently (capitalized)
- ✅ "NetworkX" spelling consistent

Inconsistent:
- ⚠️  "doc-review" vs "doc review" (3 vs 2 occurrences)
- ⚠️  "Python" vs "python" mixed usage

Recommendations:
- Standardize on "doc-review" (hyphenated)
- Use "Python" (capitalized) for language name
```

______________________________________________________________________

## QA Check 4: Version Number Consistency

### Find All Version References

```bash
# Find version patterns
grep -E "v?[0-9]+\.[0-9]+\.[0-9]+" . -r --include="*.md"
grep -E "version.*[0-9]" . -r --include="*.md" -i
```

### Check Consistency

- Same version mentioned in multiple places?
- CHANGELOG.md version matches README.md?
- pyproject.toml version matches documentation?

**Report Format:**

```text
📊 Version Consistency:

Found Versions:
- README.md: v1.2.0
- CHANGELOG.md: 1.2.0 (latest entry)
- pyproject.toml: 1.1.5

Issues:
- ❌ Version mismatch: README (1.2.0) vs pyproject.toml (1.1.5)

Recommendation:
- Update pyproject.toml to 1.2.0 or clarify version strategy
```

______________________________________________________________________

## QA Check 5: SDD Consistency (if applicable)

### Check Requirement Traceability

Find all requirement IDs (FR-\*, NFR-\*):

```bash
grep -E "(FR|NFR)-[0-9]+" . -r --include="*.md"
```

### Validate Traceability

- Are requirements in spec.md referenced in plan.md?
- Are completed requirements (✅) in spec.md also marked done in tasks.md?
- Are all requirements accounted for?

**Report Format:**

```text
🔍 SDD Traceability:

Requirements in spec.md: [count]
Requirements in plan.md: [count]
Requirements in tasks.md: [count]

Orphaned Requirements:
- FR-005 appears in spec.md but not in tasks.md
- [...]

Completed but Not Marked:
- FR-003 marked done in tasks.md but not in spec.md
```

______________________________________________________________________

## QA Check 6: Code Example Syntax

### Find Code Blocks

```bash
# Find all code fences
grep -E "^\`\`\`" . -r --include="*.md"
```

### Basic Syntax Check

- Are code fences properly closed?
- Is language specified (`python vs`)?
- Look for obvious syntax errors in examples

**Report Format:**

```text
💻 Code Example Review:

Code blocks found: [count]
Language specified: [count]/[total]
Unclosed fences: [count]

Issues:
- README.md:50 - Code fence not closed
- CLAUDE.md:120 - No language specified
```

______________________________________________________________________

## QA Check 7: Completeness Check

### Required Sections

Check if standard files have expected sections:

**README.md:**

- [ ] Project description
- [ ] Installation
- [ ] Usage examples
- [ ] Configuration
- [ ] License

**CLAUDE.md:**

- [ ] Project overview
- [ ] Core architecture
- [ ] Key modules
- [ ] Common workflows

**CHANGELOG.md:**

- [ ] Recent version entries
- [ ] Categorized changes (Added/Changed/Fixed)
- [ ] Dates

**Report Format:**

```text
📋 Completeness Check:

README.md:
- ✅ Has installation section
- ✅ Has usage examples
- ❌ Missing troubleshooting section

CLAUDE.md:
- ✅ Has architecture overview
- ⚠️  Core modules section is sparse
```

______________________________________________________________________

## Output: QA Summary Report

### 📊 Documentation Quality Assurance Report

**Validation Date:** [YYYY-MM-DD]

______________________________________________________________________

### Auto-Fix Results

**Linting & Formatting Phase:**

- ✅ markdownlint: [X] issues auto-fixed
- ✅ prettier: [X] files reformatted
- Files modified: [list of files]
- Time taken: < 1 second

**Common fixes applied:**

- Blank lines around lists (MD032)
- Bare URLs wrapped in links (MD034)
- Link text made descriptive (MD059)
- Code blocks with language specified (MD040)
- Emphasis replaced with headings (MD036)

______________________________________________________________________

### Overall Quality Score

**Baseline Score:** [X]/100 (before fixes)
**After Fixes:** [X]/100 (after linting)

______________________________________________________________________

### Link Validation

- ✅ Valid links: [count]
- ❌ Broken links: [count]
- Score: [X]/20

### Cross-Reference Validation

- ✅ Valid references: [count]
- ❌ Invalid references: [count]
- Score: [X]/15

### Terminology Consistency

- Inconsistencies found: [count]
- Score: [X]/15

### Version Consistency

- Matches found: [count]
- Mismatches: [count]
- Score: [X]/15

### SDD Consistency

- Orphaned requirements: [count]
- Traceability: [X]%
- Score: [X]/15

### Code Example Quality

- Syntax issues: [count]
- Score: [X]/10

### Completeness

- Missing sections: [count]
- Score: [X]/10

______________________________________________________________________

### Priority Issues

**High Priority (Fix Immediately):**

1. [Issue description and location]
1. [...]

**Medium Priority (Fix Soon):**

1. [Issue description and location]
1. [...]

**Low Priority (Nice to Have):**

1. [Issue description and location]
1. [...]

______________________________________________________________________

### Recommended Actions

1. **Fix broken links:**

   - [Specific links to fix]

1. **Update version numbers:**

   - [Where to update]

1. **Standardize terminology:**

   - Use "[term]" instead of "[variation]"

1. **Complete missing sections:**

   - Add troubleshooting to README.md
   - [...]

______________________________________________________________________

## Next Steps

- [x] Auto-fixed linting issues (markdownlint + prettier)
- [ ] Review and fix high-priority semantic issues
- [ ] Fix medium-priority issues (links, terminology, versions)
- [ ] Consider low-priority improvements
- [ ] Commit auto-fixes: `git commit -m "docs: Auto-fix linting issues (markdownlint + prettier)"`
- [ ] Re-run QA to verify: `/ck:doc-review/qa`

______________________________________________________________________

## Implementation Notes

### Auto-Fix Behavior

- **Automatic:** Linting tools run automatically on every QA check
- **Non-destructive:** Only formatting and style issues are auto-fixed
- **Semantic issues:** Links, terminology, versions require manual review
- **Git-aware:** Shows diff of changes made

### Tool Requirements

- **markdownlint-cli:** Auto-fixes MD032, MD034, MD036, MD040, MD059
- **prettier:** Enforces consistent code formatting
- Both tools are lightweight and zero-dependency

### Configuration

Tools use standard configurations:

- `.markdownlintrc` - Markdownlint rules (if present)
- `.prettierrc` - Prettier rules (if present)
- Falls back to defaults if no config found
