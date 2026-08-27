---
name: commit
description: Run the professional SDD Git commit workflow
---

# SDD Git Commit

This command activates the `sdd-git-commit` skill to orchestrate a professional commit workflow.

## Usage

```
/ck:commit
```

Or naturally:

```
Commit my changes
Wrap up this task and commit
```

## Workflow

1. **Hygiene**: Check for secrets/junk in the diff.
1. **Lint**: Run project linting (if available).
1. **SDD Gate**: Sync source code with specifications.
1. **State Tracking**: Update CHANGELOG, TODO, and Session Memos.
1. **Commit**: Generate a Conventional Commit message and commit.
1. **Reflection**: Document lessons learned.
