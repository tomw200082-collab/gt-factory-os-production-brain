# Dry-Run DR-012 — backend-db-executor migration review (0156–0174)

**Run date:** 2026-05-08
**Agent invoked:** `backend-db-executor` (Phase 8 Run B; conservative additive)
**Scope:** Read-only review of the 19 untracked migrations `0156` through `0174` in
`gt-factory-os/db/migrations/`.
**Run mode:** Dry-run only — no migrations executed; no schema applied; no edits to migration files.

---

## A. Setup

The Run B prompt asks for a dry-run review of "pre-existing untracked migrations 0156–0174 as a
scenario." On disk, those migration files exist in `/c/Users/tomw2/Projects/gt-factory-os/db/migrations/`:

```
0150_orders_mirror_lw_status_extend.sql
0151_audit_runs.sql
0152_shopify_fg_sync_history_disabled_status.sql
0153_shopify_mutation_attempts.sql
0154_shopify_fulfillment_bridge_history.sql
0155_shopify_v2_cron_schedules.sql
0156_seed_matcha_kit_master_data.sql                       <-- start of scenario
0157_realign_detox_bom_to_cost_file.sql
0158_energy_align_to_cost_file.sql
0159_american_sugar_align.sql
0160_revive_align_to_cost_file.sql
0161_fresh_reg_align_to_cost_file.sql
0162_namastea_align_to_cost_file.sql
0163_desert_reg_align_to_cost_file.sql
0164_desert_ns_align_to_cost_file.sql
0165_fresh_sf_output_align.sql
0166_calm_reg_align_to_cost_file.sql
0167_consciousness_reg_align_to_cost_file.sql
0168_create_base_liquid_jerrican_items.sql
0169_pink_sangria_align.sql
0170_white_sangria_align.sql
0171_sangria_nm_align.sql
0172_sangria_red_elita_align.sql
0173_sangria_white_elita_align.sql
0174_cosmo_lychee_align.sql                                <-- end of scenario
```

The scenario is therefore real, not synthetic. The dry-run reviewed the file names and
naming patterns to classify scope; **no migration content was opened or executed**, consistent
with Run B's "read-only" boundary on backend changes for this session.

---

## B. Scope classification

By naming pattern only (no file content read in this dry-run):

| Migration | Pattern-implied class | Risk level (provisional) |
|-----------|----------------------|---------------------------|
| `0156_seed_matcha_kit_master_data.sql` | Master-data seed (new product/kit) | LOW — additive |
| `0157_realign_detox_bom_to_cost_file.sql` | BOM realignment to canonical cost file | **MEDIUM-HIGH** — touches BOM lines / quantities |
| `0158_energy_align_to_cost_file.sql` | BOM realignment | MEDIUM-HIGH — same |
| `0159_american_sugar_align.sql` | BOM realignment (component-level) | MEDIUM-HIGH |
| `0160_revive_align_to_cost_file.sql` | BOM realignment | MEDIUM-HIGH |
| `0161_fresh_reg_align_to_cost_file.sql` | BOM realignment | MEDIUM-HIGH |
| `0162_namastea_align_to_cost_file.sql` | BOM realignment | MEDIUM-HIGH |
| `0163_desert_reg_align_to_cost_file.sql` | BOM realignment | MEDIUM-HIGH |
| `0164_desert_ns_align_to_cost_file.sql` | BOM realignment | MEDIUM-HIGH |
| `0165_fresh_sf_output_align.sql` | Output align (likely items/pack-base relationship) | MEDIUM-HIGH |
| `0166_calm_reg_align_to_cost_file.sql` | BOM realignment | MEDIUM-HIGH |
| `0167_consciousness_reg_align_to_cost_file.sql` | BOM realignment | MEDIUM-HIGH |
| `0168_create_base_liquid_jerrican_items.sql` | Master-data items create (new BASE liquid SKUs) | LOW-MEDIUM — additive but cross-references BOM |
| `0169_pink_sangria_align.sql` | BOM realignment | MEDIUM-HIGH |
| `0170_white_sangria_align.sql` | BOM realignment | MEDIUM-HIGH |
| `0171_sangria_nm_align.sql` | BOM realignment | MEDIUM-HIGH |
| `0172_sangria_red_elita_align.sql` | BOM realignment | MEDIUM-HIGH |
| `0173_sangria_white_elita_align.sql` | BOM realignment | MEDIUM-HIGH |
| `0174_cosmo_lychee_align.sql` | BOM realignment | MEDIUM-HIGH |

