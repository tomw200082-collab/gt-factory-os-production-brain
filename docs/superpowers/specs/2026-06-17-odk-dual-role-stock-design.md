# Dual-Role Stock (Bought-Finished item also consumed in recipes) — Design Decision Record

> **Status:** PROPOSED — awaiting Tom decision. **BLOCKING:** requires Tom's **written sign-off on the locked-rule #4 interpretation** (below) before any data change ships (stop-condition #2).
> **Owner:** Tom · **Author:** Claude (9-agent design workflow, 4 architectures stress-tested) · **Touches STOCK TRUTH** (boot-kernel non-negotiable #1).
> **Scope:** design the GENERAL model for "bought-finished item that is ALSO consumed in production recipes"; **PILOT on ODK strawberry only**.

## Goal
The ODK strawberry concentrate is **one physical substance** but is modeled today as **two unlinked stock records**: a sellable finished good and a separate recipe ingredient. Make the physical pool **one truth** with **two consumers** drawing from it — **orders** (sales) and **recipes** (production) — without breaking the immutable ledger or the locked UOM rules.

## The problem (verified this session)
The same physical ODK exists as two records that do not talk:

| Role | Record | Table | Unit | Decremented by |
|---|---|---|---|---|
| Sold as FG | `ADD-ODK-STR-1L` "ODK STRAWBERRY 1L" (`BOUGHT_FINISHED`, barcode 8057724850369) | `private_core.items` | BOTTLE (1 bottle = 1 L) | `FG_OUT_PICK` — `reconciliation.ts` (LionWheel pickup→ledger; **frozen flag, not live yet**) |
| Recipe ingredient | `RAW-STRAWBERRY-ODK-SYRUP` "Strawberry ODK Syrup" (INGREDIENT, ADDITIVES_SYRUPS) | `private_core.components` | L | `PRODUCTION_CONSUMPTION` — `handler.ts` (live) |

Consumed in `BOM-BASE-MAR-STR` line 7 (50 L) and `BOM-BASE-DET-STR` line 8 (48 L/batch; migration `0211` also creates `FG-DET-STR-500ML` / `GT-ELT-STR-0.5L`).

**Symptom:** the "Recipe for this run" screen shows the Strawberry-ODK line as **SHORT / ~0 on-hand**, because the physical stock sits under the FG key (bottles) and is invisible to the recipe's RM lookup. (Note: that "Recipe for this run" override modal is itself **not built** — it's a proposed design; the live production-actual flow computes consumption strictly from the pinned BOM.)

## Why this is hard (the locked constraints that shape the answer)
- **Ledger is append-only**, corrections via reversal rows only; balance key = `site|item_type|item_id|batch` — **`item_type` is part of the key**, so FG and RM are *structurally distinct* balances even for the same id.
- **No cross-family UOM conversion** may enter the ledger (BOTTLE is COUNT; L is VOLUME — the L↔KG style ban). The projection is **unit-blind**: mixing two UOMs on one balance key **silently corrupts** it, and one-uom-per-key is **not DB-enforced**.
- **"Do not duplicate BOUGHT_FINISHED items into components"** (locked non-negotiable) — the crux interpretation question below.
- **Reliability over elegance; simplest path that survives daily use** (locked tiebreakers).

## Architectures evaluated (all 4 fully designed + adversarially stress-tested)

