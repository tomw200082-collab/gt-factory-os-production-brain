# GT Factory OS — Execution Policy

> **Authority layer:** operational governance for autonomous execution. Mirrors [factory-os-autonomous-builder SKILL.md](C:/Users/tomw2/.claude/skills/factory-os-autonomous-builder/SKILL.md) §4.3 / §4.4 / §5.1 / §7.3 / §9.
>
> **Sibling docs (in this directory):**
> - `claude.md` (CLAUDE.md) — durable contract. Locked architecture and non-negotiables.
> - `CURRENT_STATE.md` — volatile runtime status.
> - `ACTIVE_NOW.md` — short, fast-moving operator context.
>
> **Authority rule:** this file is an **operator-facing mirror** of the skill. **If this file diverges from the skill, the skill wins.** Update both together. This file cannot relax a locked decision in CLAUDE.md.

---

## Purpose
Autonomous build work on GT Factory OS runs under a standing-order model: once scope is locked, lanes proceed on pre-authorized backlogs without per-item operator re-authorization, bounded by the mode and constraint rules below. The goal is less operator babysitting without sacrificing stock-truth discipline.

## Window ownership (locked)

| Window | Owns | Hard limit |
|---|---|---|
| **W1 — DB / Schema / Migrations / Tests / Imports** | schema, migrations, pgTAP/tests, imports, fixture validation, runbooks, Gate 3 runtime closure | does not own UI; does not own integration contracts |
| **W2 — Canonical Portal / Production UI** | canonical portal UI, route tree, contracts-layer reconciliation, real admin/planner/operator surface | does not invent backend contracts; never adopts sandbox files literally |
| **W3 — Sandbox Portal / Mock UI** | experimental / mock / reference UI only; concepts and patterns | **never becomes canonical owner**; never owns production routes; never sources stock truth |
| **W4 — Integrations / Jobs / Exports / Dashboard Contracts** | LionWheel / Shopify / Green Invoice contract-first specs, jobs, exports, dashboard read-model contracts | must not invent core truth contracts owned elsewhere; must not write to ledger directly |
| **W5 — Architecture / Governance / Cross-Window Coordination** | orchestration, gating, overlap detection, stop conditions, rollout discipline, cross-window conflict resolution | does not implement features; routes work, does not perform it |

A move crossing a window boundary without explicit W5 approval is an **`ownership_conflict`**.

## Standing-order policy

**Global rule:** at most **three active lanes** at any time. The active set is **W1 + W2 + W4**. **W5 is service-on-demand**, not a continuously active lane.

### W1 — critical path (always-on)
Owner of db / schema / migrations / tests / imports / verification / Gate 3 runtime closure. Lane ownership and the 1→2→3 retry policy are unchanged. W1 emits `RUNTIME_READY(form)` when backend closure for a named form is sufficient for W2 to begin canonical authoring on that form.

### W2 — two modes gated by `RUNTIME_READY(form)`

- **Mode A** (default; active while no `RUNTIME_READY(form)` is in effect):
  - **Allowed:** read-only audits; canonical pattern extraction; handoff-prep docs; portal convention docs; local inspection that writes no portal code.
  - **Forbidden:** contract authoring; canonical authoring for Waste / Adjustment or Physical Count; reopening Goods Receipt.
- **Mode B** (automatically authorized on `RUNTIME_READY(form)`, scoped to that one named form):
  - **Allowed:** canonical portal authoring for the named form only. No re-authorization from the operator is required to switch Mode A → Mode B once `RUNTIME_READY(form)` is emitted.
  - **Exit:** return to Mode A after local portal E2E is green for that form.

Mode B does **not** generalize to other forms. A new `RUNTIME_READY(other_form)` is required for each additional form.

### W2 — Mode B-AMMC — RETIRED 2026-05-08 (Phase 8 Wave 0)

