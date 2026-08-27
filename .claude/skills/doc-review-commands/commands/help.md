---
description: Documentation review system help - usage guide and command reference
allowed-tools: Bash(cat:*)
---

# 📚 Documentation Review System - Help Guide

**Version:** Phase 3 (Modular Architecture)
**Last Updated:** 2025-10-24

---

## 🎯 What Is This?

The `/ck:doc-review` system is a **modular documentation update toolkit** that
helps you:

✅ Keep documentation in sync with code changes
✅ Update README, CLAUDE.md, CHANGELOG consistently
✅ Maintain SDD (Specification-Driven Development) artifacts
✅ Validate documentation quality before commits
✅ Save 88% tokens compared to manual updates

______________________________________________________________________

## 🏗️ Architecture Overview

```text
┌─────────────────────────────────────────┐
│ /ck:doc-review (Orchestrator)           │
│ • Analyzes changes                      │
│ • Asks what to update                   │
│ • Delegates to sub-commands             │
│ • Shows summary                         │
└─────────────────────────────────────────┘
           │
    ┌──────┼──────┬──────┬──────┐
    ▼      ▼      ▼      ▼      ▼
┌────────┐ │  │  │  │  │  │  └─────────┐
│:analyze│ │:core│ │:sdd│ │:qa│ │:help  │
│        │ │     │ │    │ │   │ │       │
│ 0 edits│ │3 files││SDD │ │Check││This!│
└────────┘ └─────┘ └────┘ └────┘ └──────┘
```

______________________________________________________________________

## 📋 Command Reference

### `/ck:doc-review/help` (This Command)

**Purpose:** Show help and usage guide
**Token Cost:** ~200 tokens (one-time)
**Files Modified:** None
**Use When:** First time using system, or need reminder

______________________________________________________________________

### `/ck:doc-review/analyze`

**Purpose:** Analyze documentation needs without making changes
**Token Cost:** ~600-800 tokens
**Files Modified:** None
**Execution Time:** < 1 second

**What It Does:**

- ✅ Detects project documentation principles
- ✅ Analyzes current documentation structure
- ✅ Identifies what needs updating (from git history)
- ✅ Provides actionable recommendations
- ❌ Makes zero changes

**When to Use:**

- "What docs need updating?"
- Before starting documentation work
- Quick health check
- Understanding project doc structure

**Example:**

```bash
/ck:doc-review/analyze

→ Output:
  - 61 .md files found
  - Recent changes: 5 files in src/
  - Recommendations: Update README, CLAUDE, specs/005/
  - Execution: 0.8s
```

______________________________________________________________________

### `/ck:doc-review/core`

**Purpose:** Update core documentation files
**Token Cost:** ~1,200-1,500 tokens
**Files Modified:** README.md, CLAUDE.md, CHANGELOG.md
**Execution Time:** 15-30 seconds

**What It Does:**

- ✅ Updates README.md (features, usage, installation)
- ✅ Updates CLAUDE.md (AI context, module docs)
- ✅ Updates CHANGELOG.md (version entry)
- ✅ Uses professional templates
- ✅ Validates changes

**When to Use:**

- Just added a new feature
- Need to document new API/module
- Quick documentation update
- Before sharing project

**Example:**

```bash
/ck:doc-review/core "ApstraWorkModule implementation"

→ Updates:
  - README.md: Added usage examples
  - CLAUDE.md: Added module context
  - CHANGELOG.md: Created v1.2.0 entry
  - Time: 18s
```

**Templates Provided:**

- README feature section
- CLAUDE module documentation
- CHANGELOG version entry

______________________________________________________________________

### `/ck:doc-review/sdd`

**Purpose:** Update SDD (Specification-Driven Development) artifacts
**Token Cost:** ~1,500-1,800 tokens
**Files Modified:** specs/_/spec.md, plan.md, tasks.md, contracts/_.md
**Execution Time:** 30-60 seconds

**What It Does:**

- ✅ Marks requirements (FR-\*) as completed in spec.md
- ✅ Updates implementation plan and phase status in plan.md
- ✅ Marks tasks complete and adds notes in tasks.md
- ✅ Updates design contracts and API specs
- ✅ Validates SDD ↔ code consistency

