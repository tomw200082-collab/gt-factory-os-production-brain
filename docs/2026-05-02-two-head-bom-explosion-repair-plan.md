# Two-Head BOM Explosion Repair Plan

> **For agentic workers:** REQUIRED — Use `superpowers:executing-plans` (or dispatch via the GT Factory OS executor harness: `executor-w1` for backend/SQL/tests, `executor-w2` for portal, governance via `factory-os-autonomous-builder`). Steps use checkbox (`- [ ]`) syntax for tracking. Each tranche is a separate commit + push. No tranche is "done" until verifier-PASS.

**Goal:** Fix the cross-corridor multi-head BOM-explosion blind spot that causes (a) the Production Actual form and handler to omit liquid component consumption from `stock_ledger` writes, and (b) the planning engine `fn_explode_bom_to_components` to omit liquid raw-material demand from `planning_run_component_demand`. After this plan: every MANUFACTURED item with a BASE BOM gets BOTH its packaging components AND its liquid raw-material components exploded, pinned, previewed, and posted atomically.

**Architecture decision — backend authority, two-head explosion in SQL/handler layer.** Production Actual must be atomic (one transaction, one idempotency key, one form_submissions envelope). The portal already renders whatever the open endpoint returns; we extend the open endpoint to return PACK + BASE lines as a single merged list (with a `source` tag per line) so the portal change is minimal. The submit handler walks both PACK and BASE inside one transaction. The planning engine `fn_explode_bom_to_components` gets a v2 SQL function that walks both heads. We do NOT mirror the simulator's portal-side double-fetch pattern because Production Actual is a write path; atomicity must live with the writer.

**Tech Stack:** Postgres 16 (Supabase managed), Node 20 + Fastify + Kysely + Zod, Next.js 15 App Router + TanStack Query, TypeScript across.

**Pre-launch context:** Tom has NOT launched the system live yet (confirmed 2026-05-02). All prior `production_consumption` rows in `stock_ledger` were synthetic / smoke-test data. **No historical retro-reconciliation is required.** All prior planning runs that exploded BOMs of MANUFACTURED items can be ignored — recompute on demand if/when a fresh planning run is needed.

**Expert prioritization recommendation (per Tom's Q3):** **Pause Planning Corridor v1 until Tranches 0–4 of this plan land.** Reasons:
1. The same architectural blind spot lives in both Production Actual AND the planning engine. Every planning_run cycle right now produces wrong purchase recommendations for any liquid RM (lemon grass, lime puree, tea base, alcohol, etc.). Continuing to build planning-corridor surfaces (recommendation drill-downs, blockers, dashboards) on top of this is multiplying the surface area that will need re-validation later.
2. Production Actual will be Tom's first daily-use form. Stock truth on it is non-negotiable per CLAUDE.md §non-negotiables #1 ("Stock truth ships before planning cutover"). Launching with this bug would corrupt every liquid RM `current_balances` row from day 1.
3. Planning Corridor cycle 8 was already rate-limit-interrupted (per CURRENT_STATE.md 2026-05-02). Natural breakpoint — no work-in-flight is being abandoned; uncommitted cycle-8 W1/W2 deltas can be picked up after this plan lands.
4. The fix is tightly scoped (six tranches, all surgical, no schema breaking changes for any other surface). Estimated ~1.5 working sessions end-to-end.

---

## File Structure

**Backend (`gt-factory-os/`)**
- `db/migrations/0127_production_actual_base_bom_pinning.sql` (NEW) — adds `base_bom_version_id_pinned` (nullable) to `production_actual`. **Renumbered from plan-original 0125 because slots 0125 (`v_planned_inflow_by_day`) and 0126 (`fn_explode_bom_to_components_v2` Tranche 3) were taken when Tranche 1 dispatched. Logical ordering inverted (engine v2 landed before PA pinning) — both migrations are functionally independent so no FK or apply-order dependency.**
- `db/migrations/0126_fn_explode_bom_to_components_v2.sql` (NEW) — replaces planning engine BOM-explosion function with two-head walk. **Landed 2026-05-02 in commit `4a84671`.**
- `db/tests/0127_production_actual_base_bom_pinning.test.sql` (NEW) — pgTAP for new column + nullability + FK.
- `db/tests/0126_fn_explode_bom_to_components_v2.test.sql` (NEW) — pgTAP for two-head explosion correctness on a fixture FG with both heads. **Landed 4/4 PASS 2026-05-02 in commit `4a84671`.**
- `api/src/production-actuals/schemas.ts` (MODIFY) — extend `ProductionActualOpenResponse` and `ProductionActualSubmitSchema` and `ProductionActualCommittedResponse` for two-head pinning + per-line `source` tag.
- `api/src/production-actuals/handler.ts` (MODIFY) — both `handleProductionActualOpen` and `handleProductionActualSubmit`: load both heads, pin both, explode both, post all consumption rows in one tx.
- `api/test/production_actual.test.ts` (MODIFY) — add three new test groups: TWO_HEAD_OK, BASE_BOM_DATA_ANOMALY, REPACK_NO_BASE.
- `scripts/audit_two_head_bom.ts` (NEW) — one-shot audit reporting any MANUFACTURED item whose two-head shape is incomplete or inconsistent.

**Portal (`window2-portal-sandbox/`)**
- `src/app/(ops)/stock/production-actual/page.tsx` (MODIFY) — extend `BomLineSnapshot` with `source: 'pack' | 'base'`; render preview as one table grouped/badged by source; no behavioral change to submit pipeline (the new fields pass through).

**Governance (`PRODUCTION/`)**
- `CLAUDE.md` (MODIFY) — amend §"Production reporting v1" to explicitly reference two-head BOM explosion semantics.
- `CURRENT_STATE.md` (MODIFY) — add tranche-completion checkpoint, update RUNTIME_READY signal counter once Tranches 0–4 land.
- `docs/two_head_bom_repair_evidence.md` (NEW) — final evidence pack: audit-report-v2 (anomalies = 0), pgTAP counts, node:test counts, live HTTP smoke transcripts, contract-amendment diff, deploy IDs.

---

## Sub-agent / executor mapping

| Tranche | Owner | Executor agent | Reason |
|---|---|---|---|
| 0 — Live-DB audit | W1 | `executor-w1` | Read-only DB script, no portal/UI |
| 1 — Schema migration | W1 | `executor-w1` | DDL + pgTAP |
| 2 — PA handler | W1 | `executor-w1` | Backend handler + Zod + node:test |
| 3 — Planning engine SQL | W1 | `executor-w1` | DDL + pgTAP |
| 4 — Portal preview | W2 | `executor-w2` (Mode B for `production-actual`) | Render-only change |
| 5 — Contract + docs | governance | direct (Claude main loop) | Authoritative-doc edits |
| 6 — E2E verification | verifier | `verifier` | Cross-cuts all of above |

Mode B is required for W2 in Tranche 4 — declare via the harness state file before dispatch. Mode B-Planning-Corridor amendment in EXECUTION_POLICY.md does NOT cover `/ops/stock/production-actual` — needs an explicit one-form Mode B exit from current state (W2 Mode A as of 2026-04-27T08:18Z per CURRENT_STATE.md §"W2 mode").

---

## Tranche 0 — Live-DB audit (FIRST; STOP-GATE for Tom review)

**Why first:** the design assumes a specific data shape (PACK head with one `BASE_BOM` line, BASE head with leaf component lines). The fixtures suggest this shape but the live DB may have anomalies the import didn't surface. Tom must see the gaps BEFORE we lock the handler/SQL changes.

### Task 0.1: Audit script

**Files:**
- Create: `gt-factory-os/scripts/audit_two_head_bom.ts`

- [ ] **Step 1: Write the audit script**

```typescript
// scripts/audit_two_head_bom.ts
//
// One-shot read-only audit of two-head BOM coverage across MANUFACTURED items.
// Emits a structured JSON report to stdout AND writes a human-readable
// markdown summary to docs/two_head_bom_audit_<ISO>.md.
//
// Run: npx tsx scripts/audit_two_head_bom.ts
//
// Categories reported (each is an array of {item_id, item_name, detail}):
//   ok_two_head                         — PACK + BASE both present and consistent
//   ok_pack_only                        — PACK exists, no base_bom_head_id (REPACK or pure-pack item)
//   missing_pack_head                   — supply_method=MANUFACTURED but primary_bom_head_id=NULL
//   missing_pack_active_version         — pack head exists but active_version_id=NULL
//   missing_base_active_version         — base head exists but active_version_id=NULL
//   pack_no_base_bom_line               — items.base_bom_head_id set but PACK active version has 0 BASE_BOM lines
//   pack_multiple_base_bom_lines        — PACK active version has >1 BASE_BOM lines (model only supports 1)
//   pack_base_bom_line_qty_null         — BASE_BOM line exists but final_component_qty IS NULL
//   pack_base_bom_line_uom_null         — BASE_BOM line exists but component_uom IS NULL
//   pack_base_bom_line_uom_mismatch     — BASE_BOM line uom != BASE head final_bom_output_uom
//   linked_base_inconsistent            — bom_head.linked_base_bom_head_id != items.base_bom_head_id
//   base_head_not_kind_base             — items.base_bom_head_id points to a head whose bom_kind != 'BASE'
//   pack_head_not_kind_pack             — items.primary_bom_head_id points to a head whose bom_kind not in ('PACK','REPACK')
//
// Exit code 0 always; this is a report, not a gate.

import { Pool } from 'pg';
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';

const DATABASE_URL = process.env.DATABASE_URL_POOLED ?? process.env.DATABASE_URL;
if (!DATABASE_URL) {
  console.error('DATABASE_URL_POOLED or DATABASE_URL must be set');
  process.exit(2);
}

interface ItemRow {
  item_id: string;
  item_name: string;
  primary_bom_head_id: string | null;
  base_bom_head_id: string | null;
  pack_kind: string | null;
  pack_active_version_id: string | null;
  pack_final_output_qty: string | null;
  pack_final_output_uom: string | null;
  pack_linked_base_bom_head_id: string | null;
  base_kind: string | null;
  base_active_version_id: string | null;
  base_final_output_qty: string | null;
  base_final_output_uom: string | null;
  base_bom_line_count: number;
  base_bom_line_qty: string | null;
  base_bom_line_uom: string | null;
}

interface Bucket {
  item_id: string;
  item_name: string;
  detail: Record<string, unknown>;
}

interface Report {
  generated_at: string;
  manufactured_items_total: number;
  ok_two_head: Bucket[];
  ok_pack_only: Bucket[];
  missing_pack_head: Bucket[];
  missing_pack_active_version: Bucket[];
  missing_base_active_version: Bucket[];
  pack_no_base_bom_line: Bucket[];
  pack_multiple_base_bom_lines: Bucket[];
  pack_base_bom_line_qty_null: Bucket[];
  pack_base_bom_line_uom_null: Bucket[];
  pack_base_bom_line_uom_mismatch: Bucket[];
  linked_base_inconsistent: Bucket[];
  base_head_not_kind_base: Bucket[];
  pack_head_not_kind_pack: Bucket[];
}

async function main() {
  const pool = new Pool({ connectionString: DATABASE_URL, ssl: { rejectUnauthorized: false } });
  try {
    const rows = await pool.query<ItemRow>(`
      WITH pack_base_lines AS (
        SELECT bl.bom_version_id,
               COUNT(*) AS base_bom_line_count,
               MAX(bl.final_component_qty::text) AS base_bom_line_qty,
               MAX(bl.component_uom) AS base_bom_line_uom
        FROM private_core.bom_lines bl
        WHERE bl.component_ref_type = 'BASE_BOM'
          AND bl.status IN ('ACTIVE','PENDING')
        GROUP BY bl.bom_version_id
      )
      SELECT i.item_id,
             i.item_name,
             i.primary_bom_head_id,
             i.base_bom_head_id,
             ph.bom_kind  AS pack_kind,
             ph.active_version_id::text AS pack_active_version_id,
             ph.final_bom_output_qty::text AS pack_final_output_qty,
             ph.final_bom_output_uom AS pack_final_output_uom,
             ph.linked_base_bom_head_id AS pack_linked_base_bom_head_id,
             bh.bom_kind  AS base_kind,
             bh.active_version_id::text AS base_active_version_id,
             bh.final_bom_output_qty::text AS base_final_output_qty,
             bh.final_bom_output_uom AS base_final_output_uom,
             COALESCE(pbl.base_bom_line_count, 0)::int AS base_bom_line_count,
             pbl.base_bom_line_qty,
             pbl.base_bom_line_uom
      FROM private_core.items i
      LEFT JOIN private_core.bom_head ph ON ph.bom_head_id = i.primary_bom_head_id
      LEFT JOIN private_core.bom_head bh ON bh.bom_head_id = i.base_bom_head_id
      LEFT JOIN pack_base_lines pbl ON pbl.bom_version_id = ph.active_version_id
      WHERE i.supply_method = 'MANUFACTURED'
        AND i.status = 'ACTIVE'
      ORDER BY i.item_id
    `);

    const report: Report = {
      generated_at: new Date().toISOString(),
      manufactured_items_total: rows.rowCount ?? 0,
      ok_two_head: [],
      ok_pack_only: [],
      missing_pack_head: [],
      missing_pack_active_version: [],
      missing_base_active_version: [],
      pack_no_base_bom_line: [],
      pack_multiple_base_bom_lines: [],
      pack_base_bom_line_qty_null: [],
      pack_base_bom_line_uom_null: [],
      pack_base_bom_line_uom_mismatch: [],
      linked_base_inconsistent: [],
      base_head_not_kind_base: [],
      pack_head_not_kind_pack: [],
    };

    for (const r of rows.rows) {
      const base = (k: keyof Report) =>
        (report[k] as Bucket[]).push({ item_id: r.item_id, item_name: r.item_name, detail: { ...r } });

      if (!r.primary_bom_head_id) { base('missing_pack_head'); continue; }
      if (!r.pack_active_version_id) { base('missing_pack_active_version'); continue; }
      if (r.pack_kind && !['PACK', 'REPACK'].includes(r.pack_kind)) { base('pack_head_not_kind_pack'); continue; }

      // No BASE expected (pure-pack or REPACK).
      if (!r.base_bom_head_id) {
        if (r.base_bom_line_count > 0) base('pack_no_base_bom_line'); // anomaly: line exists but no item linkage
        else base('ok_pack_only');
        continue;
      }

      // BASE expected.
      if (r.base_kind !== 'BASE') { base('base_head_not_kind_base'); continue; }
      if (!r.base_active_version_id) { base('missing_base_active_version'); continue; }
      if (r.base_bom_line_count === 0) { base('pack_no_base_bom_line'); continue; }
      if (r.base_bom_line_count > 1) { base('pack_multiple_base_bom_lines'); continue; }
      if (r.base_bom_line_qty === null) { base('pack_base_bom_line_qty_null'); continue; }
      if (r.base_bom_line_uom === null) { base('pack_base_bom_line_uom_null'); continue; }
      if (r.base_bom_line_uom !== r.base_final_output_uom) { base('pack_base_bom_line_uom_mismatch'); continue; }
      if (r.pack_linked_base_bom_head_id && r.pack_linked_base_bom_head_id !== r.base_bom_head_id) {
        base('linked_base_inconsistent'); continue;
      }
      base('ok_two_head');
    }

    // Emit JSON to stdout
    process.stdout.write(JSON.stringify(report, null, 2) + '\n');

    // Emit markdown summary to docs/
    const md = renderMarkdown(report);
    const mdPath = join('docs', `two_head_bom_audit_${report.generated_at.replace(/[:.]/g, '-')}.md`);
    writeFileSync(mdPath, md);
    console.error(`Markdown summary written to ${mdPath}`);
  } finally {
    await pool.end();
  }
}

function renderMarkdown(r: Report): string {
  const sections: string[] = [
    `# Two-Head BOM Audit — ${r.generated_at}`,
    '',
    `Total MANUFACTURED + ACTIVE items: **${r.manufactured_items_total}**`,
    '',
    `## Summary counts`,
    '',
    `| Category | Count |`,
    `|---|---|`,
    `| ok_two_head (PACK + BASE both healthy) | ${r.ok_two_head.length} |`,
    `| ok_pack_only (no BASE expected) | ${r.ok_pack_only.length} |`,
    `| missing_pack_head | ${r.missing_pack_head.length} |`,
    `| missing_pack_active_version | ${r.missing_pack_active_version.length} |`,
    `| missing_base_active_version | ${r.missing_base_active_version.length} |`,
    `| pack_no_base_bom_line | ${r.pack_no_base_bom_line.length} |`,
    `| pack_multiple_base_bom_lines | ${r.pack_multiple_base_bom_lines.length} |`,
    `| pack_base_bom_line_qty_null | ${r.pack_base_bom_line_qty_null.length} |`,
    `| pack_base_bom_line_uom_null | ${r.pack_base_bom_line_uom_null.length} |`,
    `| pack_base_bom_line_uom_mismatch | ${r.pack_base_bom_line_uom_mismatch.length} |`,
    `| linked_base_inconsistent | ${r.linked_base_inconsistent.length} |`,
    `| base_head_not_kind_base | ${r.base_head_not_kind_base.length} |`,
    `| pack_head_not_kind_pack | ${r.pack_head_not_kind_pack.length} |`,
    '',
  ];
  const dump = (k: keyof Report) => {
    const arr = r[k];
    if (!Array.isArray(arr) || arr.length === 0) return;
    sections.push(`## ${k}`, '');
    for (const b of arr as Bucket[]) sections.push(`- \`${b.item_id}\` — ${b.item_name}`);
    sections.push('');
  };
  for (const k of [
    'missing_pack_head', 'missing_pack_active_version', 'missing_base_active_version',
    'pack_no_base_bom_line', 'pack_multiple_base_bom_lines',
    'pack_base_bom_line_qty_null', 'pack_base_bom_line_uom_null', 'pack_base_bom_line_uom_mismatch',
    'linked_base_inconsistent', 'base_head_not_kind_base', 'pack_head_not_kind_pack',
  ] as const) dump(k);
  return sections.join('\n');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

