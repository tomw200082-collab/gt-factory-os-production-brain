# LionWheel Alias Seeding — Tranche Contract

> **Artifact class:** W4 requirements-only contract.
> **Status:** UPDATED 2026-04-23 (resolver model locked; ODK Tier 2a / held items / bundle policy explicitly categorized; exit criteria updated).
> **Supersedes:** `docs/lionwheel_alias_seeding_spec.md` (2026-04-23 general requirements spec). This tranche contract refines that spec with Tom's approved constraints, the 3-bucket categorization, the retroactive backfill requirement, post-seeding visibility requirements, and the follow-up debt register. The earlier spec remains as background reading; this document is authoritative for the current seeding tranche.
> **Authority sources:** `docs/lionwheel_alias_seeding_spec.md`, `docs/gap_registry.md` (GAP-003, GAP-008), `CURRENT_STATE.md` (Gate 4 follow-on items, W2 Mode B-AMMC, commit 8543d2b), verified live DB analysis (W1, 2026-04-23 — 65 distinct `lionwheel_unknown_sku` exceptions, bucket categorization sourced from live exception + item_id cross-query). Resolver model locked by Tom 2026-04-23.

---

## 1. Tranche intent

This is a planning-input tranche, not a UI tranche. Its sole purpose is to close the LionWheel demand-ingestion gap that has left every planning run operating on forecast-only demand since Gate 4 closed. The tranche seeds 39 HIGH-confidence alias mappings (Bucket A) into `private_core.integration_sku_map` — a defined subset of the 65 unresolved `lionwheel_unknown_sku` exceptions — chosen specifically because they are unambiguous exact matches between the LionWheel external SKU namespace and the platform's canonical `items.item_id` namespace, plus three ODK suffix variants whose mapping is unambiguous. Seeding these 39 items, running the retroactive backfill, re-running the LionWheel poll, and triggering a planning run will bring open-order demand into `v_planning_demand` for a substantial portion of GT's finished-goods portfolio, materially improving planning truth. The 26 remaining unresolved exceptions (Buckets B and C) are withheld from this tranche because they require either Tom's confirmation on ambiguous mappings or a policy decision on bundle modeling that is not yet made.

---

## 2. Resolver model

Tom's locked decision (2026-04-23): the platform uses a **hybrid resolver** with three ordered steps. `items.legacy_sku` remains canonical and is not changed.

### Step 1 — Exact `legacy_sku` match

The resolver attempts a direct lookup of the incoming LionWheel external SKU against `private_core.items.legacy_sku`. If a match is found, the item is resolved immediately with no alias row required.

- Covers: Tier 1 (36 items). All 36 items in the Bucket A exact-match table resolve at this step.
- No `integration_sku_map` row is created or needed for these items.
- This is the primary resolution path for the bulk of GT's finished-goods catalog.

### Step 2 — `integration_sku_map` alias lookup

If Step 1 finds no match, the resolver looks up the external SKU in `private_core.integration_sku_map` for `source_channel='lionwheel'` and `approval_status='approved'`. If a matching approved alias row exists, the mapped `item_id` is used.

- Covers: Tier 2a (3 ODK alias items seeded in this tranche) and any future approved aliases for genuine external divergences.
- This table is reserved for cases where LionWheel's external SKU genuinely differs from the canonical item identifier. It is not used to chase boundary-system quirks by mutating core master data.

### Step 3 — Unresolved exception

If neither Step 1 nor Step 2 resolves the SKU, the resolver writes the mirror line with `item_id = NULL`, `resolution_status = 'unresolved'`, and fires a `lionwheel_unknown_sku` exception.

Unresolved exceptions are subcategorized as follows:

- **`bundle_sku=true`**: GTSET-* bundle SKUs. These are multi-item composite products; no single `item_id` can represent them. Exceptions fire but are tagged with `bundle_sku=true` in the exception detail. They are NOT silently ignored.
- **Standard unknown**: all other unresolved external SKUs — ambiguous mappings pending Tom confirmation, new products not yet in the item master, malformed or test SKUs.

**Rationale:** `legacy_sku` remains canonical. The alias table is reserved for genuine external divergences. No core master data is mutated to chase boundary system quirks. The bundle subcategorization ensures GTSET-* exceptions are distinguishable from new or unknown product exceptions without a separate bundle-policy decision being required now.

---

## 3. Exit criteria

A tranche is not successful until ALL seven of the following hold simultaneously. No partial credit. Verify in order.

**EC-1 — 39 aliases active: 36 Tier-1 items resolve via `legacy_sku`; 3 ODK aliases seeded and approved.**
Verify: (a) the 36 Tier-1 items listed in §4 Bucket A Tier 1 each match an existing `items.legacy_sku` value — no alias row needed or created for them; (b) `private_core.integration_sku_map` contains exactly 3 rows with `source_channel='lionwheel'` and `approval_status='approved'`, corresponding to the 3 ODK Tier-2a items listed in §4 Bucket A Tier 2a. No Bucket B, Held, or Bucket C SKU may be approved as part of this tranche.

**EC-2 — LionWheel poll rerun after seeding completes.**
A LionWheel mirror poll run completes successfully after all 3 Bucket A Tier-2a aliases have reached `approval_status='approved'`. The poll must be verifiably newer than the last alias approval timestamp. Check the jobs log at `/admin/integrations` or query `private_core.job_runs` for the most recent `lionwheel_pull` run with `status='success'`.

