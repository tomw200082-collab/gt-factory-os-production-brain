# SDD Git Commit

Orchestrates a professional Git commit workflow including hygiene checks, documentation parity (SDD), project state tracking (CHANGELOG, TODO, Session Memos), and post-commit reflection.

______________________________________________________________________

## Installation

For marketplace setup and general install instructions, see the [ck-skills README](../../../../README.md).

**Quick install:**

```bash
# Claude Code (installs the whole ck plugin)
claude plugin install ck@ck-skills

# Copilot CLI
copilot plugin install ck@ck-skills

# Manual
cp -r plugins/ck/skills/sdd-git-commit ~/.claude/skills/sdd-git-commit
```

______________________________________________________________________

## Usage

The Git commit workflow is **AI-Native**. Just tell the tool what you want:

```
Commit my changes
Wrap up this task and commit
```

The AI will automatically activate the `sdd-git-commit` skill, check hygiene, sync specs, and guide you through the professional commit process.

______________________________________________________________________

## Workflow

1. **Hygiene**: Check for secrets, local configs, or build artifacts in the diff.
1. **Lint**: Run project linting (if available).
1. **SDD Gate**: Ensure source code and its corresponding specification file remain in sync.
1. **State Tracking**: Update `CHANGELOG.md`, `TODO.md`, and `SESSION_MEMO.md`.
1. **Commit**: Generate a Conventional Commit message and commit.
1. **Reflection**: Briefly reflect on surprising findings or learned lessons.

______________________________________________________________________

## SDD Parity Table Example

The skill encourages maintaining a one-to-one relationship between source files and specifications:

| Source File | Spec File |
| -- | -- |
| `src/core.py` | `specs/core.md` |
| `src/api.py` | `specs/api.md` |

______________________________________________________________________

## Related

- [sdd-project-init](../sdd-project-init/README.md) — bootstrap a new SDD project
- [doc-review-commands](../doc-review-commands/README.md) — keep docs in sync during development
- [ck-skills](../../../../README.md) — full marketplace README
