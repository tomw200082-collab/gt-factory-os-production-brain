---
name: decision-capture
description: >
  Mid-session decision-to-spec-commit workflow. Invoke as soon as a design
  decision is reached in conversation (a scope choice, schema change,
  source-of-truth ruling, naming convention, or any "we decided X, not Y"
  moment) -- not at session end. Writes/amends the repo's spec/decision
  documentation to reflect exactly what was decided, gets explicit human
  sign-off on the diff, commits it on its own (before any implementation
  code), and pushes. Use when the user says "capture this decision",
  "write this to specs", "record this decision", "commit that decision",
  or invokes /decision-capture. Complements, but is not the same as,
  session-close: this fires many times per session (once per decision);
  session-close fires once, at the very end.
---

Run this immediately after a design decision is reached in conversation --
do not wait until other decisions in the same session accumulate, and do
not bundle it with implementation code in the same commit. Goal: the
repo's spec/decision trail always reflects reality *before* any code lands,
so a future session (any AI tool, or a human) can reconstruct "why" without
re-deriving it from chat history that won't persist.

## Steps

1. **Identify exactly what was decided**, distinct from what's still open.
   Re-state it back in one or two sentences before writing anything, so the
   user can correct a misunderstanding before it's committed. A "decision"
   is a concrete, closed choice (e.g. "use config as source of truth for X,
   not the CSV") -- not a plan, not a TODO, not an open question still
   awaiting the user's input.

2. **Find where this repo records decisions.** Look for (in priority
   order): a per-skill spec file already covering this area (e.g.
   `specs/NNN-<topic>.md`), a dated decision log (e.g. `specs/workflow.md`,
   `docs/decisions.md`, `DECISIONS.md`), or whatever the repo's own
   `AGENTS.md`/`CLAUDE.md`/root instructions designate. If none exists and
   the repo has no established decision-recording convention, ask the user
   where this should live instead of inventing a new file/pattern
   unprompted.

3. **Draft the update**, matching the existing spec/log's own format and
   level of detail (don't introduce a new structure or verbosity level
   inconsistent with neighboring entries). Include:
   - What was decided (the concrete choice).
   - The alternative(s) considered and rejected, briefly, if that context
     came up in conversation -- future readers benefit from knowing what
     was *not* chosen and why, not just the outcome.
   - Who confirmed it (the user), and the date.
   - If this decision supersedes or amends an earlier documented decision,
     say so explicitly and point to it -- don't silently overwrite prior
     rationale.

4. **If the repo has a durable "what's next" pointer file** (e.g.
   `specs/NEXT.md`) and this decision changes what's actionable next,
   update that pointer too, in the same commit -- but only if the content
   genuinely changes; don't touch it just to satisfy a mechanical check.

5. **Show the exact diff to the user and wait for explicit confirmation
   before committing.** Do not proceed on an assumed "looks good" -- a
   decision recorded inaccurately is worse than one not yet recorded,
   since it will misdirect a future session with false confidence.

6. **Commit the spec/decision change on its own** -- no implementation
   code in the same commit, even if the implementation feels trivial or
   the user asks for both in one go. If the user explicitly insists on
   combining them, say plainly that this departs from spec-before-code
   practice before proceeding, so it's a visible choice, not a silent
   default.

7. **Push**, unless the repo/user has indicated pushes require a separate
   step or review gate. If unsure whether this repo pushes directly to a
   protected branch vs. via PR, ask once rather than assuming.

8. **Confirm success**: report the commit hash and push result plainly.
   If any repo-specific pre-commit/CI convention check exists (e.g. a
   `scripts/check_*.py` referenced in the repo's own docs), it will have
   already run via the commit hook -- report its pass/fail, don't
   re-invent a separate check.

## What this skill deliberately does NOT do

- It does not write or modify implementation code -- that is explicitly a
  later, separate step (see spec-before-code convention, Step 6).
- It does not replace `session-close` -- it has no opinion on end-of-session
  cleanup, uncommitted-work sweeps, or test runs unrelated to the specific
  decision just made.
- It does not invent a decision-recording convention the repo doesn't
  already have, without asking first.
