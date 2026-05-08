# LionWheel Unresolved Demand — Boundary Closure Audit

**Date:** 2026-05-02 (Asia/Jerusalem)
**Owner:** executor-w1
**Scope:** Tom-ruled OPTION 1 — diagnostics + advisory artifacts only. Read-only DB inspection. Zero runtime files touched, zero view bodies modified, zero migrations modified, zero auto-resolution executed.
**Boundaries respected:** A3 LOCKED (`v_planning_demand`), A4 LOCKED (`fn_compute_fg_net_requirements`), `stock_ledger` LOCKED. W4 lane (`api/src/integrations/lionwheel/*.ts`) untouched.

---

## §1. Method

**Connection:** Session-mode pooler (`aws-1-eu-central-1.pooler.supabase.com:5432`) via `DATABASE_URL_POOLED` from `gt-factory-os/.env`. Live Supabase project `rvadsozabmxkkrktwgnv`, PG17.

**Scripts (committed to canonical repo):**
- `scripts/_w1_lionwheel_unresolved_audit_inspect.mjs` — schema discovery (table/column existence, exception category counts)
- `scripts/_w1_lionwheel_unresolved_audit_inspect2.mjs` — data-shape probe (resolution_status enum, line-status distribution, exception payload shape)
- `scripts/_w1_lionwheel_unresolved_audit_inspect3.mjs` — deterministic candidate matching against `private_core.items.item_id`
- `scripts/_w1_lionwheel_unresolved_audit.mjs` — main audit (104 unresolved rows / 31 SKUs)
- `scripts/_w1_lionwheel_stale_inspect.mjs` — stale-exception split (bulk-resolvable vs needs-Tom)

**Schema confirmed in live DB:**
- `private_core.orders_mirror` (mirror_id PK, retired_at nullable, pickup_at, lw_status)
- `private_core.orders_mirror_lines` (line_mirror_id PK, lw_sku, lw_qty_ordered numeric, item_id nullable, resolution_status text NOT NULL — observed values: `resolved`, `unresolved`)
- `private_core.exceptions` (category, status, dedupe_key — NOT `related_entity_id` for lionwheel rows; payload usually NULL)
- `private_core.integration_sku_map` (source_channel, external_sku, item_id, approval_status — observed values: `approved`)
- `private_core.items` (item_id PK text, supply_method, status)

**Live data-shape note (deviation from dispatch wording):**
The dispatch said "halt with `data_failure` if the resolution_status column is named differently". Column exists exactly as named. The dispatch also said "halt if no `lionwheel_unknown_sku` exceptions exist". Recent exceptions exist (32 rows, all <=14 days old). The **stale (>14d) set is empty** — `0` rows — but this reflects Tom's prior bulk-close action 2026-04-30 (logged in `CURRENT_STATE.md` §"Day-1 prep stale-exception bulk-close"). The schema is healthy; no `data_failure` halt.

**Exception SKU extraction:** Lionwheel-unknown-sku exceptions have `related_entity_id IS NULL` and `raw_payload IS NULL` in current production. SKU is encoded in `dedupe_key` with format `lw_sku:<SKU>`. Audit scripts use `regexp_replace(dedupe_key, '^lw_sku:', '')` for SKU extraction.

---

## §2. Unresolved demand by category

Scope: `private_core.orders_mirror_lines WHERE orders_mirror.retired_at IS NULL AND (resolution_status != 'resolved' OR item_id IS NULL)`.

**Headline:** 104 unresolved lines across 31 distinct SKUs, total qty = 370.

