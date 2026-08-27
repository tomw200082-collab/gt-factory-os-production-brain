---
name: python-repo-init
description: >
  Scaffold a new Python repository pre-wired with spec-first, agent-agnostic
  AI-workflow governance (AGENTS.md + thin per-tool pointers, specs/ with a
  session-handoff NEXT.md, a mechanical convention guard, uv/mise tooling, a
  staged data/ layout). Use when the user says "init a python repo", "new
  python project with the workflow", "scaffold a python repo like this one",
  or invokes /python-repo-init.
allowed-tools: Bash(python3 *) Read(~/.claude/plugins/**) Read(~/.agents/skills/**)
---

# Python Repo Init

## Purpose

Create a new Python repo that already follows the spec-first, agent-agnostic
workflow conventions, so a fresh project starts governed instead of ad hoc.
The scaffold contains no application code — just the governance skeleton and a
first `specs/NEXT.md` pointer telling the next session to build skill #1. The
generated repo works identically with any AI coding tool (Claude Code, Copilot
CLI, Gemini CLI, others) — and with none.

## Trigger

`/python-repo-init <target-dir>` or when the user asks to initialize/scaffold a
new Python repository with this workflow.

## What it generates

Into `<target-dir>`:

- `AGENTS.md` (minimal ≤70-line map) + thin `CLAUDE.md`, `GEMINI.md`,
  `.github/copilot-instructions.md` pointers.
- `specs/workflow.md` (spec→skill→test→track, `data/` contract, the
  shallow-spec two-file pattern, enforcement), `specs/workflow-log.md`
  (append-only dated decision log — kept OUT of workflow.md so the
  always-loaded file stays readable in one pass), `specs/memory.md` (seeded),
  `specs/NEXT.md` (first Active-work pointer).
- `docs/README.md` (domain-analysis home).
- `scripts/check_repo_conventions.py` (stdlib-only convention guard, incl. an
  advisory-only shallow-spec size nudge) + `scripts/split_spec_history.py`
  (performs the two-file spec split mechanically) +
  `.githooks/pre-commit` & `post-commit` +
  `.github/workflows/repo-conventions.yml` (same guard in CI).
- `pyproject.toml`, `mise.toml` (uv / pytest; Python version via `--python`),
  `.gitignore`, `README.md`.
- `src/<package>/__init__.py`, `tests/`, `data/01_raw/`, `data/03_generated/`
  (tracked), `data/work/`, `data/tmp/` (gitignored scratch, kept via .gitkeep).

## How to run

1. The generator is `scripts/generate.py`, inside this skill's own directory
   (with templates in `templates/`). **You already know that directory** — it
   was announced when this skill loaded, in the line
   `Base directory for this skill: <path>`. Use that path as `<skill-dir>`
   below. **Never run find/ls/glob to locate this skill or its files, and do
   not Read the generator source or templates** — this document plus the
   generator's own output tell you everything, and every needless search or
   Read costs the user a permission prompt. The generator works from
   **any cwd** — no `cd` needed:

   ```
   python3 <skill-dir>/scripts/generate.py <target-dir> \
       [--name NAME] [--package PKG] [--author AUTHOR] \
       [--description DESC] [--python VERSION] [--force]
   ```

   - `<target-dir>` — where to create the repo (required).
   - `--name` — project name (default: target dir basename).
   - `--package` — import package name (default: sanitized project name).
   - `--author` — owner handle (default: `git config user.name`, then
     `user.email`, then a TODO placeholder).
   - `--description` — short project description.
   - `--python` — Python version written into `pyproject.toml`/`mise.toml`
     (default: 3.14; pass e.g. `--python 3.12` for older environments).
   - `--force` — allow writing into a non-empty directory (pre-existing files
     that get overwritten are listed in the output).

2. Placeholders (`__PROJECT_NAME__`, `__PKG_NAME__`, `__AUTHOR__`, `__DATE__`,
   `__DESCRIPTION__`, `__PYTHON_VERSION__`) are substituted; the
   `src/__PKG_NAME__/` directory is renamed to the chosen package. `${{ ... }}`
   GitHub Actions expressions are left untouched (placeholders use `__NAME__`,
   not `{{ }}`).

3. The generator **lays files down only**. Report the printed next steps to the
   user (they run them, or you run them only if the user asks):

   ```
   cd <target-dir>
   git init
   git config core.hooksPath .githooks   # once per clone; hook is stdlib-only
   uv sync --dev                         # deps + test tooling
   git add -A && git commit -m "chore: scaffold repo governance"
   ```

## After scaffolding

- Point the user at `<target-dir>/specs/NEXT.md` — it already contains the
  first actionable item (define & build skill #1, spec-first).
- Remind them that `specs/NEXT.md` flags parked human decisions (e.g. enabling
  GitHub Actions) that should not be actioned without confirmation.
- If the user wants project-specific content (real description, domain notes in
  `docs/README.md`), offer to fill those in as a follow-up — the scaffold
  leaves them as clearly-marked placeholders.

## What this skill deliberately does NOT do

- It does not write application code or a first skill — that is the first
  spec-first task *inside* the new repo (`specs/NEXT.md`).
- It does not run `git init`, `uv sync`, wire hooks, or commit — it prints those
  as next steps so the human stays in control of repo creation.
- It does not overwrite a non-empty target unless `--force` is passed.