| Stance | Idea | Verdict | Killer reason |
|---|---|---|---|
| **A** | Canonical RM-backed identity; FG becomes a stockless sell-side facade over one RM balance | rejected | Makes FG **stockless** → every FG-availability read (verified: `v_fg_stock_export` filters `item_type='FG'`; FG projections seed by `item_id` with no type filter) **silently returns 0** for ODK across **~45 consumers** (Excel FG sheet, Shopify on-hand, dashboards, daily-inventory-agent). Silent stock-truth corruption. |
| **B** | FG is the single home; retire the component; teach BOM lines to reference items | rejected | **Highest blast radius.** Adds a `bom_line→items` FK to BOM core (absent today) and rewrites the **live** production hot path used by *every* manufactured item; verified landmines (`handler.ts` defaults unknown ids to `RM` → phantom key; explode chain zeroes ODK demand). Violates "reliability over elegance / simplest that survives." |
| **C** | Component is the single home, made sellable; FG becomes stockless facade | rejected | Same fatal stockless-FG silent-zero as A, **plus** leans hardest into the locked-rule #4 stretch and depends on a fail-closed facade trigger never being bypassed. |
| **D** ✅ | **Two records kept & linked; no ledger merge.** A `STOCK_TRANSFER` matched-pair event moves stock FG→RM at production-pull; one pooled number at the read layer. | **recommended** | The **only** option with **no wide silent-zero blast radius** and **no edit to either live write path**. Both keys stay populated in their native units; nothing reads zero. Weaknesses are application-layer and fixable (4 ship-gates below). |

## Recommended model — Stance D: STOCK_TRANSFER bridge + read-model rollup

### Core idea
Keep **both** master records and **both** ledger balance keys exactly as today. Reconcile them to **one physical pool** with an explicit, audited `STOCK_TRANSFER` event that moves stock from the sell-side key (bottles) to the consume-side key (litres) **at the moment ODK is pulled into production**. "One stock" is delivered at the **read layer** (a pooled view), never by merging the immutable ledger keyspace. Stock is **moved, not duplicated** — the physical total is never double-counted.

### The bridge (matched pair, one transaction)
- `STOCK_TRANSFER_OUT`: `qty_delta = −N` **BOTTLE** on the FG key.
- `STOCK_TRANSFER_IN`: `qty_delta = +(N × factor)` **L** on the RM key (`factor = 1.0` for ODK: 1 bottle = 1 L).

Each row lands on its own single-family key; **no converting row ever enters the ledger**. After the transfer the litres exist on the RM key for the recipe to consume, and the bottles are gone from the FG key so sales cannot also claim them.

### Schema changes (all additive — **no ledger DDL**)
1. `components.fg_twin_item_id text NULL REFERENCES items(item_id)` — one-way RM→FG link; NULL for every non-dual-role component.
2. `components.fg_twin_units_per_inv_uom ratio_8dp NULL CHECK (>0)` — sell-unit↔inventory-uom factor (ODK = 1.0). An **item-pair attribute, not a `uom` row, not a cross-family conversion**.
3. `CHECK ((fg_twin_item_id IS NULL) = (fg_twin_units_per_inv_uom IS NULL))` — both set or neither.
4. `CREATE TABLE private_core.stock_transfers` — header tying the matched OUT/IN pair into one auditable document (`factor_used` snapshotted; links both `movement_id`s; `idempotency_key UNIQUE`).
5. **No `stock_ledger` change** — `movement_type` has no CHECK, so the two new literals are legal with zero DDL; append-only shape untouched.
6. `CREATE VIEW api_read.v_dual_role_pooled_on_hand` (+ `v_odk_pooled_on_hand`) — joins the two keys, reports `fg_on_hand` (bottles), `rm_on_hand` (L), `pooled_on_hand_litres = fg_on_hand × factor + rm_on_hand`, **names not IDs**.

### Both consumer paths
- **FG sales-out (`reconciliation.ts`): UNCHANGED** — still writes `FG_OUT_PICK` on the FG key in `sales_uom`, still behind the **frozen** `fg_out_bridge_enabled`.
- **Production-consume (`handler.ts`): UNCHANGED core** — still `PRODUCTION_CONSUMPTION` on the RM key in L; shortage gate still reads the RM key.
- **NEW — STOCK_TRANSFER handler/form:** inputs `component_id`, `qty_sell_units`, `event_at`, `idempotency_key`; in one transaction validates the FG key won't go negative, asserts transfer-OUT uom == FG `sales_uom`, INSERTs the matched pair with **deterministic** ledger keys `ST:<key>:OUT` / `ST:<key>:IN`, INSERTs the `stock_transfers` header.