**When to Use:**

- Completed an implementation phase
- Need to sync specs with code
- Mark requirements as done
- Document architecture decisions

**Example:**

```bash
/ck:doc-review/sdd "Phase 2 completion"

→ Updates:
  - spec.md: Marked FR-005-1, FR-005-2 complete
  - plan.md: Phase 2 status = ✅ Completed
  - tasks.md: 15 tasks marked done
  - Consistency: 100%
  - Time: 42s
```

**SDD Consistency Checks:**

- Requirements → Implementation alignment
- Plan → Tasks alignment
- Contracts → Code alignment
- Traceability validation

______________________________________________________________________

### `/ck:doc-review/qa`

**Purpose:** Quality assurance - validate documentation
**Token Cost:** ~1,800-2,000 tokens
**Files Modified:** None
**Execution Time:** 10-20 seconds

**What It Does:**

- ✅ Validates markdown links (finds broken links)
- ✅ Checks file:line references (path/to/file.py:123)
- ✅ Checks terminology consistency
- ✅ Validates version number consistency
- ✅ Checks SDD requirement traceability
- ✅ Basic code example syntax validation
- ✅ Completeness check (required sections)
- ✅ Generates scored report (0-100)

**When to Use:**

- Before committing documentation changes
- After major documentation updates
- Find and fix broken links
- Ensure documentation quality

**Example:**

```bash
/ck:doc-review/qa

→ Results:
  - Valid links: 156
  - Broken links: 3
  - Version mismatches: 1
  - Overall score: 87/100
  - Time: 12s

→ Recommendations:
  1. Fix broken link in README.md:45
  2. Update version in pyproject.toml
```

**QA Categories:**

1. Link Validation (20 points)
1. Cross-Reference Validation (15 points)
1. Terminology Consistency (15 points)
1. Version Consistency (15 points)
1. SDD Consistency (15 points)
1. Code Example Quality (10 points)
1. Completeness (10 points)

______________________________________________________________________

### `/ck:doc-review` (Main Orchestrator)

**Purpose:** Smart orchestration - analyze and delegate
**Token Cost:** ~900-1,200 tokens (orchestrator only) + selected sub-commands
**Files Modified:** Depends on user selection
**Execution Time:** Variable (depends on selection)

**What It Does:**

- ✅ Runs comprehensive analysis (via doc-analyzer.sh)
- ✅ Shows analysis summary
- ✅ Asks user which areas to update
- ✅ Invokes selected sub-commands automatically
- ✅ Aggregates and shows summary

**When to Use:**

- Not sure what needs updating
- Want guided workflow
- Comprehensive documentation update
- First time using the system

**Example:**

```bash
/ck:doc-review "feature 005 implementation"

→ Analysis shown (principles, structure, changes, metrics)

→ User asked:
  Which areas to update?
  □ Core Files (README, CLAUDE, CHANGELOG)
  □ SDD Artifacts (spec, plan, tasks)
  □ Run QA Only
  □ Full Update

→ User selects "Full Update"

→ Executes:
  1. /ck:doc-review/core "feature 005"
  2. /ck:doc-review/sdd "feature 005"
  3. /ck:doc-review/qa

→ Aggregated summary:
  - 8 files updated
  - QA score: 92/100
  - Total time: 78s
```

______________________________________________________________________

## 🎓 Usage Patterns

### Pattern 1: Quick README Update (Most Common)

```bash
# Scenario: Added new feature, need docs
/ck:doc-review/core "new feature name"

# Time: 20s
# Token: 1.2K
# Updates: README, CLAUDE, CHANGELOG
```

### Pattern 2: Analysis First (Recommended for New Users)

```bash
# Step 1: Understand what needs updating
/ck:doc-review/analyze

# Step 2: Update based on recommendations
/ck:doc-review/core "feature X"

# Time: 1s + 20s = 21s
# Tokens: 600 + 1.2K = 1.8K
```

### Pattern 3: Full Update After Major Work

