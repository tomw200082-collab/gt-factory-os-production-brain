# Dev Workflow Spec: Capturing Skills & Specs While Building Code

Status: Draft
Owner: __AUTHOR__
Created: __DATE__

## 1. Purpose

This spec defines how we capture specs and "skills" (reusable code modules) as
we build, so work stays trackable across sessions instead of being ad hoc.
Every capability is specced before it is coded, tested alongside, and its
durable decisions are logged where any AI coding tool can read them.

## 1a. Standing Principle: Agent-Agnostic by Default

Any spec, tool choice, or instruction added to this repo — now or in the
future — MUST be usable by any AI coding tool (Copilot CLI, Claude Code,
Gemini CLI, or others), not just the one that authored it. Concretely:

- Do not rely on a tool-specific memory/config system (e.g. Copilot's
  `store_memory`) as the sole record of a durable decision — mirror it into
  [`specs/memory.md`](./memory.md).
- Do not put repo-specific knowledge only in a tool-specific file (e.g.
  `.github/copilot-instructions.md`, `CLAUDE.md`, `GEMINI.md`) — those must
  stay thin pointers to `AGENTS.md`, the single canonical source.
- When adding a new instruction/config file for a new tool, make it a thin
  pointer to `AGENTS.md`, matching the existing pattern.

This is a binding rule for all future additions, not just a description of past
decisions — see `specs/memory.md` for the historical record.

## 2. Current State (as of __DATE__)

- Governance scaffolding is in place (this file, `specs/memory.md`,
  `specs/NEXT.md`, `AGENTS.md` + thin pointers, `docs/README.md`, the
  convention checker + hooks + CI, the `data/` layout, `src/`/`tests/`).
- No skills implemented yet — see `specs/NEXT.md` for the first one.
- Tooling: `pyproject.toml` + `mise.toml` (uv / Python __PYTHON_VERSION__).
  Commands in Section 4 are final only after a first successful run.

## 3. Workflow: Spec → Skill → Test → Track

1. **Spec first, in `specs/`** — including decisions made purely in
   conversation, in the same turn, before any code is proposed. Before writing
   a module, add `specs/NNN-<skill-name>.md` (Section 5 template) describing:
   the problem, inputs (which `data/01_raw/*` files), expected output, and known
   edge cases. Keep `docs/` reserved for domain analysis — do not mix
   engineering/process specs into it.

   **This applies just as much when a design decision (schema change, naming
   convention, a corrected assumption) is reached mid-conversation as it does
   to a brand-new skill.** Do not defer writing it down until asked, and do not
   let it live only in chat/session context — write it into the relevant
   `specs/*.md` file (or Section 6 log) **and commit it, on its own, in that
   same turn** before proposing or writing any implementation code. The commit
   is the durable record and audit trail — see Section 8's mechanical backstop.

2. **One skill = one module in `src/`.** Each reusable capability lives in its
   own module under `src/<pkg>/`, with a docstring spec at the top restating
   inputs/outputs/assumptions.

3. **Test alongside the skill.** Add a matching `tests/test_<skill-name>.py`
   using `pytest`. This is the regression net as more skills are added.

4. **Track via `todos` table + this file.** Use the session `todos` table for
   active WIP (pending/in_progress/done/blocked). Use Section 6 as the durable,
   cross-session log, and keep `specs/NEXT.md` current (Section 8 enforces it).

5. **Close gaps explicitly.** When a skill resolves an item in `docs/` or
   `specs/NEXT.md`, cross-reference it there.

## 3a. Spec Files Stay Shallow: the Two-File Pattern

Always-loaded docs fatten — normative files accrete dated decision sections
until a session can't read them in one pass (reference project: two skill
specs hit ~830 lines each). For any `specs/NNN-<skill>.md` that accumulates
dated decision sections:

1. The spec file stays **shallow and normative** (target ≤ ~400 lines):
   problem, inputs, *current* output format, edge cases, test plan. Update
   these in place as decisions land — they describe current state, not history.
2. Dated decision sections (headings like `## 8a. …`) move **verbatim,
   numbering unchanged** to an append-only sibling
   `specs/NNN-<skill>-history.md`; new dated sections are appended THERE.
3. A **decision-index cue table** (section · date · one-line cue · status:
   implemented / planned / superseded) sits where the sections were — readers
   open a history section only when its row matters, and old references like
   "spec 001 Section 8e" resolve through it.
4. `scripts/split_spec_history.py <spec>` performs the split mechanically;
   guard check 8 (Section 8) is the advisory-only backstop.

Exempt: append-only archives that are *supposed* to grow and are read on
demand only — `specs/workflow-log.md`, `specs/memory.md`, `*-history.md`.

## 4. Tooling

- Dependency management: `uv add <pkg>` / `uv add --dev <pkg>`
- Install: `uv sync --dev`
- Test command: `uv run pytest`

These are final only after each has run successfully once.

## 5. Skill Spec Template

```
### Skill: <name>
- Problem:
- Inputs (source files):
- Output:
- Edge cases / assumptions:
- Module: src/<pkg>/<name>.py
- Tests: tests/test_<name>.py
- Status: planned | in_progress | done
```

File naming: `specs/NNN-<skill-name>.md` (e.g. `specs/001-<name>.md`), numbered
sequentially in creation order.

## 5a. `data/` Directory Contract

`data/` is organized by lifecycle stage; git-tracking differs by stage. Do not
write generated or scratch output back into `data/01_raw/`.

- `data/01_raw/` — immutable, as-provided source artifacts. Read-only input;
  **never written to by any skill.** **Tracked in git.** Numeric prefix `01_`
  keeps a plain `ls data/` in pipeline order. Sanitize secrets before adding.
