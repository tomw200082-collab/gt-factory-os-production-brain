---
description: Update core documentation files (README, CLAUDE, CHANGELOG)
allowed-tools: Bash(cat:*), Bash(git:*), Read(*), Write(*), Edit(*), Grep(*), Glob(*)
---

# Core Documentation Update Command

## Context

- Config:
  !`cat ~/.claude/commands/ck/doc-review/config/categories.json`
- Recent changes:
  !`git diff --name-only HEAD~5..HEAD 2>/dev/null || echo "No recent commits"`

## Task

**Update core documentation for:** $ARGUMENTS

**Files to update:**

- README.md
- CLAUDE.md
- CHANGELOG.md

______________________________________________________________________

## Step 1: Read Current Files

Read the current state of core files to understand what needs updating.

______________________________________________________________________

## Step 2: README.md Updates

### What to Update

Based on $ARGUMENTS, update relevant sections:

**Features Section:**
If new feature added, use this template:

````markdown
### [Feature Name]

Brief description of what it does and why it's useful.

**Usage:**

```[language]
# Code example here
```
````

**Key Features:**

- Feature point 1
- Feature point 2

`````

**Installation Section:**
- Update if new dependencies added
- Update if setup process changed
- Verify all steps still work

**Configuration Section:**
- Add new configuration options
- Update examples with new settings
- Note any breaking changes

**Troubleshooting:**
- Add common issues encountered during development
- Document solutions/workarounds

### Make Updates

Apply updates to README.md using Edit tool.

---

## Step 3: CLAUDE.md Updates

### What to Update

Add AI assistant context for: $ARGUMENTS

**Use this template:**

````markdown
### [Module/Feature Name]
- **Purpose**: [What it does in one sentence]
- **Location**: `path/to/file.py:123`
- **Key Components**:
  - `ClassName` - Description
  - `function_name()` - Description
- **Usage Pattern**:
  ```bash
  # Example usage
  ```
`````

- **Error Handling**:
  - Common error 1: Solution
  - Common error 2: Solution
- **Related Components**: [Links to related sections]

`````

**Additional Context:**
- Update architecture overview if structure changed
- Add new workflow patterns
- Document design decisions
- Add debugging tips

### Make Updates

Apply updates to CLAUDE.md using Edit tool.

---

## Step 4: CHANGELOG.md Updates

### Determine Version

Check current version and determine if this is:
- Patch (bug fix): increment 0.0.X
- Minor (new feature): increment 0.X.0
- Major (breaking change): increment X.0.0

### Use Template

````markdown
## [Version] - YYYY-MM-DD

### Added
- Feature: [description] (file.py:123)
- Feature: [description]

### Changed
- Modified: [description]
- Updated: [description]

### Fixed
- Bug: [description] (#issue)
- Issue: [description]

### Deprecated
- [What's being removed in future]
`````

### Make Updates

- Read current CHANGELOG.md
- Add new entry at the top (most recent first)
- Use Edit tool to update

______________________________________________________________________

## Step 5: Validation

**Check Updates:**

- [ ] README.md updated with new feature/changes
- [ ] CLAUDE.md has AI context for new components
- [ ] CHANGELOG.md has version entry with categorized changes
- [ ] All code examples are syntactically correct
- [ ] File:line references are accurate
- [ ] No sensitive information exposed

______________________________________________________________________

## Output: Summary

### 📊 Core Documentation Update Summary

**Scope:** $ARGUMENTS

**Files Updated:**

| File | Sections Modified | Lines Changed |
| -- | -- | -- |
| README.md | [list sections] | ~[estimate] |
| CLAUDE.md | [list sections] | ~[estimate] |
| CHANGELOG.md | [version entry] | ~[estimate] |

**Key Changes:**

- [Bullet point summary of main changes]

**Validation:**

- [x] All core files updated
- [x] Examples tested
- [x] No sensitive data
- [x] References accurate

**Execution Time:** [X]s

______________________________________________________________________

## Next Steps

Recommended follow-up:

- [ ] Review changes: `git diff README.md CLAUDE.md CHANGELOG.md`
- [ ] Test any code examples added
- [ ] Update SDD if needed: `/ck:doc-review/sdd $ARGUMENTS`
- [ ] Run QA: `/ck:doc-review/qa`
