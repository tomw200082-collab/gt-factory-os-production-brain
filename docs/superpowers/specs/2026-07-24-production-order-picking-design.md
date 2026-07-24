# Production Order Picking — Design Spec ("מעגל פקודת הייצור")

> **Date:** 2026-07-24 · **Status:** DRAFT — pending Tom written approval via PR review
> **Origin:** Tom-directed grill interview, session 2026-07-24 (9 questions, all answered by Tom in writing).
> **Supersedes (on approval):** the consumption-side of locked decision "Production reporting v1"
> (`docs/decisions/LOCKED_DECISIONS.md` §Production reporting v1, line "Do not collect manual
> per-component actual consumption in v1"). Amendment text ships in the same PR.
> **Adopted-in-principle precedent:** factory mapping 2026-07-22 — "מעגל פקודת הייצור: מאמצים".

---

## §G — Goal (one line)

Denis opens today's production runs from the plan, picks liquids once per base tank and
packaging per SKU via tap-per-row with prefilled BOM quantities (editable), and on pick
confirmation stock decrements from the ledger; the end-of-run report shrinks to
output + scrap + QC.

## Done / observable

- After a pick confirmation, projected RM/PKG stock equals shelf reality for the picked
  components (verifiable against rebuild-from-ledger).
- Denis reaches an active picking screen from cold app-open in ≤ 2 taps.
- A full clean pick (no exceptions) of ~15 rows takes < 30 seconds.
- Every deviation (shortage / excess / not-collected / unplanned run) produces a flag Tom
  can see without asking.

---

## §C — Decisions (all Tom-approved in writing, 2026-07-24)

### Entry & navigation
- Daily run list derives from `production_plan` — one tap to enter a run; no search, no typing.
- List is ordered by physical work order: "1. Prepare tank X → 2. Fill product A → 3. Fill product B".
- "Unplanned production" button: pick item + target qty → run tagged `UNPLANNED` → immediate
  flag to Tom (inbox/push) → picking proceeds without blocking. Tag persists for retro review.

### Picking structure (mirrors the two-head BOM)
- **Two-stage:** liquids (BASE head) picked **once per base tank/batch**; packaging (PACK head)
  picked **per SKU** filled from that tank. Single-head items (REPACK / pure-pack) get one screen.
- Each pick confirmation is a **separate event with its own actor** (who confirmed). Nothing in
  code assumes the same worker performs both stages — prepared for a future packaging worker.
  **Today: one unified UI, Denis does both.**

### Screen & gesture
- Row = floor name (large) + Hebrew name (small) + required qty + unit.
  Tap row = ✓ "collected as stated". Tap the number = edit → auto-✓ with edited qty.
- Liquids grouped top, packaging bottom (per-stage screens make this natural).
- "Done collecting" enables only when every row is resolved (✓ / edited / "Not collected — 0").
  This is the single deliberate gate in the flow; everything else is optional (see below).
- Language: **simple English only** (weak-English reader level; short words, no jargon).
  No Hebrew UI, no Russian toggle. All strings live in one dictionary file
  (`en` field per label) so a later language remains a contained job — not built now.
- Word-poor UI: lean on numbers, units, ✓, color + icon (never color alone — color-vision
  deficiency affects ~1 in 12 men), item photos in phase 2.

### Stock truth
- **Stock decrements at pick confirmation (start of production)** — not at the end report.
- Post-confirmation corrections: "+ Add material" / "Return" actions on an active run append
  **delta ledger rows**. Confirmed picks are never edited (append-only doctrine).
- **Physical truth wins, system raises flags:**
  - Shortage: Denis edits qty down to actual → row tagged "Missing" → on confirm, an automatic
    **shortage event** to Tom (item, gap, run). No hard block; batch-stop remains Denis's call
    (existing playbook authority).
  - Excess vs system stock: allowed; discrepancy recorded as a **count signal** (projection was
    wrong — exactly the truth this tool exists to surface).
  - Skipped component: explicit "Not collected — 0", never a silent blank.
- Cancelled batch → reversal rows (existing ledger doctrine; no new rule).

### End-of-run report (reshaped)
- Shrinks to: **output qty + scrap qty + QC + notes**. It no longer computes or posts
  component consumption (consumption already happened at pick time + deltas).
- Output/scrap still post `PRODUCTION_OUTPUT` / scrap audit rows as today.

### Governance
- Supersedes "Do not collect manual per-component actual consumption in v1" — amendment to
  `docs/decisions/LOCKED_DECISIONS.md` ships in this PR; **Tom's PR approval = written approval**.
- Portal UI-language exception list is **not** extended (surface is English).

---

## Resolved open items (Tom delegated 2026-07-24: "decide for me; nothing mandatory so nothing blocks Denis")

### 1. QC fields on the end report — all optional
Industry batch-record practice for beverages centers on Brix (sugar/dissolved solids), pH
(safety + stability), sample traceability, and free notes; records typically carry batch id,
reading values, and sample time. Adopted, minimal form:

| Field | Type | Mandatory? |
|---|---|---|
| Brix | number (°Bx, one decimal) | No |
| pH | number (one decimal) | No |
| Sample taken | toggle | No |
| QC note | short text | No |

- Fields appear on runs with a BASE head (liquid batches); pack-only runs hide Brix/pH.
- A report with zero QC fields still submits — QC completeness is surfaced as a gentle
  weekly gap metric to Tom, never a submit block. (Mapping 2026-07-22 `[qc_brx_ph]` assigns
  Brix/pH + samples to Denis's station — the fields land where he already works.)
- Meter calibration tracking: out of scope v1 (paper/routine), revisit only if QC data
  becomes decision-driving.

### 2. Device — device-agnostic touch-first web
No native app, no new hardware decision. The surface is a responsive portal page tuned for
touch: targets ≥ 60px with generous spacing (industrial-UI guidance for gloved/fast use;
consumer 44px is the floor, not the target), no hover-dependent interactions, minimal typing
(numeric keypad only when editing a qty). Works on Denis's phone today and any future
station tablet unchanged. Auth: existing portal login (operator role); session length for
floor use handled at implementation (long-lived session on his device).

### 3. Route & nav placement
- `/production` — today's run list. **Becomes the operator-role landing surface** (operator
  logs in → sees today's work immediately; ≤ 2 taps to an active pick list).
- `/production/runs/[run_id]` — picking screen (stage-aware: tank pick or pack pick).
- `/production/runs/[run_id]/report` — end report (output + scrap + QC).
- Admin/planner nav gets a "Production" entry pointing at the same list (read + oversight).

### 4. Floor-name backfill
- New nullable `floor_name` (Latin script) on RM/PKG items, editable in item master.
- At implementation, Claude generates a full draft mapping (every active RM/PKG component →
  proposed English floor name) delivered as a reviewable list for Tom's one-pass approval;
  applied via normal item-master update path.
- Missing floor name → row shows Hebrew name + a coverage flag accumulates for Tom.
  Never blocks picking. Phase 2: `photo` on items, thumbnail per row.

### 5. Transition path for `/stock/production-actual`
- **Per-date cutover.** Go-live date D is set at deploy (deliberate, flagged step).
- From D: all production flows through `/production`. Old screen leaves primary nav.
- Old screen stays reachable (direct link, admin nav) for corrections on pre-D dates for
  30 days, then retires.
- **Double-consumption guard:** the reshaped report never posts consumption; the old screen,
  during the 30-day window, warns and blocks submission if a picking-flow run exists for the
  same item + date.

---

## §I — Surfaces (implementation sketch; backend-db lane finalizes contracts)

### Schema (sketch)
- `production_run`: id, plan_id (nullable — null ⇢ unplanned), item_id, base_batch_ref
  (nullable), target_qty, status `PLANNED → PICKING → IN_PRODUCTION → REPORTED`
  (finally animates the existing dormant `in_production` value), `unplanned` bool,
  created_by, timestamps.
- `production_run_pick`: run_id, component_id, required_qty (pinned BOM explosion),
  picked_qty, state `PICKED | EDITED | NOT_COLLECTED`, actor, confirmed_at.
- `items`: + `floor_name` text null; (phase 2: + photo).
- Ledger: new movement type `PICK_CONSUMPTION` (replaces `PRODUCTION_CONSUMPTION` for
  new-flow runs) + `MATERIAL_DELTA` add/return rows; `PRODUCTION_OUTPUT` unchanged.
- BOM pinning semantics carried over verbatim: pin PACK/BASE versions at pick-list open;
  reject stale submission (409 `STALE_BOM_VERSION` / `STALE_BASE_BOM_VERSION`).

### API (sketch)
- `GET  /api/production-runs/today` — plan-derived ordered list (tank → fills).
- `POST /api/production-runs` — unplanned run (item, qty) → flag event.
- `GET  /api/production-runs/:id/pick-list` — pinned explosion for the run's stage.
- `POST /api/production-runs/:id/pick-confirm` — idempotent; writes all `PICK_CONSUMPTION`
  rows in one transaction (`PK:<idem>:CONSUME:<source>:<component_id>` key pattern, mirroring
  the existing PA convention); emits shortage / count-signal events as needed.
- `POST /api/production-runs/:id/material-delta` — add/return single component.
- `POST /api/production-runs/:id/report` — output + scrap + QC; posts output rows only.

### Events → Tom
`SHORTAGE_AT_PICK` · `COUNT_SIGNAL` (picked > projected) · `UNPLANNED_RUN_CREATED` ·
`FLOOR_NAME_COVERAGE` (weekly rollup) · `QC_COMPLETENESS` (weekly rollup, gentle).

---

## §V — Invariants (verification targets)

1. `stock_ledger` stays append-only; every correction is a delta or reversal row. N/N parity:
   projection == rebuild-from-ledger after any pick/delta/report sequence.
2. `pick-confirm` is idempotent — double-tap / retry never double-consumes.
3. For any run: Σ(picked_qty) + Σ(deltas) == total consumption attributed to the run.
4. "Done collecting" is impossible while any row is unresolved.
5. Nothing beyond row-resolution is mandatory: QC empty, notes empty, floor names missing —
   all still submit. No new hard blocks anywhere in Denis's path.
6. Shortage / excess never block; each emits exactly one event.
7. Old screen cannot post consumption for an item+date that has a picking-flow run (window
   period), and the reshaped report never posts consumption at all.
8. Every pick confirmation records its actor; tank and pack confirmations are independent events.
9. All user-visible strings resolve from the single dictionary file; no hardcoded literals.

---

## Delivery slices (tranche-sized, in order)

1. **Backend foundation** (backend-db lane): schema + endpoints + ledger movement types +
   idempotency/parity/pinning tests (N/N reported).
2. **Portal — run list + picking** (portal lane, tranche per Portal OS rules): `/production`,
   picking screens, flags wiring, dictionary file, floor-name display + coverage flag.
3. **Portal — report reshape + cutover** : shrunk report + QC fields, per-date cutover,
   old-screen guard, nav changes, floor-name backfill review list to Tom.

Each slice lands with the boot-kernel evidence standard (files changed, N/N tests, contracts,
signals, rollback, next handoff). Production deploy + prod-DB migration remain deliberate,
explicitly-flagged steps.

## Research sources (open-item decisions)

- Batch-record QC practice (Brix/pH/sample traceability): usetorg.com "What is Batch
  Manufacturing Record", tandobeverage.com "How Brix & pH Guarantee Beverage Consistency",
  inspectionmanaging.com "Quality Control in the Beverage Industry", liquorlogic.co.za
  "Alcohol Quality Testing".
- Floor-UI guidance (≥60px targets, spacing, no hover, minimal typing, color+icon):
  fuselabcreative.com "Manufacturing Dashboard UX", Bouguern "UX in Manufacturing" (Medium),
  emixa.com "UX in Manufacturing".

---

**Approval line:** Tom's approval of the PR containing this file + the LOCKED_DECISIONS
amendment constitutes the written approval required to supersede the v1 consumption rule.
Until merged, this document is a proposal and no product code may be written against it.