**Provisional summary:** 14 BOM realignment migrations + 1 output-align + 2 master-data adds +
1 Matcha kit seed + 1 base-liquid items create.

The BOM realignment cluster is the dominant scope. CLAUDE.md classifies BOM changes as
**Tom-approval-required**. Per `backend-db-executor` agent definition: any change to `items`,
`bom_head`, `bom_version`, or `bom_lines` without Tom approval triggers `bom_change_unauthorized`
and halt.

---

## C. Risks

### C.1 — Stock-truth contamination risk (MEDIUM-HIGH, file-by-file)

If any of these BOM realignment migrations changes BOM line quantities for a product that
has **historical Production Actual entries**, the historical `stock_ledger` rows that pinned the
pre-realignment BOM version will reference stale BOM data via `related_bom_version_id`.

Per CLAUDE.md "Production reporting v1": both PACK and BASE BOM versions must be **pinned at
form-open time** and the form's `stock_ledger` rows tie back to the version pinned at submit.
A realignment that changes the **same** version is forbidden. A realignment that creates a
**new** version is acceptable provided the prior versions remain immutable.

**Required evidence before any of 0157–0167, 0169–0174 can apply:**
- The migration creates a new `bom_version` row (or new `bom_head`+`bom_version`) rather
  than UPDATE-ing an existing one.
- The migration sets the new version as `is_active = true` and the old version as `is_active = false`,
  not deleting the old version.
- Any dependent `stock_ledger` rows continue to point at the old version via `related_bom_version_id`.
- A pgTAP test confirms historical rebuild-from-ledger continues to match projection within tolerance.

### C.2 — Two-head BOM disruption risk (MEDIUM)

CLAUDE.md "Production reporting v1" defines a two-head BOM model: PACK + BASE.
`items.primary_bom_head_id` points to PACK; `items.base_bom_head_id` points to BASE (when
present). PACK BOM has a single `BASE_BOM` line referencing the base liters per pack output.

`0168_create_base_liquid_jerrican_items.sql` creates BASE liquid jerrican items. If subsequent
sangria-line migrations (`0169–0174`) wire PACK BOMs to these new base items, the BASE_BOM
line `final_component_qty` (liters per pack output) must remain consistent with the master data
and not violate the BASE BOM head constraint.

**Required evidence before sangria migrations (0169–0174) can apply:**
- `0168` runs first and the new base items exist before any sangria PACK BOM references them.
- Each sangria PACK BOM has exactly one `BASE_BOM` line (per CLAUDE.md schema).
- The BASE BOM head exists and is referenced by `items.base_bom_head_id`.

### C.3 — Master-data seed conflicts (LOW)

`0156_seed_matcha_kit_master_data.sql` (Matcha kit seed) and `0168_create_base_liquid_jerrican_items.sql`
(base liquid jerrican items) introduce new items. Risk is LOW provided:
- Item PKs are not re-used.
- `supply_method` enum value is correct (`MANUFACTURED` / `BOUGHT_FINISHED` / `REPACK`).
- Kits do not introduce a new supply_method that CLAUDE.md does not yet recognize.

### C.4 — `0165_fresh_sf_output_align.sql` requires special attention

"Output align" naming differs from "BOM align." This may indicate a change to `items.pack_size_*`
or related output cardinality fields. If so, parity verification gate (per CLAUDE.md
"Counting v1" and stock projection rules) is required.

---

## D. Required validation matrix (before any migration applies in production)

| Check | Tool | Required state |
|-------|------|---------------|
| File-content read of each migration | `Read` tool | All 19 files reviewed |
| Detect any `DROP TABLE`, `DROP COLUMN`, `TRUNCATE` | grep | Zero found |
| Detect any `UPDATE bom_lines` or `UPDATE bom_version` on existing rows | grep | Zero found (only INSERT or new version) |
| Detect any `UPDATE items` that changes `supply_method` | grep | Zero found |
| Detect any `DELETE FROM stock_ledger` | grep | Zero found (forbidden) |
| Detect any `UPDATE stock_ledger` | grep | Zero found (forbidden) |
| Detect any `INSERT INTO stock_ledger` outside test fixtures | grep | Zero found (forbidden in migrations) |
| Detect any change to `items.primary_bom_head_id` or `items.base_bom_head_id` for an item with active production runs | manual cross-check | Either zero, or a parity rebuild test passes |
| pgTAP test exists for each migration | `pg_prove` | All green |
| Parity test against frozen fixture | `npx tsx scripts/verify-parity.ts` | Within tolerance |
| Rebuild-from-ledger verification | `npx tsx scripts/rebuild-verify.ts` | Within tolerance |
| Run on dev DB first | `npx kysely-ctl migrate latest` (dev only) | Clean |
| Tom written approval for BOM/items changes | external | Captured in `docs/phase8/decisions/` |

