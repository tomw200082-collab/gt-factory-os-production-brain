<!--
STATUS: PROPOSAL ONLY. This ADR authorizes nothing. It proposes a framework.
It becomes authority ONLY when Tom amends the locked decision in CLAUDE.md
(Tom is sole writer of CLAUDE.md) to reference and ratify it. Until then, the
existing locked decision stands in full:

  "git push, merge, deploy — Tom only; no autonomous push under any
   circumstance (Phase 8 Run F, 2026-05-08)."

Precedent for a PROPOSAL-ONLY governance doc that authorizes nothing:
docs/phase8/deprecation/ACTIVE_SURFACE_REDUCTION_PLAN.md.
-->

# ADR-001 — Graduated Autonomy for Push, Merge, and Deploy

- **Status:** PROPOSED (awaiting Tom ratification via `CLAUDE.md` amendment)
- **Date:** 2026-06-13
- **Deciders:** Tom (sole ratifier). Drafted for review.
- **Supersedes (on ratification only):** the absolute clause in `CLAUDE.md` →
  Write boundaries → "`git push`, merge, deploy — Tom only; no autonomous push
  under any circumstance (Phase 8 Run F, 2026-05-08)."
- **Related:** `EXECUTION_POLICY.md` (Approval thresholds; Frozen flags log),
  `AI_BRAIN_ROUTER.md` (input classification), `VERDICT_GLOSSARY.md`,
  commands `/release-check`, `/production-go-no-go`, `/integration-dry-run`,
  `/gate-close`.

---

## 1. Context

Today every `git push`, merge, and production deploy requires Tom. The goal of
this ADR is to permit **bounded autonomous push and deploy** — safely, and only
for change classes where the cost of error is reversible and internal.

**Why the current lock exists (and is correct today).** Four incidents on the
live system establish that the mechanical preconditions for safe autonomy are
not yet met:

