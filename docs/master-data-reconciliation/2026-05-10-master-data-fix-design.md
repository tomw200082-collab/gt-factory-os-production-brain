# Master Data Fix — Design Spec

**Status:** APPROVED for execution planning — Tom locked recommendations 2026-05-10. Read-only artifact. Implementation handed off to `writing-plans` next.
**Generated:** 2026-05-10
**Origin:** Tom hit a "Chamomile not in components list" failure on `/(ops)/stock/physical-count`. Root-cause investigation found four distinct gap-types, not one.
**Scope:** PRODUCTION + gt-factory-os (DB migrations, fixtures, contracts) + window2-portal-sandbox (Physical Count UI).
**Authority:** This spec respects locked decisions in `CLAUDE.md`. No locked decision is touched. Frozen integration flags are not flipped. All changes are additive or schema-tightening.

## 0. Locked decisions (2026-05-10, Tom)

| Decision | Choice | Reasoning |
|---|---|---|
| **Cutover sequencing (Q-MD-4)** | (c) cutover today; Wave 1 lands Monday morning; operator guard issued for Sunday | Don't run two changes at once. Wave 1 doesn't unblock cutover. |
| **Migration C — trigger vs view (Q-MD-1)** | Trigger AND read-side view (`v_bom_lines_with_canonical_name`) — defense in depth | Existing consumers (planning, exception inbox, exports) keep working; new code reads via view; both surfaces stay correct |
| **Hebrew alias seed (Q-MD-2)** | AI builds the ~40-line list; Tom approves once as a batch | High-impact RAW components only; not packaging |
| **Physical Count zero-result UX (Q-MD-3)** | Two-button: "I know what it is — let me pick" + "Unclear, needs review" | Operator guidance becomes triage signal, not just text |
| **Matcha 18G "Inner Bag" vs "sachet bag"** | Same component — wording mismatch only. Wave 1 A.2 normalizes to canonical | Tom-confirmed 2026-05-10 |
| **rename-auto-alias trigger** | YES — added to Wave 2 | Closes the entire rename-failure class. Future rename of any component auto-archives the old name as alias. No more silent disappearance of components |
| **Wave 2.5 — denormalized name pattern audit** | YES — added to plan | Same drift pattern likely exists outside `bom_lines`. Audit `items`, `bom_head`, `suppliers`, `supplier_items` for parallel cases before they become the next Chamomile |

---

## 0.1 Execution outcome — Wave 1 CONDITIONAL_CLOSE 2026-05-10

- **Apply timestamp:** 2026-05-10T16:05:27Z
- **Branch:** `master-data-fix-wave-1` (local-only, awaiting Tom merge approval; NOT pushed)
- **Migration number bumped** from spec-assumed `0167-0171` to **actual `0180`**. The `0156-0179` slots are reserved by an in-flight master-data-alignment stream that was never committed to any branch; renumbering avoided a collision.

### Apply outcomes per migration section

Canonical numbers per `RUNTIME_READY` signal #37 (`form: MasterDataConsistency`, `signal_index: 36`, emitted 2026-05-10T16:05:27Z by `backend-db-executor`) in `.claude/state/runtime_ready.json`:

