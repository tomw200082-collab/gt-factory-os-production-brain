# LionWheel SKU Alias Seeding — Requirements Spec

> **Artifact class:** W4 requirements-only spec.
> **Status:** AUTHORED 2026-04-23.
> **Problem being closed:** 42–168 LionWheel orders have `item_id = null` in the mirror because the LionWheel SKU strings (e.g., `GT-LUI-LOW-1L`) have no approved row in `private_core.integration_sku_map`. As a result `v_planning_demand` receives zero open-order demand and every planning run operates on forecast only.
> **Authority sources:** `docs/gate5_integration_sku_map_implementation_note.md`, `docs/gate5_input_contract.md §1.2–§1.3`, `docs/integrations/exceptions_contract.md §2.1`, `docs/integrations/lionwheel_mirror_contract.md`, `docs/integrations/lionwheel_live_inspection_2026-04-18.md §3.4`, `docs/ammc_v1_closure.md §3.2 (Aliases endpoints)`, CURRENT_STATE.md (Gate 4 follow-on items).

---

## 1. Purpose

### 1.1 The gap

Every LionWheel task carries embedded `order_items[]` lines. Each line has a `sku` field (text, e.g., `"GT-SHI-CER-18*22"`, observed in `lionwheel_live_inspection_2026-04-18.md §3.4`). When the mirror poll upserts a line, it resolves the external SKU to an internal `item_id` by looking up `private_core.integration_sku_map` for:

```
source_channel = 'lionwheel'
AND external_sku = <line.sku>
AND approval_status = 'approved'
```

If no approved alias row exists, the mirror line's `item_id` is left null, `resolution_status` is set to `'unresolved'`, and a `lionwheel_unknown_sku` exception is written to `private_core.exceptions` with `dedupe_key = 'lw_sku:<sku_value>'`.

Per `gate5_input_contract.md §1.2`, only mirror lines with `resolution_status='resolved'` and a non-null `item_id` are included in `api_read.v_planning_demand`. Lines that fail this predicate are silently excluded from demand.

### 1.2 Operational consequence

With 42–168 open `lionwheel_unknown_sku` exceptions:

- `v_planning_demand.source_type='open_order'` rows are zero or near-zero for the unresolved SKUs.
- Planning runs compute net FG requirements using forecast demand only.
- Purchase and production recommendations are systematically under-stated for every item whose open orders are unresolved.
- The planning engine does not fail; it silently produces incomplete recommendations. This is correct A3 behavior, not a defect in the engine, but it is operationally invalid until alias rows are seeded.

### 1.3 What seeding closes

Seeding an approved alias row for each unresolved LionWheel SKU causes the next LionWheel mirror poll to re-resolve previously-unresolved lines. After resolution, those lines appear in `v_planning_demand` as `source_type='open_order'` rows. The next planning run will include them.

---

## 2. Data flow

```
LionWheel /api/v1/tasks.json (polled every 15 min)
  → mirror upsert: orders_mirror_lines row with lw_sku = "GT-LUI-LOW-1L"
  → resolver lookup:
      SELECT item_id
      FROM private_core.integration_sku_map
      WHERE source_channel = 'lionwheel'
        AND external_sku   = 'GT-LUI-LOW-1L'
        AND approval_status = 'approved'
  →  MISS (no row)  → resolution_status = 'unresolved', item_id = null
                    → lionwheel_unknown_sku exception emitted
                    → line EXCLUDED from v_planning_demand
  →  HIT (row exists) → resolution_status = 'resolved', item_id = <canonical>
                      → line INCLUDED in v_planning_demand as open_order demand
                      → planning run picks it up
```

The `integration_sku_map` table is the mapping bridge. It is the only place where the join between LionWheel's external SKU namespace and the platform's canonical `items.item_id` namespace lives. Every other layer (mirror, demand view, planning engine) is downstream of this table.

### 2.1 Key table facts (from verified schema `0033_integration_sku_map.sql`)

