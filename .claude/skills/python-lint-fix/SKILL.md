---
name: python-lint-fix
description: Checks environment health and guides pre-commit setup. Lint, format, and test run automatically via pre-commit on every git commit. Use when the user asks to lint, fix, format, set up hooks, or check environment readiness.
---

# Python Lint Fix

Lint, format, and test are handled automatically by **pre-commit** on every `git commit`.
This skill checks that the environment is healthy and pre-commit hooks are installed.

## References

- **MarkdownLint Rules**: [DavidAnson/markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- **Ruff Documentation**: [Ruff Rules](https://docs.astral.sh/ruff/rules/)
- **pre-commit**: [pre-commit.com](https://pre-commit.com)

## First-Time Setup (once per clone)

```bash
uv tool install pre-commit    # install pre-commit if not already present
uv run pre-commit install     # install git hook
```

After installation, every `git commit` automatically runs:

- **ruff** — Python lint + format
- **mdformat** — Markdown format (GFM, frontmatter, tables, shfmt)
- **markdownlint** — Markdown style (`--fix`)
- **pytest** — tests on `pre-push` stage

## Environment Health Check

Run the bundled script to verify tools and hook installation:

```bash
bash plugins/ck/skills/python-lint-fix/tools/lint-fix.sh
```

It checks: `uv`, `pre-commit`, git hook presence, `.pre-commit-config.yaml`, and markdownlint version (≥ 0.45.0).

## Manual Run (without committing)

```bash
uvx pre-commit run --all-files
```

## Summary Reporting

After running, report:

- Whether the pre-commit hook is installed.
- Any missing tools or version mismatches found.
- Next action for the user if issues were detected.
