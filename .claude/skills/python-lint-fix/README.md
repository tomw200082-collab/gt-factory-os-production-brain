# Python Lint Fix

One-shot auto-fix and formatting for Python (Ruff) and Markdown (mdformat, markdownlint). It handles linting, formatting, verification, and testing in a single command.

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
cp -r plugins/ck/skills/python-lint-fix ~/.claude/skills/python-lint-fix
```

______________________________________________________________________

## Usage

All logic is **AI-Native**. Just tell the tool what you want:

```
Fix lint errors
Lint and format my code
Make it clean and passing
```

The AI will automatically activate the `python-lint-fix` skill, run the necessary tools (Ruff, mdformat, markdownlint), and verify the results.

______________________________________________________________________

## Workflow

1. **Python Auto-fix**: Runs `ruff check --fix` and `ruff format`.
1. **Markdown Auto-format**: Runs `mdformat`.
1. **Markdown Linting**: Runs `markdownlint --fix`.
1. **Verification**: Confirms a clean state.
1. **Testing**: Runs `pytest -q` to ensure no regressions.

______________________________________________________________________

## Requirements

- **Python**: Ruff, pytest (recommended: installed via `uv`)
- **Markdown**: mdformat, markdownlint-cli (installed via `npm`)

______________________________________________________________________

## Related

- [sdd-project-init](../sdd-project-init/README.md) — bootstrap a new SDD project
- [sdd-git-commit](../sdd-git-commit/README.md) — professional SDD commit workflow
- [ck-skills](../../../../README.md) — full marketplace README