| Column | Type | Purpose |
|---|---|---|
| `alias_id` | uuid PK | System-generated |
| `source_channel` | text CHECK `('lionwheel','shopify','green_invoice')` | Must be `'lionwheel'` for this seeding cycle |
| `external_sku` | text | The literal SKU string as it appears in LionWheel `order_items[].sku` |
| `item_id` | text NOT NULL FK → `items.item_id` | The canonical internal item this SKU resolves to |
| `approval_status` | text CHECK `('pending','approved','rejected')` | Must be `'approved'` to resolve demand; `'pending'` rows never resolve |
| `created_by_user_id` | uuid FK → `app_users.user_id` | Admin who created the row |
| `created_by_snapshot` | jsonb | Audit snapshot of creator display name / email |
| `approved_by_user_id` | uuid FK → `app_users.user_id` | Admin who approved |
| `approved_at` | timestamptz | Timestamp of approval |
| `notes` | text | Free-text rationale |
| `UNIQUE (source_channel, external_sku)` | — | At most one row per (channel, sku) pair |

A pending row behaves identically to no row for resolution purposes. An admin creating a row via the portal creates it in `pending` state and must separately approve it before it feeds demand.

---

## 3. Admin workflow

### 3.1 See the worklist

Navigate to `/admin/sku-aliases` in the portal. This page lists all rows in `integration_sku_map`. Filter or sort by `source_channel = 'lionwheel'` and `approval_status = 'pending'` to see the current unmapped queue.

Alternatively, open the **Exceptions Inbox** (`/inbox`) and filter for category `lionwheel_unknown_sku`. Each open exception has a `related_entity_id` field carrying the unresolved SKU string, and `detail` text identifying the LionWheel-side SKU. The exceptions list is the live unresolved queue; the `/admin/sku-aliases` page is the mapping management surface. Both reflect the same underlying state.

**Volume note:** as of 2026-04-23 there are 42–168 open `lionwheel_unknown_sku` exceptions. Tom may need to map up to 168 distinct LionWheel SKU strings to internal item IDs. The exact count changes as the mirror polls new orders.

### 3.2 Identify the correct internal item

For each unresolved LionWheel SKU string (e.g., `GT-LUI-LOW-1L`), the admin must identify the corresponding `item_id` in `private_core.items`.

- LionWheel SKU format observed in production: `GT-<family>-<variant>-<pack>` (e.g., `GT-SHI-CER-18*22`, `GT-ODK-MAN-1`). In most cases the LionWheel SKU will closely match or equal the canonical `item_id`. The mapping is not guaranteed to be identity — verify against the items master.
- Use `/admin/items` to search by `item_id` or name. The item must have `supply_method` of `MANUFACTURED`, `BOUGHT_FINISHED`, or `REPACK` as appropriate for the finished good being ordered.
- If no matching item exists in the master, the item must be created first (via `/admin/items`) before the alias can be seeded. **Do not create an alias pointing to a non-existent item_id; the FK constraint will reject it.**
- If the LionWheel SKU maps to a variant that does not exist as a discrete item (e.g., a pack-size the platform does not track separately), raise this as a master-data gap — do not invent an item to satisfy the alias.

### 3.3 Create the alias row

**Via the portal (recommended for operator-facing seeding):**

The `/admin/sku-aliases` page provides a create flow (QuickCreate drawer or equivalent). Required fields:
- `source_channel`: set to `lionwheel`
- `external_sku`: the exact LionWheel SKU string as it appears in the exception (copy-paste; do not retype — casing and special characters matter)
- `item_id`: the canonical internal item ID confirmed in step 3.2
- `notes`: optional rationale

On creation, the row is written with `approval_status = 'pending'`. It does not yet resolve demand.

**Via the backend endpoint (verified in `ammc_v1_closure.md §3.2`):**

The mutations endpoint `POST /api/v1/mutations/integration-sku-map/approve` exists. The exact request body shape for creating-then-approving a row in a single call is UNRESOLVED — see §7 below. The separate create-then-approve two-step is safe and uses the portal surface. If a bulk import path is needed for seeding many rows at once, see §6.

### 3.4 Approve the alias row

After creating the alias row (which starts in `pending`), it must be approved to become active.

**Via the portal:** on `/admin/sku-aliases`, locate the pending row and use the approve action. Only users with `admin` or `planner` role may approve.

**Via the backend endpoint:** `POST /api/v1/mutations/integration-sku-map/approve` (observed in `ammc_v1_closure.md §3.2`). The exact request body shape is UNRESOLVED — see §7.

Self-approval is permitted in v1 (the table schema does not enforce a separate approver). For audit quality, Tom should consider creating the row and having a second admin approve it, but this is a process decision, not a system constraint.

