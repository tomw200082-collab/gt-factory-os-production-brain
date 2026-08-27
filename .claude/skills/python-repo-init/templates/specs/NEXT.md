# Next Session — Start Here

Purpose: the single, fast, git-tracked pointer to "what's actionable right
now." Read this file FIRST, before `specs/workflow.md` or any spec — it exists
precisely so a new session doesn't have to grep through the workflow log or
spec `Status:` lines to figure out where to resume. Session-local `todos`
(SQL) do **not** persist across sessions — this file is the only durable
handoff.

Last updated: __DATE__ (governance scaffolding created; no skills implemented
yet).

## Active work

Define and build the **first skill**, spec-first:

1. Decide the first capability this repo needs and write
   `specs/001-<skill-name>.md` (Section 5 template of `specs/workflow.md`) —
   problem, inputs (`data/01_raw/*`), output, edge cases. Record design
   decisions before coding.
2. Implement it as `src/__PKG_NAME__/<skill-name>.py` (one skill = one module).
3. Add `tests/test_<skill-name>.py`; `uv run pytest` must pass.
4. Commit the spec in the same turn the design is decided, *before/with* the
   code (the convention checker enforces a `specs/**` change alongside any
   `src/**/*.py` change, and requires this file to be touched too).

Not started yet.

## Mechanical enforcement

`scripts/check_repo_conventions.py` (Section 8 of `specs/workflow.md`) fails a
commit that touches `src/**/*.py`, `data/03_generated/**`, or another
`specs/**/*.md` without also touching this file (same commit or the one
immediately before). It can't verify what you write here is accurate — only
that you touched it. Still write a real, accurate pointer.

## Open items requiring a human decision (not agent-actionable alone)

Parked, not forgotten — confirm with __AUTHOR__ first:
- **Enable GitHub Actions at the repo level.** The CI workflow
  (`.github/workflows/repo-conventions.yml`) is committed but will not run
  until Actions is enabled for this repo. Do not enable without asking.

## Convention: keep this file current

**Update this file as the last step of every session**, before ending — not
just when work is incomplete. Rules:
1. If there's an in-progress or planned item, put exactly one concrete "Active
   work" bullet block: skill/spec name, one-line action, and a direct
   file/section pointer (not "see spec").
2. If nothing is pending, explicitly write "None." — an empty or stale "Active
   work" section is a bug, not an acceptable default.
3. Do not duplicate the full decision rationale here, and never stack
   completed "Prior:" history — both live in `specs/workflow-log.md` and the
   relevant `specs/NNN-*.md` (or its `-history.md` sibling). This file only
   holds the *pointer*.
4. This file's own edits do not need a matching `specs/NNN-*.md` skill spec
   (it's process bookkeeping) — but commit it with the work it reflects.