**EC-3 — `lionwheel_unknown_sku` exception count drops materially.**
Open exception count for `category='lionwheel_unknown_sku'` in `private_core.exceptions` drops from 65 to 26 or fewer. The resolution breaks down as: Tier-1 (36 items, resolved by Step 1 `legacy_sku` match) + Tier-2a ODK (3 items, resolved by Step 2 alias lookup) = 39 items resolved. The remaining 26 or fewer open exceptions correspond to Bucket B items (held for Tom review), Held items (3 prefix/body-mismatch items), and Bucket C items (bundles + other). GTSET-* exceptions remain open but are tagged `bundle_sku=true` in exception detail; they count toward the 26 remaining, not toward the closed set.

**EC-4 — Retroactive backfill complete and non-zero open-order demand confirmed.**
The retroactive backfill SQL (`backfill_lionwheel_item_ids.sql`, authored by W1 at `C:/Users/tomw2/Projects/gt-factory-os/scripts/backfill_lionwheel_item_ids.sql`) has been run after alias seeding. The backfill must execute two passes in order (Pass 1: `legacy_sku` match for historical Tier-1 rows; Pass 2: alias-based match for ODK rows — see §5). After the backfill and the subsequent LionWheel poll, `api_read.v_planning_demand` contains at least one row with `demand_source='open_order'` (or `source_type='open_order'` per the view's column naming) and a non-null `item_id` corresponding to a Bucket A item. Recommended first check: `item_id='FG-DET-1L'` (DETOX 1L, mapped from LionWheel SKU `GT-LUI-LOW-1L` via Step 1 `legacy_sku` match).

**EC-5 — Next planning run reflects non-zero open-order net requirements.**
A planning run is triggered after EC-4 is confirmed. The resulting `planning_run_lines` output shows non-zero net requirements for at least one Bucket A FG item, attributable to open-order demand (not forecast alone). This confirms the full pipeline: resolver active → mirror resolved → demand view populated → planning engine consumed.

**EC-6 — `v_planning_demand` shows `source_type='open_order'` rows for at least one resolved item.**
After EC-4 is confirmed, `api_read.v_planning_demand` must contain at least one row with `source_type='open_order'` (or `demand_source='open_order'`) and a non-null `item_id` that is a Bucket A item. This exit criterion is distinct from EC-4: EC-4 confirms the backfill ran and demand exists; EC-6 confirms the view's column semantics are correct and the demand source label is present as expected by the planning engine consumer. If EC-6 fails after EC-4 passes, diagnose the view's source-type labeling before triggering EC-5.

**EC-7 — GTSET-* exceptions have `bundle_sku=true` in detail.**
Open `lionwheel_unknown_sku` exceptions for GTSET-* SKUs carry `bundle_sku=true` in their exception detail field. They are not silently absent from the exception queue. Verify: query `private_core.exceptions` for `category='lionwheel_unknown_sku'` and `detail->>'bundle_sku' = 'true'` — at least one GTSET-* exception must match. If GTSET-* exceptions are absent entirely (silently dropped) rather than present and tagged, this exit criterion fails and the resolver's exception-subcategorization behavior must be diagnosed.

---

## 4. Three-bucket categorization

The 65 distinct `lionwheel_unknown_sku` exceptions have been categorized into four groups based on confidence of mapping and readiness to seed: Bucket A (seed now), Held items (pending confirmation), Bucket B (hold for Tom review), Bucket C (policy or new-item decision required). Each group has a hard rule.

---

### Bucket A — Seed now (39 items total, HIGH confidence)

These 39 SKUs have unambiguous 1:1 mappings to existing `items.item_id` values. They are split into two sub-tiers based on resolver step.

---

#### Tier 1 — Exact `legacy_sku` match (36 items)

These 36 items resolve via Step 1 of the resolver (direct `legacy_sku` match). No `integration_sku_map` alias row is created for them. The resolver handles them automatically once the `legacy_sku` resolver path is active.

Tom must verify each `item_id` value below against `private_core.items` via `/admin/items` before the seeding session. If any canonical `item_id` does not exist in `private_core.items`, that row must be held and treated as a Bucket B item until the master-data discrepancy is resolved.

| LionWheel external SKU | Canonical item_id | Product name |
|---|---|---|
| FG-CAL-0.5L | FG-CAL-0.5L | CALM 0.5L |
| FG-CAL-1L | FG-CAL-1L | CALM 1L |
| FG-FRE-0.5L | FG-FRE-0.5L | FRESH 0.5L |
| FG-FRE-1L | FG-FRE-1L | FRESH 1L |
| FG-FRE-NS-0.5L | FG-FRE-NS-0.5L | FRESH NS 0.5L |
| FG-FRE-NS-1L | FG-FRE-NS-1L | FRESH NS 1L |
| FG-CON-0.5L | FG-CON-0.5L | CONSCIOUSNESS 0.5L |
| FG-CON-1L | FG-CON-1L | CONSCIOUSNESS 1L |
| FG-ENE-0.5L | FG-ENE-0.5L | ENERGY 0.5L |
| FG-ENE-1L | FG-ENE-1L | ENERGY 1L |
| FG-DET-0.5L | FG-DET-0.5L | DETOX 0.5L |
| FG-DET-1L | FG-DET-1L | DETOX 1L |
| FG-DET-NS-0.5L | FG-DET-NS-0.5L | DETOX NS 0.5L |
| FG-DET-NS-1L | FG-DET-NS-1L | DETOX NS 1L |
| FG-NAM-0.5L | FG-NAM-0.5L | NAMASTEA 0.5L |
| FG-NAM-1L | FG-NAM-1L | NAMASTEA 1L |
| FG-DES-1L | FG-DES-1L | DESERTEA 1L |
| FG-REV-0.5L | FG-REV-0.5L | REVIVE 0.5L |
| FG-REV-1L | FG-REV-1L | REVIVE 1L |
| FG-COS-LYC-0.3L | FG-COS-LYC-0.3L | COSMO LYCHEE 0.3L |
| FG-SAN-ELI-RED-0.75L | FG-SAN-ELI-RED-0.75L | SANGRIA ELITA RED 0.75L |
| FG-SAN-ELI-WHI-0.75L | FG-SAN-ELI-WHI-0.75L | SANGRIA ELITA WHITE 0.75L |
| FG-NON-SAN-1L | FG-NON-SAN-1L | NONOMIMI SANGRIA 1L |
| FG-NON-SAN-3.85L | FG-NON-SAN-3.85L | NONOMIMI SANGRIA 3.85L |
| FG-PINK-SAN-1L | FG-PINK-SAN-1L | PINK SANGRIA 1L |
| FG-WHI-SAN-1L | FG-WHI-SAN-1L | WHITE SANGRIA 1L |
| FG-MUZ-JAS-MIX-1L | FG-MUZ-JAS-MIX-1L | MUZA JASMIN MIXER 1L |
| FG-MUZ-PNMM-MIX-1L | FG-MUZ-PNMM-MIX-1L | MUZA PINK MAMA MIXER 1L |
| FG-MUZ-PURK-MIX-1L | FG-MUZ-PURK-MIX-1L | MUZA PURPLE KISS MIXER 1L |
| FG-MUZ-TRO-MIX-1L | FG-MUZ-TRO-MIX-1L | MUZA TROPICAL ISRAELI MIXER 1L |
| FG-MUZ-HER-0.2L | FG-MUZ-HER-0.2L | MUZA HERBAL COCKTAIL 0.2L |
| FG-MUZ-JAS-0.2L | FG-MUZ-JAS-0.2L | MUZA JASMINE COCKTAIL 0.2L |
| FG-MUZ-NEG-0.2L | FG-MUZ-NEG-0.2L | MUZA NEGRONI COCKTAIL 0.2L |
| FG-MUZ-QUV-0.2L | FG-MUZ-QUV-0.2L | MUZA QUEEN VIOLET COCKTAIL 0.2L |
| FG-MAT-18G | FG-MAT-18G | MATCHA 18G |
| FG-MAT-500G | FG-MAT-500G | MATCHA 500G |

Count: 36 rows. These 36 resolve automatically via Step 1 (`legacy_sku` exact match). No alias rows are created for them.

---

#### Tier 2a — ODK aliases seeded in this tranche (3 items)

These 3 items do NOT match any `legacy_sku` exactly (LionWheel omits the `-1L` pack suffix). They resolve via Step 2 (alias lookup) once the alias rows below are approved in `integration_sku_map`. These are the only 3 rows that require a seed operation in this tranche.

| LionWheel external SKU | Canonical item_id | Mapping rationale |
|---|---|---|
| GT-ODK-MAN-1 | ADD-ODK-MAN-1L | ODK suffix variant; LionWheel omits the `-1L` pack suffix; maps to confirmed 1L item |
| GT-ODK-PEA-1 | ADD-ODK-PEA-1L | ODK suffix variant; same pattern |
| GT-ODK-STR-1 | ADD-ODK-STR-1L | ODK suffix variant; same pattern |

**Seeding instruction for Tier 2a:** Tom must verify each `item_id` value above against `private_core.items` via `/admin/items` before seeding. If any row does not resolve to an existing, active item, that row must be held until the item master discrepancy is resolved. Do not create an alias pointing to a non-existent `item_id`; the FK constraint will reject it.

**Bucket A total: 36 (Tier 1) + 3 (Tier 2a) = 39 items.**

---

### Held for review — 3 items (do not seed until Tom confirms)

These 3 items have a candidate mapping but carry a prefix or body mismatch between the LionWheel external SKU and the candidate canonical `item_id`. They were previously listed in Bucket B. They are separated here because the mismatch pattern is specific and the confirmation needed is narrow — Tom must confirm which string is canonical before any alias can be seeded. They are NOT part of Bucket B's open-ended worklist; they are a distinct confirmation gate.

| LionWheel external SKU | Candidate canonical item_id | Mismatch type | Confirmation needed |
|---|---|---|---|
| GTCC-MUZ-JASM-1L | GTMX-MUZ-JASM-1L | Prefix mismatch: `GTCC` vs `GTMX` | Which prefix is canonical? If `GTMX` is correct in items, this alias seeds as-is. If `GTCC` is canonical, the items row must be corrected first. |
| GTCC-MUZ-PNMM-1L | GTMX-MUZ-PNMM-1L | Prefix mismatch: `GTCC` vs `GTMX` | Same question as above for Pink Mama variant. |
| GTCC-NM-SAN-3.85L | GTCC-NON-SAN-3.85L | Body mismatch: `NM` vs `NON` | Is `NM` an abbreviation for `NON` (Nonomimi)? Which string appears in `private_core.items.item_id`? |

**Status of all 3: `HELD_PENDING_REVIEW`.**

Do not seed any of these 3 items in this tranche. They fire `lionwheel_unknown_sku` exceptions with standard unknown subcategory (not `bundle_sku=true`) until resolved. After Tom provides confirmation, they can be seeded in a follow-on pass as Tier 2b aliases (they require alias rows because the external SKU does not match the canonical item_id exactly). See §9 Held items tracking table for full status.

---

### Bucket B — Hold for Tom review (10 items, MEDIUM confidence)

These 10 SKUs have a candidate mapping but require Tom's explicit confirmation before seeding. Each has a specific question that must be answered. Tom must answer each question before these aliases can be seeded in a follow-on tranche.

Note: 3 items previously listed here (GTCC-MUZ-JASM-1L, GTCC-MUZ-PNMM-1L, GTCC-NM-SAN-3.85L) have been promoted to the "Held for review" section above because their confirmation need is narrower and more specific. The 10 items below require more open-ended confirmation.

| LionWheel external SKU | Question requiring Tom's answer |
|---|---|
| AP-DRI-ORA | Does this map to `ADD-GAR-ORA-DRY` (Orange Dry)? Confirm the AP- prefix is an alternate supplier code and this is the same physical item. |
| AP-DRI-ROS | Does this map to `ADD-GAR-ROSE-DRY` (Rose Dry)? Same AP- prefix question as above. |
| GT-GLA-CUP | Is the Measuring Cup a stockable item or a promotional/packaging accessory? If it is a real stock item, a row in `private_core.items` must exist before the alias can be seeded. |
| GT-PUE-FRE-1L | Is Pu-erh lemon sugar-free an active product, discontinued, or a new product not yet in the item master? If active and missing from items, add the item row first. |
| GT-MUZ-JASM-1L | Is this a Muza 1L Jasmine Cocktail? Items currently has Muza 0.2L cocktails and Muza 1L mixers; a Muza 1L cocktail item row may not exist. See also §7 Muza 1L debt item. |
| GT-MUZ-PNMM-1L | Is this a Muza 1L Pink Mama Cocktail? Same question as above. |
| GT-MUZ-PSSP-1L | Is this a Muza 1L Purple Kiss/Passion cocktail? Same question. |
| GT-MUZ-TROJ-1L | Is this a Muza 1L Tropical Israeli Cocktail? Same question. |
| GT-MUZ-ANBL-1L | Is this a Muza 1L Anabelle Cocktail or similar? No matching item_id confirmed. |
| GT-MUZ-APPZ-1L | Is this a Muza 1L Apple/Zen Cocktail or similar? No matching item_id confirmed. |

Note: GT-MUZ-BLBR-1L and GT-MUZ-SMAR-1L previously listed in Bucket B are not shown above. If they were part of the original 13-item Bucket B list, verify their current exception status against `private_core.exceptions` before the next seeding pass; they may have been resolved or may require separate treatment.

These 10 items are NOT seeded in this tranche. They are logged here as an actionable worklist for Tom. Once Tom confirms the answers, a follow-on seeding pass can close these.

---

### Bucket C — Policy or new-item decision required (13 items, do not seed)

These 13 SKUs cannot be seeded in any near-term tranche without first making a structural or policy decision. They are excluded from both this tranche and the Bucket B follow-on pass until the prerequisite decision is made.

#### GTSET-* bundle SKUs — Bundle demand excluded, pending bundle-policy tranche

These 9 GTSET-* SKUs represent multi-item gift sets or promotional packs. They are explicitly categorized as "bundle demand excluded — pending bundle-policy tranche."

**Key facts about GTSET-* SKUs:**
- They cannot be resolved by alias. Multi-item bundles have no single GT item that maps to them. Creating an alias to any one `item_id` would be semantically wrong and would misrepresent the demand.
- They are NOT silently ignored. They fire `lionwheel_unknown_sku` exceptions with `bundle_sku=true` in the exception detail. This subcategorization allows them to be filtered separately from standard unknown-SKU exceptions without requiring a policy decision now.
- They are NOT phantom items. No `items` row is created for them in this tranche.
- A separate bundle-policy tranche will define the correct modeling approach. That tranche must choose one of: (a) model bundles as items with a BOM (demand explosion), (b) exclude bundles from planning demand via a non-planning item type, or (c) suppress at the ingestion layer. None of these options is a requirements-only decision; each requires schema, runtime, or master-data changes outside this tranche's scope.
- Bundle order volume is expected to be a small fraction of total LionWheel order volume. The planning risk of missing bundle demand is lower than the risk of making the wrong structural decision about bundle modeling.

| LionWheel external SKU | Reason for exclusion | Decision required |
|---|---|---|
| GTSET-001 (and 8 other GTSET-* SKUs) | Multi-item bundle; no single item_id represents the bundle; cannot be resolved by alias | Bundle-policy tranche: choose demand explosion, planning exclusion, or ingestion suppression |

#### Other Bucket C items

| LionWheel external SKU | Reason for exclusion | Decision required |
|---|---|---|
| GTMN-PIK-254 | Unknown product type. SKU pattern does not match any known GT product family prefix. No candidate `item_id` can be determined. | Tom must identify what physical product this represents. If it is a real FG item not yet in the master, add the item row first. |
| 7290003803217 | Barcode for a non-GT hardware accessory (verified: international barcode format, not GT SKU format). This is not a GT finished good. | Dismiss this line from the exception queue. Do not create an alias. The mirror line should be suppressed at the ingestion layer. |
| Empty string SKU (blank) | Malformed LionWheel order line with no SKU value. This is a data quality defect in the source order, not an unmapped item. | Suppress, not alias. The exception should be acknowledged and the underlying LionWheel order line flagged for cleanup. Do not create an alias row for an empty string. |
| TEST-LW-PROBE-FG-1 | Test artifact injected into LionWheel (likely from a development probe or test order). Should not exist in production order data. | Dismiss and resolve the exception. Remove the test order from LionWheel. Do not create an alias for a test SKU. |

---

## 5. Mandatory retroactive backfill requirement

### 5.1 Why backfill is required

When the 39 Bucket A items are activated (36 via `legacy_sku` resolver, 3 via approved aliases), the `orders_mirror_lines` rows that were previously written with `item_id = NULL` and `resolution_status = 'unresolved'` for those SKUs do NOT automatically update. The mirror poll resolver only runs at poll time — it does not retroactively re-resolve existing rows when a new alias is approved or when the `legacy_sku` resolver path is activated.

This means: even after all 39 Bucket A items are resolved, any `orders_mirror_lines` row written before the resolver was active will continue to have `item_id = NULL`. Those rows will be excluded from `api_read.v_planning_demand` by the `resolution_status='resolved'` predicate (`gate5_input_contract.md §1.2`). Open orders placed before the activation date will not contribute demand until the backfill is run.

### 5.2 Backfill must run in two passes, in order

The backfill SQL is documented separately at `C:/Users/tomw2/Projects/gt-factory-os/scripts/backfill_lionwheel_item_ids.sql` (authored by W1). W1 must run this script immediately after Tom approves the final Bucket A Tier-2a alias — not at the next poll cycle, not the following day.

**Pass 1 — Exact `legacy_sku` match backfill (Tier 1, 36 items):**

For each `orders_mirror_lines` row where `resolution_status = 'unresolved'` and `lw_sku` matches an `items.legacy_sku` value exactly:
- Set `item_id` to the matched item's `item_id`
- Set `resolution_status` to `'resolved'`

Pass 1 must run before Pass 2. Pass 1 handles the bulk of the backfill volume (36 items). Running Pass 2 first would leave Tier-1 rows unresolved and produce an incorrect post-backfill count.

**Pass 2 — Alias-based backfill (Tier 2a ODK, 3 items):**

For each `orders_mirror_lines` row where `resolution_status = 'unresolved'` and `lw_sku` matches an approved alias in `integration_sku_map` for `source_channel = 'lionwheel'`:
- Set `item_id` to the approved alias's `item_id`
- Set `resolution_status` to `'resolved'`

Pass 2 runs after Pass 1. It must not overwrite rows already resolved by Pass 1.

**Both passes must be idempotent:** running either pass twice must produce the same result. Neither pass must modify any row whose `resolution_status` is already `'resolved'`.

### 5.3 EC-4 completion condition

Exit criterion EC-4 (§3 above) is only satisfied when BOTH of the following are true:
1. Both backfill passes have run and completed without errors (Pass 1 first, Pass 2 second).
2. `api_read.v_planning_demand` shows at least one row with `demand_source='open_order'` for a Bucket A item.

A poll re-run alone (without the backfill) will not satisfy EC-4, because the poll only processes the current snapshot of open LionWheel tasks — it does not retroactively resolve previously-written mirror lines.

---

## 6. Post-seeding visibility requirements

After this tranche lands, the operational system must make the following questions answerable by an admin without writing SQL. As of 2026-04-23, none of these are surfaced in the portal. This section documents the required end-state; the gap between today and that end-state is logged as operational debt in §7.

**Required question 1: How many LionWheel SKUs remain unresolved?**
The admin must be able to see, from the portal, a current count of open `lionwheel_unknown_sku` exceptions broken down by bucket (or at minimum: total unresolved). After this tranche closes, the expected steady-state count is 26 or fewer. Of those 26, some will be tagged `bundle_sku=true` (GTSET-*) and some will be standard unknowns. Both subcategories should be visible. New unresolved SKUs introduced by future LionWheel orders should appear in this count promptly. Current state: the Exceptions Inbox (`/inbox`) shows the raw exception list but provides no aggregate count by category or bucket.

**Required question 2: Which seeded aliases are active?**
The admin must be able to see all approved alias rows for `source_channel='lionwheel'` on a dedicated review surface, showing: the LionWheel external SKU, the mapped canonical item name and item_id, the approval date, and the approver. This surface is needed for ongoing maintenance and for verifying that the 3 Tier-2a ODK aliases landed correctly. Current state: `/admin/sku-aliases` shows all `integration_sku_map` rows including pending ones, but there is no dedicated "approved aliases" tab showing only live aliases with full context.

**Required question 3: Is open-order demand now entering planning?**
After seeding and backfill, the admin must be able to verify that at least one item is receiving non-zero `open_order` demand in the planning layer, without needing to query `v_planning_demand` directly. A demand-source indicator on the planning review surface (`/planner/runs/[id]`) or a dashboard tile showing "N SKUs with active open-order demand" would satisfy this requirement. Current state: the `/planner/runs/[id]` surface shows net requirements but does not break them down by demand source (forecast vs. open_order). An admin cannot tell from the portal alone whether the open-order demand pipeline is functioning.

---

## 7. Follow-up debt register

The following items are deferred operational debt created or made visible by this tranche. They are not blocked by this tranche — the tranche can close without them — but they must be tracked and prioritized. Each entry carries a severity rating aligned with `docs/gap_registry.md` conventions.

---

### Alias correction path (P1 debt — developer-assistance dependency)

**Problem:** If Tom seeds a wrong alias (i.e., approves the wrong `item_id` for a LionWheel external SKU), the only supported correction path today is a direct SQL statement executed by a developer:

```sql
UPDATE private_core.integration_sku_map 
SET item_id = '<correct_id>', approved_at = now()
WHERE source_channel = 'lionwheel' AND external_sku = '<the_sku>';
```

The portal has a revoke endpoint (`POST /api/v1/mutations/integration-sku-map/:id/revoke`), but the post-revoke state transition semantics are UNRESOLVED (see `lionwheel_alias_seeding_spec.md §7, UNRESOLVED-3`): it is not confirmed whether revoke soft-deletes the row, sets it to `rejected`, or sets it to `pending`. If the row is not removed or set to a state that allows a new row to be inserted, the `UNIQUE (source_channel, external_sku)` constraint will block seeding a corrected alias.

**Required:** A portal "view + revoke/remap" flow on the approved aliases tab at `/admin/sku-aliases`. Until this is built, any alias correction requires developer assistance and direct DB access.

**Severity:** P1. With 39 items being activated in a single session (including 3 alias seeds), the probability of at least one mapping error is non-trivial. Tom needs a self-service correction path.

---

### Approved alias review surface (P2 debt)

**Problem:** No portal surface currently shows all approved aliases at a glance. The `/admin/sku-aliases` page shows the full `integration_sku_map` including pending rows, but there is no second tab dedicated to approved mappings with full context (item name, source SKU, approval date, approver).

**Required:** A second tab on `/admin/sku-aliases` — "Approved Mappings" — showing: `external_sku`, mapped item name, `item_id`, approval date, approver identity (email or display name from `approved_by_snapshot`).

**Severity:** P2. Tom can work without this but cannot efficiently audit or review the alias set after seeding.

---

### New unknown SKU alert (P2 debt)

**Problem:** When LionWheel introduces a new SKU (a new product GT begins selling via LionWheel), the `lionwheel_unknown_sku` exceptions accumulate silently. There is no notification mechanism — no digest email entry, no dashboard alert, no freshness_check integration — that tells Tom "N new unmapped SKUs appeared since the last check."

**Required:** Either (a) inclusion in the daily digest email showing "N new `lionwheel_unknown_sku` exceptions since last digest" or (b) a freshness_check producer entry that alerts when the exception count for this category has grown since the prior successful poll. See `docs/integrations/freshness_check_contract.md` for the freshness producer model.

**Severity:** P2. After this tranche closes, Tom will not know when LionWheel introduces new SKUs unless he manually checks the Exceptions Inbox.

---

### Muza 1L cocktail items (P1 debt — blocks 8 Bucket B aliases)

**Problem:** Eight LionWheel SKUs (GT-MUZ-JASM-1L, GT-MUZ-PNMM-1L, GT-MUZ-PSSP-1L, GT-MUZ-TROJ-1L, GT-MUZ-ANBL-1L, GT-MUZ-APPZ-1L, GT-MUZ-BLBR-1L, GT-MUZ-SMAR-1L — listed in Bucket B) represent Muza 1L cocktail variants. The current `private_core.items` master has Muza 0.2L cocktails and Muza 1L mixers, but Muza 1L cocktails are not confirmed as distinct items in the master. These 8 LionWheel SKUs cannot be seeded until:
1. Tom confirms whether these are distinct products from the Muza 1L mixer line.
2. If distinct, item rows must be created in `private_core.items` for each Muza 1L cocktail variant.
3. Once item rows exist, the 8 aliases can be seeded as a follow-on pass.

**Severity:** P1. These 8 aliases represent real open orders in LionWheel that are currently invisible to planning. Every planning run that runs while these are unresolved understates Muza demand.

---

### Bundle policy decision (P2 debt — blocks 9 Bucket C GTSET aliases)

**Problem:** Nine GTSET-* bundle SKUs appear in LionWheel orders. Bundles are multi-item composite products (e.g., a gift set containing two or more FG items). The platform does not currently model bundles as items. There are three possible policies:

- **(a) Model bundles as items with a BOM:** Each bundle becomes an `items` row with `supply_method='MANUFACTURED'` and a BOM that explodes into the constituent FG items. Bundle demand would propagate through the planning engine as BOM-driven consumption.
- **(b) Exclude bundles from planning demand entirely:** Bundle SKUs are mapped to a special `exclude_from_planning` flag (or a dedicated non-planning item type) so that they create an alias (satisfying the FK constraint) but are filtered out of `v_planning_demand`.
- **(c) Suppress at ingestion layer:** The LionWheel edge function (or mirror handler) is modified to recognize GTSET-* SKUs and suppress them before writing `orders_mirror_lines` rows. No alias is created; the lines are silently dropped.

None of these options is a requirements-only decision — option (a) requires new item rows and potentially new BOM rows; option (b) may require a schema extension; option (c) requires a runtime handler change. The requirements contract here is: Tom must choose the policy before any GTSET-* alias is seeded or suppressed. Until then, GTSET-* exceptions fire with `bundle_sku=true` tag and remain open.

**Severity:** P2. These 9 SKUs represent bundle orders that are currently invisible to planning, but bundles likely represent a small fraction of total order volume compared to the direct FG items. The risk of over-ordering from missing bundle demand is lower than the risk of making the wrong structural decision about how bundles are modeled.

---

## 8. Tranche sequence

Exact steps, in order. Each step has a clear owner and a clear done condition.

**Step 1 — Tom navigates to `/admin/sku-aliases`.**
Owner: Tom. Done: page loads and shows the current `integration_sku_map` contents (including any existing pending rows).

**Step 2 — Tom verifies Tier 1 items resolve via `legacy_sku`.**
Owner: Tom. Verify that the 36 Tier-1 items in §4 Bucket A Tier 1 each correspond to an existing `items.legacy_sku` value via `/admin/items`. This step is a pre-flight check, not a seeding operation — no alias rows are created. If any Tier-1 item does not exist in `private_core.items`, treat that item as Bucket B until the master-data discrepancy is resolved. Done: Tom has confirmed all 36 Tier-1 item_ids are live in the items master.

**Step 3 — Tom seeds the 3 ODK Tier-2a aliases.**
Owner: Tom. Done: all 3 rows from §4 Bucket A Tier 2a exist in `integration_sku_map` with `approval_status='approved'`. Before seeding each row, verify the target `item_id` exists in `private_core.items` via `/admin/items`. Do not seed any Held, Bucket B, or Bucket C item. If the portal QuickCreate flow requires creating in `pending` state first and then approving separately, complete both steps for each alias before moving to the next.

**Step 4 — W1 runs the retroactive backfill SQL (two passes in order).**
Owner: W1. Must run immediately after Step 3 completes — do not wait for the next poll cycle. Script location: `C:/Users/tomw2/Projects/gt-factory-os/scripts/backfill_lionwheel_item_ids.sql`. Pass 1 (legacy_sku match) runs first; Pass 2 (alias match) runs second. Done: both passes run without errors; W1 confirms the number of rows updated in each pass (expected: previously-unresolved `orders_mirror_lines` rows for the 36 Tier-1 SKUs and 3 ODK SKUs now have `item_id` populated and `resolution_status='resolved'`).

**Step 5 — W1 re-runs the LionWheel poll.**
Owner: W1. Trigger via `POST /api/v1/mutations/lionwheel/poll` (or via pg_cron trigger if the manual endpoint is not exposed — see jobs log at `/admin/integrations` for the relevant trigger path). Done: a new `lionwheel_pull` job run completes with `status='success'` with a timestamp after the last alias approval in Step 3.

**Step 6 — W1 verifies the pipeline with `verify_lionwheel_demand_flow.sql`.**
Owner: W1. This verification script (or equivalent targeted queries) must confirm:
- `lionwheel_unknown_sku` exception count dropped from 65 to 26 or fewer (EC-3). GTSET-* exceptions remain open but must carry `bundle_sku=true` in detail (EC-7).
- `api_read.v_planning_demand` contains at least one row with `demand_source='open_order'` (or `source_type='open_order'`) for a Bucket A item (EC-4 and EC-6). Recommended first check: item_id for DETOX 1L (`FG-DET-1L`) — verify this item has non-zero `open_order` demand in `v_planning_demand`.
- At least one GTSET-* exception has `bundle_sku=true` in detail (EC-7).

Done: all three conditions above are confirmed. If any fails, do not proceed to Step 7; diagnose and resolve.

**Step 7 — W1 triggers a planning run.**
Owner: W1. Trigger via `POST /api/v1/mutations/planning/runs`. Done: planning run completes with `status='completed'` (or equivalent terminal status per `planning_runs` status lifecycle).

**Step 8 — W1 verifies net requirements for at least one Bucket A FG item are non-zero (EC-5).**
Owner: W1. Query `planning_run_lines` for the run created in Step 7. Find at least one `item_id` corresponding to a Bucket A FG item (recommended: DETOX 1L or any seeded item known to have open orders). Confirm `net_required_qty > 0`. Done: EC-5 confirmed.

**Step 9 — Tom reviews §7 deferred debt items and decides prioritization.**
Owner: Tom. The alias correction path (P1), Muza 1L items (P1), approved alias review surface (P2), new unknown SKU alert (P2), bundle policy decision (P2), and Held items (§9) should each receive a priority assignment. Tom decides which to address in the next layer and which to defer further.

---

## 9. Held items tracking table

The 3 held items from the "Held for review" section (§4) are tracked here with their current status and the confirmation required before each can be promoted to a seeding pass.

| LionWheel external SKU | Candidate canonical item_id | Status | Reason held | Confirmation required before seeding |
|---|---|---|---|---|
| GTCC-MUZ-JASM-1L | GTMX-MUZ-JASM-1L | HELD_PENDING_REVIEW | Prefix mismatch: `GTCC` in LionWheel vs `GTMX` in candidate item_id | Tom confirms: which prefix is canonical in `private_core.items`? If `GTMX-MUZ-JASM-1L` is the live item_id, alias seeds as GT-ODK pattern. If `GTCC-MUZ-JASM-1L` is canonical, the items row must be corrected first. |
| GTCC-MUZ-PNMM-1L | GTMX-MUZ-PNMM-1L | HELD_PENDING_REVIEW | Prefix mismatch: `GTCC` in LionWheel vs `GTMX` in candidate item_id | Same confirmation as above for Pink Mama variant. |
| GTCC-NM-SAN-3.85L | GTCC-NON-SAN-3.85L | HELD_PENDING_REVIEW | Body mismatch: `NM` in LionWheel vs `NON` in candidate item_id | Tom confirms: is `NM` an abbreviation for `NON` (Nonomimi)? Which string is the live `item_id` in `private_core.items`? If `GTCC-NON-SAN-3.85L` is the live item_id, the alias maps `GTCC-NM-SAN-3.85L` → `GTCC-NON-SAN-3.85L`. |

When Tom provides confirmation for any held item, the item moves from `HELD_PENDING_REVIEW` to a follow-on seeding pass as a Tier 2b alias (all three require alias rows because the external SKU does not exactly match the canonical item_id). Until confirmation is received, these 3 items fire standard `lionwheel_unknown_sku` exceptions (without `bundle_sku=true`) and contribute to the 26 remaining open exception count after this tranche closes.

---

## 10. What this tranche does NOT do

Explicit exclusions — these are outside scope and must not be attempted as part of this tranche:

- **Does not change `items.legacy_sku`.** It remains canonical and unchanged.
- **Does not decide bundle policy.** The nine GTSET-* SKUs in Bucket C remain unresolved. No GTSET alias is seeded. They fire exceptions tagged `bundle_sku=true`.
- **Does not seed Held items.** The 3 prefix/body-mismatch items in §4 "Held for review" remain at `HELD_PENDING_REVIEW` until Tom confirms the canonical string.
- **Does not create new item rows for Muza 1L cocktails.** The eight Bucket B Muza 1L aliases are held pending Tom's confirmation and potential item master additions.
- **Does not build the alias correction portal surface.** The P1 debt of "view + revoke/remap" flow on the approved aliases tab is acknowledged and logged but not built in this tranche.
- **Does not build the approved alias review tab.** The P2 debt second tab on `/admin/sku-aliases` is acknowledged and logged but not built.
- **Does not build new unknown SKU alerting.** The P2 debt of digest or freshness_check integration for new unmapped SKUs is acknowledged and logged but not built.
- **Does not modify the LionWheel edge function or mirror handler.** All work in this tranche is at the `integration_sku_map` data layer (Tom seeding) and at the backfill + verification layer (W1 running scripts). No runtime code is authored or modified.

---

## UNRESOLVED items

The following items are carried forward from `lionwheel_alias_seeding_spec.md` (UNRESOLVED-1 through UNRESOLVED-5) and remain unresolved. None of them block the core Bucket A seeding path; they gate scripted/API-driven approaches and edge-case correction paths.

- **UNRESOLVED-1: Create endpoint path.** The AMMC v1 closure doc lists approve, reject, and revoke endpoints but does not list a create endpoint. If the portal QuickCreate drawer uses an undocumented route (not `POST /api/v1/mutations/integration-sku-map`), scripted seeding cannot proceed until this route is verified from the live backend code. Gates: any scripted or API-driven seeding path beyond portal UI.

- **UNRESOLVED-2: Request body shape for approve and create endpoints.** The exact field names and required parameters for `POST /api/v1/mutations/integration-sku-map/approve` are not confirmed from any inspected artifact. Gates: API-driven bulk seeding; automated scripting.

- **UNRESOLVED-3: Revoke semantics (state transition).** The `revoke` endpoint exists but whether it soft-deletes, sets `approval_status='rejected'`, or sets `approval_status='pending'` is not stated. This matters for the alias correction path: if the old row is not removable, a corrected alias cannot be inserted due to the `UNIQUE (source_channel, external_sku)` constraint. Gates: alias correction workflow (§7, alias correction path debt).

- **UNRESOLVED-4: Whether the mirror re-resolver runs automatically on alias approval.** If the approval handler triggers synchronous re-resolution of matching `orders_mirror_lines` rows, the backfill pass sequencing interaction semantics change. Pass 2 of the backfill (§5.2) may become redundant for newly-created rows if synchronous re-resolution runs. Pass 1 (legacy_sku) is still required regardless. Gates: step sequencing precision.

- **UNRESOLVED-5: Whether `lionwheel_unknown_sku` exceptions auto-resolve on alias approval.** If the approval handler or re-resolver closes the associated exception, EC-3 verification may show a count drop even before the next manual poll. The worst-case path (exceptions do not auto-resolve) is documented in the sequence above. Gates: exception-inbox cleanup expectations after seeding.

- **UNRESOLVED-6: Exact live `item_id` values for Bucket A Tier-1 items.** The item_id values listed in §4 Bucket A Tier 1 are derived from the W1 DB analysis cross-referencing `lionwheel_unknown_sku` exception SKUs against `private_core.items.item_id`. Tom must verify each against the live items master before the seeding session. If any canonical `item_id` in the Tier-1 table does not exist in `private_core.items`, that row must be held (moved to Bucket B) until the master-data discrepancy is resolved. Cannot be silently healed: the Tier-1 table is a starting-point worklist, not a guaranteed-correct mapping list.

- **UNRESOLVED-7: Tier-1 count discrepancy.** The prior version of this document stated "37 exact legacy_sku matches" but the table contained 36 rows. CURRENT_STATE.md line 191 notes this. The resolver model update resolves this as: 36 Tier-1 items + 3 Tier-2a ODK = 39 Bucket A total. W1 must confirm the Tier-1 count equals exactly 36 by cross-referencing the table above against `private_core.items` before the seeding session.

---

*Authored: 2026-04-23. Updated: 2026-04-23 (resolver model locked; Tier-1/Tier-2a split; Held items section added; Bucket B reduced to 10; Bucket C GTSET bundle policy explicitly stated; EC-1/EC-3 updated; EC-6/EC-7 added; backfill two-pass ordering added; §9 Held items tracking table added). W4 executor (executor-w4). Requirements-only. No schema, no migrations, no runtime code. Supersedes `docs/lionwheel_alias_seeding_spec.md` as the authoritative contract for the current seeding tranche.*