1. **The trust-anchor self-check was vacuous.** `private_core.rebuild_verifier()`
   was found **stubbed to `return 0`** on the live DB; every nightly parity check
   passed vacuously. True drift on restoration: 32 keys. *(PR #70.)*
2. **Tests wrote to the production DB.** Test fixtures (`TEST-GR-RUNTIME`,
   LionWheel phase tests) polluted live, forcing a one-time physical purge — a
   deviation from the append-only locked decision. *(PR #70.)*
3. **The repo is not a faithful mirror of live.** Migrations merged but not
   applied; migrations applied but not committed; filename collisions in the
   deploy glob. Two divergent numbering sequences. *(PR #71.)*
4. **CI gated almost nothing.** 3 of 86 API test files ran; 166 pgTAP tests ran
   nowhere; the portal PR guard ran typecheck only. *(PR #51, #62.)*

**Reframing.** Autonomy is not "remove the human." It is **replace Tom's review
with mechanical gates that must be more trustworthy than that review.** The lock
is lifted by *earning the right* — making invariants un-fakeable and the repo a
faithful mirror — not by flipping a switch. Some change classes never become
autonomous because their error cost is irreversible or externally visible.

---

## 2. Decision — the autonomy ladder

Autonomy is graduated. Each level is enabled independently and only after its
preconditions (§4) are met and proven.

| Level | What becomes autonomous | Human role |
|---|---|---|
| **L0** | nothing | Tom does push, merge, deploy |
| **L1** | push to a `claude/*` feature branch + open **draft** PR | Tom merges |
| **L2** | **merge to `main`** of LOW-RISK, reversible classes (docs, tests, portal copy/UI behind no schema change) when all gates green | Tom audits after |
| **L3** | **deploy to production** of code only (no schema, no data) behind a feature flag, with automatic rollback on health regression | Tom audits after |
| **L4** | **schema migrations** — additive / forward-only / reversible only — with shadow verification | Tom audits after |
| **L5** | data-affecting ops, frozen-flag flips, external-system writes | **never autonomous** |

**Current real-world state:** L1 is already in effect (this very PR; the existing
`claude/*` draft PRs). This ADR's near-term target is **L2 → L3**. L4 is a later,
cautious step. **L5 is permanently human.**

### 2.1 What stays human forever (L5 — non-negotiable)

Consistent with the boot-kernel non-negotiables, these never become autonomous
at any level:

- Any write to `stock_ledger` or any stock-truth-impacting operation.
- Frozen-flag flips (`LIONWHEEL_FG_OUT_BRIDGE_ENABLED`,
  `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`).
- External-system writes (Shopify inventory, Green Invoice, LionWheel POST/PUT/DELETE).
- Any edit to `CLAUDE.md`, or any change that relaxes a locked decision.

Rationale: autonomy targets **code and configuration**, never **truth** and never
**the outside world**.

---

## 3. The gates already exist — autonomy reuses them

This ADR invents no new verification machinery. It makes the **existing
human-invoked gate commands run mechanically**, and treats their PASS verdict as
the authorization that today comes from Tom's eyes:

| Autonomy step | Existing gate | Authorizing verdict |
|---|---|---|
| L2 merge to `main` | `/release-check` (`release-verifier`) | `SAFE_FOR_HUMAN_REVIEW` → becomes `SAFE_TO_MERGE` |
| L3 production deploy | `/production-go-no-go` (`factory-os-governor`) | `PROCEED` (never `PROCEED_WITH_CONSTRAINTS`) |
| L4 migration deploy | `/gate-close` evidence + `/production-go-no-go` | `PROCEED` + shadow-parity proof |
| L5 (any) | `/integration-dry-run` → **Tom** | `READY_FOR_*_REQUEST` → human flip only |

A non-`PROCEED` verdict, a `CONDITIONALLY_SAFE`, or any `HOLD` halts autonomy and
falls back to L1 (draft PR for Tom).

---

## 4. Preconditions (the safety stack)

No level is enabled until its preconditions are built **and proven**. These are
the same P0/P1 items already identified in the architecture review; autonomy is
their payoff, not a parallel track.

**Gate A — Un-fakeable invariants (blocks L2+).**
- A canary fixture that `rebuild_verifier()` MUST report as non-zero; alarm if it
  ever returns 0 on the canary. Closes incident #1.
- Every invariant in the boot kernel has a test that fails loudly when violated.

**Gate B — Environment isolation (blocks L2+).**
- Tests run against a disposable / branch database (Supabase branching). Zero test
  writes reach production. Closes incident #2.

**Gate C — Repo = live mirror (blocks L3+).**
- CI check: live `schema_migrations` ≡ `db/migrations/` filenames; deploy fails on
  drift. Filename-glob ordering replaced by a manifest with checksums. Closes #3.

**Gate D — CI is the real gate (blocks L2+).**
- Full suites run and block: API node tests, the 166 pgTAP, portal Vitest,
  Playwright critical paths. Quarantine list shrinks on a schedule, never grows.
  Closes incident #4. (PRs #51, #62 are the start.)

**Gate E — Observability + tested rollback (blocks L3+).**
- Reachable post-deploy health/smoke check (today `/health` is not reliably
  reachable from the exec env — #34, #71).
- Automatic rollback on health regression, and the rollback path is itself tested.

**Gate F — Blast-radius bounding (blocks L3+).**
- Every autonomous deploy ships behind a feature flag and rolls out to a slice
  first. Generalize the proven `SHOPIFY_LIVE_SCOPE_SKU_ALLOWLIST` / Gate-E
  "one SKU at a time" pattern (#34) into a deploy-plane canary.

**Gate G — Audit + kill switch (blocks all autonomy).**
- Every autonomous push/merge/deploy writes an append-only record
  (what / why / gates passed / rollback point) — same discipline as the ledger /
  `maintenance_log`.
- A single global kill switch (`AUTONOMY_ENABLED=false`) revokes all autonomy
  instantly. A daily budget (max N autonomous merges) and auto-pause on any
  rollback act as a dead-man's switch.

---

## 5. Governance change required to ratify

This ADR is inert until **all** of the following are done by their owners:

1. **Tom** amends `CLAUDE.md` → Write boundaries, replacing the absolute clause
   with a bounded one. Proposed text:

   > `git push`, merge, deploy — bounded autonomy permitted within levels L1–L3
   > per `docs/decisions/ADR-001-autonomous-push-and-deploy.md`, governed by the
   > mechanical gates therein. L4 requires explicit per-tranche Tom approval.
   > L5 classes (stock-truth writes, frozen-flag flips, external-system writes,
   > edits to this file) remain human-only under all circumstances. A global
   > `AUTONOMY_ENABLED=false` kill switch overrides all of the above.

2. **`ops-docs-curator`** (under `factory-os-governor` approval) updates
   `EXECUTION_POLICY.md` → Approval thresholds: add the L1–L4 rows; keep
   `git push` "explicit instruction" semantics for any class not yet enabled;
   keep all L5 rows human. Add `AUTONOMY_ENABLED` to the Frozen flags log with the
   same four-prerequisite discipline (Tom written + dry-run + ≥24h soak +
   RUNTIME_READY) for each level's first enablement.

3. **`AI_BRAIN_ROUTER.md`** gains a `risk-tier → autonomy-level` map so each
   input is classified LOW / MEDIUM / HIGH / FORBIDDEN and routed to the highest
   permitted level (or to L1 draft-PR fallback).

4. **`VERDICT_GLOSSARY.md`** adds `SAFE_TO_MERGE` and `AUTONOMY_HALTED`.

Until step 1 is done, the current lock stands in full and this document changes
nothing.

---

## 6. Rollout sequence (recommended)

1. Build **Gate A + Gate B** (canary + env isolation).
2. Build **Gate C + Gate D** (mirror check + real CI).
3. Ratify §5; enable **L2** with a ≥24h soak and the kill switch live.
4. Build **Gate E + Gate F** (health/rollback + canary deploy).
5. Enable **L3** with a ≥24h soak.
6. Defer **L4** until L3 has run clean for a defined window; enable per-tranche.

---

## 7. Consequences

**Positive.** Less operator babysitting; faster delivery on the safe majority of
changes; the invariant-hardening work (which is needed regardless) gets a
forcing function; gates become mechanical and auditable instead of dependent on
one person's attention.

**Negative / risks.** Mechanical gates can themselves rot (the `return 0`
lesson) — hence Gate A canaries and Gate G audit are mandatory, not optional. A
mis-classified change could be merged autonomously — hence the conservative
default (anything not provably LOW/MEDIUM falls to L1) and the kill switch.
Building the safety stack is real work; until it exists, the answer to
"enable autonomy now?" is **no**.

---

<!--
This ADR authorizes nothing. It is a proposal for Tom's review. Ratification
requires the CLAUDE.md amendment in §5.1. The existing locked decision stands
until then.
-->