| Category | row_count | distinct_sku_count | qty_sum | sample SKUs | planning_impact_class |
|---|---:|---:|---:|---|---|
| `bundle` (`GTSET-*`) | 44 | 9 | 47.00 | GTSET-LOW-6FLAV-SALE; GTSET-FREE-3FLAV-SALE; GTSET-FREE-DETOX-X4; GTSET-FREE-FRESH-DETOX | underplanning_risk |
| `non_catalog` | 25 | 7 | 218.00 | GT-GLA-CUP; GT-PUE-FRE-1L; GT-MAT-KIT; GTMN-PIK-254 | visibility_only |
| `alias_safe_candidate` | 11 | 2 | 36.00 | GTCC-MUZ-PNMM-1L; GTCC-MUZ-JASM-1L | underplanning_risk |
| `alias_ambiguous_needs_tom` | 23 | 12 | 68.00 | GTCC-MUZ-APPZ-1L; GTCC-MUZ-SMAR-1L; GTCC-MUZ-TROJ-1L; AP-DRI-ORA | underplanning_risk |
| `malformed` | 1 | 1 | 1.00 | (empty string SKU) | visibility_only_parser_bug |
| **TOTAL** | **104** | **31** | **370.00** | | |

**Critical-today (pickup today/tomorrow Asia/Jerusalem):** 0 rows. No immediate operational damage from any category.
**7-day backlog (pickup within next 7 days):** 0 rows. The 104 unresolved rows are all on orders with no pickup_at populated, OR pickup_at beyond the 7-day horizon. (Most likely: pickup_at is null on these mirror rows; the picker discipline soak in `lionwheel_chain_repair_plan_2026-04-30.md` is still in flight.)

---

## §3. Stale exception analysis

**Stale (>14d) open `lionwheel_unknown_sku` exceptions: 0.** Tom's bulk-close (`CURRENT_STATE.md` §"Day-1 prep stale-exception bulk-close") executed successfully prior to this cycle — the historical 41 stale rows are no longer present. No bulk-resolve SQL needed.

**Recent (<=14d) open exceptions: 32.** These remain genuinely open per Tom-locked semantics — the 14-day stability window is correct.

| Bucket | Count | Disposition |
|---|---:|---|
| stale (>14d), bulk_resolvable (alias exists) | 0 | n/a — empty |
| stale (>14d), needs_tom (no alias) | 0 | n/a — empty |
| recent (<=14d), alias already approved (W4 reconciler gap) | **2** | See §6 — W4 follow-up |
| recent (<=14d), no alias yet | 30 | Day-1 inbox — Tom-actionable via `/admin/sku-aliases` |

**Recent rows where alias is already approved but exception remains open** (W4 reconciler gap):

| exception_id | sku | alias_target | alias_created | exception_created | age_days |
|---|---|---|---|---|---:|
| `82dd0f2e-6034-40a7-97d9-2facee215886` | `AP-DRI-ROS` | `ADD-GAR-ROSE-DRY` | 2026-04-26 13:24 | 2026-04-21 13:45 | 11 |
| `af13205d-804d-40a8-b064-ec253df38328` | `AP-DRI-ORA` | `ADD-GAR-ORA-DRY` | 2026-04-26 13:24 | 2026-04-19 10:00 | 13 |

These are NOT included in the stale-resolve SQL artifact (Tom-locked threshold is strictly >14d). They will become bulk-resolvable in 1-3 days and a follow-up cycle can pick them up. The deeper signal here is a W4 reconciler defect — the reconciler should have closed these on the same poll cycle that ingested the alias. See §6.

---

## §4. Per-category planning impact

### 4a. Bundles (`GTSET-*`) — 9 SKUs, 44 rows, 47 qty
**Disposition:** Tom-locked cycle 17 default — do NOT explode bundles in raw mirror; classify as planning-impacting unresolved demand; do NOT propose alias guesses.

**Specific SKUs blocked from planning:**
- GTSET-LOW-6FLAV-SALE (17 rows / 17 qty)
- GTSET-FREE-3FLAV-SALE (7 / 10)
- GTSET-FREE-DETOX-X4 (4 / 4)
- GTSET-FREE-FRESH-DETOX (4 / 4)
- GTSET-LOW-3FLAV-SALE (4 / 4)
- GTSET-LOW-DETOX-X4 (3 / 3)
- GTSET-LOW-3FLAV-PREMI (3 / 3)
- GTSET-LOW-JASMI-SENCH (1 / 1)
- GTSET-LOW-ENERG-DETOX (1 / 1)

