# Quick Start Guide

Get up and running with Doc Review Commands in 5 minutes.

## Installation

### Option 1: Plugin Marketplace (When Published)

```bash
# In Claude Code:
/plugin marketplace add kimcharli/doc-review-commands
/plugin install doc-review-commands@doc-review-commands
# Then restart Claude Code
```

### Option 2: Manual Install

```bash
git clone https://github.com/kimcharli/doc-review-commands.git
cd doc-review-commands
./install.sh
```

See [Installation Guide](INSTALLATION.md) for more options.

## First Use

```bash
# Get help
/ck:doc-review/help

# Analyze your project
/ck:doc-review/analyze
```

## Common Workflows

### Quick README Update

```bash
# After adding a feature
/ck:doc-review/core "added user authentication"

→ Updates: README.md, CLAUDE.md, CHANGELOG.md
→ Time: ~20 seconds
```

### Complete Documentation Update

```bash
# After finishing a major phase
/ck:doc-review/main "Phase 2 implementation complete"

→ Shows analysis
→ You select what to update
→ Runs selected sub-commands
→ Shows summary
```

### Quality Check Before Commit

```bash
# Before git commit
/ck:doc-review/qa

→ Checks links
→ Validates references
→ Scores quality (0-100)
→ Lists issues to fix
```

## Command Cheat Sheet

| Command | When to Use |
| -- | -- |
| `/ck:doc-review/help` | Need usage guide |
| `/ck:doc-review/analyze` | "What docs need updating?" |
| `/ck:doc-review/core "X"` | Quick README/CLAUDE update |
| `/ck:doc-review/sdd "X"` | Update SDD artifacts |
| `/ck:doc-review/qa` | Before committing docs |
| `/ck:doc-review/main "X"` | Full guided update |

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- See [examples/](../examples/) for more workflows
- Customize [config/categories.json](../config/categories.json) for your project