```bash
# Completed major implementation
/ck:doc-review "Phase 2 complete"

→ Select "Full Update"
→ All docs updated + QA validated

# Time: 60-90s
# Tokens: 3-4K
# Updates: Everything
```

### Pattern 4: QA Before Commit (Best Practice)

```bash
# Before git commit
/ck:doc-review/qa

→ Fix any issues found
→ Re-run QA
→ Commit with confidence

# Time: 10-15s per run
# Tokens: 1.8K
```

### Pattern 5: SDD Update After Phase

```bash
# Completed implementation phase
/ck:doc-review/sdd "Phase 2"

# Time: 40-50s
# Tokens: 1.5K
# Updates: All SDD artifacts
```

______________________________________________________________________

## 🗂️ File Structure Reference

### Command Files Location

```text
~/.claude/commands/ck/
├── doc-review.md              # Main orchestrator
├── doc-review:analyze.md      # Analysis only
├── doc-review:core.md         # Core files update
├── doc-review:sdd.md          # SDD artifacts update
├── doc-review:qa.md           # Quality validation
├── doc-review:help.md         # This help file
└── doc-categories.json        # Pattern configuration
```

### Supporting Tools

```text
~/.claude/tools/
└── doc-analyzer.sh            # External analysis script
    ├── principles             # Extract doc principles
    ├── structure              # Analyze doc structure
    ├── categorize             # Categorize files
    ├── impact                 # Assess change impact
    ├── metrics                # Generate metrics
    └── all                    # Run all analyses
```

### Documentation

```text
docs/
├── ck-doc-review-analysis.md            # Architecture analysis
├── ck-doc-review-phase1-improvements.md # Phase 1 docs
├── ck-doc-review-phase2-improvements.md # Phase 2 docs
└── ck-doc-review-phase3-improvements.md # Phase 3 docs (current)
```

______________________________________________________________________

## 📊 Token Budgeting

### Per-Command Token Costs

| Command | Tokens | Use Case |
| -- | -- | -- |
| `:help` | ~200 | One-time reference |
| `:analyze` | ~600-800 | Analysis only |
| `:core` | ~1.2-1.5K | Quick update |
| `:sdd` | ~1.5-1.8K | SDD update |
| `:qa` | ~1.8-2K | Quality check |
| `doc-review` | ~900-1.2K + sub-commands | Full orchestration |

### Monthly Token Budget Examples

**Light Usage (10 updates/month):**

```plaintext
10x :core updates: 12-15K tokens
2x :qa checks: 3.6-4K tokens
1x :help reference: 200 tokens
Total: ~16-19K tokens/month
```

**Medium Usage (20 updates/month):**

```plaintext
15x :core updates: 18-22.5K tokens
4x :sdd updates: 6-7.2K tokens
4x :qa checks: 7.2-8K tokens
1x :help reference: 200 tokens
Total: ~31-38K tokens/month
```

**Heavy Usage (40 updates/month):**

```plaintext
25x :core updates: 30-37.5K tokens
8x :sdd updates: 12-14.4K tokens
8x :qa checks: 14.4-16K tokens
4x orchestrated: 12-16K tokens
1x :help reference: 200 tokens
Total: ~69-84K tokens/month
```

**Original System (Same Usage):**

```
40x monolithic commands: 400-480K tokens/month
Savings with Phase 3: 83-93%
```

______________________________________________________________________

## 🔧 Troubleshooting

### "Command not found: /ck:doc-review/core"

**Cause:** Sub-command file not installed
**Solution:**

```bash
# Check if files exist
ls ~/.claude/commands/ck/doc-review*.md

# Should see all sub-command files
# If missing, reinstall from docs
```

______________________________________________________________________

### "Analysis fails with error"

**Cause:** doc-analyzer.sh not executable or not found
**Solution:**

```bash
# Check if tool exists
ls -l ~/.claude/tools/doc-analyzer.sh

# Make executable
chmod +x ~/.claude/tools/doc-analyzer.sh

# Test manually
~/.claude/tools/doc-analyzer.sh help
```