### Auto-pull hook (the friction fix — pilot DEFAULT)
Just before the shortfall gate in `handler.ts`: if a component is short **AND** `fg_twin_item_id IS NOT NULL` **AND** the FG twin holds enough bottles, **synthesize a STOCK_TRANSFER inside the same transaction**, re-read the balance, proceed. Strictly additive — guarded by `fg_twin_item_id IS NOT NULL`, so every non-dual-role component takes the unchanged path. This is what makes the recipe **never show SHORT for stock that physically exists as bottles** — the symptom is cured without operator memory.

### How the symptom is fixed
Production submit (or an explicit transfer) deposits litres onto the RM key first; the recipe's RM lookup then finds real litres → the line flips **SHORT → in-stock**. The pooled view lets any UI show the true combined on-hand.

### Generalization (after the pilot soak, Tom-gated)
Item-pair-generic: set `fg_twin_*` on any component that is also bought-as-FG. Guardrails before generalizing: (a) transfer-OUT uom must equal the FG `sales_uom` (a future multi-unit pack like CASE would accrete two COUNT uoms on one key and silently corrupt it); (b) `factor` validated per pairing; (c) any dashboard reading a single key for a dual-role item must be re-pointed at the pooled view.

## Four mandatory ship-gates (baked in from the stress review)
1. **Deterministic idempotency keys** for the matched OUT/IN pair (`ST:<key>:OUT` / `ST:<key>:IN`) inside one transaction — else a retry double-posts and corrupts **both** balances. *(The single most important correctness fix.)*
2. **Transfer-OUT uom == FG `sales_uom`** guard — keeps each key single-uom (not DB-enforced).
3. **FG-key non-negative** guard at transfer time.
4. **Auto-pull is the pilot default** — manual-only validates a worse experience than the problem being solved.

## Pilot plan — ODK strawberry ONLY
0. **READ-ONLY PROD PROBE FIRST** (mandatory — PROD diverges from on-disk dumps; Babka/Elita precedent). Confirm both records, UOMs, BOM references, capture starting balances on both keys, confirm no live `FG_OUT_PICK` rows. **HALT → factory-os-governor on any mismatch.**
1. **Migration** on a worktree cut from `origin/main`, numbered from the highest committed file (not the drifted ledger). Add the columns, `stock_transfers` table, and views. Dry-run `BEGIN…ROLLBACK`, apply via the gated manual path, verify with read-only SELECTs.
2. **Data step (pilot scope only):** `UPDATE components SET fg_twin_item_id='ADD-ODK-STR-1L', fg_twin_units_per_inv_uom=1.0 WHERE component_id='RAW-STRAWBERRY-ODK-SYRUP'`. **← gated behind Tom's locked-rule sign-off.**
3. Build the **STOCK_TRANSFER handler + form** (ship-gates 1–3).
4. Implement the **auto-pull hook** as default (ship-gate 4).
5. **Unit tests (N/N):** matched-pair posting; deterministic idempotency replay = zero new rows; non-negative guard; uom guard; auto-pull turns a previously-failing run into success; **golden regression**: a non-dual-role run is byte-for-byte unchanged; `reconciliation.ts` untouched.
6. **Dry-run on scratch/staging** seeded from the probe: post a 10-bottle transfer → FG −10 bottles, RM +10 L; run a previously-SHORT production-consume → passes; run `rebuild_verifier()` → **N/N parity both keys**.
7. **Read-model:** point ODK availability at `v_odk_pooled_on_hand`; confirm the recipe line reads real on-hand; confirm sell-side FG availability still correct (no stockless-zero regression).
8. **Pilot live on ODK only**, `fg_out_bridge_enabled` stays FROZEN. ≥24h soak; one real transfer matching a real production pull; observe SHORT→in-stock; reconcile pooled litres against a physical count; re-run `rebuild_verifier()`.
9. **Separately Tom-gated:** flipping `fg_out_bridge_enabled` is its own hard-stop gate (written approval + dry-run + ≥24h soak + RUNTIME_READY).

