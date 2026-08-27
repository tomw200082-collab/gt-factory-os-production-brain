# Memory Log (Agent-Agnostic, Git-Tracked)

Status: Living document
Purpose: Durable decisions and conventions that any AI coding tool should know,
regardless of which tool's native memory system (if any) is in use. GitHub
Copilot's `store_memory` facts are NOT visible to Claude Code, Gemini CLI, or
any other tool — this file is the portable mirror. When a durable fact is
recorded via any tool's memory mechanism, append it here too (see
`specs/workflow.md` Section 7).

Format: one entry per fact, dated, with a one-line reason and citation.
Append-only — do not delete entries; mark superseded ones instead.

---

## __DATE__ — Directory conventions

**Fact:** `specs/` holds process/engineering specs (spec-per-skill,
`workflow.md`); `docs/` is reserved for domain analysis only — don't mix the
two. One skill = one module under `src/<pkg>/` with a matching
`tests/test_<name>.py`.

**Why:** Prevents a future session from putting process specs in `docs/`, and
keeps the spec→skill→test mapping one-to-one.

**Citation:** `specs/workflow.md` Sections 3, 5; `AGENTS.md` ("Repo Map").

---

## __DATE__ — `data/` directory tracking

**Fact:** `data/01_raw/` (source inputs) and `data/03_generated/` (outputs, with
provenance headers) are tracked in git; `data/work/` and `data/tmp/` are
gitignored. Never write generated/scratch output back into `data/01_raw/`.
Sanitize secrets before adding anything to `data/01_raw/` — the convention
checker blocks obvious plaintext secrets. Use `data/tmp/` (not the machine
`/tmp`) for throwaway files, heredocs, and temp scripts.

**Why:** A future session must not assume all of `data/` is ignored, nor commit
un-sanitized secrets.

**Citation:** `.gitignore`, `specs/workflow.md` Section 5a,
`scripts/check_repo_conventions.py` (check 4).

---

## __DATE__ — Cross-tool instruction files

**Fact:** `AGENTS.md` is the single canonical map for repo conventions and
execution rules; it must stay a short map of pointers (≤70 lines, mechanically
enforced). `CLAUDE.md`, `GEMINI.md`, and `.github/copilot-instructions.md` are
thin pointers (≤20 lines) to it, not duplicated content.

**Why:** Each AI tool auto-loads a different file at session start; a single
canonical file with thin pointers satisfies every tool's trigger while avoiding
silent drift.

**Citation:** `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
`.github/copilot-instructions.md`, `specs/workflow.md` Section 7,
`scripts/check_repo_conventions.py` (checks 1–3).