Once `approval_status` is set to `'approved'`, the row is immediately live. The resolver will use it on the next poll.

### 3.5 Confirm resolution after next poll

The LionWheel mirror polls every 15 minutes. After the next successful poll following alias approval:

1. The previously-unresolved `orders_mirror_lines` rows that carried the now-mapped SKU will be re-resolved: `resolution_status='resolved'`, `item_id` populated.
2. The `lionwheel_unknown_sku` exception for that SKU will remain open until manually acknowledged or until the dedup mechanism evaluates it. It does NOT auto-resolve when the SKU is mapped (exception auto-resolution rules per `exceptions_contract.md §4` do not include `lionwheel_unknown_sku`). The admin must manually resolve or acknowledge the exception.
3. On the next planning run, those order lines will appear as `source_type='open_order'` rows in `v_planning_demand`.

**How to confirm:** after 15–30 minutes, run a planning run or query `v_planning_demand` filtered by the newly-mapped `item_id` and `source_type='open_order'`. If rows appear, the alias is live and working. If no rows appear, check that the alias `approval_status` is `'approved'` (not `'pending'`) and that the mirror poll has completed at least one successful run since approval (check `/admin/integrations` or the jobs log for the most recent `lionwheel_pull` success timestamp).

---

## 4. Backend contract

### 4.1 Table-level contract (verified from schema)

The creating/approving workflow writes to `private_core.integration_sku_map`. The table shape is fully verified in `docs/gate5_integration_sku_map_implementation_note.md §2` and confirmed by the live migration `db/migrations/0033_integration_sku_map.sql`. The three core fields for a LionWheel alias row are:

| Field | Required value |
|---|---|
| `source_channel` | `'lionwheel'` (exactly; lowercase; CHECK-bounded) |
| `external_sku` | exact LionWheel SKU string from `order_items[].sku` |
| `item_id` | canonical `items.item_id` (text PK; must reference a real item) |

Additionally:
- `approval_status` must be `'approved'` for the alias to resolve demand (creating as `'pending'` then approving is the normal workflow).
- The `UNIQUE (source_channel, external_sku)` constraint means only one alias per LionWheel SKU string. If an alias already exists in any status, attempting to create a duplicate will fail. Use the reject + revoke path (see §5) to replace a wrong mapping.

### 4.2 API endpoints (observed in `ammc_v1_closure.md §3.2`)

The following endpoints exist in the backend as of AMMC v1 closure:

| Verb | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/mutations/integration-sku-map/approve` | Approve a pending alias row (or batch) |
| `POST` | `/api/v1/mutations/integration-sku-map/:id/reject` | Reject a pending alias row |
| `POST` | `/api/v1/mutations/integration-sku-map/:id/revoke` | Revoke an approved alias row (returns it to a non-resolving state) |

**UNRESOLVED:** The endpoint for creating a new alias row (`POST /api/v1/mutations/integration-sku-map` or equivalent create path) is not listed in the AMMC v1 closure doc. The closure lists only approve, reject, and revoke. Either the create step happens via the portal UI with a separate backend route, or creation is embedded in the approve call. This must be verified against the live backend code before bulk seeding is scripted. See §7, UNRESOLVED item 1.

**UNRESOLVED:** The exact request body shape for `POST /api/v1/mutations/integration-sku-map/approve` is not in any inspected artifact. The field names and required vs optional body parameters are unknown from requirements artifacts alone. See §7, UNRESOLVED item 2.

### 4.3 `form_submissions` envelope

The approval path uses the `form_submissions` idempotency envelope with `form_type = 'integration_sku_map_approve'` (per migration `0062_form_submissions_integration_sku_map_approve.sql`). This means:

- Each approval operation should carry a client-generated `idempotency_key`.
- Replaying the same key is safe (server dedup holds).
- The operation is logged in `form_submissions` for audit.

---

## 5. Rollback — undoing a wrong mapping

If an alias is approved with the wrong `item_id` (e.g., the LionWheel SKU was mapped to the wrong canonical item), the correction path is:

1. **Revoke the approved alias** via `POST /api/v1/mutations/integration-sku-map/:id/revoke`. This returns the alias to a non-resolving state. The `UNIQUE` constraint prevents a new alias for the same `external_sku` while the old row exists in any status, so the old row must be handled first.

2. The exact semantics of `revoke` — whether it soft-deletes the row, sets it to `rejected`, or sets it to `pending` — are **UNRESOLVED**. See §7, UNRESOLVED item 3. The revoke endpoint exists; its state-transition semantics must be verified from the backend code.

3. Once the old row is no longer in `approved` state, create a new alias row with the correct `item_id` and approve it.

4. On the next mirror poll (within 15 minutes), the previously-resolved lines that carried the old wrong `item_id` will be re-evaluated. If the new alias resolves to a different `item_id`, they will be updated. Any demand rows in `v_planning_demand` that referenced the old `item_id` via those lines will reflect the corrected item on the next read.

**Impact boundary:** revoking an alias affects only the mirror resolution path. It does not modify the `stock_ledger`, `current_balances`, or any historical planning run. Planning runs are immutable snapshots; a run that used the wrong `item_id` remains in history with the old data. The correction takes effect on the next planning run after the alias is corrected.

---

## 6. Volume note and bulk seeding path

### 6.1 Volume

CURRENT_STATE.md and `gate5_closure_decision_pack.md §8.1` both cite 42–168 open `lionwheel_unknown_sku` exceptions. The range reflects the live mirror state, which changes with each poll. The upper bound of 168 means Tom may need to map up to 168 distinct LionWheel SKU strings.

In practice, many LionWheel SKU strings likely follow the `GT-<family>-<variant>-<pack>` convention and will map 1:1 to existing `items.item_id` values. The actual manual mapping effort depends on how closely LionWheel SKUs match the canonical item ID namespace, which requires Tom to walk the worklist.

### 6.2 Bulk seeding

For seeding many rows at once, a SQL import script is the safest path:

```sql
-- Pattern for each row (to be run by an admin with DB access)
-- Source of truth for exact column names: 0033_integration_sku_map.sql
INSERT INTO private_core.integration_sku_map
  (source_channel, external_sku, item_id, approval_status, notes)