**Planning impact:** Underplanning of FG components inside the bundle. The system does not see the constituent FG demand because the bundle SKU is unmapped. To resolve, Tom must rule on bundle policy (one of):
- Option A: define each bundle as a virtual `MANUFACTURED` item with a BOM that explodes to constituent FGs (medium engineering; preserves audit clarity)
- Option B: explode bundles in the mirror reconciler (W4 lane; faster but couples bundle definition to integration code)
- Option C: keep bundles unresolved and accept the underplanning (status quo — current behavior)

→ Surfaced as decision **LWR-1** in §5.

### 4b. Non-catalog — 7 SKUs, 25 rows, 218 qty
**Disposition:** Tom-locked cycle 17 default — excluded from planning demand unless mapped; remain visible with classification.

**Specific SKUs:**
- GT-GLA-CUP (9 rows / 11 qty) — "Measuring Cup" — accessory, not produced
- GT-PUE-FRE-1L (5 / 6) — likely defunct PUE-Fresh line (no `GT-PUE` items in catalog)
- GT-MAT-KIT (4 / 4) — "Complete Matcha Kit" — bundle-like, no item
- GTMN-PIK-254 (4 / 84) — "Pikadon 254" — likely promotional/legacy
- GT-GLA-MAT-PRINT (1 / 100) — printed matcha glass — accessory
- GTEL-BAB-RED-0.75L (1 / 12) — likely "GTEL Babylon Red" — no GTEL item in catalog
- 7290003803217 (1 / 1) — barcode-as-SKU; ambiguous which item

**Planning impact:** None on planning engine (correctly excluded). Visibility-only — operator should know these orders exist and that we cannot fulfill them through standard FG flow.

→ Surfaced as per-SKU decision worklist **LWR-3** in §5.

### 4c. Alias safe candidates — 2 SKUs, 11 rows, 36 qty
**Disposition:** Tom-locked cycle 17 default — deterministic alias proposals only.

| LW SKU | Proposed canonical item_id | Reason | Confidence |
|---|---|---|---|
| `GTCC-MUZ-JASM-1L` | `ADD-MUZ-JASM-1L` | Channel prefix (`GTCC-`) → catalog prefix (`ADD-`); root token `MUZ-JASM-1L` matches exactly | high (deterministic) |
| `GTCC-MUZ-PNMM-1L` | `ADD-MUZ-PNMM-1L` | Same pattern | high (deterministic) |

These are the JASM/PNMM aliases held for Tom in `CURRENT_STATE.md` §Gate 4 follow-on. Both proposals are deterministic via the rule "`GTCC-MUZ-<X>-1L` → `ADD-MUZ-<X>-1L`" where `<X>` matches an existing item.

→ Surfaced as decision **LWR-2** in §5.

### 4d. Alias ambiguous (needs Tom) — 12 SKUs, 23 rows, 68 qty
**Disposition:** Tom-locked cycle 17 default — mark "ambiguous-needs-Tom"; do NOT propose alias guesses.

| LW SKU | LW name (if known) | Why ambiguous |
|---|---|---|
| `GTCC-MUZ-APPZ-1L` | (Muza Appz?) | No `ADD-MUZ-APPZ-1L` in catalog; could be misspelling or new flavor |
| `GTCC-MUZ-SMAR-1L` | | No `ADD-MUZ-SMAR-1L` |
| `GTCC-MUZ-TROJ-1L` | | No `ADD-MUZ-TROJ-1L` |
| `GTCC-MUZ-PSSP-1L` | | No `ADD-MUZ-PSSP-1L` |
| `GTCC-MUZ-ANBL-1L` | | No `ADD-MUZ-ANBL-1L` |
| `GTCC-MUZ-BLBR-1L` | | No `ADD-MUZ-BLBR-1L` (closest: `ADD-MUZ-BZSM-1L`) |
| `GTCC-MUZ-CHRBL-1L` | | No `ADD-MUZ-CHRBL-1L` (closest: hard to determine — multiple `ADD-MUZ-*`) |
| `AP-DRI-PIN` | | `AP-DRI-*` family pattern — `AP-DRI-ORA`/`AP-DRI-ROS` map to `ADD-GAR-ORA-DRY`/`ADD-GAR-ROSE-DRY`; PIN could be Pineapple → `ADD-GAR-PIN-DRY` (no such item in catalog list dump) |
| `AP-FRO-MAT` | | Frozen Matcha? no `ADD-*-FRO-MAT` pattern |
| `AP-TAP-PIN` | | Tapioca Pineapple? unclear |
| `AP-DRI-ORA` | | **Has approved alias `ADD-GAR-ORA-DRY` already; lines unresolved due to W4 reconciler gap (see §6)** |
| `AP-DRI-ROS` | | **Has approved alias `ADD-GAR-ROSE-DRY` already; lines unresolved due to W4 reconciler gap (see §6)** |