## Verification
- **`rebuild_verifier()` N/N zero-diff on BOTH keys** — the load-bearing gate. OUT lands on the FG PK, IN on the RM PK (distinct rows); each key sums independently; the unit-blind rebuild reproduces both.
- **Conservation proof:** `pooled_on_hand_litres` before a transfer == after (a move never creates/destroys): `(b×1.0 + L) == ((b−N)×1.0 + (L+N))`.
- **Idempotency:** replaying a transfer key posts zero new rows, balances unchanged.
- **Symptom evidence:** capture the recipe line on-hand BEFORE (≈0/SHORT) and AFTER (real litres).
- **Physical reconciliation:** pooled litres == physical count (sealed bottles ×1.0 + open litres) within tolerance.

## Rollback (Stance D is the most reversible candidate)
- **Behavior:** disable/ revert the additive auto-pull branch — every non-dual-role path is unchanged; `reconciliation.ts` was never edited.
- **Master data:** `UPDATE … SET fg_twin_*=NULL` — clean overlay removal; both records otherwise untouched (no merge, no retirement).
- **Schema:** additive/nullable; safe to leave.
- **Ledger (forward-only by contract):** undo a transfer by posting the **negated matched pair** with `related_movement_id` set; `rebuild_verifier()` confirms both keys net correctly. (Caution: a `COUNT_APPROVAL` recount rebases via the anchor; reverse before any recount on that key.)

## Open decisions for Tom

**① BLOCKING — locked-rule #4 interpretation (needs written sign-off before step 2):**
Does treating ODK as both a `BOUGHT_FINISHED` item *and* a recipe component violate **"Do not duplicate BOUGHT_FINISHED items into components"**?
- **Narrow (recommended):** the rule forbids creating a *new* component row that mirrors a BOUGHT_FINISHED item and carries its own *duplicate balance*. Stance D creates **no new record** (the component already exists and is consumed by real BOMs), only **adds a link**; stock is **moved**, never double-counted; the `supplier_items` trigger still single-homes the **purchasing** side. → **compliant.**
- **Broad:** "one substance must not be both an item and a component at all." Under this only Stance B (retire the component) literally obeys — at the cost of the heaviest hot-path change.
- **Defer:** pilot ODK under a written one-time exception; decide the general rule after the soak.
→ Recommendation: adopt **Narrow** as the canonical reading; append a one-line clarification to `LOCKED_DECISIONS.md`. **HALT before step 2 until signed.**

**② Auto-pull default vs manual-only** → recommend **auto-pull default** (cures the symptom; blast radius one item).

**③ Sales-driven component demand** → recommend **on-hand only for v1**; selling ODK bottles correctly reduces the on-hand seed but is **invisible to the planner's reorder signal** (known limitation; planning-input completeness, not stock truth). Revisit before wide generalization.

**④ Physical-count UX for dual-role items** → recommend **count bottles→FG key, open litres→RM key, reconcile via pooled view**; document in the counting operator note.

## Governance / locked-decision risks
- **#4 interpretation is BLOCKING** (stop-condition #2) — written sign-off required before the data UPDATE.
- One-uom-per-key is **not DB-enforced** — safe for ODK by construction; the uom guard MUST exist before any generalization.
- Deterministic transfer idempotency is a **ship gate**, not advisory (double-post = stock-truth corruption).
- `fg_out_bridge_enabled` stays **FALSE** through steps 1–8; flipping it is a separate hard-stop gate.
- PROD divergence: never apply the data UPDATE without the step-0 read-only probe + halt-on-mismatch.
- This is **stock-truth production work** → decision packet → `factory-os-governor` verdict → `release-verifier` before any merge/deploy.