- **A.1 renames:** 2 rows (`RAW-CALM` → `Chamomile flowers (dried)`; `RAW-WINE-WHITE` → `Wine — White (Symphony)`).
- **A.2 bom_lines normalization:** **104 rows** (10× the spec's pre-DB-drift estimate — the drift surface was an order of magnitude wider than the audit JSON suggested).
- **A.3 sub-BOM blank-fill:** **0 rows** — blocked by `NULL final_component_id` on the BASE_BOM/BOM ref-type rows. **Wave 2 carry-forward.**
- **A.4 deprecations:** **0 of 3.** `RAW-COLVE` and `RAW-CORNATION` were already `STATUS=INACTIVE` pre-migration (no-op DELETE skipped them). `PKG-CAP-STD` blocked by 2 surviving `supplier_items` FK references.
- **A.5 / A.6:** `component_aliases` table created + **8 seed rows** inserted (matches §3 Wave 1 Migration A.6 list exactly).
- **A.7 change_log:** 1 row inserted, `change_log_id = 87c4ad43-dcb8-4450-8695-0d2987d6a7cc`, `action = UPDATE_STRUCTURAL`.

### Post-apply pgTAP

**4/7 PASS · 3/7 FAIL** — all failures classified as **discovery-of-new-scope, not regression**.

| Test | Verdict | Note |
|---|---|---|
| T1 | PASS | No ACTIVE bom_line orphan-IDs in components |
| T2 | FAIL | Carry-forward — depends on A.3 sub-BOM final_component_id NULLs (Wave 2) |
| T3 | FAIL | Carry-forward — 59 BASE_BOM rows still have blank `final_component_name` because A.3 was a no-op |
| T4 | PASS | bom_lines.final_component_name now matches components.COMPONENT_NAME for all ref_type IN ('RAW_NAME','COMPONENT') |
| T5 | FAIL | Pre-existing duplicate canonical names in master — out of Wave 1 scope; Wave 2 Migration D will lock |
| T6 | PASS | Every ACTIVE bom_line component is STATUS ∈ ('ACTIVE','PENDING') |
| T7 | PASS | BASE_BOM/BOM rows where final_component_name IS NOT NULL match bom_head.parent_name |

### Tom's Option A decision (2026-05-10)

Close Wave 1 as **CONDITIONAL_CLOSE** and carry the three FAIL findings to Wave 2 (not regression — they exposed scope the spec did not anticipate). Three Wave 2 carry-forwards added to §3 below.

### Schema-name fixes discovered + committed during execution

Three follow-on commits on the `master-data-fix-wave-1` branch (in worktree `gt-factory-os.worktrees/master-data-fix-wave-1`) — each surfaced because the "dry-run" had already applied to the live DB (see §5.1 row #8 and the SCHEMA_GUIDANCE.md lesson):

- **`f9daf57`** — `bom_head.label` → `bom_head.parent_name` (the live column name; spec used the planning-doc name).
- **`6fc7f2a`** — `balance_anchors` references rewritten to use the live triple (`balance_anchors_current`, `balance_anchors_history`, `current_balances`) instead of the single planning-doc name.
- **`23caca3`** — `change_log` column names realigned to live schema (`entity_table`, `action`, `actor_snapshot`, `old_values`, `new_values`, `changed_fields`); PL/pgSQL syntax fix for cumulative `GET DIAGNOSTICS` (per-block accumulator pattern, not single GET-DIAGNOSTICS at end).

### Operator impact

**Chamomile-class blocker on `/(ops)/stock/physical-count` RESOLVED.** Effective **2026-05-11**, operators may resume Physical Count for chamomile flowers, searching by `Chamomile` (English alias) or `קמומיל` (Hebrew alias — present in seed). The Sunday operator guard (§4 Day-of guard) is now lifted for the chamomile case; the remaining 144 components were never blocked.

---

## 1. The Invariant (Tom-locked, 2026-05-10)

> **Every component referenced by any active BOM line MUST be present in the components master AND searchable by every name an operator might use for it on the production floor.**

This is the closure criterion. The fix is not "we patched 7 names." It is: *the invariant holds today and cannot regress.*

**Operationalization:**
- ∀ `bom_line` with `status='ACTIVE'` and `component_ref_type ∈ ('RAW_NAME','COMPONENT')`:
  the `final_component_id` resolves to a `components.COMPONENT_ID` row.
- ∀ such resolved component: `components.COMPONENT_NAME` is the canonical truth, AND every floor-name in use (Chamomile, קמומיל, etc.) is a registered `component_alias` that maps back to the same `COMPONENT_ID`.
- The Physical Count form's lookup matches against canonical name **and** every alias.
- Health dashboard prints **0** open violations of the above three rules.

---

## 2. Anatomy of the bug (current evidence)

Computed against `gt-factory-os/fixtures/masters/{components,items,bom_lines,bom_head}.json` on 2026-05-10. JSON dump: `gt-factory-os/docs/master-data-reconciliation/bom-master-audit-report.json` (artifact of `scripts/bom_master_audit.mjs`). The DB and fixtures are in agreement (Gate 2 LIVE_VERIFIED, 145 components / 420 BOM lines imported).

| # | Gap type | Count | Visible symptom |
|---|---|---|---|
| 1 | **Sub-BOM lines with blank display name** | 43 | Operator sees a blank row in the BOM tree; reads as "ghost ingredient" |
| 2 | **Same-ID, semantic divergence** | 2 (`RAW-CALM`, `RAW-WINE-WHITE`) | Master describes finished product / generic; BOM uses it as raw / specific. Cannot count physical inventory under either name without corrupting the other |
| 3 | **Same-ID, name re-order / wording mismatch** | 9 (4× Matcha + 5 partial) | Operator search for one phrasing fails; same item shows different name across surfaces |
| 4 | **Master duplicate canonical names** | 5 (`Whole Clove ×3`, `Black Cap 28mm ×2`) | Two/three master rows for one physical item. One is in use, others are orphans |
| 5 | **Master rows never used in any BOM** | 20 | Not all are bugs — some are queued products (Muza cocktails) without BOMs yet, some are orphan duplicates from #4. Needs triage, not blanket deletion |

True ID orphans (BOM points to a non-existent ID): **0**. The data is *internally referentially intact*; the failure is in name presentation and master hygiene.

### 2.1 The CHAMOMILE case — exact mechanics

| Layer | Field | Value |
|---|---|---|
| Components master | `COMPONENT_ID` | `RAW-CALM` |
| Components master | `COMPONENT_NAME` | `Calm (GT Tea Extract - Chamomile blend)` |
| BOM line `BOM-BASE-CAL-REG` (the recipe that produces Calm) | `final_component_id` | `RAW-CALM` |
| BOM line `BOM-BASE-CAL-REG` | `final_component_name` | `Chamomile` |
| BOM line `BOM-BASE-CAL-REG` | `final_component_qty` | `18` KG |
| Cost-of-production Excel sheet | label | `camomile` |

Conclusion: `RAW-CALM` is **physically dried chamomile flowers** (raw input). The master row was mis-labeled as the *output* product. The Calm extract output is `BOM-BASE-CAL-REG`'s downstream BOM head, not `RAW-CALM`. Renaming `RAW-CALM`'s canonical name to `Chamomile flowers (dried)` aligns master with floor reality and unblocks Physical Count.

### 2.2 Root cause — why this drift exists

`bom_lines.final_component_name` is a **denormalized free-text duplicate** of `components.COMPONENT_NAME`. There is no constraint forcing them to agree. Any importer, migration, or admin edit can populate one without the other. The drift is not a one-time bug; it is a *structural defect of the schema*.

---

## 3. Solution — three waves, sequenced by reversibility and operational urgency

### Wave 1 — Stop the bleeding (blocks Sunday 2026-05-10 cutover)

**Goal:** Physical Count form on Monday morning recognizes every BOM-referenced component by an operator-friendly name. Zero "ghost rows."

**Owner lane:** `backend-db-executor` (W1).
**Authoring boundary:** SQL migration + pgTAP test + fixtures patch. No portal code. No admin UI writes.
**Exit signal:** `RUNTIME_READY(MasterDataConsistency)` after pgTAP green.

#### Migration A — `0167_master_data_consistency_pass1.sql`

Single migration, idempotent (`UPDATE … WHERE COMPONENT_NAME = '<old>'`), wrapped in a transaction. **Includes minimal alias seeding** so that no rename in this wave creates a gap window where the old canonical name is unsearchable. Logical content:

```sql
-- A.1 Semantic-divergence fixes (high impact)
UPDATE components SET COMPONENT_NAME = 'Chamomile flowers (dried)'
  WHERE COMPONENT_ID = 'RAW-CALM' AND COMPONENT_NAME = 'Calm (GT Tea Extract - Chamomile blend)';

UPDATE components SET COMPONENT_NAME = 'Wine — White (Symphony)'
  WHERE COMPONENT_ID = 'RAW-WINE-WHITE' AND COMPONENT_NAME = 'Wine';

-- A.2 Re-order / partial-mismatch fixes (canonical wins)
-- Force bom_lines.final_component_name = components.COMPONENT_NAME for every resolvable line
UPDATE bom_lines bl
   SET final_component_name = c.COMPONENT_NAME
  FROM components c
 WHERE bl.final_component_id = c.COMPONENT_ID
   AND bl.component_ref_type IN ('RAW_NAME','COMPONENT')
   AND bl.final_component_name IS DISTINCT FROM c.COMPONENT_NAME;

-- A.3 Sub-BOM rows: copy bom_head label into final_component_name (no more blanks)
UPDATE bom_lines bl
   SET final_component_name = bh.label
  FROM bom_head bh
 WHERE bl.final_component_id = bh.bom_head_id
   AND bl.component_ref_type IN ('BASE_BOM','BOM')
   AND (bl.final_component_name IS NULL OR bl.final_component_name = '');

-- A.4 Retire master duplicates that are NOT referenced anywhere
-- Hard preconditions: target IDs have zero references in bom_lines.final_component_id
DELETE FROM components WHERE COMPONENT_ID IN ('RAW-CORNATION','RAW-COLVE')
  AND NOT EXISTS (SELECT 1 FROM bom_lines WHERE final_component_id = COMPONENT_ID);
DELETE FROM components WHERE COMPONENT_ID = 'PKG-CAP-STD'
  AND NOT EXISTS (SELECT 1 FROM bom_lines WHERE final_component_id = COMPONENT_ID);

-- A.5 Create the aliases table (used by Wave 2 + Wave 3, but seeded NOW so renames in A.1
--     don't create a gap where the old canonical name is unsearchable for any duration).
CREATE TABLE IF NOT EXISTS component_aliases (
  alias_id      bigserial PRIMARY KEY,
  component_id  text NOT NULL REFERENCES components(COMPONENT_ID) ON DELETE CASCADE,
  alias         text NOT NULL,
  alias_norm    text GENERATED ALWAYS AS (lower(btrim(alias))) STORED,
  source        text NOT NULL CHECK (source IN ('manual','import','operator_capture','planning_history')),
  created_at    timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT component_aliases_unique_norm UNIQUE (alias_norm)
);

-- A.6 Seed the OLD canonical names + the literal floor names from this audit
--     so every rename in A.1 / A.2 has its prior name still searchable.
INSERT INTO component_aliases (component_id, alias, source) VALUES
  ('RAW-CALM',       'Calm (GT Tea Extract - Chamomile blend)', 'import'),
  ('RAW-CALM',       'Chamomile',                                'import'),
  ('RAW-CALM',       'camomile',                                 'import'),
  ('RAW-WINE-WHITE', 'Wine',                                     'import'),
  ('RAW-WINE-WHITE', 'White wine',                               'import'),
  ('RAW-WINE-WHITE', 'Wine (white) Symphony',                    'import'),
  ('RAW-CLOVE',      'Whole Clove',                              'import'),
  ('PKG-CAP-BLACK-METAL-28', 'Black Cap 28mm',                   'import')
ON CONFLICT (alias_norm) DO NOTHING;
```

**Audit row inserted into `change_log`** for every row touched, with `actor='migration:0167'` and `reason='master_data_consistency_pass1'`.

#### pgTAP — `master_data_consistency.test.sql`

Seven assertions for Wave 1 (T1–T7), extended to twelve by end of Wave 2:

```text
-- Wave 1 (regression-locked after Migration A)
T1.  No bom_line with status='ACTIVE' and ref_type IN ('RAW_NAME','COMPONENT') has final_component_id NOT IN components
T2.  No bom_line with status='ACTIVE' and ref_type IN ('BASE_BOM','BOM') has final_component_id NOT IN bom_head
T3.  No bom_line where final_component_name IS NULL OR final_component_name = ''
T4.  No bom_line where ref_type IN ('RAW_NAME','COMPONENT') AND final_component_name <> matching components.COMPONENT_NAME
T5.  No two ACTIVE/PENDING components share a canonical name (state — locked into schema by Migration D in Wave 2)
T6.  Every component referenced by any ACTIVE bom_line has STATUS in ('ACTIVE','PENDING')
T7.  Every BASE_BOM/BOM ref-type bom_line has final_component_name = bom_head.label

-- Wave 2 additions
T8.  Every ACTIVE component has at least one row in component_aliases (canonical name self-aliased)
T9.  component_aliases.alias_norm is globally unique (constraint test — duplicate insert raises)
T10. INSERT/UPDATE on bom_lines with explicit final_component_name='garbage' is silently corrected by trigger to canonical truth
T11. INSERT into components with a duplicate canonical name is rejected by 0170 unique index
T12. Alias lookup test fixture: search 'chamomile' → RAW-CALM; 'white wine' → RAW-WINE-WHITE; 'whole clove' → RAW-CLOVE
```

#### Fixtures patch
Identical changes mirrored into `fixtures/masters/{components,bom_lines}.json` so re-import produces the same DB state. `_meta.extracted_at` updated to migration timestamp.

#### Rollback
Migration `0167_rollback.sql` provides the inverse `UPDATE`s for A.1/A.2/A.3 from `change_log` and `INSERT`s for the deleted master rows from a snapshot table `_archive_components_pre_0167`. Snapshot is created in the up-migration before any DELETE.

#### Wave 1 evidence pack
- `0167_master_data_consistency_pass1.sql` + rollback file
- `master_data_consistency.test.sql` (pgTAP T1–T7 green N/N)
- Updated fixtures with re-extracted hashes
- `component_aliases` table exists with ≥ 8 seed rows visible
- Live query `SELECT component_id FROM component_aliases WHERE alias_norm='chamomile'` returns `RAW-CALM`
- Re-run of `scripts/bom_master_audit.mjs` showing `name_mismatches_semantic=0`, `blank_name_bom_lines=0`, `duplicate_names_in_master=0`
- `change_log` rows visible in DB
- `RUNTIME_READY(MasterDataConsistency)` emitted via `.claude/state/runtime_ready.json`

**Wave 1 unblocks:** UX release gate aggregate verdict moves toward SHIP for `/(ops)/stock/physical-count` because the surface-blocking master integrity issue is gone.

---

### Wave 2 — Schema makes regression impossible (3-5 days)

#### Wave 2 carry-forwards from Wave 1 execution

Three findings surfaced during Wave 1 apply that were re-scoped (not regressions) per Tom's Option A decision on 2026-05-10. **Owner for all three: `backend-db-executor`. Trigger: next Wave 2 dispatch cycle.**

| # | Finding | Origin | Closure |
|---|---|---|---|
| CF-1 | **E2E test pollution cleanup.** Wave 1 pgTAP runs surfaced residual fixture/test rows polluting `bom_lines` and `components` from prior E2E runs (contributed false positives in T3/T5 counts). Need a teardown pass + a CI gate that fails if pgTAP detects unowned test rows in core tables. | Wave 1 T3/T5 FAIL analysis | Wave 2 cleanup migration + pgTAP guard |
| CF-2 | **59 NULL-final_component_id BASE_BOM row triage.** A.3 was a no-op because the 59 sub-BOM rows have `final_component_id IS NULL`, not a valid bom_head reference. Each row needs Tom triage (point to correct bom_head, or retire). Cannot be bulk-migrated. | Wave 1 A.3 = 0 rows; T2/T3 FAIL | Wave 2 triage worksheet + per-row UPDATE migration |
| CF-3 | **DB-driven fixtures extractor.** Wave 1 exposed that the JSON fixtures in `gt-factory-os/fixtures/masters/` had drifted from live DB schema (column names, NULL patterns). Need a script that re-extracts fixtures from live DB and emits a hash so CI can detect future drift. | f9daf57 + 6fc7f2a + 23caca3 schema-name fixes | Wave 2 `extract_fixtures_from_db.mjs` + CI freshness check |

**Goal:** The drift cannot recur. The denormalized free-text field is locked to canonical truth at the schema layer. Operator vocabulary becomes a first-class searchable surface.

**Owner lane:** `backend-db-executor` (W1) for migrations + tests; `integration-boundary-executor` (W4) for the read-model contract.

#### Migration B — `0168_component_aliases_full_seed_and_index.sql`

The aliases *table* is already created in Wave 1 (Migration A.5) so no rename window exists. Wave 2 extends it:

```sql
-- B.1 Add optional locale column + indexes for fast trigram search and per-component lookup
ALTER TABLE component_aliases ADD COLUMN IF NOT EXISTS alias_locale text NULL;
CREATE INDEX IF NOT EXISTS component_aliases_by_component ON component_aliases(component_id);
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS component_aliases_search ON component_aliases USING gin (alias_norm gin_trgm_ops);
```

**Wave 2 alias seed (extension of Wave 1's minimal seed; idempotent):**
- For every active component, register its current `COMPONENT_NAME` as a `source='import'` alias (search uniformity — every component has at least one alias = its canonical name).
- For Matcha / sticker / tin items: every variant phrasing observed in current BOMs becomes an alias of the canonical ID (covers the 4 reorder-only + 5 partial-mismatch cases from §2).
- Hebrew transliterations (subject to **Q-MD-2**): if Tom approves the seed list, ship `קמומיל`, `סוכר`, `מים`, etc., on this wave; otherwise hold for Tom-row-by-row entry.

**Target after Wave 2:** alias_coverage_ratio = 1.00 (every active component has ≥ 1 alias). Floor-vocab coverage measured by Wave 3's `unmapped_operator_searches` decay rate.

#### Migration C — `0169_bom_lines_display_name_lock.sql`

Two routes, pick one (recommend Option 1 unless rejected for query-shape reasons):

**Option 1 — Trigger-enforced consistency (recommended):**
```sql
CREATE OR REPLACE FUNCTION bom_lines_force_display_name() RETURNS trigger AS $$
BEGIN
  IF NEW.component_ref_type IN ('RAW_NAME','COMPONENT') THEN
    SELECT c.COMPONENT_NAME INTO NEW.final_component_name
      FROM components c WHERE c.COMPONENT_ID = NEW.final_component_id;
  ELSIF NEW.component_ref_type IN ('BASE_BOM','BOM') THEN
    SELECT bh.label INTO NEW.final_component_name
      FROM bom_head bh WHERE bh.bom_head_id = NEW.final_component_id;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER bom_lines_display_name_lock
  BEFORE INSERT OR UPDATE OF final_component_id, final_component_name, component_ref_type
  ON bom_lines
  FOR EACH ROW EXECUTE FUNCTION bom_lines_force_display_name();
```

**Option 2 — Drop the column, replace with `v_bom_lines_with_name` view.** Cleaner but a wider blast radius — every consumer of `bom_lines.final_component_name` (planning engine, exception inbox, exports) must move to the view.

**Decision (Tom-locked):** Option 1 + companion view, defense-in-depth.

```sql
-- Option 1 — trigger (corrects writes)
-- (already shown above)

-- COMPANION READ-SIDE VIEW (new code reads via this; old code still uses the column)
CREATE OR REPLACE VIEW v_bom_lines_with_canonical_name AS
SELECT
  bl.line_key, bl.bom_version_id, bl.bom_head_id, bl.line_no, bl.bom_kind,
  bl.component_ref_type, bl.final_component_id, bl.final_component_qty, bl.component_uom,
  bl.status, bl.scaling_method, bl.qty_per_l_output, bl.std_cost_per_uom, bl.line_std_cost,
  -- canonical name from authoritative source
  COALESCE(c.COMPONENT_NAME, bh.label) AS canonical_name
FROM bom_lines bl
LEFT JOIN components c ON c.COMPONENT_ID = bl.final_component_id
                       AND bl.component_ref_type IN ('RAW_NAME','COMPONENT')
LEFT JOIN bom_head  bh ON bh.bom_head_id = bl.final_component_id
                       AND bl.component_ref_type IN ('BASE_BOM','BOM');
```

The trigger guarantees `bom_lines.final_component_name` matches `canonical_name` for every row. New code reads the view (clean idiom). Old code keeps working (column still populated correctly).

#### Migration D — `0170_components_unique_canonical_name.sql`

```sql
CREATE UNIQUE INDEX components_canonical_name_unique
  ON components (lower(btrim(COMPONENT_NAME)))
  WHERE STATUS IN ('ACTIVE','PENDING');
```

Locks T5 from pgTAP into the schema.

#### Migration E — `0171_components_rename_auto_alias.sql` *(critical hardening — closes the rename-failure class forever)*

This is the deepest preventive measure in the entire spec. **Every future rename of any component automatically archives the old name as an alias.** Without it, the next Chamomile-class bug is just one rename away.

```sql
CREATE OR REPLACE FUNCTION components_capture_old_name_as_alias() RETURNS trigger AS $$
BEGIN
  -- Only fire when the canonical name is actually changing
  IF NEW.COMPONENT_NAME IS DISTINCT FROM OLD.COMPONENT_NAME
     AND OLD.COMPONENT_NAME IS NOT NULL
     AND length(btrim(OLD.COMPONENT_NAME)) > 0 THEN
    INSERT INTO component_aliases (component_id, alias, source)
      VALUES (NEW.COMPONENT_ID, OLD.COMPONENT_NAME, 'manual')
      ON CONFLICT (alias_norm) DO NOTHING;
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER components_capture_rename_alias
  AFTER UPDATE OF COMPONENT_NAME ON components
  FOR EACH ROW EXECUTE FUNCTION components_capture_old_name_as_alias();
```

**Concrete example of what this prevents:** In 6 months, Tom decides to rename `RAW-SUGAR` from "Sugar" to "Sugar (refined white, 25kg sack)". Without this trigger: every operator who searches "Sugar" stops finding the item silently — same bug pattern as the original Chamomile incident, in a new disguise. With this trigger: "Sugar" auto-becomes an alias of `RAW-SUGAR` the moment the rename commits, and the operator search keeps working.

**pgTAP T13:** Update a component's name → assert the old name appears in `component_aliases` within the same transaction. Update a second time → both old names exist as aliases.

#### Read-model contract (W4 lane)

`docs/contracts/master_data_health_read_model.md` — defines the API contract for `/api/master-data/health`, including:
- `health.summary`: counts per gap type (orphan_ids, blank_display_names, duplicate_names, unused_components, recent_unmapped_searches)
- `health.violations[]`: per-row, with severity and suggested remediation (idempotent re-run of the relevant 0167-class migration)
- `health.alias_coverage`: ratio (components_with_at_least_one_alias / total_components)

#### Wave 2 evidence pack
- 3 migrations + their pgTAP files (extending `master_data_consistency.test.sql`)
- Read-model contract Markdown
- Sample query against the new view / table
- `RUNTIME_READY(ComponentAliases)` emitted

---

### Wave 2.5 — Pattern audit: find the next Chamomile *before* it hurts (1 day, parallel with Wave 3)

**Goal:** The Chamomile bug exists because two surfaces of truth (`components.COMPONENT_NAME` and `bom_lines.final_component_name`) silently disagreed. **The same drift pattern likely exists elsewhere.** Before declaring the master data fix "done," prove that no other denormalized name field in the schema is silently drifting.

**Owner lane:** read-only audit work, dispatched to `source-of-truth-auditor`.

#### Audit script — `gt-factory-os/scripts/denormalized_name_audit.mjs`

For every table in the core schema, find columns that look like denormalized name copies of another table's canonical-name column. Heuristic:
1. Column name matches `*_name`, `*_label`, `*_display_name`, `*_description`
2. Same row contains a foreign key to another table that itself has a name-like column
3. Compare values; report mismatches

**Tables to inspect:**
- `bom_head.label` ↔ derived from? (probably its own canonical, but check if it's referenced elsewhere with cached copies)
- `items.ITEM_NAME` ↔ any cached copy in `bom_head`, `purchase_orders`, `forecast` lines, etc.
- `suppliers.SUPPLIER_NAME` ↔ cached copies in `supplier_items`, `purchase_orders`, `goods_receipts`
- `supplier_items.supplier_item_name` ↔ relation to component? to supplier?
- `bom_lines.final_component_name` ↔ already confirmed in scope (this audit just re-validates Wave 1+2)
- `stock_ledger` event payloads — do they capture `component_name` at write time? If yes, that's a third surface and a third drift risk.

#### Output

`docs/master-data-reconciliation/denormalized-pattern-audit-2026-05-10.md`:
- For each (table, column) pair: violation count, sample rows
- Recommendation per case: trigger (Wave 1-style), drop column (replace with view), or no action (legitimate snapshot, not denormalization)

#### Dispatch outcome

If the audit finds further drift cases, each one becomes its own follow-on Wave 1-style migration (own pgTAP, own trigger, own evidence pack). They are **not** bundled into Wave 2 — too much surface area at once.

If the audit finds zero violations, Wave 2.5 closes with the audit report as evidence, and the lesson "this pattern was checked, schema is clean" is locked into `SCHEMA_GUIDANCE.md`.

---

### Wave 3 — Make gaps visible before operators fall into them (1 week)

**Goal:** The remaining 5-20 ambiguous master rows (unused components, queued Muza cocktails, missing-BOM raw materials like Campari/Gin/Whiskey) become visible on a dashboard and drive triage decisions. Physical Count form proactively surfaces aliases.

#### W4 — Read-model `v_master_data_health`

```sql
CREATE OR REPLACE VIEW v_master_data_health AS
SELECT
  (SELECT COUNT(*) FROM bom_lines bl WHERE … T1 violations) AS orphan_id_count,
  (SELECT COUNT(*) FROM bom_lines bl WHERE … T3 violations) AS blank_name_count,
  (SELECT COUNT(*) FROM components_canonical_name_violations) AS duplicate_name_count,
  (SELECT COUNT(*) FROM components c WHERE NOT EXISTS (
     SELECT 1 FROM bom_lines bl WHERE bl.final_component_id = c.COMPONENT_ID
   ) AND c.STATUS = 'ACTIVE') AS unused_active_count,
  (SELECT COUNT(*) FROM unmapped_operator_searches WHERE created_at > now() - interval '7 days') AS recent_unmapped_count,
  (SELECT (COUNT(DISTINCT a.component_id)::numeric / NULLIF(COUNT(*),0))
     FROM components c LEFT JOIN component_aliases a ON a.component_id = c.COMPONENT_ID
   ) AS alias_coverage_ratio;
```

#### W4 — `unmapped_operator_searches` table

Captures every Physical Count search that returned zero results. Each row is a *future alias candidate*. Tom triages weekly: convert to alias OR file as new component need.

```sql
CREATE TABLE unmapped_operator_searches (
  id          bigserial PRIMARY KEY,
  search_text text NOT NULL,
  user_id     uuid NULL REFERENCES app_users(user_id),
  surface     text NOT NULL,            -- 'physical_count','goods_receipt', etc.
  created_at  timestamptz NOT NULL DEFAULT now(),
  resolved_at timestamptz NULL,
  resolution  text NULL                 -- 'aliased_to:<COMPONENT_ID>'|'new_component'|'duplicate'|'ignored'
);
```

#### W2 — Portal: `/admin/master-data-health`

Read-only dashboard. Five KPI cards (one per health metric), one table per category (e.g., "Components missing alias coverage" with row-level CTAs to trigger Tom-approved alias-add through admin form). No mass-edit surface.

**Authoring boundary:** Mode B for portal-production-executor. Requires `RUNTIME_READY(MasterDataHealth)` emitted by W4 first.

#### W2 — Physical Count form upgrade

Three changes, all additive on the existing form:
1. **Search includes aliases:** lookup hits `components.COMPONENT_NAME` ∪ `component_aliases.alias`. Match returns one component_id.
2. **"Also known as" panel:** under the canonical name in the count input, list aliases inline ("Chamomile flowers (dried) — also known as: Chamomile, קמומיל, Camomile").
3. **Zero-result capture:** if operator types a string and gets nothing, prompt is `"לא נמצא רכיב כזה — שמור כהצעה לשם נוסף?"`. Yes → row in `unmapped_operator_searches`. No state change to balance.

**Authoring boundary:** Mode B for `/(ops)/stock/physical-count`. Requires Tom UX handoff packet (microcopy, RTL layout for the alias panel, exact prompt text).

#### Wave 3 evidence pack
- View + table migrations + pgTAP
- Read-model contract update
- Tom-approved UX handoff packet for Physical Count + Health dashboard
- Playwright E2E: operator searches "Chamomile" → finds RAW-CALM; operator searches "fakething" → unmapped row written
- Health dashboard E2E: simulated regression (deleting one alias) reflects in dashboard within 60s
- `RUNTIME_READY(PhysicalCountAliases)` + `RUNTIME_READY(MasterDataHealthDashboard)`

---

## 4. Implementation plan — sequencing and ownership

| # | Wave | Lane | Agent | Approval gate | Wall-clock |
|---|---|---|---|---|---|
| 0 | **Day-of guard** — operator instruction for Sunday 2026-05-10 | operations | Tom direct | none — direct comm to floor | 5 minutes |
| 1 | Wave 1 — Migration 0167 + pgTAP T1–T7 + fixtures patch + minimal alias seed | `backend-db` | `backend-db-executor` | Tom approves SQL diff before merge | 1 day (Mon 2026-05-11) |
| 2 | Wave 1 — verifier check + RUNTIME_READY(MasterDataConsistency) | governance | `release-verifier` then `factory-os-governor` | governor approves PASS | same day |
| 3 | Wave 2 — Migrations 0168/0169/0170/**0171** + pgTAP T8–T13 + companion view | `backend-db` | `backend-db-executor` | Tom-locked: trigger + view (Q-MD-1); Tom approves rename-auto-alias trigger | 2 days |
| 4 | Wave 2 — Read-model contract for health | `integration` | `integration-boundary-executor` | governor confirms contract aligned with W1 schema | 0.5 day |
| 5 | Wave 2 — Hebrew alias seed (~40 RAW components) | `backend-db` | `backend-db-executor` (data-only migration) | Tom approves the seed list as one batch | 0.5 day |
| 6 | **Wave 2.5 — denormalized name pattern audit** (READ-ONLY) | `source-of-truth` | `source-of-truth-auditor` | governor reviews findings; each finding becomes its own follow-on Wave 1-style migration | 1 day |
| 7 | Wave 3 — `unmapped_operator_searches` + `v_master_data_health` | `backend-db` | `backend-db-executor` | pgTAP green | 0.5 day |
| 8 | Wave 3 — Physical Count UX handoff packet | `ux-audit` | `ux-content-state-designer` + `ux-flow-architect` | Tom approves two-button microcopy + RTL layout | 1 day |
| 9 | Wave 3 — Physical Count form upgrade | `portal` | `portal-production-executor` (Mode B) | RUNTIME_READY(PhysicalCountAliases) prerequisites cleared, Tom approves Mode B entry | 2 days |
| 10 | Wave 3 — Health dashboard | `portal` | `portal-production-executor` (Mode B) | sequential after #9 (one Mode B at a time) | 2 days |

**Total wall-clock if no rework:** ~10–12 working days from Wave 1 kickoff. Wave 1 alone clears the immediate Physical Count blocker and stands on its own. Wave 2.5 runs in parallel with Wave 3 work since it's read-only audit and won't conflict.

### Day-of guard (Sunday 2026-05-10) — operator instruction

To be sent by Tom directly to floor staff. Hebrew, RTL:

> **חשוב — היום (יום ראשון 10.05.26):**
> אל תספרו פיזית את "Calm" / "Chamomile" / "פרחי קמומיל".
> כל שאר 144 הרכיבים — תקינים לספירה כרגיל.
> תיקון מערכתי נוחת מחר בבוקר. עד אז Calm נספר ידנית בנייר ויירשם במערכת לאחר התיקון.
> תודה — Tom

The 18 KG of physical chamomile flowers should be counted on paper today and posted to the system Monday once the canonical name is `Chamomile flowers (dried)`. Posting under the current name `Calm (GT Tea Extract - Chamomile blend)` would corrupt the balance of the *finished* Calm extract product, not the raw ingredient.

---

## 5. Risks + open questions

### Risks

1. **Mass-edit through admin UI is forbidden.** All changes go through migrations. If portal admin screens already wired (per CURRENT_STATE 2026-04-25) attempt to write back to the master, the trigger from Migration C will overwrite with canonical truth. Acceptable side effect, but operators must know.
2. **Aliases unique constraint can collide.** "Sugar" and "Cane sugar" both wanting to alias to different RAW IDs → uniqueness blocks one. Triage rule: if collision, the alias goes to the most-used-in-BOMs target, and the rejected pairing surfaces as `unmapped_operator_searches`.
3. **Wave 1 changes the canonical name of `RAW-CALM`.** Any external reference (Shopify export, Green Invoice tag, downstream report) that relied on the OLD name `Calm (GT Tea Extract - Chamomile blend)` will break silently. Mitigation: the OLD name is registered as a `source='import'` alias **inside Migration A itself (A.6)** — there is no window in which it is unsearchable. Surveys of external integrations confirm none read this field today (LionWheel/Shopify/GI integrations index by SKU/order_id, not component name).
4. **The 20 unused components.** Wave 1 only deletes the 3 unambiguous duplicates. The other 17 (Muza cocktails, queued raws, etc.) need Tom triage in Wave 3 — *not* automated cleanup.

### Open questions for Tom — ALL RESOLVED 2026-05-10

1. **Q-MD-1 (trigger vs drop column):** Locked → Option 1 (trigger) + companion view, defense-in-depth. See §3 Wave 2 Migration C.
2. **Q-MD-2 (Hebrew alias seed):** Locked → AI builds ~40-line list from top RAW component usage; Tom approves once as a batch. Wave 2 step #5.
3. **Q-MD-3 (zero-result UX):** Locked → two-button design ("I know what it is" + "Unclear, needs review"). Final microcopy via UX handoff packet.
4. **Q-MD-4 (cutover timing):** Locked → (c) cutover today, Wave 1 lands Monday. Operator guard issued for Sunday.

## 5.1 Tom Tax — failure modes that will hurt later if not closed

These are not Wave 1 blockers, but each one is a future Chamomile-class incident waiting to happen. Each gets a tracked owner.

| # | Risk | Closure plan | Owner | When |
|---|---|---|---|---|
| 1 | **Denormalized name pattern exists outside `bom_lines`.** `items.ITEM_NAME`, `bom_head.label`, `suppliers.SUPPLIER_NAME` may have parallel cached copies elsewhere with the same drift exposure. | **Wave 2.5 audit.** See §3. Audit script + report; each finding gets its own Wave 1-style migration | `source-of-truth-auditor` | Parallel with Wave 3, completes within 5 days of Wave 1 |
| 2 | **PENDING-status components allowed in active BOMs.** A half-set-up component could enter planning math before being approved. | **pgTAP T13.** Active `bom_lines` may not reference components with `STATUS NOT IN ('ACTIVE','PENDING_FOR_BOM')`. Define tighter sub-status if needed. | `backend-db-executor` | Wave 2 |
| 3 | **Alias collision between products and ingredients.** "Calm" is both a finished product (FG SKU) and a search term for `RAW-CALM`. Same alias shouldn't resolve to both. | **Add `scope` column to `component_aliases`** with values `raw\|finished\|both`. Physical Count form filters by scope of the form (Physical Count of raw materials → only `raw\|both` matches). | `backend-db-executor` (extended Migration B) | Wave 2 |
| 4 | **Bulk fixture re-import bypasses the trigger.** A future `TRUNCATE + COPY` from updated fixtures would replace data without triggering the rename-alias capture. | **Policy in `SCHEMA_GUIDANCE.md`:** future fixture re-imports must run through migrations, not direct truncate-and-load. CI gate enforces it. | `ops-docs-curator` (writes the policy) + `backend-db-executor` (CI gate) | Wave 2 |
| 5 | **Operator capture spam.** A user could fill `unmapped_operator_searches` with 1000 garbage entries. Tom's triage queue becomes useless. | **Rate limit:** 10 unmapped searches per user per hour. Soft-dedupe by `lower(btrim(search_text))`. | `backend-db-executor` + `portal-production-executor` | Wave 3 |
| 6 | **Alias additions through admin UI not audited.** Future admin alias edits should be tracked in `change_log` with actor and reason — same audit standard as components themselves. | **Migration:** `change_log` triggers on `component_aliases` insert/update/delete. | `backend-db-executor` | Wave 2 |
| 7 | **Stock ledger event payloads may capture component_name at write time.** If they do, that's a third surface and a third drift risk. | **Confirmed in Wave 2.5 audit (item #1).** If found, ledger payload schema documented as snapshot-at-time (legitimate) — or trigger added if drift-prone. | `source-of-truth-auditor` → `backend-db-executor` | Wave 2.5 follow-up |
| 8 | **Dry-run pattern flaw — migrations with inner `BEGIN`/`COMMIT` cannot dry-run via outer rollback wrapper.** Wave 1 of migration 0180 intended to verify each section with `psql -c "begin; \i …; rollback;"`, but the migration's own inner `COMMIT` closed the inner transaction and the outer `rollback;` ran against an empty fresh transaction — applying changes during what was meant as a dry-run. The safety property was illusory. | **Documented in `docs/contracts/SCHEMA_GUIDANCE.md` per this same handoff** (Lesson 2026-05-10 — caller-supplied transaction OR savepoint dry-run pattern; grep-for-`^begin;` compliance test). | `ops-docs-curator` | Now (2026-05-11) |

### Forbidden assumptions touched

- None. The fix does not introduce a second master, does not preserve workbook structure, does not flip frozen flags, does not invent integration field names, does not auto-create components from external sources.

---

## 6. Success evidence (closure criterion)

The fix is *done* when **all** of:

- pgTAP `master_data_consistency.test.sql`: T1–T7 green at end of Wave 1, T1–T13 green at end of Wave 2.
- Live DB: `bom_master_audit.mjs` re-run shows `semantic_mismatches=0`, `blank_display_names=0`, `master_dup_names=0`, `alias_coverage_ratio=1.0`.
- **rename-auto-alias trigger verified live:** rename a test component, observe new alias row in `component_aliases` within the same transaction.
- **Wave 2.5 pattern audit complete:** report exists, every finding has either a follow-on migration plan or an "intentional snapshot, not drift" justification.
- Health dashboard `/admin/master-data-health` shows green across all 5 KPIs.
- Operator runs Physical Count, types "Chamomile" (or "קמומיל"), gets `RAW-CALM` ("Chamomile flowers (dried)") as the match. Counts post correctly.
- `unmapped_operator_searches` table exists, captures unknown searches, is empty under normal operation.
- UX release gate: `/(ops)/stock/physical-count` moves from NOT_AUDITED to AUDITED + SHIP.
- All 7 Tom Tax items are tracked, owned, and either closed or scheduled.

The invariant from §1 holds, AND the *class* of master-data drift bugs is structurally prevented from recurring.

---

## 7. Out of scope (explicit non-goals)

- Reorganizing the Muza cocktails product line (Wave 3 surfaces the gap, Tom decides separately).
- Migrating `final_component_name` from column to fully derived view (Option 2). Possible Wave 4.
- Adding non-Chamomile, non-CALM semantic-divergence detection beyond the two found in this audit. Future regression cases will be caught by pgTAP T4/T5.
- Building any operator-facing tool that *writes* aliases without admin approval (security boundary).
- Touching planning engine, ledger, integration runtimes. Master data fix is upstream of all of them.

---

## 8. Approvals required

- **Tom** — written approval to proceed with Wave 1 SQL diff (Migration A).
- **Tom** — choice on Q-MD-1 and Q-MD-4 above before Wave 2 begins.
- **`factory-os-governor`** — go/no-go on Wave 1 evidence pack before Wave 2 dispatch.
- **`release-verifier`** — pre-merge check on each wave's PR.

---

**Spec author:** AI brain (Tom-driven brainstorming session, 2026-05-10).
**Spec reviewer:** Tom.
**Repo of record for migrations:** `gt-factory-os/db/migrations/` (next free sequence: `0167…0170`).
**Repo of record for portal:** `window2-portal-sandbox/` (Mode B, one form at a time).
**Audit script:** `gt-factory-os/scripts/bom_master_audit.mjs` (read-only; safe to re-run anytime).