**Status:** RETIRED. Closure condition met: `gt-factory-os/docs/checkpoints/ammc_v1_closure.md` exists (path moved to the docs/checkpoints/ subdirectory in PR #21 docs hierarchy). AMMC v1 §G.7 wizard + integration + verification is closed. Per the original expiry clause, this amendment terminated automatically on closure-doc landing. The full text is preserved in §Legacy amendments (retired) at the end of this file. Subsequent admin-master surface work returns to standard Mode B with per-form `RUNTIME_READY`.

### W2 — Mode B-Portal-Refactor (portal-wide substrate, route-tree, and truthfulness authoring)

**Amendment dated 2026-04-21 (Tom-authorized; unblocks Round-3 portal-full-production-refactor plan). Introduces a second pan-form W2 authoring carve-out alongside Mode B-AMMC. Where Mode B-AMMC scopes `/admin/**` authoring under `crystalline-drifting-dusk.md`, Mode B-Portal-Refactor scopes pan-portal substrate + route-tree + truthfulness authoring under `portal-full-production-refactor.md`.**

**Activation:** W2 may enter Mode B-Portal-Refactor when ALL of the following hold:
1. A Tom-approved plan file at `C:/Users/tomw2/.claude/plans/portal-full-production-refactor.md` exists and explicitly names portal-full-production-refactor as in-scope (the plan codifies Rounds 1–3 of the portal-rebuild ping-pong dialogue).
2. The dispatch cites the plan's specific tranche section (§C through §K, i.e., Tranche A through Tranche I per the plan's numbering).
3. No `contract_failure` or `assumption_failure` is open on portal-full-production-refactor prerequisites.

**Allowed under Mode B-Portal-Refactor:**
- Canonical portal authoring across all production-portal surfaces simultaneously within a single dispatch, scoped to the cited tranche:
  - `/dashboard` (control tower — Tranche C)
  - `/inbox` (unified triage — Tranche B)
  - `/stock/**` (operator form family — Tranches A, D, F)
  - `/planning/**` (forecast + runs + recommendations review — Tranches A, D)
  - `/purchase-orders/**` (PO list + detail — Tranches A, D)
  - `/admin/**` (all master-data + integrations + users + jobs + signals — Tranches A, D, E, F, G)
  - layouts under `src/app/**/layout.tsx`
  - auth surfaces (`/login`, `/auth/callback`) for role-gate wiring only
- Route normalization: domain-first URL moves; route-group filesystem reorganization; legacy/quarantined/mock route deletions
- Shared substrate authoring: `src/lib/api/client.ts`, `src/lib/auth/authorize.ts`, `src/lib/nav/manifest.ts`, `src/components/patterns/{ListPage,DetailPage,FormPage}.tsx`
- Dev-shim vestige cleanup: delete `X-Fake-Session` forwarding from client fetches; rename `FakeSession` → `Session` in client pages; remove internal milestone names ("Slice", "Phase", "MVP", "endgame") from user-visible UI strings
- CI lint guards against route-group leakage into URL strings
- Portal proxy routes (mirrors of upstream backend contracts — **mirror only**, no contract authorship)
- Consumes W1-authored backend; consumes W4 contract packs verbatim — **does not author backend code**