- [ ] **Step 2: Smoke-test the script syntactically**

Run: `cd C:/Users/tomw2/Projects/gt-factory-os && npx tsc --noEmit scripts/audit_two_head_bom.ts`
Expected: no errors. (If `pg` is not in package.json, install: `npm i pg @types/pg --save`.)

- [ ] **Step 3: Run against live Supabase**

Run: `cd C:/Users/tomw2/Projects/gt-factory-os && npx tsx scripts/audit_two_head_bom.ts > docs/two_head_bom_audit_$(node -e "process.stdout.write(new Date().toISOString().replace(/[:.]/g,'-'))").json 2>&1`

Expected:
- Process exits 0.
- JSON file in `gt-factory-os/docs/` with structured report.
- Markdown summary in `gt-factory-os/docs/`.

- [ ] **Step 4: Tom-visible report**

Copy the markdown summary into `PRODUCTION/docs/two_head_bom_repair_evidence.md` §1 ("Pre-fix audit"). Surface to Tom in the run summary.

- [ ] **Step 5: Commit + push (audit script + first audit output)**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os
git add scripts/audit_two_head_bom.ts docs/two_head_bom_audit_*.md docs/two_head_bom_audit_*.json
git commit -m "audit: two-head BOM coverage report (Tranche 0 of two-head repair)"
git push origin main
```

### Task 0.2: STOP-GATE — Tom reviews audit, decides on anomalies

**This is a hard checkpoint.** Do not proceed to Tranche 1 until Tom acknowledges the audit results.

- [ ] **Step 1: Surface audit categories to Tom in the run summary**

Format: "audit found X items in `ok_two_head`, Y in `ok_pack_only`, Z in <each anomaly category>." For each non-zero anomaly category, list the affected `item_id` values.

- [ ] **Step 2: Decision matrix**

For each anomaly category Tom must say: (a) fix the data manually now (defer Tranche 1), (b) accept as exception (handler treats as `ITEM_DATA_ANOMALY` 409), or (c) the case is not real (close as false positive).

- [ ] **Step 3: Document Tom's decisions**

Append decisions into `PRODUCTION/docs/two_head_bom_repair_evidence.md` §2.

---

## Tranche 1 — Schema migration: add `base_bom_version_id_pinned`

> **Note (2026-05-02):** plan-original migration number 0125 was unavailable at dispatch time (`0125_v_planned_inflow_by_day.sql` already on main, `0126_*` taken by parallel Tranche 3). Tranche 1 takes **0127** instead. All filenames below updated. SQL body unchanged. Logical ordering with Tranche 3 inverted (engine v2 landed first); both migrations are functionally independent so no apply-order dependency.

### Task 1.1: Create migration 0127

**Files:**
- Create: `gt-factory-os/db/migrations/0127_production_actual_base_bom_pinning.sql`

- [ ] **Step 1: Write migration SQL**

```sql
-- ===========================================================================
-- 0127_production_actual_base_bom_pinning.sql
-- ===========================================================================
-- Two-head BOM repair — Tranche 1. Renumbered from plan-original 0125
-- (slots 0125/0126 already taken at dispatch time on 2026-05-02).
--
-- Scope:
--   1. Add nullable column production_actual.base_bom_version_id_pinned
--      (FK to bom_version), capturing the BASE BOM version that was active
--      at form-open time when the produced item has a base_bom_head_id.
--   2. Backfill is a no-op (column nullable; no existing rows assumed real
--      pre-launch — see plan §"Pre-launch context").
--
-- Why a new column rather than reusing bom_version_id_pinned:
--   bom_version_id_pinned MUST point at the PACK active version (existing
--   semantic; 0060 §3 STALE_BOM_VERSION gate uses it). Adding a separate
--   column for BASE preserves backward audit reads and lets the handler
--   reject stale pinning on each head independently.
--
-- Contract source:
--   PRODUCTION/docs/2026-05-02-two-head-bom-explosion-repair-plan.md §Tranche 1
--   CLAUDE.md §"Production reporting v1" (post-amendment)
--
-- Depends on:
--   0003 (bom_head, bom_version)
--   0060 (production_actual)
--
-- Rollback: forward-only once any submission row sets the column non-null.
--   Pre-data rollback:
--     ALTER TABLE private_core.production_actual
--       DROP COLUMN base_bom_version_id_pinned;
-- ===========================================================================

begin;

set search_path to private_core, public;

alter table private_core.production_actual
  add column base_bom_version_id_pinned uuid
    references private_core.bom_version(bom_version_id);

comment on column private_core.production_actual.base_bom_version_id_pinned is
  'The BASE BOM version that was active when the operator opened the form. NULL when the produced item has no base_bom_head_id (REPACK or pure-pack items). When non-null, the handler enforces stale-pinning rejection on this column independently of bom_version_id_pinned (which always pins the PACK head). Two-head explosion gate; see plan 2026-05-02-two-head-bom-explosion-repair-plan.md.';

