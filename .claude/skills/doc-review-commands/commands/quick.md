---
description: Quick documentation update - skip analysis, direct edits only
allowed-tools: Read(*), Edit(*), Write(*), Bash(git:*)
---

# Quick Documentation Update

**⚡ Lightweight Mode** - No analysis, no validation, just updates
**Token Cost:** 400-600 tokens (vs 1.2-1.5K for full :core)
**Execution Time:** < 30 seconds
**Use Case:** Known, simple documentation updates

---

## Task

**Quick update for:** $ARGUMENTS

**Fast path:** Skip analysis → Update files → Done

______________________________________________________________________

## Files to Update

Based on $ARGUMENTS, update one or more:

- **README.md** - Features, installation, usage, configuration
- **CLAUDE.md** - AI context, module documentation
- **CHANGELOG.md** - Add new version entry

______________________________________________________________________

## Step 1: Identify Target File

Based on $ARGUMENTS, determine which file to update:

- Feature/usage change → README.md
- New module/component → CLAUDE.md
- Release/version change → CHANGELOG.md

______________________________________________________________________

## Step 2: Direct Edit (No Analysis)

Quickly update the target file without analysis:

**For README.md:**

- Add/update feature description in Features section
- Update Installation if dependencies changed
- Add Usage example

**For CLAUDE.md:**

- Add new module documentation
- Update architecture notes if changed
- Document new components

**For CHANGELOG.md:**

- Add new version entry at top
- Categorize: Added/Changed/Fixed
- Include dates and file references

______________________________________________________________________

## Step 3: Quick Validation

Only check what was actually changed:

- ✅ File exists and is readable
- ✅ No syntax errors in edited sections
- ✅ Basic formatting correct

Do NOT run full QA or linting.

______________________________________________________________________

## Step 4: Summary

Show what was changed:

- Files modified: [list]
- Lines changed: [approximate count]
- Execution time: [< 30 seconds]

______________________________________________________________________

## Example Usage

```bash
/ck:doc-review:quick "added new feature X"
# Updates README.md with new feature → Done (< 1K tokens)

/ck:doc-review:quick "new API endpoint"
# Updates CLAUDE.md with endpoint docs → Done (< 1K tokens)

/ck:doc-review:quick "version 1.2.0 release"
# Updates CHANGELOG.md with release notes → Done (< 1K tokens)
```

______________________________________________________________________

## When to Use Quick Mode

✅ **Use quick mode when:**

- Update is simple and straightforward
- You know exactly what needs changing
- No validation needed
- Speed is priority over completeness

❌ **Don't use quick mode when:**

- Update is complex or affects multiple files
- Need comprehensive analysis first
- Want full QA validation
- Documentation has many interconnections

______________________________________________________________________

## When to Use Full Mode

For comprehensive updates with analysis and validation:

```bash
# Full analysis before updating
/ck:doc-review:analyze "feature"

# Full update with QA validation
/ck:doc-review:core "feature"

# SDD artifact updates
/ck:doc-review:sdd "phase"

# Quality assurance
/ck:doc-review:qa
```

______________________________________________________________________

## Token Savings Comparison

| Task | Mode | Tokens | Time |
| -- | -- | -- | -- |
| Add feature to README | quick | 400-600 | < 30s |
| Add feature to README | core | 1.2-1.5K | 2-3s |
| New module to CLAUDE | quick | 400-600 | < 30s |
| New module to CLAUDE | core | 1.2-1.5K | 2-3s |
| CHANGELOG entry | quick | 300-500 | < 20s |
| CHANGELOG entry | core | 1.2-1.5K | 2-3s |

**Savings:** 60-70% tokens, 90%+ execution time reduction