**Planning impact:** Underplanning of ADD-* (additive/garnish) items. Each unmapped SKU silently removes 1-13 units of demand from the planning engine.

→ Surfaced as decision **LWR-2** + **LWR-4** (per-SKU resolution) in §5.

### 4e. Malformed — 1 SKU, 1 row, 1 qty
**Disposition:** Tom-locked cycle 17 default — parser-bug candidate (W4 follow-up); don't fix here.

The SKU is the empty string. This indicates either (a) LionWheel returned a row with `sku=""` and the normalizer accepted it, or (b) a JSON path issue where `body.task.order_items[].sku` was missing and silently coerced to `""`. Either is a W4 normalize-layer concern. See §6.

---

## §5. Tom-decisions surfaced

| Decision ID | Topic | Options | Recommended |
|---|---|---|---|
| **LWR-1** | Bundle policy for `GTSET-*` (9 SKUs / 44 rows) | A. Virtual MANUFACTURED items + BOMs; B. Mirror reconciler explodes; C. Status quo (accept underplanning) | Tom-only call — not a W1 decision. W1 awaits ruling. |
| **LWR-2** | JASM/PNMM alias creation (2 SKUs, both safe deterministic candidates) | Approve `GTCC-MUZ-JASM-1L → ADD-MUZ-JASM-1L` and `GTCC-MUZ-PNMM-1L → ADD-MUZ-PNMM-1L` via `/admin/sku-aliases` UI | APPROVE. Both are deterministic via the `GTCC-MUZ-<X>-1L → ADD-MUZ-<X>-1L` rule and both targets exist. |
| **LWR-3** | Non-catalog admission per-SKU (7 SKUs / 25 rows / 218 qty) | Per SKU: (a) treat as out-of-scope (status quo); (b) create catalog item; (c) retire the LionWheel SKU | Tom-only call per-SKU. W1 cannot rule on whether `GTMN-PIK-254` is a valid product. |
| **LWR-4** | Per-SKU ambiguous-MUZ resolution (10 unmapped SKUs in `GTCC-MUZ-*` and `AP-*` families) | Tom inspects in `/admin/sku-aliases`, decides "create item" / "map to existing" / "drop"; or commissions investigation into source LW catalog | Tom-only. |

---

## §6. W4 follow-up patches needed

Strictly outside W1 lane (`api/src/integrations/lionwheel/*.ts` is W4-owned). Surfaced here for governor → W4 routing.

1. **W4 reconciler gap — alias-already-approved but lines/exceptions remain unresolved.** Detected at two levels:
   - Line level: `AP-DRI-ORA` (2 lines) and `AP-DRI-ROS` (1 line) are still `resolution_status='unresolved'` despite their aliases being approved on 2026-04-26. The reconciler should re-process unresolved lines on alias-approval and update `item_id` + `resolution_status='resolved'` + close associated exceptions.
   - Exception level: 2 recent exceptions (`82dd0f2e` for AP-DRI-ROS, `af13205d` for AP-DRI-ORA) remain open despite alias approval.
   - **Suspected location:** `api/src/integrations/lionwheel/reconciliation.ts` — likely no on-alias-create back-fill logic, or the back-fill query is missing the `OR item_id IS NULL` predicate.
   - **W4 patch shape:** add a one-shot back-fill on alias creation, OR a periodic re-resolution pass over `unresolved` lines that match an `approved` mapping.

