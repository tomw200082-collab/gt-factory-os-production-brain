---
name: plan-doc
description: >
  Plan-first workflow for multi-item change batches. Before executing any
  batch of related changes (review-driven fixes, a refactor, doc
  restructuring, multi-file feature work), write a plan document into the
  repo's specs/ (or docs/) directory, commit it on its own, THEN execute
  commit-by-commit against it. Use when the user says "plan first",
  "create a plan doc", "write the plan before executing", or invokes
  /plan-doc. Complements decision-capture (which records a SINGLE
  mid-conversation decision) and session-close (end-of-session pointer
  refresh): plan-doc governs a whole batch of work.
---

Standing rule this skill encodes (user directive, 2026-07-16): for any
multi-item change, the plan is a committed repo artifact *before* the
first fix lands — not a chat message. The commit is the audit trail that
the plan preceded the work.

## Steps

1. **Write the plan file** — `specs/<topic>-plan-<YYYY-MM-DD>.md` (follow
   the repo's own naming if it has a convention; `docs/` if the repo has
   no `specs/`). Required sections:
   - **Status line**: approved-by/when, and that it executes this session
     (or is awaiting approval).
   - **Context**: what prompted the batch (review findings, user ask),
     in 2–5 sentences.
   - **Scope rulings**: anything explicitly ruled OUT and why — "dropped
     by design" is different from "deferred"; record which.
   - **Items to execute**: one subsection per item, each with concrete
     file pointers (path, function, line/section) — precise enough that a
     different session could execute it cold.
   - **Parked / deferred**: items needing a human decision. Say who must
     decide and where the item is tracked (open-items list, NEXT file).
   - **Commit sequence**: which items land in which commit, in order.
   - **Verification**: the exact commands/observations that prove the
     batch done (tests green, lint green, "no diffs under X expected").
2. **Update the repo's session pointer** (e.g. `specs/NEXT.md` Active
   work) to point at the plan, so an interrupted session can resume from
   the plan's commit sequence.
3. **Commit the plan + pointer on their own** (no implementation mixed
   in). If the repo has convention-guard hooks, satisfy their
   choreography honestly (e.g. spec-file + NEXT-file co-touch rules).
4. **Execute the commit sequence**, checking off against the plan.
   Deviations found mid-execution get written back into the plan (or its
   parked list) — the plan stays truthful, not aspirational.
5. **Close out**: final pointer refresh per the repo's convention (or run
   session-close), with verification results stated plainly — including
   anything that failed or was skipped.

## What this skill deliberately does NOT do

- It does not replace decision-capture: a single "we decided X" moment
  still gets its own decision commit, immediately, not batched into a
  future plan.
- It does not execute anything before the plan commit exists — if the
  user wants to skip the plan for a trivial one-liner, that's their
  call to make explicitly, not this skill's shortcut.