**Forbidden under Mode B-Portal-Refactor:**
- Any backend authorship (`api/src/**` writes remain W1-owned; any change there requires explicit W1 dispatch)
- New migrations, schema changes, handler stacks
- Invented backend contract values (if a portal hook needs a value not in upstream schemas, emit `assumption_failure`)
- Sandbox-to-canonical file promotion (`window2-portal-sandbox` IS the canonical portal per Tom's ruling; this rule still forbids literal copies from any other sandbox surface)
- Touching `.env*`, credentials, or secrets
- Touching `.claude/state/runtime_ready.json` (W1-owned signal registry)
- Editing prior entries in `.claude/state/active_mode.json` (W2 writes its own current-mode entry and appends history; does not rewrite prior rows)
- Splitting Tranche A into partial commit sets ("substrate first, truthfulness later" is explicitly forbidden by the plan § C)

**Exit:** Mode B-Portal-Refactor exits **per-tranche**. Each tranche within the plan is a separate exit boundary. For each dispatched tranche:
- The tranche's validation gate (per plan §C.2, §D.x, …) must pass: typecheck, build, lint (if available), Playwright real-HTTP smoke on touched surfaces, role-matrix walkthrough, and any tranche-specific evidence listed in the plan.
- `active_mode.json` records mode exit (W2 writes its own exit row).
- Between tranches, mode returns to A.
- Tranche dependencies are strict: a tranche cannot be dispatched unless its predecessor per the plan has landed.

**Expiry:** this amendment terminates automatically on portal-full-production-refactor plan Tranche I closure (commit boundary: whichever commit authors `docs/portal_refactor_tranche_i_closure.md` in `window2-portal-sandbox`). Subsequent portal work post-Tranche-I returns to standard Mode B with per-form `RUNTIME_READY` or to future dedicated amendments.

**Precedent reconciliation:** this amendment does NOT retroactively cover the 2026-04-21T00:00 production-cutover-phase-2 cycle or the 2026-04-21T02:00 Phase 4 HALT. Those remain on record as policy-stretched / policy-blocked per their `active_mode.json` rows. Forward-only authorization.

**Coexistence with Mode B-AMMC:** the two amendments can coexist. Per-form Mode B and Mode B-AMMC (for `/admin/**` under `crystalline-drifting-dusk.md`) remain available outside portal-full-production-refactor dispatches. Only one mode-B-variant may be active at a time; W2 remains a single-lane.

### W2 — Mode B-Planning-Corridor (planning-corridor production-facing surfaces)

**Amendment dated 2026-05-02 (Tom-authorized in response to overnight Ralph Loop cycle 1 governance question Q1). Introduces a third pan-form W2 authoring carve-out alongside Mode B-AMMC and Mode B-Portal-Refactor. Where Mode B-AMMC scopes `/admin/**` under `crystalline-drifting-dusk.md`, and Mode B-Portal-Refactor scopes pan-portal substrate/route-tree under `portal-full-production-refactor.md`, Mode B-Planning-Corridor scopes the production-facing planning corridor under Tom's overnight Ralph Loop directive 2026-04-30 + 2026-05-01 + 2026-05-02.**

**Activation:** W2 may enter Mode B-Planning-Corridor when ALL of the following hold:
1. The dispatch cites the active "Planning Corridor v1 (baseline 2026-04-30)" tracked in `CURRENT_STATE.md`.
2. The target surface is one of the production-facing planning corridor surfaces enumerated under "Allowed" below, OR is a navigation/dashboard quick-link that connects two corridor surfaces.
3. No `contract_failure` or `assumption_failure` is open on planning-corridor prerequisites.
4. The dispatch names the specific P0/P1 audit finding(s) being closed (per `PRODUCTION/docs/overnight_audit_2026-05-01.md`) OR the specific cycle deliverable per the overnight directive's tonight-priority list.

**Allowed under Mode B-Planning-Corridor:**
- Canonical portal authoring on the following production-facing planning corridor surfaces:
  - `/planning/production-plan` (Daily Production Plan board)
  - `/ops/stock/production-actual` (Production Actual form — once `RUNTIME_READY(ProductionActual-FromPlan)` is emitted, the from_plan_id UX is in scope)
  - `/planning/runs` (Planning Runs list)
  - `/planning/runs/[run_id]` (Planning Run detail)
  - `/planning/runs/[run_id]/recommendations/[rec_id]` (Recommendation drill-down)
  - `/planning/forecast/[version_id]` (Forecast version detail)
  - `/planning/blockers` (Tranche 3 blockers worklist — Hebrew page-title `חסמים בתכנון` is Tom-locked per CURRENT_STATE.md; English/LTR rule does NOT apply to this surface)
  - `/planning/inventory-flow` (Inventory Flow board) — read-only normalization only
  - `/dashboard/v2` (Control-tower v2 morning-view page — added 2026-05-02 per DCT2-8 default and dashboard control-tower v2 spec; consumes `RUNTIME_READY(DashboardCriticalToday)` signal #23 + `RUNTIME_READY(DashboardSlippedPlans)` signal #24 + future per-block RUNTIME_READY signals for §4.2/§4.3/§4.5/§4.6/§4.7/§4.8/§4.9; existing `/dashboard` 7-block page remains untouched)
  - Navigation manifest entries connecting the above (`src/lib/nav/manifest.ts`)
  - Dashboard Quick Actions block when adding/editing links to corridor surfaces
- English-only, LTR-only normalization (per Tom's portal-wide standard locked 2026-05-01)
- Wiring to already-approved API endpoints (current contract pack + signal #18)
- Removing raw IDs / JSON / SQL / enum codes from primary UI
- Mobile @ 390px UX hardening on corridor surfaces
- Empty/loading/error state hygiene on corridor surfaces
- Source/freshness display on existing-data surfaces
- Dead-end fixes on corridor navigation paths
- Consumes W1-authored backend; consumes W4 contract packs verbatim — **does not author backend code**

**Forbidden under Mode B-Planning-Corridor:**
- Any backend authorship (`api/src/**` writes remain W1-owned; cross-lane bundling requires explicit W1 dispatch)
- New migrations, schema changes, handler stacks
- Invented backend contract values (if a portal hook needs a value not in upstream schemas, emit `assumption_failure`)
- Changing stock_ledger semantics, current_balances triggers, planning engine logic, or A3/A4 locked invariants
- Changing auth / role model
- Changing external integration authority
- Surfaces outside the enumerated list above (admin surfaces stay under Mode B-AMMC; portal substrate stays under Mode B-Portal-Refactor; per-form RUNTIME_READY surfaces remain available outside this amendment)
- Touching `.env*`, credentials, or secrets
- Touching `.claude/state/runtime_ready.json` (W1-owned)
- Editing prior entries in `.claude/state/active_mode.json` (W2 writes its own current-mode entry and appends history; does not rewrite prior rows)

**Exit:** Mode B-Planning-Corridor exits **per-tranche**. Each named P0 closure cycle is a separate exit boundary. For each dispatched tranche:
- Validation gate must pass: typecheck, build, route lint (if available), and the cycle-specific evidence (live-API smoke / mobile probe / role-matrix where applicable).
- `active_mode.json` records mode exit (W2 writes its own exit row).
- Between tranches, mode returns to A.
- A second tranche cannot dispatch until the prior tranche's exit row lands.

**Expiry:** this amendment terminates automatically when all 11 P0 audit findings on planning corridor surfaces (per `PRODUCTION/docs/overnight_audit_2026-05-01.md` §16) are CLOSED-and-verified, OR when Tom dispatches an explicit termination. Subsequent planning corridor work post-expiry returns to standard Mode B with per-form `RUNTIME_READY`.

**Coexistence with Mode B-AMMC and Mode B-Portal-Refactor:** all three amendments can coexist as policies; only one mode-B-variant may be ACTIVE at a time. W2 remains a single-lane.

### W1 — Mode B-LionWheel-Runtime-Closure — RETIRED 2026-05-08 (Phase 8 Wave 0)

**Status:** RETIRED. Closure condition met: cycle 19 closed via commit `3ac1964` "feat(lionwheel): runtime closure — back-fill + exception related_entity_id + empty-string SKU rejection + bundle-map contract commit (cycle 19 carve-out, signal #30)". Active mode history (`active_mode.json`) further evidences cycles 20, 21 closing after cycle 19. Per the original expiry clause, this single-cycle carve-out terminated automatically on cycle 19 closure. The full text is preserved in §Legacy amendments (retired) at the end of this file. Any post-cycle-19 LionWheel runtime edit needs a fresh Tom dispatch with an explicit carve-out — no rolling precedent.

### W4 — rolling standing-order requirements lane
Executes one artifact at a time in the pre-authorized backlog order:

1. Shopify FG sync contract-requirements spec
2. Green Invoice supplier-price evidence contract-requirements spec
3. Dashboard read-model requirements spec
4. Integration freshness / failure-surface requirements spec

**Per-artifact constraints (hard):** requirements-only, file-only, **no schema**, **no migrations**, **no mirror tables**, **no runtime code**, **no handlers**, **no jobs**, **no invented provider field names**, **no endpoint invention**, **no auth-mechanics invention**, **no reopening of locked project decisions**.

#### Pre-write fresh-read protocol (FR1→write→FR2 bracket) — MANDATORY

**Scope (when this protocol applies).** Any W4 artifact — new file or edit to an existing file — that references `db/migrations/` filenames by number, OR that implies a "next free migration number" claim, OR whose correctness depends on the current state of the migrations directory. Illustrative examples (not an exhaustive enumeration): a handoff pack that names a target migration path such as `NNNN_orders_mirror.sql`; a contract that cites a "target migration `NNNN_*.sql`"; an integration spec that asserts "the mirror lives at the next available migration slot". Out of scope: requirements-only specs that name no migration file and make no numbering claim — do not apply this protocol to non-numerical references.

**The bracket has three phases.**

1. **FR1 — pre-write fresh-read.** IMMEDIATELY before opening the artifact for write, run `ls -la C:/Users/tomw2/Projects/gt-factory-os/db/migrations/` and capture the full filename listing plus the mtime of the latest file. If any migration filename collides with a number the artifact is about to reference, OR if any unexpected migration file appeared since the prior cycle's verifier run, **HALT IMMEDIATELY** and emit `contract_failure` to the governor. Do NOT silently substitute renumbered targets — silent renumber substitution is `assumption_failure`.

2. **WRITE the artifact.** The write must complete within **60 seconds** of the FR1 capture timestamp. If the FR1→write-end window exceeds 60 seconds, abort the write, discard the in-flight artifact state, and restart the bracket from a fresh FR1.

3. **FR2 — post-write fresh-read.** IMMEDIATELY after the last `Edit` / `Write` tool call on the artifact, re-run `ls -la C:/Users/tomw2/Projects/gt-factory-os/db/migrations/`. If any new migration file appeared between FR1 and write completion, **HALT** and emit `contract_failure` to the governor: the artifact is stale on landing because W1 raced the bracket.

**Two-try ceiling (cross-reference: `.claude/SIGNALS.md`).** The two-try retry ceiling defined in `.claude/SIGNALS.md` applies inside this bracket. A second FR1 collision OR FR2 race detection on the same artifact within the same cycle = `TOOL_FAILURE_UNCLEARED` per the existing W4 variant: park the artifact and escalate to the governor. Do not attempt a third bracket.

**Failure-class semantics (cross-reference: `.claude/SIGNALS.md` "Five failure classes (locked)").** An FR1 collision OR an FR2 race detection emits `contract_failure` (failure class 1: no retry, human checkpoint mandatory). A silent renumber substitution by the executor — i.e., quietly bumping a referenced migration number to dodge a collision instead of halting — emits `assumption_failure` (failure class 4: no retry, human checkpoint mandatory). A repeat FR1/FR2 collision on the same artifact within the same cycle escalates to `TOOL_FAILURE_UNCLEARED` (status marker inside failure class 3, `tool_failure`).

**Why this protocol exists.** Cycles **3, 4, 5, and 5c** of the GT Factory OS rebuild produced a recurring W1↔W4 timing race: autonomous W1 migration landings invalidated W4 renumber math mid-flight. Cycle 5 produced a `contract_failure` on a W4 handoff pack whose referenced target migration number had been claimed by a W1 landing during W4 authoring. Cycle 5c's surgical fix was itself partially stale by 6 minutes when a follow-on W1 migration landed during the fix window. The FR1→write→FR2 bracket catches this race deterministically by bounding the write window and verifying the directory state on both sides of the write.

**Non-retroactive.** This protocol governs W4 artifacts authored or edited from this codification forward. It does not retroactively invalidate or re-classify any previously landed W4 artifact.

### W5 — service-on-demand
Invoked only for (a) approve / reject review of a landed artifact, (b) real ownership collision, (c) `contract_failure` or `assumption_failure` requiring arbitration, (d) explicit execution-map revision request. W5 is not a continuously running lane.

## Signals

Signals flow from W1 outward. They are **not aliases**.

- **`FILE_READY(form)`** — file / surface readiness only. Relevant files, paths, or implementation surfaces exist in a usable handoff shape. **Does not authorize W2 canonical authoring.**
- **`RUNTIME_READY(form)`** — execution-authorization signal from W1. Backend / runtime contract for the named form is sufficiently closed and evidenced for W2 to begin canonical authoring for that one form only, under Mode B.
- **`TOOL_FAILURE_UNCLEARED`** — status marker on a W4 rolling-requirements artifact whose same tool failure has repeated after one retry. Parks the artifact; does **not** authorize silent continuation. Lives inside the `tool_failure` class — not a sixth failure class.

**Rule:** W2 moves from Mode A to Mode B **only on `RUNTIME_READY(form)`**, never on `FILE_READY(form)` alone.

> **`FILE_READY` may be necessary, but is not sufficient, for W2 authoring authorization.**

Edit discipline: preserve historical `FILE_READY` references where they genuinely denote file-surface readiness. Upgrade any older "go build" use of `FILE_READY` to `RUNTIME_READY`. Never alias the two terms silently.

## `TOOL_FAILURE_UNCLEARED` handling (W4 variant)

On a W4 rolling-requirements artifact:
- Retry once.
- If the same failure repeats, mark the **current artifact** `TOOL_FAILURE_UNCLEARED` and **park it**. The parked artifact stays parked until explicitly revisited.
- W4 may continue to the **next backlog item** only if **all** of the following hold:
  - no open `contract_failure`
  - no open `assumption_failure`
  - no dependency collision with the parked artifact
- If the dependency relationship is **unclear**, **escalate to the governor (W5)** rather than silently skipping ahead.
- Do **not** convert a single W4 tool failure into a reassessment of the whole project.

The 1→2→3 retry policy (retry / replan / human checkpoint) continues to apply unchanged to W1 critical-path work and to W2 canonical authoring under Mode B. A `contract_failure` or `assumption_failure` inside W4 collapses the W4 two-try budget to 0 and forces governor escalation.

## Artifact visibility rule (W5 review)

W5 may review an artifact only when one of the following is present:

1. the **full artifact text pasted inline** in the activation message, **or**
2. a **verified readable path** on disk (the path exists, the file is readable, and the content has been inspected, not merely named).

**Summary-only review is forbidden.** If only a summary, abstract, or second-hand description is available, do not render a PASS / APPROVE / REJECT decision — emit `assumption_failure` and request the full artifact or a verified path before continuing.

## No-dead-air rule

A response must **never** end with all lanes parked and no next action for Tom. If every lane is parked, blocked, or awaiting upstream input, the "What the user must do" section must still name the **single smallest concrete operator action** that moves the system forward — e.g., "paste the W1 checkpoint for migration X", "supply LionWheel sandbox credentials", "approve or reject landed artifact Y", "confirm the auth-method UNRESOLVED item". Silence, "waiting", or "all lanes idle" are **not** valid output states.

## Per-window reply mode

If the activation message contains updates from **more than one window**, the reply must emit a **separate reply block per window** (clearly labeled `Reply for W1`, `Reply for W2`, `Reply for W4` as applicable), and the operator action must close with **one overall next action for Tom** that reconciles across the per-window blocks (for example, which lane to unblock first, or which governor decision resolves the cross-window dependency).

## Window-label sanity check

If a pasted message carries a window label that does not match the actual surface touched (e.g., labeled "Window 2" but content is W4 integration work, or labeled "Window 1" but content is a W2 portal change), **correct the window classification before any routing, contract check, or reply drafting.** Record the relabel explicitly: "message labeled WX → reclassified as WY because <reason>". Never pass a mislabeled window through to later steps.

## Stop semantics

Any of the following halts the standing order for the affected lane and forces governor arbitration:

- stop condition
- ownership collision
- `contract_failure`
- `assumption_failure`
- W4 `TOOL_FAILURE_UNCLEARED` with unclear dependency

The standing-order policy does **not** override the failure taxonomy or human-checkpoint rules. Collapsing any of these into silent continuation is an anti-pattern.

## Global constraints (also locked in CLAUDE.md)
- no live integration runtime
- no DDL outside W1 ownership
- no auth wiring beyond locked decisions
- no dashboard runtime
- no planning runtime
- no W3 → canonical promotion
- no reopening of locked decisions
- MCP is not a runtime input channel
- Claude Code tooling must not become part of the live operational path

---

## Legacy amendments (retired)

> Amendments below were retired in Phase 8 Wave 0 (2026-05-08) after their per-amendment closure conditions were verified met. Full original text is preserved here as audit trail. Active policy lives in the §W2 / §W1 / §W4 sections above.

### W2 — Mode B-AMMC (RETIRED 2026-05-08; original text preserved)

**Original amendment dated 2026-04-21 (Tom-authorized); codified the pan-form W2 authoring carve-out previously invoked via per-slice Path C overrides during AMMC v1 build (cutover-phase-2 → slice 3/4/5 precedent).**

**Activation (now historical):** W2 may enter Mode B-AMMC when ALL of the following hold:
1. A Tom-approved plan file at `C:/Users/tomw2/.claude/plans/*.md` explicitly names AMMC as in-scope (the current approved plan is `crystalline-drifting-dusk.md` — AMMC v1 integrated design)
2. The dispatch cites the plan's §G slice number AND that slice is within §G.1-§G.7 of the AMMC v1 scope
3. No `contract_failure` or `assumption_failure` is open on AMMC prerequisites

**Allowed under Mode B-AMMC (now historical):**
- Canonical portal authoring across `/admin/**` surfaces (items, components, suppliers, supplier-items, planning-policy, sku-aliases, boms, products/[item_id] Product 360) in a single dispatch
- Pan-entity page + detail + wizard + drawer-stack components
- Portal proxy routes mirroring AMMC Slice-2 admin mutation endpoints
- Consumes W1-authored backend (mutations, readiness views, readiness GETs) — **does not author backend code**

**Forbidden under Mode B-AMMC (now historical):**
- Any non-`/admin/**` surface (operator forms, planner forms, dashboard, auth flow, sku-aliases alias workflow — all remain under individual Mode B or Mode A rules)
- Any backend authorship (`api/src/**` writes remain W1-owned; cross-lane bundling requires explicit W1 dispatch)
- New migrations, schema changes, handler stacks

**Original exit:** Mode B-AMMC exits when AMMC v1 §G.7 (Wizard + integration + verification) closes and `docs/ammc_v1_closure.md` lands.

**Original expiry:** this amendment terminates automatically on AMMC v1 closure (commit boundary: whichever commit authors `docs/ammc_v1_closure.md`). Further admin-master edits post-AMMC-v1 require either a new named mode amendment or standard per-form Mode B.

**Precedent reconciliation:** Slices 3, 4, 5 (primitives, list pages, detail + Product 360) were authored under Path C overrides before this amendment. This amendment retroactively codifies those as policy-compliant; no rollback or re-authorship required. Checkpoints `docs/ammc_slice3_primitives_checkpoint.md`, `docs/ammc_slice4_list_pages_checkpoint.md`, `docs/ammc_slice5_ui_checkpoint.md` were ratified.

**Phase 8 retirement evidence (2026-05-08):** closure doc found at `gt-factory-os/docs/checkpoints/ammc_v1_closure.md` (path moved to checkpoints/ subdir in PR #21 docs hierarchy). Closure condition met → amendment auto-expired.

---

### W1 — Mode B-LionWheel-Runtime-Closure (Cycle 19 only carve-out, 2026-05-02 — RETIRED 2026-05-08; original text preserved)

**Original Tom-authorization 2026-05-02 in response to cycle 18 W4 lane-ambiguity halt. Single-cycle bounded carve-out — does NOT broadly reopen the W1/W4 boundary.**

**Activation (now historical):** Cycle 19 dispatch only. Auto-expires when cycle 19 closes.

**Allowed files (W1 may edit, exclusively) (now historical):**
- `c:/Users/tomw2/Projects/gt-factory-os/api/src/integrations/lionwheel/reconciliation.ts`
- `c:/Users/tomw2/Projects/gt-factory-os/api/src/integrations/lionwheel/schemas.ts`
- `c:/Users/tomw2/Projects/gt-factory-os/api/src/integrations/lionwheel/sku_resolver.ts`
- `c:/Users/tomw2/Projects/gt-factory-os/api/src/integrations/lionwheel/poller.ts` — only if strictly necessary

**Original purpose:**
- Historical back-fill after alias creation (closes 11 JASM/PNMM rows + 2 AP-DRI rows)
- `related_entity_id` population on `lionwheel_unknown_sku` exceptions
- Empty-string SKU rejection if local + safe

**Forbidden under this carve-out (now historical):**
- Raw mirror semantic changes
- Bundle explosion in raw mirror
- A3 `v_planning_demand` changes
- A4 planning netting changes
- `stock_ledger` writes
- FG_OUT_PICK enablement
- Green Invoice calls
- Guessed alias mapping
- Autonomous resolution of ambiguous rows
- Broad runtime refactor

**Rationale (preserved):** historical W1 ownership of integration runtime signals #5 LionWheel + #10 GreenInvoice + #11 Shopify (per `runtime_ready.json` evidence_path docs); W4's agent file `executor-w4.md` forbids runtime code; W1's agent file forbids "W4 integration runtime" — both refusals are correct in spirit but leave a real gap. Tom's cycle 17 dispatch text named W4 as runtime owner; cycle 18 W4 correctly enforced its agent file. This carve-out resolved the ambiguity for cycle 19 only without changing either agent file.

**Original expiry:** automatic on cycle 19 closure. Subsequent LionWheel runtime work returns to standard lane discipline (W4 contracts, W1 schema/views/imports). Any post-cycle-19 LionWheel runtime edit needs a fresh Tom dispatch with explicit carve-out — no rolling precedent.

**Phase 8 retirement evidence (2026-05-08):** cycle 19 closure commit `3ac1964` "feat(lionwheel): runtime closure — back-fill + exception related_entity_id + empty-string SKU rejection + bundle-map contract commit (cycle 19 carve-out, signal #30)". Active-mode history shows cycles 20 and 21 subsequent and closed. Closure condition met → amendment auto-expired.

---

### Future Phase 8 lane-rename mapping note (informational)

Phase 8 (revision 2) plans to introduce production-named replacements for the build-era executor agents:
- `executor-w1` → `backend-db-executor`
- `executor-w2` → `portal-production-executor`
- `executor-w4` → `integration-boundary-executor`

The rename is **not** applied in Wave 0. It will land in Phase 8 Waves 3 + 5 (add-new-alongside, then refit EXECUTION_POLICY.md). Until then, all references in this file to `executor-w1` / `executor-w2` / `executor-w4` remain authoritative for the existing agent files. After Phase 8 Wave 5, this section will be expanded with a Legacy mapping table.