- `data/03_generated/` — stable pipeline outputs that downstream code or people
  depend on. **Tracked in git.** Every file needs a provenance header (below).
- `data/work/<skill-name>/` — disposable scratch/intermediate artifacts. Never
  referenced by other skills or committed as a deliverable; safe to delete and
  regenerate. **Gitignored.**
- `data/tmp/` — throwaway temp files, heredocs, temp scripts. Use this instead
  of the machine `/tmp`. **Gitignored.**

A `data/02_config/` tier (hand-maintained, human-owned config/override files a
skill may seed but never overwrite once present) is **reserved but not yet
created** — add it only when a skill actually needs one.

**Provenance header:** every file written under `data/03_generated/` must start
with (or, for binary formats, be accompanied by a sibling
`<file>.manifest.yaml` containing) a provenance block:

```yaml
# generated_by: src/<pkg>/<name>.py
# spec: specs/NNN-<skill-name>.md
# source: data/01_raw/<file1>, data/01_raw/<file2>
# generated_at: <ISO8601 timestamp>
# count: <N> <noun>   # optional, when the file's top-level body is a list
```

This makes the chain `specs/ -> src/ -> data/03_generated/` inspectable
without re-reading code.

## 6. Log

The dated decision log lives in [`specs/workflow-log.md`](./workflow-log.md) —
**append new dated entries there, not here.** This file stays normative-only.
(Lesson from the reference project: an inline log grew this file past 1000
lines / ~26k tokens, too large for an AI session to read in one pass at
session start.)

## 7. Cross-Tool Persistence Caveat

Different AI coding tools auto-load different instruction files at session
start: Copilot CLI reads `AGENTS.md` + `.github/copilot-instructions.md`;
Claude Code reads `CLAUDE.md`; Gemini CLI reads `GEMINI.md`. To avoid amnesia
when switching tools, `CLAUDE.md`, `GEMINI.md`, and
`.github/copilot-instructions.md` are kept as thin pointers to `AGENTS.md`
(single source of truth) rather than duplicated content.

Tool-specific memory systems (e.g. GitHub Copilot's `store_memory`) do **not**
transfer across tools. To make durable facts portable, mirror any fact recorded
via a tool's native memory mechanism into [`specs/memory.md`](./memory.md) — a
plain, git-tracked, append-only log any tool can read.

## 8. Mechanical Enforcement: Pre-Commit Convention Guard

`scripts/check_repo_conventions.py` enforces the deterministically-checkable
subset of these conventions. It is stdlib-only and run directly by
`.githooks/pre-commit` (wired with `git config core.hooksPath .githooks` —
repo-local, not global; no virtualenv or dependency install is needed for the
hook itself). `.githooks/post-commit` re-runs a machine-wide auto-sync hook if
present, so it isn't lost. The checker reads the *staged* content of files
(`git show :path`), so unstaged working-tree edits can neither mask nor fake a
violation.

**What it checks (mechanical only):**
1. `AGENTS.md` stays under a line-count ceiling (70 lines) — catches content
   bloat / re-inlining.
2. `AGENTS.md` doesn't contain markers that belong in `specs/workflow.md` (the
   provenance-header fields, the skill-spec template) — duplication guard.
3. `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` stay thin
   (≤20 lines) and link to `AGENTS.md`.
4. No staged text file under `data/01_raw/` or `data/03_generated/` contains an
   obvious plaintext secret (private-key header, AWS key, `password`/
   `plain-text-password`/`pre-shared-key` with a real value) — sample inputs
   must be sanitized. False positive on a known-safe value (e.g. an
   already-hashed credential)? Append the marker `conventions:allow-secret`
   to that line to exempt it — the exemption is visible in the diff.
5. Any staged file under `data/03_generated/` has the required provenance
   header fields (`generated_by`, `spec`, `source`, `generated_at`).
6. Any commit touching `src/**/*.py` or `data/03_generated/**` also has a
   `specs/**/*.md` change — same commit/PR range, or (local single-commit run)
   the immediately preceding commit. Backstop for the spec-before-or-with-code
   practice (Section 3). Intentionally coarse (one-commit lookback locally).
7. Any commit touching `src/**/*.py`, `data/03_generated/**`, or another
   `specs/**/*.md` file also touches `specs/NEXT.md` — backstop for "refresh
   the session-start pointer before ending." Same coarseness as 6; editing
   `specs/NEXT.md` itself never trips its own check.
8. **Soft advisory only (never fails the commit):** a staged `specs/NNN-*.md`
   (excluding `*-history.md`) over 400 lines gets a non-blocking nudge to
   apply the Section 3a two-file split (`scripts/split_spec_history.py`).
   Advisory, not a gate: a spec legitimately grows while decisions are in
   flight; the nudge fires at commit time, when acting on it is cheap.

**What it cannot check:** whether a decision's reasoning was sound, or whether
an agent actually read `specs/memory.md`. Those stay trust-based (Sections 1a, 7).

**Setup for a fresh clone:** `git config core.hooksPath .githooks` (the
hooksPath is not itself tracked by git, so re-run it once per clone). The hook
needs only a system `python3`; `uv sync --dev` is required only to run tests.

**CI enforcement (`.github/workflows/repo-conventions.yml`):** runs the same
check on every push to `main` and every PR, diffing against the PR base or
`HEAD~1` via `CHECK_CONVENTIONS_BASE_REF`. Note: GitHub Actions must be enabled
at the repo level for this to actually run — treat that as a human decision
(see `specs/NEXT.md`).
