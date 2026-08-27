---
description: Run documentation analysis without making changes
allowed-tools: Bash(~/.claude/commands/ck/doc-review/tools/analyzer.sh:*), Bash(~/.claude/tools/doc-analyzer.sh:*)
---

# Documentation Analysis Command

## Context

- Analysis Results:
  !`~/.claude/commands/ck/doc-review/tools/analyzer.sh all || ~/.claude/tools/doc-analyzer.sh all`

## Task

**Analysis-only mode** - Review project documentation without making changes.

---

## Analysis Summary

Present the analysis results in a user-friendly format:

### 📋 Project Documentation Principles

[Summarize principles detected from analysis output above]

**Detected Constraints:**

- [List any detected principles or "None detected"]

**Impact:** [Explain what this means for documentation updates]

______________________________________________________________________

### 📁 Documentation Structure

**Inventory:**

- Total .md files: [from metrics]
- Root directory: [count]
- docs/ directory: [count]
- specs/ directory: [count]

**Organization Assessment:**

- [Summarize if current structure is good or needs reorganization]
- [List any potential improvements]

______________________________________________________________________

### 🎯 Change Impact Assessment

**Recent Changes:**
[List files changed from git analysis]

**Documentation Impact:**

- README.md: [Needs update? Why?]
- CLAUDE.md: [Needs update? Why?]
- SDD artifacts: [Needs update? Why?]
- API/Technical docs: [Needs update? Why?]

**Recommended Actions:**

1. [Prioritized list of documentation updates needed]
1. [...]

______________________________________________________________________

### 📊 Current Metrics

**Documentation Health:**

- Total documentation lines: [from metrics]
- Last commit: [from git]
- Last doc update: [from git]

**Quality Indicators:**

- Large files (>200 lines): [count and list]
- Potential misplaced files: [count and list]
- SDD coverage: [number of active specs]

______________________________________________________________________

## Recommendations

Based on this analysis, here's what you should do:

### High Priority

- [List high-priority updates]

### Medium Priority

- [List medium-priority updates]

### Low Priority / Optional

- [List optional improvements]

______________________________________________________________________

## Next Steps

**To update documentation, use:**

- `/ck:doc-review/core [feature]` - Update core files
- `/ck:doc-review/sdd [feature]` - Update SDD artifacts
- `/ck:doc-review/main [feature]` - Full update with user choice

**To validate quality:**

- `/ck:doc-review/qa` - Run quality checks

______________________________________________________________________

## Benefits

✅ **No Changes Made** - Safe to run anytime
✅ **Fast** - Completes in < 1 second
✅ **Comprehensive** - Full picture of doc health
✅ **Actionable** - Clear next steps