2. **Malformed parser bug — empty-string SKU accepted.** One row currently has `lw_sku=''`. The normalizer should either reject the line at parse time (and emit a `lionwheel_malformed_line` exception) or at minimum emit `lionwheel_unknown_sku` so it surfaces in the inbox. Right now it shows up only in the per-line audit.
   - **Suspected location:** `api/src/integrations/lionwheel/normalize.ts` — Zod schema permits empty string, or empty string passes the unknown-SKU check.

3. **Bundle handling defaults (depends on Tom LWR-1 ruling).** If Tom selects Option B (mirror-explosion), this is W4 work in `normalize.ts` / `reconciliation.ts`.

4. **`related_entity_id` population for `lionwheel_unknown_sku` exceptions.** Currently NULL on all rows; SKU only available via `dedupe_key`. Consumer-side code (admin inbox, this audit) has to regex-extract. W4 should populate `related_entity_id = lw_sku` at exception emit time. Cosmetic, not blocking.

---

## §7. Boundaries respected

- **No runtime files touched.** `api/src/integrations/lionwheel/*.ts` UNCHANGED. `api/src/inventory/handler.flow.ts` UNCHANGED. All five W1 audit scripts are read-only Node.js scripts in `gt-factory-os/scripts/_w1_lionwheel_*.mjs`.
- **No view bodies modified.** `v_planning_demand` (A3 LOCKED) UNCHANGED. `v_critical_today` UNCHANGED. `v_daily_inventory_flow` UNCHANGED. `v_production_plan_slippage` UNCHANGED.
- **No migrations modified.** No new migration files. Latest migration on disk remains `0120_holidays_il_archived_filter.sql` (cycle 8 partial state, separate concern).
- **No semantics changed.** `private_core.orders_mirror_lines.resolution_status`, `private_core.exceptions.category`/`status`, `private_core.integration_sku_map.approval_status` semantics all preserved.
- **No automatic resolution.** Stale-resolve SQL artifact (script #5) is Tom-to-execute in a wrapped `BEGIN; … COMMIT;` block; statement count is 0 because the stale set is empty.
- **No new RUNTIME_READY signal.** This is diagnostic, not contract closure.
- **A3 + A4 + stock_ledger LOCKED.** No probing of these. No fixture loads. No advisory-lock acquisition. No transaction wrapping audit reads (autocommit-equivalent SELECTs only).

---

## §8. What remains blocked

| Blocker | Owner | Notes |
|---|---|---|
| LWR-1 bundle policy | Tom | 9 SKUs / 44 rows / 47 qty silently underplanning until ruled. None are critical-today. |
| LWR-2 JASM/PNMM aliases | Tom | 2 SKUs / 11 rows / 36 qty underplanning. Deterministic candidates ready in `lionwheel_alias_review_candidates_2026-05-02.csv`. |
| LWR-3 non-catalog admission | Tom | 7 SKUs / 25 rows / 218 qty. Visibility only. |
| LWR-4 per-SKU ambiguous resolution | Tom (likely with operator input) | 10 SKUs / ~22 rows. |
| W4 reconciler back-fill on alias creation | W4 | 2 SKUs (AP-DRI-ORA, AP-DRI-ROS) currently in this state. |
| W4 normalizer empty-string SKU rejection | W4 | 1 row currently affected. |
| LionWheel pick-reconciliation chain repair | W1 (per `CURRENT_STATE.md` §Active corridor) | Separate corridor — operator soak + Phase 1 + Phase 2 code defects per `lionwheel_chain_root_cause_2026-04-30.md`. NOT addressed by this audit. |

**Net assessment:** No critical-today damage. Underplanning risk = ~91 rows / ~151 qty across alias and bundle categories. All resolutions are gated on Tom rulings or W4 patches; no W1 work remains in this lane until Tom rules.

---

**End of audit.**