______________________________________________________________________

### "QA reports many broken links"

**Cause:** Links broken after file reorganization
**Solution:**

```bash
# Run QA to identify broken links
/ck:doc-review/qa

# Fix links in reported files
# Re-run QA to verify
/ck:doc-review/qa
```

______________________________________________________________________

### "SDD consistency check fails"

**Cause:** Requirements/tasks out of sync with code
**Solution:**

```bash
# Update SDD artifacts
/ck:doc-review/sdd "current feature"

# Manually review any remaining inconsistencies
# Update as needed
```

______________________________________________________________________

## 💡 Tips & Best Practices

### 1. Run `:analyze` First (New Projects)

```bash
# When starting with a new project
/ck:doc-review/analyze

→ Understand doc structure
→ Identify gaps
→ Plan updates
```

### 2. Use `:core` for Quick Updates

```bash
# Daily workflow: added feature, need docs
/ck:doc-review/core "feature name"

→ Fast (20s)
→ Low token cost (1.2K)
→ Updates essentials
```

### 3. Run `:qa` Before Commits

```bash
# Git workflow
git add .
/ck:doc-review/qa    # Check doc quality
→ Fix any issues
git commit -m "docs: ..."
```

### 4. Use Orchestrator When Unsure

```bash
# Not sure what needs updating?
/ck:doc-review "what changed"

→ Guided workflow
→ Smart recommendations
→ You choose scope
```

### 5. Batch SDD Updates

```bash
# Don't update SDD after every task
# Batch at phase boundaries
/ck:doc-review/sdd "Phase 2 complete"

→ More efficient
→ Better overview
→ Cleaner commits
```

______________________________________________________________________

## 🎯 Decision Tree: Which Command to Use?

```text
Start
  │
  ├─ Need help? → /ck:doc-review/help
  │
  ├─ Just want to see what needs updating?
  │  └─ /ck:doc-review/analyze
  │
  ├─ Added new feature/module?
  │  └─ /ck:doc-review/core "feature name"
  │
  ├─ Completed implementation phase?
  │  └─ /ck:doc-review/sdd "phase name"
  │
  ├─ About to commit documentation?
  │  └─ /ck:doc-review/qa
  │
  ├─ Not sure what to do?
  │  └─ /ck:doc-review "what changed"
  │
  └─ Want comprehensive update?
     └─ /ck:doc-review "scope" → Select "Full Update"
```

______________________________________________________________________

## 📚 Further Reading

**Architecture Deep Dive:**

- `docs/ck-doc-review-analysis.md` - Initial architecture analysis
- `docs/ck-doc-review-phase3-improvements.md` - Current system design

**Phase Evolution:**

- Phase 1: Progressive disclosure + patterns config
- Phase 2: External tool architecture
- Phase 3: Full modularization (current)

**External Tools:**

- `~/.claude/tools/doc-analyzer.sh help` - Tool documentation
- Run `doc-analyzer.sh all` to see full analysis output

______________________________________________________________________

## 🆘 Getting Help

### Within the System

```bash
/ck:doc-review/help              # This guide
~/.claude/tools/doc-analyzer.sh help  # Tool help
```

### Documentation Files

```bash
cat docs/ck-doc-review-phase3-improvements.md  # Full system docs
```

### Quick Reference Card

```bash
# Analysis
/ck:doc-review/analyze

# Updates
/ck:doc-review/core "feature"    # Quick
/ck:doc-review/sdd "phase"       # SDD
/ck:doc-review "scope"           # Full

# Validation
/ck:doc-review/qa

# Help
/ck:doc-review/help
```

______________________________________________________________________

## ✨ Key Takeaways

1. **Modular = Efficient** - Use focused commands, not monolithic tool
1. **Analyze First** - Understand before updating
1. **Core for Speed** - Most common use case
1. **QA Before Commit** - Catch issues early
1. **Orchestrate When Unsure** - Guided workflow helps

______________________________________________________________________

**Last Updated:** 2025-10-24
**Version:** Phase 3 (Modular Architecture)
**System Status:** Production Ready ✅