create index if not exists idx_production_actual_base_bom_version
  on private_core.production_actual(base_bom_version_id_pinned)
  where base_bom_version_id_pinned is not null;

commit;

-- ===========================================================================
-- End of 0127_production_actual_base_bom_pinning.sql
-- ===========================================================================
```

- [ ] **Step 2: Apply against live Supabase**

Run via the standard project pattern (Node `pg` client in autocommit, same as 0081 in DB-ops log):
```bash
cd C:/Users/tomw2/Projects/gt-factory-os
DATABASE_URL_POOLED="<from .env>" node -e "
  import('pg').then(({Client}) => {
    const c = new Client({connectionString: process.env.DATABASE_URL_POOLED, ssl:{rejectUnauthorized:false}});
    c.connect().then(()=>require('fs').readFileSync('db/migrations/0125_production_actual_base_bom_pinning.sql','utf8'))
     .then(sql=>c.query(sql)).then(()=>console.log('OK')).catch(e=>{console.error(e);process.exit(1)}).finally(()=>c.end());
  });
"
```
Expected: `OK`. No errors.

- [ ] **Step 3: Verify column exists**

```bash
DATABASE_URL_POOLED="..." node -e "
  import('pg').then(({Client})=>{
    const c=new Client({connectionString:process.env.DATABASE_URL_POOLED,ssl:{rejectUnauthorized:false}});
    c.connect().then(()=>c.query(\`select column_name, data_type, is_nullable from information_schema.columns where table_schema='private_core' and table_name='production_actual' and column_name='base_bom_version_id_pinned'\`))
     .then(r=>console.log(r.rows)).finally(()=>c.end());
  });
"
```
Expected: one row, `data_type=uuid`, `is_nullable=YES`.

### Task 1.2: pgTAP for migration

**Files:**
- Create: `gt-factory-os/db/tests/0127_production_actual_base_bom_pinning.test.sql`

- [ ] **Step 1: Write pgTAP**

```sql
-- pgTAP for 0127_production_actual_base_bom_pinning.sql
-- Run: pg_prove -f db/tests/0127_production_actual_base_bom_pinning.test.sql

\unset ECHO
\set ON_ERROR_ROLLBACK 1
\set ON_ERROR_STOP true

begin;
  select plan(5);

  -- 1. Column exists.
  select has_column(
    'private_core', 'production_actual', 'base_bom_version_id_pinned',
    'production_actual.base_bom_version_id_pinned column exists'
  );

  -- 2. Type is uuid.
  select col_type_is(
    'private_core', 'production_actual', 'base_bom_version_id_pinned', 'uuid',
    'base_bom_version_id_pinned is uuid'
  );

  -- 3. Nullable.
  select col_is_null(
    'private_core', 'production_actual', 'base_bom_version_id_pinned',
    'base_bom_version_id_pinned is nullable'
  );

  -- 4. FK to bom_version.
  select fk_ok(
    'private_core', 'production_actual', 'base_bom_version_id_pinned',
    'private_core', 'bom_version', 'bom_version_id',
    'base_bom_version_id_pinned references bom_version(bom_version_id)'
  );

  -- 5. Index exists.
  select has_index(
    'private_core', 'production_actual', 'idx_production_actual_base_bom_version',
    'partial index on base_bom_version_id_pinned exists'
  );

  select * from finish();
rollback;
```

- [ ] **Step 2: Run pgTAP**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os
pg_prove -h aws-1-eu-central-1.pooler.supabase.com -p 5432 -U "<from .env>" -d postgres -f db/tests/0127_production_actual_base_bom_pinning.test.sql
```
Expected: `5/5 PASS`.

If `pg_prove` is unavailable on this machine, run the file via `psql` with `\i` and confirm the tap output ends with `# Looks like all 5 tests passed.`

- [ ] **Step 3: Commit + push**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os
git add db/migrations/0127_production_actual_base_bom_pinning.sql db/tests/0127_production_actual_base_bom_pinning.test.sql
git commit -m "schema: add production_actual.base_bom_version_id_pinned (Tranche 1 two-head repair, slot 0127)"
git pull --rebase origin main && git push origin main
```

---

## Tranche 2 — Production Actual handler (open + submit two-head)

### Task 2.1: Extend Zod schemas + response types

**Files:**
- Modify: `gt-factory-os/api/src/production-actuals/schemas.ts`

- [ ] **Step 1: Edit `ProductionActualOpenResponse`**

Replace the `bom_lines` array element shape (currently lines 30–36) with the tagged-source variant, and add the BASE pinning fields:

```typescript
export interface ProductionActualOpenResponse {
  item_id: string;
  item_name: string;
  supply_method: 'MANUFACTURED' | 'REPACK';
  output_uom_default: string;

  // PACK head pinning (always present for MANUFACTURED + REPACK).
  bom_version_id_pinned: string;
  bom_head_id: string;
  bom_version_label: string;
  bom_final_output_qty: string;
  bom_final_output_uom: string;

  // BASE head pinning (present only when items.base_bom_head_id is set
  // AND the BASE head has an active version). NULL otherwise.
  base_bom_version_id_pinned: string | null;
  base_bom_head_id: string | null;
  base_bom_version_label: string | null;
  base_bom_final_output_qty: string | null;
  base_bom_final_output_uom: string | null;

  // Liters of BASE liquid required per 1 unit of PACK output, derived from
  // the PACK BASE_BOM line (final_component_qty / pack.final_bom_output_qty).
  // NULL when no BASE head linked.
  base_qty_per_pack_unit: string | null;

  bom_lines: Array<{
    line_id: string;
    component_id: string;
    component_name: string;
    final_component_qty: string;
    component_uom: string | null;
    // 'pack' for components from the PACK head; 'base' for components from
    // the BASE head. The portal uses this to badge / group rows in the
    // preview but submit math does not depend on it.
    source: 'pack' | 'base';
  }>;
}
```

- [ ] **Step 2: Add `BASE_*` conflict reason codes**

Extend `ProductionActualConflictReason` (currently lines 108–123):

```typescript
export type ProductionActualConflictReason =
  | 'ITEM_NOT_FOUND'
  | 'ITEM_INACTIVE'
  | 'WRONG_SUPPLY_METHOD'
  | 'NO_BOM_HEAD'
  | 'NO_ACTIVE_BOM_VERSION'
  | 'STALE_BOM_VERSION'
  | 'UOM_MISMATCH'
  | 'UNIT_NOT_FOUND'
  | 'IDEMPOTENCY_KEY_REUSED'
  | 'NO_BOM_LINES'
  // ----- two-head additions (Tranche 2) -----
  | 'NO_ACTIVE_BASE_BOM_VERSION'        // items.base_bom_head_id set but no active version
  | 'STALE_BASE_BOM_VERSION'            // base pinning drifted between open and submit
  | 'MULTIPLE_BASE_BOM_LINES'           // PACK has >1 BASE_BOM lines (model violation)
  | 'BASE_BOM_LINE_QTY_NULL'            // BASE_BOM line exists but qty is null
  | 'BASE_BOM_LINE_UOM_MISMATCH'        // BASE_BOM line uom != BASE head output uom
  | 'BASE_BOM_LINKAGE_INCONSISTENT'     // bom_head.linked_base != items.base_bom_head_id
  | 'NO_BASE_BOM_LINES'                 // BASE active version has zero leaf lines
  // ----- from_plan link conflicts (existing) -----
  | 'PLAN_NOT_FOUND'
  | 'PLAN_ITEM_MISMATCH'
  | 'PLAN_ALREADY_COMPLETED'
  | 'PLAN_CANCELLED';
```

- [ ] **Step 3: Extend `ProductionActualSubmitSchema`**

Add the BASE pinning field (after `bom_version_id_pinned`):

```typescript
export const ProductionActualSubmitSchema = z.object({
  idempotency_key: z.string().min(1).max(255),
  event_at: z.string().datetime(),
  item_id: z.string().min(1),
  bom_version_id_pinned: z.string().uuid(),
  // Two-head: present iff the open response returned a non-null
  // base_bom_version_id_pinned. Null otherwise. Handler enforces
  // presence-equals-shape against the item's current base_bom_head_id.
  base_bom_version_id_pinned: z.string().uuid().nullable().optional(),
  output_qty: z.number().nonnegative(),
  scrap_qty: z.number().nonnegative().default(0),
  output_uom: z.string().min(1),
  notes: z.string().max(2000).nullable().optional(),
  from_plan_id: z.string().uuid().nullable().optional(),
});
```

- [ ] **Step 4: Extend `ProductionActualCommittedResponse`**

Add the linked-base pinning + base consumption tag (mirror open):

```typescript
export interface ProductionActualCommittedResponse {
  submission_id: string;
  status: 'posted';
  event_at: string;
  posted_at: string;
  item_id: string;
  bom_version_id_pinned: string;
  base_bom_version_id_pinned: string | null;   // NEW
  output_qty: string;
  scrap_qty: string;
  output_uom: string;
  output_ledger_row_id: string;
  scrap_ledger_row_id: string | null;
  consumption: Array<{
    component_id: string;
    consumption_qty: string;
    component_uom: string | null;
    stock_ledger_movement_id: string;
    source: 'pack' | 'base';                    // NEW
  }>;
  idempotent_replay: boolean;
  linked_plan_id: string | null;
}
```

### Task 2.2: Failing tests first (TDD)

**Files:**
- Modify: `gt-factory-os/api/test/production_actual.test.ts`

- [ ] **Step 1: Add new test group `TWO_HEAD_OK`**

Add three new tests in this group, each against live pooled Supabase via the existing test harness conventions in `production_actual.test.ts`:

```typescript
import { describe, it, beforeAll, afterAll } from 'node:test';
import assert from 'node:assert/strict';

describe('production-actual two-head BOM (Tranche 2)', () => {
  // Uses fixture FG-DES-1L (DESERTEA 1L). Confirmed in audit (Tranche 0)
  // to be in the ok_two_head bucket.

  it('TWO_HEAD_OK_OPEN: open returns pack lines + base lines + base pinning', async () => {
    const res = await fetch(`${API_BASE}/api/v1/queries/production-actuals/open?item_id=FG-DES-1L`, {
      headers: { 'X-Test-Session': testSessionAdmin() },
    });
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.ok(body.base_bom_version_id_pinned, 'base pin present');
    assert.ok(body.base_bom_head_id?.startsWith('BOM-BASE-'));
    assert.ok(Number(body.base_qty_per_pack_unit) > 0);
    const packCount = body.bom_lines.filter((l: any) => l.source === 'pack').length;
    const baseCount = body.bom_lines.filter((l: any) => l.source === 'base').length;
    assert.ok(packCount >= 1, 'has pack components');
    assert.ok(baseCount >= 1, 'has base (liquid) components — THE BUG: was 0');
  });

  it('TWO_HEAD_OK_SUBMIT: submit posts pack + base consumption rows in one tx', async () => {
    // Open → pin → submit, then verify stock_ledger has both pack and base
    // rows linked to the same submission_id with related_bom_version_id
    // matching either the pack pin or the base pin.
    const open = await fetch(`${API_BASE}/api/v1/queries/production-actuals/open?item_id=FG-DES-1L`, {
      headers: { 'X-Test-Session': testSessionAdmin() },
    }).then(r => r.json());

    const idem = `pa-two-head-${Date.now()}`;
    const submitRes = await fetch(`${API_BASE}/api/v1/mutations/production-actuals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Test-Session': testSessionAdmin() },
      body: JSON.stringify({
        idempotency_key: idem,
        event_at: new Date().toISOString(),
        item_id: 'FG-DES-1L',
        bom_version_id_pinned: open.bom_version_id_pinned,
        base_bom_version_id_pinned: open.base_bom_version_id_pinned,
        output_qty: 1,        // tiny smoke qty so this is reversible
        scrap_qty: 0,
        output_uom: open.output_uom_default,
      }),
    });
    assert.equal(submitRes.status, 201);
    const body = await submitRes.json();

    const packConsumption = body.consumption.filter((c: any) => c.source === 'pack');
    const baseConsumption = body.consumption.filter((c: any) => c.source === 'base');
    assert.ok(packConsumption.length >= 1, 'pack consumption rows present');
    assert.ok(baseConsumption.length >= 1, 'base consumption rows present — THE BUG: was 0');

    // Cleanup: emit corrective reversal rows OR mark submission test-only
    // and delete via an admin path. (Use the existing test cleanup helper if
    // present; otherwise leave a TODO and use a tiny qty so the mutation is
    // operationally negligible — pre-launch context, no real stock at risk.)
  });

  it('TWO_HEAD_STALE_BASE: stale base pin is rejected with STALE_BASE_BOM_VERSION', async () => {
    // Forge a deliberately-wrong base_bom_version_id_pinned (random uuid that
    // is not the active BASE version). Expect 409 with reason_code=STALE_BASE_BOM_VERSION.
    const open = await fetch(`${API_BASE}/api/v1/queries/production-actuals/open?item_id=FG-DES-1L`, {
      headers: { 'X-Test-Session': testSessionAdmin() },
    }).then(r => r.json());

    const submitRes = await fetch(`${API_BASE}/api/v1/mutations/production-actuals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Test-Session': testSessionAdmin() },
      body: JSON.stringify({
        idempotency_key: `pa-stale-base-${Date.now()}`,
        event_at: new Date().toISOString(),
        item_id: 'FG-DES-1L',
        bom_version_id_pinned: open.bom_version_id_pinned,
        base_bom_version_id_pinned: '00000000-0000-0000-0000-000000000000', // forged
        output_qty: 1,
        scrap_qty: 0,
        output_uom: open.output_uom_default,
      }),
    });
    assert.equal(submitRes.status, 409);
    const body = await submitRes.json();
    assert.equal(body.reason_code, 'STALE_BASE_BOM_VERSION');
  });
});

describe('production-actual REPACK no-base path (regression)', () => {
  it('REPACK_NO_BASE_OK: REPACK item open returns base_bom_version_id_pinned=null and pack-only lines', async () => {
    // Pick a REPACK item from the audit (e.g., the items.json fixture has
    // BOUGHT_FINISHED + REPACK items; use one in the ok_pack_only bucket).
    // ... assertion: body.base_bom_version_id_pinned === null;
    //                body.bom_lines.every(l => l.source === 'pack');
  });
});
```

- [ ] **Step 2: Run tests; confirm they FAIL with the current code**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os
node --test --import tsx api/test/production_actual.test.ts 2>&1 | tail -50
```
Expected: the three TWO_HEAD_* tests FAIL — at minimum `TWO_HEAD_OK_OPEN` fails because `base_bom_version_id_pinned` is undefined / not present in the response. This is the test-driven proof that the bug exists.

### Task 2.3: Helper — `loadTwoHeadBomContext`

**Files:**
- Modify: `gt-factory-os/api/src/production-actuals/handler.ts`

- [ ] **Step 1: Add module-private helper above `handleProductionActualOpen`**

```typescript
// ===========================================================================
// Two-head BOM context loader (Tranche 2 of two-head repair).
// Resolves PACK + BASE heads, active versions, and lines for an item.
// Returns a unified context for both open and submit paths.
// ===========================================================================
interface TwoHeadBomLine {
  line_id: string;
  component_id: string;
  component_name: string;
  final_component_qty: string;
  component_uom: string | null;
  source: 'pack' | 'base';
}

interface TwoHeadBomContext {
  pack: {
    bom_head_id: string;
    bom_version_id: string;
    bom_version_label: string;
    final_bom_output_qty: string;
    final_bom_output_uom: string;
    leaf_lines: TwoHeadBomLine[];   // PACK lines that are leaf components (no BASE_BOM ref)
    base_bom_line_qty: string | null;  // qty from the BASE_BOM line, if present
    base_bom_line_uom: string | null;
  };
  base: {
    bom_head_id: string;
    bom_version_id: string;
    bom_version_label: string;
    final_bom_output_qty: string;
    final_bom_output_uom: string;
    leaf_lines: TwoHeadBomLine[];
  } | null;
  base_qty_per_pack_unit: string | null; // computed: pack.base_bom_line_qty / pack.final_bom_output_qty
}

type LoadResult =
  | { kind: 'ok'; ctx: TwoHeadBomContext }
  | { kind: 'conflict'; reason: ProductionActualConflictReason; detail: string; field?: string };

async function loadTwoHeadBomContext(
  exec: Db | { execute: typeof sql },
  item: { item_id: string; primary_bom_head_id: string | null; base_bom_head_id?: string | null },
): Promise<LoadResult> {
  if (!item.primary_bom_head_id) {
    return { kind: 'conflict', reason: 'NO_BOM_HEAD', detail: `item ${item.item_id} has no primary_bom_head_id`, field: 'item_id' };
  }

  // 1. PACK head + active version
  const packHeadRows = await sql<{
    active_version_id: string | null;
    final_bom_output_qty: string;
    final_bom_output_uom: string;
    linked_base_bom_head_id: string | null;
  }>`
    select active_version_id,
           final_bom_output_qty::text as final_bom_output_qty,
           final_bom_output_uom,
           linked_base_bom_head_id
      from private_core.bom_head
     where bom_head_id = ${item.primary_bom_head_id}
  `.execute(exec as Db);
  if (packHeadRows.rows.length === 0 || !packHeadRows.rows[0].active_version_id) {
    return { kind: 'conflict', reason: 'NO_ACTIVE_BOM_VERSION', detail: `bom_head ${item.primary_bom_head_id} has no active bom_version` };
  }
  const packHead = packHeadRows.rows[0];
  const packVersionId = packHead.active_version_id!;

  // Sanity: linked_base must agree with items.base_bom_head_id when both set.
  if (item.base_bom_head_id && packHead.linked_base_bom_head_id
      && packHead.linked_base_bom_head_id !== item.base_bom_head_id) {
    return {
      kind: 'conflict',
      reason: 'BASE_BOM_LINKAGE_INCONSISTENT',
      detail: `bom_head.linked_base_bom_head_id=${packHead.linked_base_bom_head_id} != items.base_bom_head_id=${item.base_bom_head_id}`,
    };
  }

  // 2. PACK active version label
  const packVerRows = await sql<{ version_label: string }>`
    select version_label from private_core.bom_version where bom_version_id = ${packVersionId}::uuid
  `.execute(exec as Db);
  const packVersionLabel = packVerRows.rows[0]?.version_label ?? '';

  // 3. PACK lines, partitioned by component_ref_type.
  const packLineRows = await sql<{
    line_id: string;
    component_ref_type: string;
    final_component_id: string | null;
    component_name: string | null;
    final_component_qty: string | null;
    component_uom: string | null;
  }>`
    select bl.line_id::text,
           bl.component_ref_type,
           bl.final_component_id,
           c.component_name,
           bl.final_component_qty::text as final_component_qty,
           bl.component_uom
      from private_core.bom_lines bl
      left join private_core.components c on c.component_id = bl.final_component_id
     where bl.bom_version_id = ${packVersionId}::uuid
       and bl.status in ('ACTIVE', 'PENDING')
     order by bl.line_no
  `.execute(exec as Db);

  const packLeafLines: TwoHeadBomLine[] = [];
  let baseBomLineQty: string | null = null;
  let baseBomLineUom: string | null = null;
  let baseBomLineCount = 0;
  for (const row of packLineRows.rows) {
    if (row.component_ref_type === 'BASE_BOM') {
      baseBomLineCount += 1;
      baseBomLineQty = row.final_component_qty;
      baseBomLineUom = row.component_uom;
    } else if (row.final_component_id && row.component_name && row.final_component_qty) {
      packLeafLines.push({
        line_id: row.line_id,
        component_id: row.final_component_id,
        component_name: row.component_name,
        final_component_qty: row.final_component_qty,
        component_uom: row.component_uom,
        source: 'pack',
      });
    }
  }
  if (baseBomLineCount > 1) {
    return { kind: 'conflict', reason: 'MULTIPLE_BASE_BOM_LINES', detail: `PACK version ${packVersionId} has ${baseBomLineCount} BASE_BOM lines; model supports exactly one` };
  }

  // 4. BASE head — only if items.base_bom_head_id is set
  let baseCtx: TwoHeadBomContext['base'] = null;
  let baseQtyPerPack: string | null = null;
  if (item.base_bom_head_id) {
    if (baseBomLineCount === 0) {
      return { kind: 'conflict', reason: 'NO_BOM_LINES', detail: `items.base_bom_head_id=${item.base_bom_head_id} but PACK version has no BASE_BOM line — data anomaly` };
    }
    if (baseBomLineQty === null) {
      return { kind: 'conflict', reason: 'BASE_BOM_LINE_QTY_NULL', detail: `BASE_BOM line on PACK version ${packVersionId} has null final_component_qty` };
    }
    const baseHeadRows = await sql<{
      active_version_id: string | null;
      final_bom_output_qty: string;
      final_bom_output_uom: string;
    }>`
      select active_version_id,
             final_bom_output_qty::text as final_bom_output_qty,
             final_bom_output_uom
        from private_core.bom_head
       where bom_head_id = ${item.base_bom_head_id}
    `.execute(exec as Db);
    if (baseHeadRows.rows.length === 0 || !baseHeadRows.rows[0].active_version_id) {
      return { kind: 'conflict', reason: 'NO_ACTIVE_BASE_BOM_VERSION', detail: `BASE bom_head ${item.base_bom_head_id} has no active version` };
    }
    const baseHead = baseHeadRows.rows[0];
    const baseVersionId = baseHead.active_version_id!;

    if (baseBomLineUom !== baseHead.final_bom_output_uom) {
      return { kind: 'conflict', reason: 'BASE_BOM_LINE_UOM_MISMATCH', detail: `BASE_BOM line uom=${baseBomLineUom} != BASE head output uom=${baseHead.final_bom_output_uom}` };
    }

    const baseVerRows = await sql<{ version_label: string }>`
      select version_label from private_core.bom_version where bom_version_id = ${baseVersionId}::uuid
    `.execute(exec as Db);
    const baseVersionLabel = baseVerRows.rows[0]?.version_label ?? '';

    const baseLineRows = await sql<{
      line_id: string;
      component_id: string;
      component_name: string;
      final_component_qty: string;
      component_uom: string | null;
    }>`
      select bl.line_id::text,
             bl.final_component_id as component_id,
             c.component_name,
             bl.final_component_qty::text as final_component_qty,
             bl.component_uom
        from private_core.bom_lines bl
        join private_core.components c on c.component_id = bl.final_component_id
       where bl.bom_version_id = ${baseVersionId}::uuid
         and bl.final_component_id is not null
         and bl.status in ('ACTIVE', 'PENDING')
       order by bl.line_no
    `.execute(exec as Db);
    if (baseLineRows.rows.length === 0) {
      return { kind: 'conflict', reason: 'NO_BASE_BOM_LINES', detail: `BASE version ${baseVersionId} has zero leaf lines` };
    }

    baseCtx = {
      bom_head_id: item.base_bom_head_id,
      bom_version_id: baseVersionId,
      bom_version_label: baseVersionLabel,
      final_bom_output_qty: baseHead.final_bom_output_qty,
      final_bom_output_uom: baseHead.final_bom_output_uom,
      leaf_lines: baseLineRows.rows.map((r) => ({
        line_id: r.line_id,
        component_id: r.component_id,
        component_name: r.component_name,
        final_component_qty: r.final_component_qty,
        component_uom: r.component_uom,
        source: 'base' as const,
      })),
    };

    // base_qty_per_pack_unit = (PACK BASE_BOM line qty) / (PACK final_bom_output_qty)
    const denom = Number(packHead.final_bom_output_qty);
    if (denom > 0) {
      baseQtyPerPack = (Number(baseBomLineQty) / denom).toFixed(8);
    }
  }

  return {
    kind: 'ok',
    ctx: {
      pack: {
        bom_head_id: item.primary_bom_head_id,
        bom_version_id: packVersionId,
        bom_version_label: packVersionLabel,
        final_bom_output_qty: packHead.final_bom_output_qty,
        final_bom_output_uom: packHead.final_bom_output_uom,
        leaf_lines: packLeafLines,
        base_bom_line_qty: baseBomLineQty,
        base_bom_line_uom: baseBomLineUom,
      },
      base: baseCtx,
      base_qty_per_pack_unit: baseQtyPerPack,
    },
  };
}
```

### Task 2.4: Update `handleProductionActualOpen`

**Files:**
- Modify: `gt-factory-os/api/src/production-actuals/handler.ts:98-211`

- [ ] **Step 1: Replace lines 107-211 with two-head-aware open**

Replace the body of `handleProductionActualOpen` after the role gate (line 105) with:

```typescript
  // Resolve item incl. base_bom_head_id
  const itemRows = await sql<{
    item_id: string;
    item_name: string;
    supply_method: string;
    status: string;
    sales_uom: string | null;
    primary_bom_head_id: string | null;
    base_bom_head_id: string | null;
  }>`
    select item_id, item_name, supply_method, status, sales_uom,
           primary_bom_head_id, base_bom_head_id
      from private_core.items
     where item_id = ${query.item_id}
  `.execute(db);
  if (itemRows.rows.length === 0) {
    return conflictResult('ITEM_NOT_FOUND', `item ${query.item_id} not found`, 'item_id');
  }
  const item = itemRows.rows[0];
  if (item.status !== 'ACTIVE') {
    return conflictResult('ITEM_INACTIVE', `item ${query.item_id} status=${item.status}`, 'item_id');
  }
  if (item.supply_method !== 'MANUFACTURED' && item.supply_method !== 'REPACK') {
    return conflictResult('WRONG_SUPPLY_METHOD',
      `item ${query.item_id} supply_method=${item.supply_method}; only MANUFACTURED or REPACK are producible`, 'item_id');
  }

  const ctxRes = await loadTwoHeadBomContext(db, {
    item_id: item.item_id,
    primary_bom_head_id: item.primary_bom_head_id,
    base_bom_head_id: item.base_bom_head_id,
  });
  if (ctxRes.kind === 'conflict') {
    return conflictResult(ctxRes.reason, ctxRes.detail, ctxRes.field);
  }
  const ctx = ctxRes.ctx;

  // Merge pack + base lines into one display list
  const allLines = [...ctx.pack.leaf_lines, ...(ctx.base?.leaf_lines ?? [])];
  if (allLines.length === 0) {
    return conflictResult('NO_BOM_LINES', `bom_version has no usable component lines`);
  }

  return {
    kind: 'ok',
    status: 200,
    body: {
      item_id: item.item_id,
      item_name: item.item_name,
      supply_method: item.supply_method as 'MANUFACTURED' | 'REPACK',
      output_uom_default: item.sales_uom ?? '',
      bom_version_id_pinned: ctx.pack.bom_version_id,
      bom_head_id: ctx.pack.bom_head_id,
      bom_version_label: ctx.pack.bom_version_label,
      bom_final_output_qty: ctx.pack.final_bom_output_qty,
      bom_final_output_uom: ctx.pack.final_bom_output_uom,
      base_bom_version_id_pinned: ctx.base?.bom_version_id ?? null,
      base_bom_head_id: ctx.base?.bom_head_id ?? null,
      base_bom_version_label: ctx.base?.bom_version_label ?? null,
      base_bom_final_output_qty: ctx.base?.final_bom_output_qty ?? null,
      base_bom_final_output_uom: ctx.base?.final_bom_output_uom ?? null,
      base_qty_per_pack_unit: ctx.base_qty_per_pack_unit,
      bom_lines: allLines,
    },
  };
```

### Task 2.5: Update `handleProductionActualSubmit`

**Files:**
- Modify: `gt-factory-os/api/src/production-actuals/handler.ts:216-570`

- [ ] **Step 1: Replace BOM resolution (lines 304-369) with two-head context**

After the item-validation block (lines 268-301) and before the form_submissions envelope (line 371), replace:

```typescript
      // 3b/c — resolve active BOM (PACK + optional BASE) and validate pinning
      const ctxRes = await loadTwoHeadBomContext(trx, {
        item_id: item.item_id,
        primary_bom_head_id: item.primary_bom_head_id,
        base_bom_head_id: item.base_bom_head_id,  // NEW field on items select
      });
      if (ctxRes.kind === 'conflict') {
        return conflictResult(ctxRes.reason, ctxRes.detail, ctxRes.field);
      }
      const ctx = ctxRes.ctx;

      // 3c — stale PACK pinning rejection
      if (ctx.pack.bom_version_id !== request.bom_version_id_pinned) {
        return conflictResult('STALE_BOM_VERSION',
          `bom_version_id_pinned=${request.bom_version_id_pinned} is not the current active PACK version (${ctx.pack.bom_version_id})`,
          'bom_version_id_pinned');
      }

      // 3c.2 — stale BASE pinning rejection (when item has BASE)
      if (ctx.base) {
        if (!request.base_bom_version_id_pinned) {
          return conflictResult('STALE_BASE_BOM_VERSION',
            `item has base_bom_head_id but request omitted base_bom_version_id_pinned`,
            'base_bom_version_id_pinned');
        }
        if (ctx.base.bom_version_id !== request.base_bom_version_id_pinned) {
          return conflictResult('STALE_BASE_BOM_VERSION',
            `base_bom_version_id_pinned=${request.base_bom_version_id_pinned} is not the current active BASE version (${ctx.base.bom_version_id})`,
            'base_bom_version_id_pinned');
        }
      } else if (request.base_bom_version_id_pinned) {
        return conflictResult('STALE_BASE_BOM_VERSION',
          `request supplied base_bom_version_id_pinned but item has no base_bom_head_id`,
          'base_bom_version_id_pinned');
      }

      // 3d — production_quantity = output + scrap
      const outputQty = request.output_qty;
      const scrapQty = request.scrap_qty;
      const productionQty = outputQty + scrapQty;
      const packDenom = Number(ctx.pack.final_bom_output_qty);
      if (packDenom <= 0) throw new Error(`PACK final_bom_output_qty must be > 0; got ${ctx.pack.final_bom_output_qty}`);

      // 3e — assemble unified consumption plan: pack lines + base lines
      // PACK leaf line consumption: qty = line.final_component_qty * productionQty / packDenom
      // BASE leaf line consumption: qty = base_line.final_component_qty * total_liters / baseDenom
      //   where total_liters = (pack.base_bom_line_qty * productionQty) / packDenom
      interface PlannedConsumption {
        line_id: string;
        component_id: string;
        component_uom: string | null;
        consumption_qty: number;
        source: 'pack' | 'base';
        related_bom_version_id: string;
      }
      const plan: PlannedConsumption[] = [];
      for (const l of ctx.pack.leaf_lines) {
        plan.push({
          line_id: l.line_id,
          component_id: l.component_id,
          component_uom: l.component_uom,
          consumption_qty: Number(l.final_component_qty) * productionQty / packDenom,
          source: 'pack',
          related_bom_version_id: ctx.pack.bom_version_id,
        });
      }
      if (ctx.base) {
        const baseDenom = Number(ctx.base.final_bom_output_qty);
        if (baseDenom <= 0) throw new Error(`BASE final_bom_output_qty must be > 0`);
        const totalBaseLiters = (Number(ctx.pack.base_bom_line_qty) * productionQty) / packDenom;
        for (const l of ctx.base.leaf_lines) {
          plan.push({
            line_id: l.line_id,
            component_id: l.component_id,
            component_uom: l.component_uom,
            consumption_qty: Number(l.final_component_qty) * totalBaseLiters / baseDenom,
            source: 'base',
            related_bom_version_id: ctx.base.bom_version_id,
          });
        }
      }
      if (plan.length === 0) {
        return conflictResult('NO_BOM_LINES', `no consumption lines computed for item ${request.item_id}`);
      }
```

- [ ] **Step 2: Replace existing consumption-write loop (lines 393-488)**

Replace the `componentIds`/`balRows`/`shortfalls` block AND the consumption-INSERT loop with one that iterates `plan` (pack + base merged):

```typescript
      // 3e.1 — bulk shortage check across all planned components
      const planComponentIds = Array.from(new Set(plan.map((p) => p.component_id)));
      const balRows = await sql<{ item_id: string; calculated_on_hand: string }>`
        select item_id, sum(calculated_on_hand)::text as calculated_on_hand
          from private_core.current_balances
         where site_id = ${SITE_ID}
           and item_id = any(${planComponentIds}::text[])
         group by item_id
      `.execute(trx);
      const balMap = new Map(balRows.rows.map((r) => [r.item_id, Number(r.calculated_on_hand)]));
      // Aggregate required qty per component (because pack and base could
      // both reference the same component_id in pathological edge cases).
      const requiredByComp = new Map<string, number>();
      for (const p of plan) requiredByComp.set(p.component_id, (requiredByComp.get(p.component_id) ?? 0) + p.consumption_qty);
      const shortfalls: Array<{ component_id: string; required_qty: string; available_qty: string }> = [];
      for (const [cid, required] of requiredByComp.entries()) {
        const available = balMap.get(cid) ?? 0;
        if (required > available + 1e-8) {
          shortfalls.push({ component_id: cid, required_qty: required.toFixed(8), available_qty: available.toFixed(8) });
        }
      }
      if (shortfalls.length > 0) {
        throw new HandlerError('INSUFFICIENT_STOCK', 409, {
          error: 'INSUFFICIENT_STOCK',
          message: 'One or more components have insufficient stock for this production run.',
          shortfalls,
        });
      }

      // 3e.2 — write consumption rows
      const consumptionResponses: ProductionActualCommittedResponse['consumption'] = [];
      for (const p of plan) {
        const compType = await sql<{ component_class: string | null; inventory_uom: string | null }>`
          select component_class, inventory_uom from private_core.components where component_id = ${p.component_id}
        `.execute(trx);
        const compClass = compType.rows[0]?.component_class ?? '';
        const componentItemType: ItemType =
          compClass === 'PACKAGING' || compClass === 'PACKAGING_SET' ? 'PKG' : 'RM';
        const uomCode = p.component_uom ?? compType.rows[0]?.inventory_uom ?? '';
        if (!uomCode) throw new Error(`line ${p.line_id} (${p.component_id}) has no resolvable UOM`);

        const consumptionLedger = await trx
          .insertInto('private_core.stock_ledger')
          .values({
            // Idempotency key is per (submission, source, component) so pack+base
            // never collide even if the same component appears in both.
            idempotency_key: `PA:${request.idempotency_key}:CONSUME:${p.source}:${p.component_id}`,
            movement_type: 'production_consumption',
            item_type: componentItemType,
            item_id: p.component_id,
            qty_delta: `-${p.consumption_qty.toFixed(8)}`,
            uom: uomCode,
            event_at: request.event_at,
            reported_at: submissionNow,
            reported_by_user_id: session.user_id,
            reported_by_snapshot: session.display_name,
            post_status: 'POSTED' as const,
            posted_by_user_id: session.user_id,
            source_channel: 'FORM',
            source_event_id: submissionId,
            source_id: p.line_id,
            related_bom_version_id: p.related_bom_version_id, // pack OR base version
          })
          .returning(['movement_id'])
          .executeTakeFirstOrThrow();

        consumptionResponses.push({
          component_id: p.component_id,
          consumption_qty: p.consumption_qty.toFixed(8),
          component_uom: uomCode,
          stock_ledger_movement_id: consumptionLedger.movement_id,
          source: p.source,
        });
      }
```

- [ ] **Step 3: Update the items SELECT (line 268-278) to include `base_bom_head_id`**

Add `base_bom_head_id` to the column list and the row type:

```typescript
      const itemRows = await sql<{
        item_id: string;
        supply_method: string;
        status: string;
        sales_uom: string | null;
        primary_bom_head_id: string | null;
        base_bom_head_id: string | null;
      }>`
        select item_id, supply_method, status, sales_uom,
               primary_bom_head_id, base_bom_head_id
          from private_core.items
         where item_id = ${request.item_id}
      `.execute(trx);
```

- [ ] **Step 4: Update the production_actual INSERT (lines 545-561)**

Add `base_bom_version_id_pinned`:

```typescript
      await sql`
        insert into private_core.production_actual
          (submission_id, event_at, actor_user_id, item_id,
           bom_version_id_pinned, base_bom_version_id_pinned,
           output_qty, scrap_qty, output_uom,
           notes, output_ledger_row_id)
        values
          (${submissionId}::uuid,
           ${request.event_at}::timestamptz,
           ${session.user_id}::uuid,
           ${request.item_id},
           ${ctx.pack.bom_version_id}::uuid,
           ${ctx.base?.bom_version_id ?? null}::uuid,
           ${String(outputQty)}::private_core.qty_8dp,
           ${String(scrapQty)}::private_core.qty_8dp,
           ${request.output_uom},
           ${request.notes ?? null},
           ${outputLedgerRowId}::uuid)
      `.execute(trx);
```

- [ ] **Step 5: Update committed response (look for `return { kind: 'committed' ... }` block)**

Add `base_bom_version_id_pinned: ctx.base?.bom_version_id ?? null` to the committed body, and `consumption: consumptionResponses` already carries `source` per row from Step 2.

- [ ] **Step 6: Run the failing tests; confirm they now PASS**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os
node --test --import tsx api/test/production_actual.test.ts 2>&1 | tail -50
```
Expected: TWO_HEAD_OK_OPEN, TWO_HEAD_OK_SUBMIT, TWO_HEAD_STALE_BASE all PASS. Existing tests still PASS (regression-free).

- [ ] **Step 7: Update `fetchExistingPaSubmission` (idempotent replay) to include base pin in the response shape**

Find the helper (referenced at line 261). Ensure its `consumption` array includes `source` per row (read from `stock_ledger.idempotency_key` parsing, or from the row's `related_bom_version_id` matched against the pinned versions of the original submission), and that it returns `base_bom_version_id_pinned` from `production_actual.base_bom_version_id_pinned`.

- [ ] **Step 8: Re-run all tests**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os
node --test --import tsx api/test/production_actual.test.ts api/test/production_actual_from_plan.test.ts api/test/production_actual_list.test.ts 2>&1 | tail -80
```
Expected: all green. No regression.

### Task 2.6: Deploy + live HTTP smoke

- [ ] **Step 1: Commit + push handler changes**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os
git add api/src/production-actuals/schemas.ts api/src/production-actuals/handler.ts api/test/production_actual.test.ts
git commit -m "feat(production-actual): two-head BOM explosion (Tranche 2 two-head repair)"
git push origin main
```

- [ ] **Step 2: Watch Railway deploy**

```bash
railway logs --service gt-factory-os-api -f 2>&1 | head -60
# Wait for "Listening on 0.0.0.0:3333" and a successful /health response.
```

- [ ] **Step 3: Live smoke against deployed instance**

```bash
API="https://gt-factory-os-api-production.up.railway.app"
TOKEN="<Tom's Supabase JWT>"

# Open
curl -s "$API/api/v1/queries/production-actuals/open?item_id=FG-DES-1L" \
  -H "Authorization: Bearer $TOKEN" | jq '{
    pack_pin: .bom_version_id_pinned,
    base_pin: .base_bom_version_id_pinned,
    pack_lines: ([.bom_lines[] | select(.source=="pack")] | length),
    base_lines: ([.bom_lines[] | select(.source=="base")] | length),
    base_qty_per_pack: .base_qty_per_pack_unit
  }'
```
Expected: `base_pin` is a uuid (not null), `base_lines` >= 1, `base_qty_per_pack` > 0. **THIS IS THE LIVE PROOF that the bug is fixed.**

- [ ] **Step 4: Deploy ID into evidence pack**

Append to `PRODUCTION/docs/two_head_bom_repair_evidence.md` §3 ("Tranche 2 deploy"): Railway deployment id + smoke response JSON.

---

## Tranche 3 — Planning engine: `fn_explode_bom_to_components_v2`

### Task 3.1: Migration 0126

**Files:**
- Create: `gt-factory-os/db/migrations/0126_fn_explode_bom_to_components_v2.sql`

- [ ] **Step 1: Write migration SQL**

```sql
-- ===========================================================================
-- 0126_fn_explode_bom_to_components_v2.sql
-- ===========================================================================
-- Two-head BOM repair — Tranche 3.
--
-- Replaces fn_explode_bom_to_components (from 0041) with a two-head walker
-- that handles items whose primary BOM head (PACK) references a BASE BOM.
--
-- Algorithm:
--   For each FG coverage row with shortage_flag=true and supply_method in
--   ('MANUFACTURED','REPACK'):
--     1. Resolve PACK bom_head + active version (as before).
--     2. Walk PACK bom_lines:
--          - For lines with component_ref_type IN ('RAW_NAME','COMPONENT')
--            and final_component_id NOT NULL: explode to component_demand
--            using pack.final_bom_output_qty as the denominator (existing
--            v1 logic, but explicit on the ref_type filter).
--          - For lines with component_ref_type='BASE_BOM': set
--              total_base_units = make_qty * (line.final_component_qty
--                                             / pack.final_bom_output_qty)
--            then resolve items.base_bom_head_id and its active version,
--            and walk that version's leaf lines, exploding each line as:
--              component_qty = base_line.final_component_qty
--                              * total_base_units / base.final_bom_output_qty
--          - Lines with component_ref_type='BOM' (sub-pack reference) are
--            NOT in scope for v1 — none observed in audit; emit
--            'unsupported_bom_ref' exception if encountered.
--     3. Aggregate via the existing UPSERT on
--        (run_id, component_id, period_bucket_key).
--
-- Why a v2 function instead of an in-place ALTER:
--   The v1 function (0041) is referenced by orchestration (0046, 0104) via
--   `private_core.fn_explode_bom_to_components(uuid)`. Replacing with
--   CREATE OR REPLACE preserves the signature and invocation sites.
--
-- Forward-compat note: this migration also updates the function name
-- (`fn_explode_bom_to_components`) in place via CREATE OR REPLACE — no
-- v2 suffix on the function itself, so callers don't change. The "v2"
-- suffix is only on the migration file for human readability.
--
-- Contract source:
--   PRODUCTION/docs/2026-05-02-two-head-bom-explosion-repair-plan.md §Tranche 3
--   CLAUDE.md §"Production reporting v1" (post-amendment)
--
-- Depends on:
--   0040 (planning_run_fg_coverage)
--   0041 (planning_run_component_demand + v1 function)
--   0003 (bom_head, bom_version, bom_lines)
--
-- Rollback: re-create the v1 body of the function from 0041 SQL.
-- ===========================================================================

begin;

set search_path to private_core, public;

create or replace function private_core.fn_explode_bom_to_components(
  p_run_id uuid
) returns integer
language plpgsql
security definer
as $$
declare
  v_rows_written       integer := 0;
  v_cov                record;
  v_item_supply        text;
  v_pack_head_id       text;
  v_base_head_id       text;
  v_pack_version_id    uuid;
  v_pack_output_qty    private_core.qty_8dp;
  v_base_version_id    uuid;
  v_base_output_qty    private_core.qty_8dp;
  v_make_qty           private_core.qty_8dp;
  v_pack_line          record;
  v_base_line          record;
  v_total_base_units   private_core.qty_8dp;
  v_component_qty      private_core.qty_8dp;
  v_already_flagged    boolean;
begin
  -- One coverage row at a time
  for v_cov in
    select c.item_id, c.period_bucket_key, c.projected_on_hand
    from private_core.planning_run_fg_coverage c
    where c.run_id = p_run_id
      and c.shortage_flag = true
    order by c.item_id, c.period_bucket_key
  loop
    select i.supply_method, i.primary_bom_head_id, i.base_bom_head_id
      into v_item_supply, v_pack_head_id, v_base_head_id
    from private_core.items i
    where i.item_id = v_cov.item_id;

    if v_item_supply not in ('MANUFACTURED','REPACK') then
      continue;
    end if;

    -- PACK head
    v_pack_version_id := null;
    v_pack_output_qty := null;
    if v_pack_head_id is not null then
      select bh.active_version_id, bh.final_bom_output_qty
        into v_pack_version_id, v_pack_output_qty
      from private_core.bom_head bh
      where bh.bom_head_id = v_pack_head_id;
    end if;

    if v_pack_version_id is null then
      select exists (
        select 1 from private_core.planning_run_exceptions e
        where e.run_id = p_run_id and e.category = 'missing_bom' and e.item_id = v_cov.item_id
      ) into v_already_flagged;
      if not v_already_flagged then
        insert into private_core.planning_run_exceptions
          (run_id, category, severity, item_id, detail)
        values
          (p_run_id, 'missing_bom', 'warning', v_cov.item_id,
           jsonb_build_object('reason','no_active_pack_version','phase','4B-v2'));
      end if;
      continue;
    end if;

    if v_pack_output_qty is null or v_pack_output_qty <= 0 then
      insert into private_core.planning_run_exceptions
        (run_id, category, severity, item_id, detail)
      values
        (p_run_id, 'missing_bom', 'warning', v_cov.item_id,
         jsonb_build_object('reason','pack_final_bom_output_qty_nonpositive','phase','4B-v2'));
      continue;
    end if;

    if v_cov.projected_on_hand >= 0 then continue; end if;
    v_make_qty := -v_cov.projected_on_hand;

    -- BASE head (optional)
    v_base_version_id := null;
    v_base_output_qty := null;
    if v_base_head_id is not null then
      select bh.active_version_id, bh.final_bom_output_qty
        into v_base_version_id, v_base_output_qty
      from private_core.bom_head bh
      where bh.bom_head_id = v_base_head_id;
      if v_base_version_id is null or v_base_output_qty is null or v_base_output_qty <= 0 then
        insert into private_core.planning_run_exceptions
          (run_id, category, severity, item_id, detail)
        values
          (p_run_id, 'missing_bom', 'warning', v_cov.item_id,
           jsonb_build_object('reason','no_active_base_version_or_invalid_output_qty','phase','4B-v2'));
        -- Continue WITHOUT base; pack-only explosion still produces useful demand.
        v_base_version_id := null;
      end if;
    end if;

    -- Walk PACK lines
    for v_pack_line in
      select bl.component_ref_type, bl.final_component_id, bl.final_component_qty
      from private_core.bom_lines bl
      where bl.bom_version_id = v_pack_version_id
        and bl.status in ('ACTIVE','PENDING')
        and bl.final_component_qty is not null
    loop
      if v_pack_line.component_ref_type in ('RAW_NAME','COMPONENT') and v_pack_line.final_component_id is not null then
        -- Pack leaf line — explode normally
        v_component_qty := v_make_qty * (v_pack_line.final_component_qty / v_pack_output_qty);
        insert into private_core.planning_run_component_demand
          (run_id, component_id, period_bucket_key, required_qty, sources)
        values
          (p_run_id, v_pack_line.final_component_id, v_cov.period_bucket_key,
           v_component_qty,
           jsonb_build_array(jsonb_build_object(
             'item_id', v_cov.item_id, 'qty', v_component_qty, 'source','pack',
             'bom_version_id', v_pack_version_id, 'bom_head_id', v_pack_head_id,
             'make_qty', v_make_qty,
             'final_component_qty', v_pack_line.final_component_qty,
             'bom_output_qty', v_pack_output_qty
           )))
        on conflict (run_id, component_id, period_bucket_key) do update
          set required_qty = private_core.planning_run_component_demand.required_qty + excluded.required_qty,
              sources = private_core.planning_run_component_demand.sources || (excluded.sources -> 0);
        v_rows_written := v_rows_written + 1;

      elsif v_pack_line.component_ref_type = 'BASE_BOM' and v_base_version_id is not null then
        -- Base reference — compute total base liters and walk BASE lines
        v_total_base_units := v_make_qty * (v_pack_line.final_component_qty / v_pack_output_qty);
        for v_base_line in
          select bl2.final_component_id, bl2.final_component_qty
          from private_core.bom_lines bl2
          where bl2.bom_version_id = v_base_version_id
            and bl2.final_component_id is not null
            and bl2.final_component_qty is not null
            and bl2.status in ('ACTIVE','PENDING')
        loop
          v_component_qty := v_base_line.final_component_qty * v_total_base_units / v_base_output_qty;
          insert into private_core.planning_run_component_demand
            (run_id, component_id, period_bucket_key, required_qty, sources)
          values
            (p_run_id, v_base_line.final_component_id, v_cov.period_bucket_key,
             v_component_qty,
             jsonb_build_array(jsonb_build_object(
               'item_id', v_cov.item_id, 'qty', v_component_qty, 'source','base',
               'bom_version_id', v_base_version_id, 'bom_head_id', v_base_head_id,
               'make_qty', v_make_qty, 'total_base_units', v_total_base_units,
               'final_component_qty', v_base_line.final_component_qty,
               'bom_output_qty', v_base_output_qty
             )))
          on conflict (run_id, component_id, period_bucket_key) do update
            set required_qty = private_core.planning_run_component_demand.required_qty + excluded.required_qty,
                sources = private_core.planning_run_component_demand.sources || (excluded.sources -> 0);
          v_rows_written := v_rows_written + 1;
        end loop;

      elsif v_pack_line.component_ref_type = 'BOM' then
        -- Sub-pack reference (out of v1 scope) — emit exception + skip
        insert into private_core.planning_run_exceptions
          (run_id, category, severity, item_id, detail)
        values
          (p_run_id, 'unsupported_bom_ref', 'warning', v_cov.item_id,
           jsonb_build_object('reason','component_ref_type_BOM_not_supported_in_v1','phase','4B-v2'));
      end if;
    end loop;
  end loop;

  return v_rows_written;
end
$$;

comment on function private_core.fn_explode_bom_to_components(uuid) is
  'Gate 5 Phase 4B v2 (two-head repair) — BOM explosion. Walks PACK head; for BASE_BOM lines, recursively walks the linked BASE head. Aggregates component demand across pack and base sources. Same signature as v1 (0041) so callers are unchanged. Plan 2026-05-02-two-head-bom-explosion-repair-plan.md §Tranche 3.';

commit;

-- ===========================================================================
-- End of 0126_fn_explode_bom_to_components_v2.sql
-- ===========================================================================
```

**Important compatibility note:** the existing `planning_run_component_demand.component_id` has a FK to `components`. The v1 function would have crashed if it ever saw a BASE_BOM line with a non-null `final_component_id` (because that would point to a bom_head, not a component). With the v2 logic, BASE_BOM lines NEVER write to `component_id` directly — they recurse to the BASE leaf lines, which DO point to real components. So no FK risk.

- [ ] **Step 2: Apply against live Supabase** (same `node -e` pattern as Tranche 1).

- [ ] **Step 3: Verify function body**

```bash
DATABASE_URL_POOLED="..." node -e "
  import('pg').then(({Client})=>{
    const c=new Client({connectionString:process.env.DATABASE_URL_POOLED,ssl:{rejectUnauthorized:false}});
    c.connect().then(()=>c.query(\`select pg_get_functiondef('private_core.fn_explode_bom_to_components(uuid)'::regprocedure)\`))
     .then(r=>console.log(r.rows[0].pg_get_functiondef.includes('BASE_BOM') ? 'OK two-head v2 deployed' : 'FAIL still v1')).finally(()=>c.end());
  });
"
```
Expected: `OK two-head v2 deployed`.

### Task 3.2: pgTAP

**Files:**
- Create: `gt-factory-os/db/tests/0126_fn_explode_bom_to_components_v2.test.sql`

- [ ] **Step 1: Write pgTAP**

```sql
-- pgTAP for 0126_fn_explode_bom_to_components_v2.sql
-- Strategy: build a synthetic planning run on a fixture item we know is two-head
-- (FG-DES-1L from Tranche 0 audit), call the function, then assert that the
-- resulting planning_run_component_demand contains BOTH pack and base components.

\unset ECHO
\set ON_ERROR_ROLLBACK 1
\set ON_ERROR_STOP true

begin;
  select plan(4);

  -- Fixture: insert a planning_run + planning_run_fg_coverage shortage row for FG-DES-1L
  -- (test data; rolled back at end-of-tx).

  insert into private_core.planning_runs (run_id, status, requested_at, created_at)
    values ('11111111-1111-1111-1111-111111111111'::uuid, 'running', now(), now());

  insert into private_core.planning_run_fg_coverage
    (run_id, item_id, period_bucket_key, projected_on_hand, shortage_flag)
    values ('11111111-1111-1111-1111-111111111111'::uuid,
            'FG-DES-1L', current_date, -100, true);

  -- Call the function
  select ok(
    private_core.fn_explode_bom_to_components('11111111-1111-1111-1111-111111111111'::uuid) > 0,
    'fn_explode_bom_to_components writes >0 rows for two-head item'
  );

  -- Assert there is at least one PACK-source component
  select ok(
    exists (
      select 1 from private_core.planning_run_component_demand prcd, jsonb_array_elements(prcd.sources) src
      where prcd.run_id = '11111111-1111-1111-1111-111111111111'::uuid
        and (src ->> 'source') = 'pack'
    ),
    'planning_run_component_demand has at least one pack-source row'
  );

  -- Assert there is at least one BASE-source component (THE BUG: v1 had zero)
  select ok(
    exists (
      select 1 from private_core.planning_run_component_demand prcd, jsonb_array_elements(prcd.sources) src
      where prcd.run_id = '11111111-1111-1111-1111-111111111111'::uuid
        and (src ->> 'source') = 'base'
    ),
    'planning_run_component_demand has at least one base-source row — THE BUG: was zero'
  );

  -- Assert no FK violations (component_id values resolve to real components)
  select ok(
    not exists (
      select 1 from private_core.planning_run_component_demand prcd
      left join private_core.components c on c.component_id = prcd.component_id
      where prcd.run_id = '11111111-1111-1111-1111-111111111111'::uuid
        and c.component_id is null
    ),
    'every planning_run_component_demand.component_id resolves to a real component'
  );

  select * from finish();
rollback;
```

- [ ] **Step 2: Run pgTAP**

`pg_prove ... -f db/tests/0126_fn_explode_bom_to_components_v2.test.sql` — expect 4/4 PASS.

- [ ] **Step 3: Commit + push**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os
git add db/migrations/0126_fn_explode_bom_to_components_v2.sql db/tests/0126_fn_explode_bom_to_components_v2.test.sql
git commit -m "planning: fn_explode_bom_to_components two-head walker (Tranche 3 two-head repair)"
git push origin main
```

### Task 3.3: Recompute affected planning runs

- [ ] **Step 1: Identify any in-flight planning runs and recommend recompute**

Per CURRENT_STATE.md (2026-05-02), the most recent completed planning run was 2026-04-21 — pre-launch test data. **No live runs need correction.** Just document that any future planning_run will use the v2 logic automatically.

- [ ] **Step 2: Append to evidence pack**

`PRODUCTION/docs/two_head_bom_repair_evidence.md` §4: confirm no live planning runs were affected, future runs will be correct.

---

## Tranche 4 — Portal preview rendering

### Task 4.1: Update portal contract mirror + page

**Files:**
- Modify: `window2-portal-sandbox/src/app/(ops)/stock/production-actual/page.tsx`

- [ ] **Step 1: Extend `BomLineSnapshot` and `ProductionActualOpenResponse` (lines 66-85)**

```typescript
interface BomLineSnapshot {
  line_id: string;
  component_id: string;
  component_name: string;
  final_component_qty: string;
  component_uom: string | null;
  source: 'pack' | 'base';        // NEW
}

interface ProductionActualOpenResponse {
  item_id: string;
  item_name: string;
  supply_method: 'MANUFACTURED' | 'REPACK';
  output_uom_default: string;
  bom_version_id_pinned: string;
  bom_head_id: string;
  bom_version_label: string;
  bom_final_output_qty: string;
  bom_final_output_uom: string;
  base_bom_version_id_pinned: string | null;     // NEW
  base_bom_head_id: string | null;               // NEW
  base_bom_version_label: string | null;         // NEW
  base_bom_final_output_qty: string | null;      // NEW
  base_bom_final_output_uom: string | null;      // NEW
  base_qty_per_pack_unit: string | null;         // NEW
  bom_lines: BomLineSnapshot[];
}
```

- [ ] **Step 2: Extend `ProductionActualSubmit` (lines 87-101)**

```typescript
interface ProductionActualSubmit {
  idempotency_key: string;
  event_at: string;
  item_id: string;
  bom_version_id_pinned: string;
  base_bom_version_id_pinned: string | null;     // NEW
  output_qty: number;
  scrap_qty: number;
  output_uom: string;
  notes: string | null;
  from_plan_id?: string | null;
}
```

- [ ] **Step 3: Pass `base_bom_version_id_pinned` through submit**

Find the `useMutation` that POSTs the submit body (search for `bom_version_id_pinned` in the file body) and add `base_bom_version_id_pinned: open.base_bom_version_id_pinned` alongside it.

- [ ] **Step 4: Update preview table rendering**

Find the preview component (search for "Preview — expected component consumption" / "Preview" / `bom_lines.map`). Add either:
- An en-dash badge per row: `<Badge variant={line.source==='pack' ? 'outline' : 'default'}>{line.source==='pack' ? 'אריזה' : 'נוזל'}</Badge>`, OR
- A grouped section: render PACK lines and BASE lines under separate sub-headings ("רכיבי אריזה" / "רכיבי נוזל").

Tom-locked Hebrew register:
- "רכיבי אריזה" — packaging components header
- "רכיבי נוזל" — liquid components header
- "אריזה" — pack badge
- "נוזל" — base badge

- [ ] **Step 5: Add a banner above the preview when `base_qty_per_pack_unit` is non-null**

```tsx
{open.base_bom_version_id_pinned && (
  <div className="text-sm text-muted-foreground">
    מוצר זה מורכב מאריזה ({open.bom_version_label}) ובסיס נוזל ({open.base_bom_version_label}).
    כל יחידה צורכת {open.base_qty_per_pack_unit} {open.base_bom_final_output_uom} בסיס.
  </div>
)}
```

### Task 4.2: Build verify + deploy

- [ ] **Step 1: Typecheck + build**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox
pnpm typecheck && pnpm build
```
Expected: both EXIT=0.

- [ ] **Step 2: Commit + push**

```bash
cd C:/Users/tomw2/Projects/window2-portal-sandbox
git add src/app/(ops)/stock/production-actual/page.tsx
git commit -m "portal: render two-head BOM preview in production-actual (Tranche 4 two-head repair)"
git push origin main
```

- [ ] **Step 3: Wait for Vercel deploy + smoke**

```bash
# In a browser: hard-refresh https://gt-factory-os-portal.vercel.app/ops/stock/production-actual
# Pick FG-DES-1L; expect to see BOTH packaging components AND liquid components
# in the preview table, with the new banner explaining the two-head composition.
```

---

## Tranche 5 — Contract amendment + governance docs

### Task 5.1: Amend CLAUDE.md §"Production reporting v1"

**Files:**
- Modify: `c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION/CLAUDE.md`

- [ ] **Step 1: Replace §"Production reporting v1"**

Find the section currently reading:
```
### Production reporting v1
- Operator reports output quantity + scrap quantity + notes
- System computes standard consumption from BOM
- Do **not** collect manual per-component actual consumption in v1
```

Replace with:
```
### Production reporting v1
- Operator reports output quantity + scrap quantity + notes
- System computes standard consumption from the **two-head BOM**:
  - **PACK head** (`items.primary_bom_head_id` → `bom_kind='PACK'` or `'REPACK'`): packaging components consumed proportionally to (output + scrap).
  - **BASE head** (`items.base_bom_head_id` → `bom_kind='BASE'`, when present): liquid raw-material components consumed proportionally to total base liters required, derived from the PACK BOM's `BASE_BOM` line.
  - REPACK and pure-pack items have no BASE head — single-head explosion applies.
- Both BOM versions (PACK and BASE-when-applicable) are **pinned at form-open time** and **rejected on stale submission** (409 `STALE_BOM_VERSION` / `STALE_BASE_BOM_VERSION`).
- All consumption rows for a single submission are written to `stock_ledger` inside one transaction with the form's `idempotency_key`. Per-row idempotency keys carry the source (`pack` / `base`) and `component_id` so pack and base never collide.
- Do **not** collect manual per-component actual consumption in v1.
```

### Task 5.2: Update CURRENT_STATE.md

**Files:**
- Modify: `c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION/CURRENT_STATE.md`

- [ ] **Step 1: Add a tranche-completion entry under "Active corridor"**

After cycle 8 entry, add:

```
- **Two-head BOM repair (2026-05-02 → 2026-05-XX)**: pre-launch correction landed across Tranches 0–6.
  - Tranche 0 audit baseline: docs/two_head_bom_audit_<ts>.md
  - Tranche 1 schema migration 0125_production_actual_base_bom_pinning.sql — applied + pgTAP 5/5
  - Tranche 2 PA handler — node:test TWO_HEAD_OK_OPEN/SUBMIT/STALE_BASE PASS; Railway deploy <id>; live smoke confirmed pack + base lines on FG-DES-1L
  - Tranche 3 migration 0126_fn_explode_bom_to_components_v2.sql — applied + pgTAP 4/4; v2 function body verified live
  - Tranche 4 portal — Mode B exit at portal main <commit>; Vercel deploy <id>
  - Tranche 5 contract amended — CLAUDE.md §"Production reporting v1" v2 (two-head explosion explicit)
  - Tranche 6 verifier — PASS (parity + idempotency + stale-base + repack-no-base + smoke)
  - Net effect: every MANUFACTURED item with a base_bom_head_id now consumes BOTH pack and base components atomically. Planning runs use two-head explosion automatically.
- **Planning Corridor v1 — RESUMES** after Tranche 6 closes. Cycle 8 uncommitted W1/W2 deltas resume per CURRENT_STATE.md §"Cycle 8 partial state".
```

- [ ] **Step 2: Increment RUNTIME_READY signal counter**

`RUNTIME_READY(ProductionActual-TwoHead)` — emit signal, append to `.claude/state/runtime_ready.json`. Bump count in CURRENT_STATE.md from 26 → 27.

### Task 5.3: Author final evidence pack

**Files:**
- Create: `c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION/docs/two_head_bom_repair_evidence.md`

- [ ] **Step 1: Compile sections**

```
# Two-Head BOM Repair — Evidence Pack
1. Pre-fix audit (Tranche 0 markdown + JSON paths)
2. Tom-locked decisions on anomalies (from §Task 0.2)
3. Tranche 1 — schema migration applied (timestamp + pg_index check)
4. Tranche 2 — handler change committed/deployed (commit hash + Railway deploy ID + smoke jq output)
5. Tranche 3 — planning function v2 deployed (function body grep + pgTAP output)
6. Tranche 4 — portal change deployed (commit + Vercel deploy ID + browser screenshot reference)
7. Tranche 5 — contract amendment diff
8. Tranche 6 — verifier verdict
9. Post-fix audit (Tranche 6 second run; ALL anomaly buckets must be 0 OR explicitly accepted in §2)
```

- [ ] **Step 2: Commit governance docs (PRODUCTION repo)**

```bash
cd "c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION"
git add CLAUDE.md CURRENT_STATE.md docs/two_head_bom_repair_evidence.md
git commit -m "governance: two-head BOM repair Tranches 5 wrap-up (CLAUDE.md §Production reporting v1 v2 + CURRENT_STATE + evidence pack)"
git push origin main
```

(If PRODUCTION/ is not a git repo, copy the diff into the dropbox-tracked file directly per existing convention; no push needed.)

---

## Tranche 6 — End-to-end verification

### Task 6.1: Re-run audit script (post-fix)

- [ ] **Step 1: Re-run Tranche 0 audit script**

```bash
cd C:/Users/tomw2/Projects/gt-factory-os
npx tsx scripts/audit_two_head_bom.ts > docs/two_head_bom_audit_post_fix_$(date -Iseconds).json
```
Expected: every anomaly bucket is 0 OR matches §2 of the evidence pack (Tom-accepted exceptions).

### Task 6.2: Live HTTP smoke matrix

- [ ] **Step 1: Smoke 5 representative items**

For each item below, run the open + submit sequence (with tiny output_qty so any consumption is operationally negligible — pre-launch context):
- `FG-DES-1L` (DESERTEA — has BASE)
- One other MANUFACTURED + BASE item (pick from `ok_two_head` audit bucket)
- One REPACK item (pick from `ok_pack_only`)
- One BOUGHT_FINISHED item (expect 409 WRONG_SUPPLY_METHOD — regression check)
- One MANUFACTURED item without BASE (if any in audit; expect base_bom_version_id_pinned=null)

Capture each (open response summary + submit committed response) into `PRODUCTION/docs/two_head_bom_repair_evidence.md` §6.2.

### Task 6.3: rebuild_verifier check

- [ ] **Step 1: Run `rebuild_verifier()` after the smoke matrix**

```bash
DATABASE_URL_POOLED="..." node -e "
  import('pg').then(({Client})=>{
    const c=new Client({connectionString:process.env.DATABASE_URL_POOLED,ssl:{rejectUnauthorized:false}});
    c.connect().then(()=>c.query('select private_core.rebuild_verifier()'))
     .then(r=>console.log('rebuild_verifier:', r.rows[0])).finally(()=>c.end());
  });
"
```
Expected: `0` (no parity drift). Log result into evidence pack §6.3.

### Task 6.4: Verifier dispatch

- [ ] **Step 1: Dispatch the `verifier` agent**

Brief: "Verify the two-head BOM repair end-to-end against `PRODUCTION/docs/2026-05-02-two-head-bom-explosion-repair-plan.md`. Confirm Tranches 0–5 evidence is present in `PRODUCTION/docs/two_head_bom_repair_evidence.md`, `rebuild_verifier()=0`, post-fix audit shows all anomaly buckets at 0 (or matching Tom-accepted exceptions), and live HTTP smoke confirms `base_bom_version_id_pinned` non-null + `bom_lines` includes `source='base'` rows for FG-DES-1L. Return PASS or FAIL with line-level evidence."

- [ ] **Step 2: On PASS — Tom acceptance**

Surface verifier verdict + final evidence pack to Tom. **STOP-GATE for Tom acceptance** before declaring CLOSED.

- [ ] **Step 3: On FAIL — diagnose + fix in a follow-up tranche; do not declare CLOSED**

---

## Open questions and risks

1. **`final_component_id` content for `BASE_BOM` lines** — fixture suggests it equals the BASE bom_head_id (e.g. `'BOM-BASE-DES-REG'`), which would violate the FK on `bom_lines.final_component_id → components(component_id)`. Tranche 0 audit verifies the live state. If the FK is in fact bypassed (the fixture loaded before the FK landed, or via a path that disabled it), the v2 handler must IGNORE `final_component_id` on BASE_BOM lines and resolve the BASE head exclusively from `items.base_bom_head_id`. The plan's `loadTwoHeadBomContext` already does this — it does not read `final_component_id` for BASE_BOM lines.

2. **Multiple BASE_BOM lines per PACK** — model says one. Audit will reveal. Handler returns 409 `MULTIPLE_BASE_BOM_LINES` if encountered (Tranche 2 Task 2.3 §3).

3. **REPACK items with `base_bom_head_id`** — the plan's design treats this the same as MANUFACTURED + BASE (both heads exploded). If the audit shows REPACK items whose `base_bom_head_id` is set but represents repack-source rather than liquid base, Tom must decide whether to (a) include or (b) skip BASE explosion for REPACK. Default in this plan: **include** (consistent semantics).

4. **Idempotency key collision risk** — the original handler used `PA:${idem}:CONSUME:${component_id}` per row. The new handler uses `PA:${idem}:CONSUME:${source}:${component_id}` to avoid collisions when the same component_id appears in both pack and base lines (rare but possible). This is a **break in idempotency-key shape** for production_consumption rows. Pre-launch context = no rollback risk. Post-launch this would need a retro-mapping migration.

5. **Cost rollup (Phase 10)** — out of scope for this repair. Phase 10 was already deferred per CURRENT_STATE.md §Gate 5 closure. When it lands, it must use the same two-head explosion semantics for unit cost.

---

## Done = all of the following

- [ ] Tranches 0–5 committed + pushed
- [ ] Verifier PASS on Tranche 6
- [ ] `PRODUCTION/docs/two_head_bom_repair_evidence.md` complete and Tom-acknowledged
- [ ] `RUNTIME_READY(ProductionActual-TwoHead)` signal #27 emitted
- [ ] CURRENT_STATE.md updated; Planning Corridor v1 marked RESUMES
- [ ] CLAUDE.md §"Production reporting v1" amended to v2 (two-head explosion explicit)
- [ ] Live screenshot of `/ops/stock/production-actual` for FG-DES-1L showing PACK + BASE lines in preview, sent to Tom for visual confirmation