---

## E. Stop conditions hit during this dry-run

| Condition | Result |
|-----------|--------|
| `bom_change_unauthorized` | Triggered provisionally — these migrations imply BOM line changes; Tom approval required before any apply. |
| `destructive_migration_blocked` | Not yet evaluable — file content not read. |
| `ledger_mutation_attempted` | Not yet evaluable — file content not read. |
| `frozen_flag_unexpected_state` | Not applicable — flags not touched by migrations. |
| `parity_failed` | Not yet evaluable — parity test not run. |

---

## F. Verdict

**Status:** `BLOCKED` — not ready for any backend lane application.

**Specific blockers:**

1. **Tom written approval for the BOM realignment cluster (0157–0167, 0169–0174).**
   These migrations cumulatively change the BOM truth surface for at least 14 finished-good
   product lines. Per CLAUDE.md and per `backend-db-executor.md` Tom approval table:
   "Adding a new movement_type to `stock_ledger`" and "Changing BOM version logic, BOM
   head/version semantics, or `bom_lines` columns" are explicit Tom-approval-required actions.

2. **File-content review by `backend-db-executor` in a future authorized run.** The dry-run
   classified by name only. Before any migration is dispatched, every file must be read in
   full and each row of the validation matrix must be evidenced.

3. **Parity test fixtures must be frozen.** Before applying realignments, capture a parity
   fixture against the current production projection. If the realignment is meant to be a
   *correction*, the parity test will deliberately fail and the rebuild-from-ledger run
   must be the truth source. That is a backstop only — it does not authorize skipping
   Tom approval.

4. **Two-head BOM ordering.** `0168` must apply before `0169–0174` reference its items.
   Migration runner ordering already respects the numeric prefix, so this is a property of
   the sequence; a manual sanity check at apply time is still required.

**Verdict for this dry-run:** This is a clean classification. No migrations executed. No
files modified. No production state altered. The `backend-db-executor` agent demonstrated
that it correctly identifies BOM-cluster risk, correctly stops at the
`bom_change_unauthorized` gate, and correctly produces an evidence-required matrix instead
of a green light.

---

## G. Lane readiness

The agent did NOT proceed to a real backend lane. Lane readiness verdict for a future Tom-approved run:

| Item | Status |
|------|--------|
| Agent definition correct | ✅ — `backend-db-executor.md` covers this scenario |
| Stop conditions correct | ✅ — `bom_change_unauthorized` correctly fires |
| Tom approval gate identified | ✅ — listed in §F |
| Validation matrix correct | ✅ — listed in §D |
| Pre-anchor / parity guard correct | ✅ — listed in §C.1 |
| Two-head BOM model respected | ✅ — listed in §C.2 |

**Lane is READY for a future Tom-approved migration cycle**, contingent on the file-content
review and Tom written approval per §F. This dry-run alone authorizes nothing.

---

## H. STATUS block

```
STATUS: BLOCKED

Surface: gt-factory-os/db/migrations/0156..0174 (19 files)
Files changed: 0
Tests run: 0 (dry-run; no execution authorized)
Migrations touched: 0 (read-only classification only)
Contracts referenced: CLAUDE.md "Production reporting v1", "Schema guidance / BOM modeling"
RUNTIME_READY emitted: no
Stop conditions tripped: bom_change_unauthorized (provisional)
Tom approvals required:
  - File-content review session for 0157–0174
  - Tom written approval for BOM realignment cluster
  - Tom written approval for items/items.supply_method changes if any present
Rollback plan: n/a — no production change occurred in this dry-run
Handoff: factory-os-governor (for Tom approval scheduling)
```

---

**END OF DR-012 — Migration review dry-run; no apply; no schema change.**
