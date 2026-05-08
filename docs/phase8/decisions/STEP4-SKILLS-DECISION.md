# Phase 8 Run B — STEP 4 — Skills Decision

**Date:** 2026-05-08
**Decision:** **No skills created in Run B.**
**Author:** factory-os-governor (read-only audit) — applied as a Run B operating decision.

---

## What was considered

Run B's optional skill targets per the run prompt:

1. `.claude/skills/release-safety-check/`
2. `.claude/skills/ux-handoff-packet/`
3. `.claude/skills/integration-dry-run-protocol/`
4. `.claude/skills/source-truth-conflict-review/`

## Why none was created

### A. The agents already encode the protocols

The four execution agents authored in Run B Step 2 each include in-line:

- Required pre-checks
- Required post-checks
- Validation commands
- Stop conditions
- Tom approval triggers
- Output format

Adding a skill that restates the same protocol creates two surfaces saying the same thing.
Per `feedback_docs_not_bottleneck.md` (2026-04-17), doc architecture is frozen and duplication
is the wrong move unless it removes a live execution blocker.

### B. The commands already encode the workflows

The five conservative commands authored in Run B Step 3 each carry their own canonical input
list, output schema, allowed scope, forbidden scope, and stop conditions. A skill would not
add reusable behavior on top — it would add a third place to read the same rules.

Specifically:

| Proposed skill | Already encoded by |
|---------------|---------------------|
| `release-safety-check` | `release-verifier` agent + `/release-check` command |
| `ux-handoff-packet` | UX agents' handoff format (in `docs/phase8/handoffs/`) + `/ux-release-gate` command |
| `integration-dry-run-protocol` | `integration-boundary-executor` agent + `/integration-dry-run` command |
| `source-truth-conflict-review` | `source-of-truth-auditor` agent + `/source-truth-audit` command |

### C. No live execution blocker is removed by adding a skill

A skill is justified when it shortens a frequently-repeated invocation prompt. None of the
four candidates qualify yet:

- `/integration-dry-run` already produces a complete prompt-able output schema.
- `/portal-pr-review` already handles the cross-agent coordination.
- `release-verifier` is invoked by name; no prompt savings from a skill wrapper.

Run A established that the new operating layer is "read-only by default". Adding a skill that
auto-activates on certain triggers would push the system back toward implicit invocation,
which contradicts the conservative posture for Run B.

### D. Skill creation is reversible later

If a future run finds a clear repeated-prompt pattern that a skill would shorten, the skill
can be added without affecting any agent or command authored in Run B. The agents and
commands are not blocked on skills.

## When skills should be reconsidered

A skill becomes worth creating when ALL of these hold:

1. The same multi-step protocol is being invoked > 3 times per week.
2. The protocol has a single canonical entry point (no per-invocation customization needed).
3. Putting it in a skill measurably shortens the operator's prompt.
4. The protocol is not already a command.

Until then, the agents and commands are sufficient.

## Skills explicitly NOT to create

These skill names should NOT be reserved or created without explicit Tom approval:

- `release-safety-check` — duplicates `release-verifier` + `/release-check`.
- `ux-handoff-packet` — duplicates UX agent handoff format.
- `integration-dry-run-protocol` — duplicates `/integration-dry-run`.
- `source-truth-conflict-review` — duplicates `/source-truth-audit`.

If a future Tom-approved run needs one of these names for a different purpose, that's fine —
just document why the new use case is distinct from the agent/command above.

---

**END OF STEP 4 DECISION — No skills created in Run B.**