VALUES
  ('lionwheel', '<lw_sku_string>', '<canonical_item_id>', 'approved', 'Seeded <date> by <admin>');
```

The import script must:
- Set `source_channel = 'lionwheel'` on every row.
- Use the exact `external_sku` string as observed in the LionWheel exception detail (character-for-character).
- Reference a `item_id` that exists in `private_core.items`.
- Set `approval_status = 'approved'` directly if Tom is performing a supervised bulk seed (bypasses the create-then-approve two-step).

A SQL-level bulk import is a W1-scope operation (CLI/script path per CLAUDE.md §"Input-source map"). W4 cannot author the import script itself; this spec documents the requirements for what the script must do.

### 6.3 Verifying the worklist before bulk seeding

Before running a bulk seed, extract the live unresolved SKU list:

```sql
-- Extract the current unresolved SKU strings for source_channel='lionwheel'
-- (conceptual query; field names verified against exceptions_contract.md §3.2)
SELECT detail, related_entity_id
FROM private_core.exceptions
WHERE category = 'lionwheel_unknown_sku'
  AND status IN ('open', 'acknowledged')
ORDER BY created_at;
```

The `related_entity_id` field carries the unresolved SKU string per `exceptions_contract.md §3.2` dedupe pattern `lw_sku:<sku_value>`. Cross-reference each against `private_core.items` to build the mapping table before importing.

---

## 7. UNRESOLVED items

The following items cannot be filled from existing W4 artifacts and inspection evidence. Each must be resolved before the item it gates is safe to execute.

- **UNRESOLVED-1: Create endpoint path.** The AMMC v1 closure doc lists approve, reject, and revoke endpoints but does not list a create endpoint. The portal may use an undocumented route or the create may be embedded in the approve call. Must be verified from the live backend code (`api/src/`) before scripted seeding. Gates: step 3.3 portal-create flow and any scripted approach that bypasses SQL import.

- **UNRESOLVED-2: Request body shape for approve and create endpoints.** The exact field names, required vs optional parameters, and response shape for `POST /api/v1/mutations/integration-sku-map/approve` (and the create endpoint, if separate) are not in any inspected requirements artifact. Must be verified from the backend handler code or from a live probe against the portal. Gates: API-driven bulk seeding; automated scripting.

- **UNRESOLVED-3: Revoke semantics (state transition).** The `revoke` endpoint exists (`POST /api/v1/mutations/integration-sku-map/:id/revoke`) but its exact state transition — whether it hard-deletes, sets `approval_status='rejected'`, or sets `approval_status='pending'` — is not stated in any inspected artifact. The `UNIQUE (source_channel, external_sku)` constraint makes the post-revoke state critical: if the row is soft-deleted, a new row can be inserted; if it remains with a non-approved status, the create will conflict on the unique constraint. Must be verified from the backend migration or handler code. Gates: rollback workflow (§5).

- **UNRESOLVED-4: Whether the mirror re-resolver runs automatically on alias approval, or only on the next poll.** The spec above states re-resolution happens on the next 15-minute poll. If the backend handler for alias approval also triggers a synchronous re-resolution of matching `orders_mirror_lines` rows, the wait time is zero. This is a UX-accuracy item; the worst case (15-minute wait) is documented. Must be verified from the W1 approval handler code. Gates: step 3.5 confirmation timing.

- **UNRESOLVED-5: Whether `lionwheel_unknown_sku` exceptions auto-resolve on alias approval.** Per `exceptions_contract.md §4`, `lionwheel_unknown_sku` is not in the auto-resolution list. Step 3.5 states the admin must manually acknowledge or resolve the exception. If a post-approval re-resolver runs (per UNRESOLVED-4) and closes the exception automatically, this requirement changes. Must be verified from the W1 handler. Gates: exception-inbox cleanup expectations.

---

## 8. Acceptance criteria

After a successful seeding cycle, all of the following must be true:

**(a) Exception count for `lionwheel_unknown_sku` drops.**
The `private_core.exceptions` table has fewer open rows with `category='lionwheel_unknown_sku'` than before seeding. The count drops to zero once every LionWheel SKU that appears in `orders_mirror_lines` has an approved alias row.

**(b) `integration_sku_map` has N approved rows for `source_channel='lionwheel'`.**
The count of `approval_status='approved'` rows with `source_channel='lionwheel'` equals the number of distinct LionWheel SKU strings that appear in active (non-retired) mirror lines.

**(c) The next LionWheel poll resolves the previously-unknown orders.**
After alias approval and the next successful `lionwheel_pull` run (within 15 minutes), the `orders_mirror_lines` rows that previously had `item_id=null` now have `item_id` populated and `resolution_status='resolved'`.

**(d) A planning run shows non-zero open-order demand for seeded items.**
After criteria (a)–(c) are met, the next planning run produces `v_planning_demand` rows with `source_type='open_order'` and `item_id` matching the newly-seeded items. The planning run's purchase and production recommendations reflect the open-order demand signal.

**(e) No new `lionwheel_unknown_sku` exceptions appear on subsequent polls.**
After seeding is complete, new mirror polls should not emit new `lionwheel_unknown_sku` exceptions (assuming no new LionWheel SKU strings are introduced by GT operations). If new exceptions appear, they indicate LionWheel has introduced new product SKUs not yet in the alias table; those require a follow-on seeding pass.

---

## 9. References

- `docs/gate5_integration_sku_map_implementation_note.md` — ratified DDL shape, column semantics, resolution semantics.
- `docs/gate5_input_contract.md §1.2–§1.3` — inclusion rules for `v_planning_demand`; why `pending` and `rejected` aliases never resolve.
- `docs/integrations/exceptions_contract.md §2.1, §3.2, §4` — `lionwheel_unknown_sku` category, dedupe key pattern, auto-resolution rules.
- `docs/integrations/lionwheel_live_inspection_2026-04-18.md §3.4` — confirmed that LionWheel `order_items[].sku` is a text field with observed format `GT-<family>-<variant>-<pack>`.
- `docs/integrations/lionwheel_mirror_contract.md` — mirror architecture; dependency on `integration_sku_map` for SKU resolution.
- `docs/ammc_v1_closure.md §3.2` — confirmed backend endpoints (approve, reject, revoke) and `/admin/sku-aliases` portal route.
- `db/migrations/0033_integration_sku_map.sql` — live schema; verified column names and constraints.
- `db/migrations/0062_form_submissions_integration_sku_map_approve.sql` — confirms `form_type='integration_sku_map_approve'` is in the `form_submissions` envelope CHECK.
- `CURRENT_STATE.md` (Gate 4 follow-on items) — cites 42–168 open exceptions; identifies SKU alias saturation as a post-Gate-5 priority.

---

*Authored: 2026-04-23. W4 executor. Requirements-only. No schema, no migrations, no runtime code.*
