# Recipe Master-Data Import — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking. Map the work to GT Factory OS executor windows: Chunks 1–4 = W1 (DB / migrations / fixtures); Chunk 5 = W2 (portal smoke). Verifier runs after each chunk; Governor decides chunk-to-chunk advance.

**Goal:** Atomically import the corrected fixture JSONs into Supabase such that (a) the 4 new MUZA cocktail BOMs become live and simulatable, (b) Sangria W Elita and 5 other Excel-confirmed recipe corrections take effect, (c) component master is cleaned of duplicates, (d) all 47 manufactured items round-trip through the simulator with correct material requirements, and (e) the system has zero internal contradictions across master / BOMs / simulator / planning paths.

**Architecture:** Idempotent UPSERT via the existing `scripts/import_masters.ts` (which has 9 pre-flight checks and atomic transaction). The schema and simulator already support the canonical-ratio model — DB trigger `0077_bom_lines_qty_per_unit_trigger` auto-computes `qty_per_l_output` on every write, and the `/api/v1/queries/boms/heads/:id/simulate` endpoint already prefers `qty_per_l_output` with fallback to inline division. **No application code change is required.** The work is entirely data import + verification + cross-cutting consistency gates.

**Tech Stack:** PostgreSQL 16 (Supabase managed), Node 20 + tsx, `pg` driver, pgTAP, Next.js 15 portal, Fastify API. All dependencies already pinned in `gt-factory-os/package.json` and `window2-portal-sandbox/package.json`.

**Spec / source artifacts:**
- Fixture JSONs (modified): `gt-factory-os/fixtures/masters/{components,supplier_items,bom_head,bom_version,bom_lines,items}.json`
- Final verification: `gt-factory-os/scripts/_final_verify_all.py` — **48/48 PASS as of 2026-04-27**
- Audit history: `docs/recipe-audit-2026-04-27.md`, `docs/recipe-reconciliation-v2-2026-04-27.md`, `docs/recipe-closure-status-2026-04-27.md`
- Trigger 0077: `gt-factory-os/db/migrations/0077_bom_lines_qty_per_unit_trigger.sql` (auto-computes `qty_per_l_output = final_component_qty / final_bom_output_qty` on insert/update)
- Simulator endpoint: `gt-factory-os/api/src/boms/simulate.ts` (already reads `qty_per_l_output`)

**Rollback envelope:** every chunk has an explicit revert procedure. Until Chunk 5 succeeds, the production database is untouched. At any point before Chunk 5 the engineer can `git restore fixtures/masters/` and the work disappears.

---

## Pre-conditions (verify before starting)

- [ ] **Pre-1:** Final verification still passes
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  python scripts/_final_verify_all.py
  ```
  Expected last line: `=== Summary: 48 PASS, 0 FAIL (48 total) ===`
  If any FAIL appears, STOP. Re-run the audit + reconciliation pipeline before proceeding.

- [ ] **Pre-2:** Working directory is clean except for the intended fixture changes
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  git status --short
  ```
  Expected: only files under `fixtures/masters/` and new files under `scripts/_*.py` should be modified/new. Anything else (random `package.json` edits, log files, etc.) means an unintended change has crept in. Investigate before proceeding.

- [ ] **Pre-3:** `.env` has `DATABASE_URL` pointing to **local dev DB** (not prod)
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  grep -E '^DATABASE_URL=' .env
  ```
  Expected: starts with `postgresql://postgres@127.0.0.1:54322/` or `postgresql://postgres@localhost:54322/`. If it points at `*.supabase.co`, **stop** — the engineer must set up a separate `.env.production` and switch deliberately at Chunk 4.

---

## Chunk 1: Pre-flight & dry-run validation

**Purpose:** Prove that the data is internally consistent and that `import_masters --dry-run` accepts every row, before touching any database.

### Task 1: Re-verify the JSON fixtures one more time

**Files:**
- Read: `gt-factory-os/scripts/_final_verify_all.py`
- Run only — no edits

- [ ] **Step 1: Run the verifier**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  python scripts/_final_verify_all.py 2>&1 | tail -3
  ```
  Expected: `=== Summary: 48 PASS, 0 FAIL (48 total) ===` and `ALL CHECKS PASSED.`

- [ ] **Step 2: Capture the pre-import row counts (write down or paste into notes)**
  ```bash
  python -c "
  import json
  for f in ['components','supplier_items','bom_head','bom_version','bom_lines','items']:
      d = json.load(open(f'fixtures/masters/{f}.json', encoding='utf-8'))
      print(f'{f}: {len(d[\"rows\"])} rows')
  "
  ```
  Expected:
  ```
  components: 151 rows
  supplier_items: 191 rows
  bom_head: 76 rows
  bom_version: 76 rows
  bom_lines: 468 rows
  items: 50 rows
  ```

### Task 2: import_masters dry-run

**Files:**
- Read: `gt-factory-os/scripts/import_masters.ts` (just the pre-flight section, lines 1–50)
- Run only — no edits

- [ ] **Step 1: Verify the script can be invoked**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  tsx scripts/import_masters.ts --dry-run 2>&1 | tee /tmp/import_dry_run.log | tail -30
  ```
  Expected behavior: the script runs through pre-flight checks P1–P9 and either:
  - prints `[DRY-RUN] No writes performed.` with `pre-flight: 0 failures` → **OK**
  - prints `[DRY-RUN] FAILED — fix issues before re-running.` → **STOP**, surface the failures

- [ ] **Step 2: Inspect the dry-run output for warnings**
  ```bash
  grep -E 'WARN|FAIL|missing|unresolved' /tmp/import_dry_run.log || echo "no warnings"
  ```
  Expected: `no warnings`. If any line appears, read it carefully. Common false positives: orphaned PKG-LABEL-MUZ-PSC-200ML (fine — PSC item exists but its BOM is intentionally absent, per Tom).

### Task 3: Snapshot baseline simulator output (so we can prove it changed after import)

**Files:**
- Run only

- [ ] **Step 1: Snapshot a "before" curl on the local dev API for White Sangria 3.85L**
  ```bash
  curl -s "http://localhost:3001/api/v1/queries/boms/heads/BOM-BASE-SAN-WHI-ELI-REG/simulate?qty=1" \
    | python -m json.tool > /tmp/before_san_whi_eli.json
  cat /tmp/before_san_whi_eli.json | head -40
  ```
  Expected: a JSON block with `lines[]` showing the OLD ratios. Specifically `RAW-WINE-WHITE` line should show `unit_ratio` ≈ `0.6808510...` (192/282) and `required_qty` ≈ `0.6808510` for qty=1. **If the API server is not running, start it now**: `cd gt-factory-os/api && npm run dev`. If the server returns 404 because the BOM head doesn't exist yet (fresh DB), skip this step and note "no baseline".

- [ ] **Step 2: Commit the baseline snapshot for posterity**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  git add /tmp/before_san_whi_eli.json 2>/dev/null || true
  # We don't actually commit /tmp; just ensure we have it on disk for later diff.
  ls -la /tmp/before_san_whi_eli.json
  ```

### Task 4: Commit the fixture changes (still local, not pushed)

**Files:**
- Modified: `gt-factory-os/fixtures/masters/components.json`, `supplier_items.json`, `bom_head.json`, `bom_version.json`, `bom_lines.json`, `items.json`
- New: `gt-factory-os/scripts/_add_muza_components.py`, `_build_muza_boms.py`, `_apply_excel_corrections.py`, `_cleanup_components_master.py`, `_deep_verification.py`, `_dump_cost_of_prod.py`, `_extract_excel_recipes.py`, `_final_verify_all.py`, `_reconcile_recipes.py`, `_reconcile_recipes_v2.py`, `_audit_recipes.mjs`
- New (artifacts): `gt-factory-os/fixtures/cost_of_production_aug2025_dump.json`, `cost_of_production_aug2025_recipes.json`, `recipe_audit_report.json`, `recipe_reconciliation_report.json`, `recipe_reconciliation_v2.json`

- [ ] **Step 1: Stage the changes**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  git add fixtures/masters/*.json
  git add fixtures/recipe_*.json fixtures/cost_of_production_aug2025_*.json
  git add scripts/_add_muza_components.py scripts/_build_muza_boms.py scripts/_apply_excel_corrections.py scripts/_cleanup_components_master.py scripts/_deep_verification.py scripts/_dump_cost_of_prod.py scripts/_extract_excel_recipes.py scripts/_final_verify_all.py scripts/_reconcile_recipes.py scripts/_reconcile_recipes_v2.py scripts/_audit_recipes.mjs
  ```

- [ ] **Step 2: Verify staged set**
  ```bash
  git diff --cached --stat | tail -20
  ```
  Expected: 6 master JSONs + 5 fixture artifacts + 11 scripts. Total ~17 files. No `.env`, no `node_modules`, no stray binary.

- [ ] **Step 3: Commit with a structured message**
  ```bash
  git commit -m "$(cat <<'EOF'
data: recipe master closure — MUZA + Excel corrections + cleanup

- Add 6 raw components for MUZA cocktails (D&D + Kill Bill suppliers)
- Build 4 MUZA BASE+PACK BOMs (HER, JAS, NEG, QUE) with per-L ratios
- Wire 4 MUZA items to PACK/BASE BOM ids and set BASE_FILL_QTY_PER_UNIT=0.2L
- Sangria W Elita: replace recipe with Excel ground truth (Calm 0.150/L,
  Elderflower 0.060/L, Wine 0.730/L, etc.)
- Apply Excel ratios on Energy lemongrass, Calm/CAL-NS lemon acid,
  Namastea cloves+puer, American sugar, Desert sugar
- Set Margarita BASE_FILL_QTY_PER_UNIT=0.3L on 3 items
- Standardize YUZU-PUREE to KG (master + 3 Margarita BOM lines)
- Retire 4 duplicate components (COLVE, CORNATION, LIME-PURE, BERGAMOT-PURE) → INACTIVE
- Backfill qty_per_l_output on 191 BASE BOM lines (canonical ratio model)

Verification: scripts/_final_verify_all.py = 48/48 PASS.
Known residual gaps documented in docs/recipe-closure-status-2026-04-27.md
(DETOX-NS, Passion Spritz, Cosmo Lychee — all pending Andrey/Tom).
EOF
)"
  ```

- [ ] **Step 4: Confirm commit landed**
  ```bash
  git log --oneline -1
  git rev-parse HEAD > /tmp/import_commit_sha.txt
  cat /tmp/import_commit_sha.txt
  ```
  Capture the SHA for rollback reference.

**Chunk 1 exit gate:** dry-run clean, fixtures committed locally, baseline snapshot taken (or noted as N/A). **Pause here for governor approval before Chunk 2.**

**Rollback for Chunk 1:** `git reset --hard HEAD~1` removes the commit; nothing else changed.

---

## Chunk 2: Local dev DB import + invariant gates

**Purpose:** Run the import against the local dev database, prove every invariant the system depends on, and prove that the simulator returns the expected new ratios before touching production.

### Task 5: Confirm local DB is at expected migration state

**Files:**
- Run only

- [ ] **Step 1: Connect and check applied migrations**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  PSQL=$HOME/pg-local/root/usr/lib/postgresql/16/bin/psql
  URL="postgresql://postgres@127.0.0.1:54322/gtfo"
  "$PSQL" "$URL" -c "SELECT name FROM private_core.migrations ORDER BY applied_at DESC LIMIT 10;"
  ```
  Expected: most-recent migration is at or after `0077_bom_lines_qty_per_unit_trigger`. Migrations after 0077 are fine. If 0077 is **not** applied, run `bash scripts/_pg_apply_migrations.sh` first and re-check.

- [ ] **Step 2: Verify the trigger exists and is enabled**
  ```bash
  "$PSQL" "$URL" -c "
    SELECT tgname, tgenabled
    FROM pg_trigger
    WHERE tgrelid = 'private_core.bom_lines'::regclass
      AND tgname = 'bom_line_compute_unit_ratio_trg';
  "
  ```
  Expected: one row with `tgenabled = 'O'` (origin, enabled). If missing, the migration didn't apply correctly — investigate before proceeding.

- [ ] **Step 3: Capture pre-import DB row counts**
  ```bash
  "$PSQL" "$URL" -c "
    SELECT 'components' AS t, COUNT(*) FROM private_core.components UNION ALL
    SELECT 'supplier_items', COUNT(*) FROM private_core.supplier_items UNION ALL
    SELECT 'bom_head', COUNT(*) FROM private_core.bom_head UNION ALL
    SELECT 'bom_version', COUNT(*) FROM private_core.bom_version UNION ALL
    SELECT 'bom_lines', COUNT(*) FROM private_core.bom_lines UNION ALL
    SELECT 'items', COUNT(*) FROM private_core.items;
  " | tee /tmp/before_db_counts.txt
  ```
  Save this output — we will diff against post-import.

### Task 6: Run import_masters against local DB

**Files:**
- Run only — `scripts/import_masters.ts`

- [ ] **Step 1: Execute the real import (not dry-run)**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  tsx scripts/import_masters.ts 2>&1 | tee /tmp/import_run.log
  ```
  Expected last lines:
  ```
  ✓ items: <N> upserted
  ✓ suppliers: <M> upserted
  ✓ components: 151 upserted (4 status=INACTIVE)
  ✓ planning_policy: <K> upserted
  ✓ supplier_items: 191 upserted
  ✓ bom_head: 76 upserted
  ✓ bom_version: 76 upserted
  ✓ bom_lines: 468 upserted
  COMMIT
  ```
  If the script aborts with `ROLLBACK` or any FK violation, **stop**. The atomic transaction means nothing was written. Read the error, fix the data, re-run.

- [ ] **Step 2: Verify post-import DB row counts**
  ```bash
  "$PSQL" "$URL" -c "
    SELECT 'components' AS t, COUNT(*) FROM private_core.components UNION ALL
    SELECT 'supplier_items', COUNT(*) FROM private_core.supplier_items UNION ALL
    SELECT 'bom_head', COUNT(*) FROM private_core.bom_head UNION ALL
    SELECT 'bom_version', COUNT(*) FROM private_core.bom_version UNION ALL
    SELECT 'bom_lines', COUNT(*) FROM private_core.bom_lines UNION ALL
    SELECT 'items', COUNT(*) FROM private_core.items;
  "
  ```
  Expected post counts: components 151, supplier_items 191, bom_head 76, bom_version 76, bom_lines 468, items 50. **All counts must match the JSON fixture counts from Chunk 1, Task 1, Step 2.**

### Task 7: Cross-cutting invariant gate (this is where horizontal consistency is enforced)

**Files:**
- Run only — invariant SQL queries

- [ ] **Step 1: Invariant I1 — every active BASE BOM line has qty_per_l_output populated and consistent with qty/declared**
  ```bash
  "$PSQL" "$URL" -c "
    SELECT bl.bom_head_id, bl.line_no, bl.final_component_qty,
           bh.final_bom_output_qty,
           bl.qty_per_l_output,
           ROUND(bl.qty_per_l_output - (bl.final_component_qty / bh.final_bom_output_qty), 8) AS drift
    FROM private_core.bom_lines bl
    JOIN private_core.bom_head bh ON bh.bom_head_id = bl.bom_head_id
    WHERE bl.status = 'ACTIVE'
      AND bl.bom_kind = 'BASE'
      AND bh.final_bom_output_uom = 'L'
      AND bh.final_bom_output_qty > 0
      AND (bl.qty_per_l_output IS NULL
           OR ABS(bl.qty_per_l_output - (bl.final_component_qty / bh.final_bom_output_qty)) > 1e-6)
    LIMIT 10;
  "
  ```
  Expected: **0 rows**. Any row means trigger 0077 failed to populate or the data was inserted with a stale ratio. If non-zero, investigate before continuing.

- [ ] **Step 2: Invariant I2 — every PACK BOM has exactly one base-mix line that resolves to a known BASE head**
  ```bash
  "$PSQL" "$URL" -c "
    SELECT ph.bom_head_id AS pack_id,
           COUNT(*) FILTER (WHERE pl.component_ref_type IN ('BOM','BASE_BOM')) AS base_mix_lines
    FROM private_core.bom_head ph
    LEFT JOIN private_core.bom_lines pl
      ON pl.bom_head_id = ph.bom_head_id AND pl.status = 'ACTIVE'
    WHERE ph.bom_kind = 'PACK'
      AND ph.linked_base_bom_head_id IS NOT NULL
    GROUP BY ph.bom_head_id
    HAVING COUNT(*) FILTER (WHERE pl.component_ref_type IN ('BOM','BASE_BOM')) <> 1;
  "
  ```
  Expected: **0 rows**. Any row means a PACK BOM that links a BASE has zero or multiple base-mix lines — operator confusion guaranteed.

- [ ] **Step 3: Invariant I3 — every active manufactured item with linked PACK has a BASE_FILL_QTY_PER_UNIT, OR its PACK BOM resolves base liquid via the linked BASE head**
  ```bash
  "$PSQL" "$URL" -c "
    SELECT i.item_id, i.item_name, i.base_fill_qty_per_unit,
           i.primary_bom_head_id, ph.linked_base_bom_head_id
    FROM private_core.items i
    LEFT JOIN private_core.bom_head ph ON ph.bom_head_id = i.primary_bom_head_id
    WHERE i.status = 'ACTIVE'
      AND i.supply_method IN ('MANUFACTURED','REPACK')
      AND i.primary_bom_head_id IS NOT NULL
      AND i.base_fill_qty_per_unit IS NULL
      AND ph.linked_base_bom_head_id IS NOT NULL
    LIMIT 20;
  "
  ```
  Expected: **0 rows**. With the Margarita fixes (BASE_FILL_QTY_PER_UNIT='0.3L') and MUZA wiring (BASE_FILL='0.2L'), every active manufactured item with a BASE BOM should have a fill explicitly set.

- [ ] **Step 4: Invariant I4 — supplier_items has at least one IS_PRIMARY=YES per active component (otherwise GR cannot resolve a PO)**
  ```bash
  "$PSQL" "$URL" -c "
    SELECT c.component_id, c.component_name
    FROM private_core.components c
    WHERE c.status = 'ACTIVE'
      AND c.component_class = 'INGREDIENT'
      AND NOT EXISTS (
        SELECT 1 FROM private_core.supplier_items si
        WHERE si.component_id = c.component_id
          AND si.is_primary IS TRUE
      )
    LIMIT 20;
  "
  ```
  Expected: **0 rows** (or only known-NEW pseudo-rows you intentionally leave with no primary). If the 6 new MUZA components show up, the import script didn't pick up the `supplier_items.json` additions — investigate.

- [ ] **Step 5: Invariant I5 — no active BOM line references an INACTIVE component**
  ```bash
  "$PSQL" "$URL" -c "
    SELECT bl.bom_head_id, bl.line_no, bl.final_component_id, c.status
    FROM private_core.bom_lines bl
    JOIN private_core.components c ON c.component_id = bl.final_component_id
    WHERE bl.status = 'ACTIVE'
      AND c.status <> 'ACTIVE'
    LIMIT 10;
  "
  ```
  Expected: **0 rows**. If any of the retired duplicates (COLVE, CORNATION, LIME-PURE, BERGAMOT-PURE) are still referenced by an active BOM line, the cleanup missed something — fix the BOM line to reference the canonical id.

### Task 8: Run pgTAP tests for BOMs

**Files:**
- Run only — `gt-factory-os/db/tests/`

- [ ] **Step 1: List the relevant test files**
  ```bash
  ls C:/Users/tomw2/Projects/gt-factory-os/db/tests/ | grep -iE 'bom|simulate|fixture|master' | head -10
  ```

- [ ] **Step 2: Run the BOM-relevant pgTAP tests**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  bash scripts/_run_pgtap_gr.sh 2>&1 | tail -30
  # Or if there's a dedicated bom test runner:
  ls scripts/ | grep pgtap
  ```
  Expected: all tests `ok`. If any fails, the test will print a clear `not ok N - <description>` line with file:line — fix the data or the test before proceeding.

- [ ] **Step 3: Spot-check Sangria W Elita ratios in DB**
  ```bash
  "$PSQL" "$URL" -c "
    SELECT bl.line_no, bl.final_component_id,
           bl.final_component_qty, bl.component_uom,
           bl.qty_per_l_output
    FROM private_core.bom_lines bl
    WHERE bl.bom_head_id = 'BOM-BASE-SAN-WHI-ELI-REG'
      AND bl.status = 'ACTIVE'
    ORDER BY bl.line_no;
  "
  ```
  Expected (Tom-confirmed Excel ratios):
  ```
   line_no | component_id            | qty    | uom |  qty_per_l_output
       1   | BOM-BASE-CAL-REG        |  42.30 | L   | 0.150000
       2   | RAW-WINE-WHITE          | 205.86 | L   | 0.730000
       3   | RAW-LEMON-ACID          |  0.282 | KG  | 0.001000
       4   | RAW-PRESERVATIVE        |  0.40  | L   | 0.001418
       5   | RAW-ELDERFLOWER-SYRUP   |  16.92 | L   | 0.060000
       6   | RAW-VODKA               |  8.46  | L   | 0.030000
       7   | RAW-MARTINI-BIANCO      |  8.46  | L   | 0.030000
  ```
  (line numbers may differ; the values must match within rounding.)

**Chunk 2 exit gate:** all 5 invariants return 0 rows; pgTAP suite green; Sangria W Elita ratios visible in DB. **Pause here.**

**Rollback for Chunk 2:** because import_masters is idempotent UPSERT, there's no clean "undo" within the DB. Roll back by either:
- restoring a pre-import DB snapshot (if you took one with `pg_dump`), OR
- re-running import_masters with the previous fixtures (`git stash` the corrections, `tsx scripts/import_masters.ts` again).

---

## Chunk 3: API + portal smoke (local)

**Purpose:** Prove that the simulator endpoint returns the new ratios end-to-end through the HTTP API and that the portal renders them correctly. This is the "operator can see the truth" gate.

### Task 9: Restart the API server and curl the simulator

**Files:**
- Run only — `gt-factory-os/api/`

- [ ] **Step 1: Start (or restart) the local API**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os/api
  # If already running, kill it. Then:
  npm run dev > /tmp/api.log 2>&1 &
  sleep 5
  curl -s http://localhost:3001/health || echo "API not up"
  ```
  Expected: a JSON `{ok: true, ...}` health response. If the API is on a different port, adjust `3001` to match `.env` `PORT`.

- [ ] **Step 2: Curl the new simulator output for White Sangria 3.85L (1 unit)**
  ```bash
  curl -s "http://localhost:3001/api/v1/queries/boms/heads/BOM-PACK-SAN-WHI-3850ML/simulate?qty=1" \
    | python -m json.tool > /tmp/after_san_whi_pack.json
  cat /tmp/after_san_whi_pack.json | python -c "
  import json, sys
  d = json.load(sys.stdin)
  for ln in d['lines']:
      print(f'  {ln[\"component_id\"]:30s} required={ln[\"required_qty\"]} {ln[\"component_uom\"]}  ratio={ln[\"unit_ratio\"]}')
  "
  ```
  Expected output **for the BASE-mix line** (resolved through the PACK):
  ```
    BOM-BASE-SAN-WHI-ELI-REG       required=3.85 L  ratio=3.85
    PKG-JERRICAN-3.85L              required=1 UNIT  ratio=1
    PKG-LABEL-SAN-WHI-3850ML        required=1 UNIT  ratio=1
    PKG-CARTON-3850ML               required=1 UNIT  ratio=1
  ```

- [ ] **Step 3: Curl the BASE recipe for the same product to verify per-L ratios**
  ```bash
  curl -s "http://localhost:3001/api/v1/queries/boms/heads/BOM-BASE-SAN-WHI-ELI-REG/simulate?qty=3.85" \
    | python -c "
  import json, sys
  d = json.load(sys.stdin)
  for ln in d['lines']:
      print(f'  {ln[\"component_id\"]:30s} required={ln[\"required_qty\"]} {ln[\"component_uom\"]}')
  "
  ```
  Expected (3.85 L of base):
  ```
    BOM-BASE-CAL-REG               required=0.5775 L
    RAW-WINE-WHITE                 required=2.8105 L     ← key number — was 2.62 before
    RAW-LEMON-ACID                 required=0.00385 KG
    RAW-PRESERVATIVE               required=0.0054593 L
    RAW-ELDERFLOWER-SYRUP          required=0.231 L
    RAW-VODKA                      required=0.1155 L
    RAW-MARTINI-BIANCO             required=0.1155 L
  ```
  **Wine 2.81 L is the proof point** — the user-reported "wrong liter quantity" is now correct.

- [ ] **Step 4: Curl a MUZA cocktail to prove the new BOMs are wired**
  ```bash
  curl -s "http://localhost:3001/api/v1/queries/boms/heads/BOM-PACK-MUZ-NEG-200ML/simulate?qty=10" \
    | python -c "
  import json, sys
  d = json.load(sys.stdin)
  print('PACK lines for 10 bottles of Negroni:')
  for ln in d['lines']:
      print(f'  {ln[\"component_id\"]:30s} required={ln[\"required_qty\"]} {ln[\"component_uom\"]}')
  "
  curl -s "http://localhost:3001/api/v1/queries/boms/heads/BOM-BASE-MUZ-NEG/simulate?qty=2" \
    | python -c "
  import json, sys
  d = json.load(sys.stdin)
  print('BASE lines for 2 L of Negroni base mix:')
  for ln in d['lines']:
      print(f'  {ln[\"component_id\"]:30s} required={ln[\"required_qty\"]} {ln[\"component_uom\"]}')
  "
  ```
  Expected: 5 PACK lines (BASE 2L for 10 bottles, bottle 10 UNIT, cap 10, label 10, carton 0.833). 6 BASE lines (water 0.952 L, campari 0.386 L, vermouth 0.386 L, gin 0.193 L, alcohol-96 0.0799 L, preservative 0.004 L).

### Task 10: Portal smoke test in browser

**Files:**
- Run only — `window2-portal-sandbox/`

- [ ] **Step 1: Start the portal dev server**
  ```bash
  cd C:/Users/tomw2/Projects/window2-portal-sandbox
  npm run dev > /tmp/portal.log 2>&1 &
  sleep 6
  ```
  Default port: 3000. Confirm with `curl -s http://localhost:3000 | head -5` — expect HTML.

- [ ] **Step 2: Browse to /planning/production-simulation**
  - Open `http://localhost:3000/planning/production-simulation` in the browser.
  - Expected: the page loads with a product selector populated.

- [ ] **Step 3: Pick "WHITE SANGRIA 3.85L" → enter qty=1 → click Simulate**
  - Expected results table:
    - White wine: **2.81 L** (was 2.62 in the previous build)
    - Calm base: **0.578 L** (was 0.273 — Tom's headline correction)
    - Elderflower syrup: **0.231 L** (was 0.164)
    - Vodka, Martini Bianco: **0.116 L** each
    - Lemon acid: **0.00385 KG**
    - Preservative: **0.005 L** (still present)
  - The component-class badges (BASE / PACK) should show correctly.
  - Stock coverage panel should populate with current on-hand vs required.

- [ ] **Step 4: Pick "MUZA NEGRONI COCKTAIL 0.2L" → qty=100**
  - Expected: 6 BASE ingredients shown including Red Vermouth + Alcohol 96% (the new components). Plus 4 PACK lines (bottle, cap, label, carton).
  - **This is the proof that MUZA is now simulatable** — was impossible before this import.

- [ ] **Step 5: Pick each of the other 3 MUZA cocktails (Jasmine, Queen Violet, Herbal Mule Bliss)**
  - Verify each shows the expected ingredient count (8, 8, 6 BASE lines respectively).
  - Verify Queen Violet shows Violet Liqueur and Melon Extract.
  - Verify Jasmine shows Triple Sec 17%.
  - Verify Herbal Mule Bliss shows Cucumber Syrup.

- [ ] **Step 6: Pick a Margarita (e.g. CLA 0.3L)**
  - Verify simulator runs without "BASE_FILL not resolvable" warnings (because we set BASE_FILL_QTY_PER_UNIT=0.3L on the item).
  - Verify YUZU-PUREE line shows UOM = KG (was L before our fix).

- [ ] **Step 7: Pick FG-MUZ-PSC-200ML (Passion Spritz, the known-gap item)**
  - Expected: an explicit "no recipe linked" or empty-state message — NOT a partial simulation. If a partial simulation appears, the items master still has phantom BOM links.

**Chunk 3 exit gate:** White Sangria 3.85L returns Wine 2.81 L; all 4 new MUZA cocktails simulate; Passion Spritz shows correct empty state. **Hand the running portal to Tom for visual sign-off before Chunk 4.**

**Rollback for Chunk 3:** kill dev servers, restore previous DB state per Chunk 2 rollback notes.

---

## Chunk 4: Production import (Supabase)

**Purpose:** Apply the same import to production Supabase atomically, with explicit pause for human approval before write.

### Task 11: Prepare production credentials and verify which DB you're about to touch

**Files:**
- Read only: `gt-factory-os/.env.production` (or whatever the prod env file is)

- [ ] **Step 1: Confirm `.env.production` exists and points to Supabase**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  test -f .env.production && echo "exists" || echo "MISSING — create it"
  grep -E '^DATABASE_URL=' .env.production | sed 's/postgres.*@/postgres:***@/'
  ```
  Expected: `DATABASE_URL=postgres:***@db.<project-ref>.supabase.co:6543/postgres` (pooled) OR `:5432/postgres` (direct). For `import_masters.ts` the rule is **direct connection (port 5432)**, not pooled (per the existing import script comments). If the URL says `:6543`, switch to the direct version before running.

- [ ] **Step 2: Quadruple-check by querying the production DB read-only**
  ```bash
  # Use a tiny SELECT to prove we're connected to the right DB.
  DOTENV_CONFIG_PATH=.env.production tsx -e "
  import 'dotenv/config';
  import pg from 'pg';
  const c = new pg.Client({ connectionString: process.env.DATABASE_URL });
  await c.connect();
  const r = await c.query('SELECT current_database(), current_user, version()');
  console.log(r.rows);
  await c.end();
  "
  ```
  Expected: `current_database = postgres`, `current_user` = the service-role user, `version` = PostgreSQL 16.x. **Read this output carefully**. If it says `current_database = gtfo` or `current_user = postgres@127.0.0.1` you are NOT on prod, you are on local. Stop and switch env files.

### Task 12: Production dry-run

**Files:**
- Run only — same script, prod env

- [ ] **Step 1: Run dry-run against production**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  DOTENV_CONFIG_PATH=.env.production tsx scripts/import_masters.ts --dry-run 2>&1 | tee /tmp/prod_dry_run.log | tail -30
  ```
  Expected: same shape as local dry-run, ending with `[DRY-RUN] No writes performed.` and no FAIL/WARN lines.
  If pre-flight P1–P9 fail against prod (but passed locally), the prod schema may not include trigger 0077 yet — apply migration first via `_pg_apply_migrations.sh` against prod (separate decision; not part of this plan).

### Task 13: Production import (the actual write) — explicit human checkpoint

**Files:**
- Run only

- [ ] **Step 1: Capture pre-import prod row counts**
  ```bash
  DOTENV_CONFIG_PATH=.env.production tsx -e "
  import 'dotenv/config';
  import pg from 'pg';
  const c = new pg.Client({ connectionString: process.env.DATABASE_URL });
  await c.connect();
  for (const t of ['components','supplier_items','bom_head','bom_version','bom_lines','items']) {
    const r = await c.query(\`SELECT COUNT(*) FROM private_core.\${t}\`);
    console.log(\`\${t}: \${r.rows[0].count}\`);
  }
  await c.end();
  " 2>&1 | tee /tmp/prod_before_counts.txt
  ```

- [ ] **Step 2: PAUSE — wait for explicit human approval**
  This step is a hard checkpoint. The engineer must paste the dry-run summary and the prod pre-import counts to Tom, and wait for an explicit "go" before proceeding to Step 3.

- [ ] **Step 3: Run the real import against production**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  DOTENV_CONFIG_PATH=.env.production tsx scripts/import_masters.ts 2>&1 | tee /tmp/prod_import.log
  ```
  Expected: same as local — final `COMMIT` line, all expected counts. If `ROLLBACK` happens, the prod DB is unchanged and the engineer must surface the error.

- [ ] **Step 4: Capture post-import prod row counts and diff**
  ```bash
  # Same query as Step 1, redirect to prod_after_counts.txt
  diff /tmp/prod_before_counts.txt /tmp/prod_after_counts.txt
  ```
  Expected diff matches: components +6, supplier_items +6, bom_head +8, bom_version +8, bom_lines +48 (or similar — depends on how stale prod was vs local fixtures). For idempotent re-run on already-imported prod, expected diff is 0 across all rows.

### Task 14: Run the same invariant gate (I1–I5) against prod

**Files:**
- Run only

- [ ] **Step 1: Re-run the I1–I5 invariant queries from Chunk 2, Task 7, but against production**
  Use the same five SQL blocks. Each must return **0 rows**. If any prod row appears (e.g., an INACTIVE component referenced by an active line, or a base-mix orphan), the import has uncovered a pre-existing data issue in prod that wasn't in local. Stop and surface to Tom.

**Chunk 4 exit gate:** prod import committed, all 5 invariants return 0 rows on prod. **Pause here.**

**Rollback for Chunk 4:**
- If commit hasn't completed (atomic rollback already happened via the import script's transaction wrapper), no action.
- If commit completed but a downstream check fails: rollback requires a `pg_dump`-based restore (Supabase has point-in-time recovery for paid tiers — use the dashboard). Otherwise, run `import_masters.ts` again with the **previous** fixtures (`git checkout HEAD~1 -- fixtures/masters/` from before the commit, then re-import). Document this prominently before starting Chunk 4 so the engineer knows their options.

---

## Chunk 5: Production smoke + sign-off

**Purpose:** Prove the operator-facing portal in prod shows the corrected recipes; capture evidence; close.

### Task 15: Production portal smoke

**Files:**
- Run only — production portal URL (e.g., `https://factory-os.gteveryday.com` or the Vercel preview URL)

- [ ] **Step 1: Open production portal `/planning/production-simulation`**
  Same flow as Chunk 3, Task 10, Steps 3–7. Verify each acceptance:
  - White Sangria 3.85L: Wine 2.81 L, Calm 0.578 L, Elderflower 0.231 L
  - All 4 MUZA cocktails simulate cleanly with the new components
  - Margaritas show YUZU-PUREE in KG
  - Passion Spritz shows empty state (no BOM)

- [ ] **Step 2: Capture screenshots of each successful simulation**
  Save screenshots into `docs/evidence/2026-04-27-recipe-import/`:
  - `01-white-sangria-3850ml-1unit.png`
  - `02-muza-negroni-100units.png`
  - `03-muza-jasmine-50units.png`
  - `04-muza-queen-violet-50units.png`
  - `05-muza-herbal-mule-50units.png`
  - `06-margarita-classic-100units.png`

- [ ] **Step 3: Final audit script confirmation**
  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  python scripts/_final_verify_all.py | tail -3
  ```
  This still runs against the JSON fixtures — must remain `48/48 PASS`. (This is a *fixture* check, not a DB check — but it confirms the fixtures we imported haven't been retroactively edited.)

### Task 16: Update CURRENT_STATE.md and close the loop

**Files:**
- Modify: `c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION/CURRENT_STATE.md`

- [ ] **Step 1: Add a status line under the "Recent landings" or equivalent section**
  Append a one-line entry:
  ```
  - 2026-04-27: Recipe master closure landed in prod — 4 MUZA cocktails live, Sangria W Elita corrected (Wine 2.81L/unit), 6 new RAW components, 4 duplicates retired. 48/48 verification PASS. Residual gaps: DETOX-NS (Andrey), Passion Spritz (no recipe), Cosmo Lychee (decision pending).
  ```

- [ ] **Step 2: Push the doc commit**
  ```bash
  cd "c:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION"
  git add CURRENT_STATE.md docs/evidence/2026-04-27-recipe-import/
  git commit -m "docs: record 2026-04-27 recipe master closure landing"
  git push
  ```

**Chunk 5 exit gate:** production portal shows new ratios, evidence captured, CURRENT_STATE updated. **Plan is COMPLETE.**

---

## Chunk 6: Residual gaps follow-ups (do NOT block this plan)

These are explicit follow-ups already documented in `docs/recipe-closure-status-2026-04-27.md`. They are **not** required for this plan to land — they are queued work after import succeeds.

- [ ] **Followup A:** DETOX-NS recipe — wait for Andrey's decision (REG-minus-sugar vs intentional half-batch). Until decided, DETOX-NS items will simulate with current (potentially stale) ratios. Surface a banner in the portal: "DETOX-NS recipe pending review."
- [ ] **Followup B:** MUZA Passion Spritz — wait for recipe. Until then, item shows empty-state in simulator (intended).
- [ ] **Followup C:** Cosmo Lychee — Excel sheet has two recipe blocks; pick canonical via inspection or Andrey, then re-import.
- [ ] **Followup D:** 33 + 4 PACK→BASE id-convention mismatches — single SQL UPDATE + revalidation. Independent of recipes; safe to do in a follow-up loop.
- [ ] **Followup E:** UOM convention for remaining purees (CRANBERRY-PUREE-ODK still L) — small data fix.

---

## Acceptance Criteria

The plan is **DONE** when ALL of the following are true:

- [ ] `python scripts/_final_verify_all.py` → 48/48 PASS (fixture invariant)
- [ ] Local DB invariants I1–I5 → 0 rows each
- [ ] Production DB invariants I1–I5 → 0 rows each
- [ ] Curl `/api/v1/queries/boms/heads/BOM-BASE-SAN-WHI-ELI-REG/simulate?qty=3.85` returns `RAW-WINE-WHITE.required_qty` ≈ `2.8105`
- [ ] Curl `/api/v1/queries/boms/heads/BOM-BASE-MUZ-NEG/simulate?qty=2` returns 6 lines including RAW-VERMOUTH-RED and RAW-ALCOHOL-96
- [ ] Production portal `/planning/production-simulation` shows White Sangria 3.85L with Wine 2.81 L (visible to the operator)
- [ ] All 4 MUZA cocktails (HER, JAS, NEG, QUE) simulate cleanly in production
- [ ] Margaritas show BASE_FILL=0.3L resolved, YUZU-PUREE in KG
- [ ] No `qty_per_l_output IS NULL` rows for active BASE BOMs in production
- [ ] No active BOM line references an INACTIVE component
- [ ] CURRENT_STATE.md updated with the landing record

---

## Test Plan

| Layer | Test | Expected |
|---|---|---|
| Fixture | `_final_verify_all.py` | 48 PASS |
| Schema | trigger 0077 present + enabled | 1 row |
| Data invariant I1 | qty_per_l_output drift query | 0 rows |
| Data invariant I2 | PACK base-mix line cardinality | 0 rows |
| Data invariant I3 | items missing BASE_FILL where required | 0 rows |
| Data invariant I4 | components missing primary supplier | 0 rows |
| Data invariant I5 | active BOM line → INACTIVE component | 0 rows |
| pgTAP | BOM/master test suite | all `ok` |
| HTTP API | Sangria W Elita simulate qty=3.85 | wine 2.8105 |
| HTTP API | MUZA Negroni simulate qty=2 | 6 BASE lines |
| Portal E2E | White Sangria 3.85L card | Wine 2.81 L |
| Portal E2E | MUZA picker shows 4 cocktails | 4 entries |
| Portal E2E | Passion Spritz empty state | empty-state UI |
| Operational | Tom visual sign-off | screenshot collected |

---

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Trigger 0077 missing in prod | Verify before Chunk 4 Task 12; if missing, apply migration first via separate plan |
| Prod DB on a different (older) schema vs local | Migration list comparison in Chunk 2 Task 5; if mismatch, treat as a separate issue and stop |
| Atomicity break (partial UPSERT) | `import_masters.ts` already wraps everything in a single transaction with `ON_ERROR_STOP` — proven idempotent in test B8 |
| Stale react-query cache hides new data | Hard refresh in browser; cache TTL is 30s by default — wait or refresh |
| Wrong env file targeted | Chunk 4 Task 11 includes a `current_database`/`current_user` SELECT proof step — reading that output is mandatory |
| Production has pre-existing data drift not in local | Chunk 4 Task 14 runs the same invariants against prod; any unexpected rows surface there |
| Operator sees old ratios after import (cached) | Mention in handoff: hard refresh; clear browser IDB if portal uses local cache |

---

## Hand-off context for the next executor

This plan was authored after a sequence of brainstorming + audit + reconciliation passes documented in:
- `docs/recipe-audit-2026-04-27.md`
- `docs/recipe-reconciliation-v2-2026-04-27.md`
- `docs/recipe-deep-verification-2026-04-27.md`
- `docs/recipe-closure-status-2026-04-27.md`

The fixtures are already in their final state; the engineer running this plan should NOT modify any JSON in `fixtures/masters/`. If a check fails, the engineer should surface to Tom rather than mutate the data — every value was Tom-confirmed.

The 48-check verifier is deterministic and runs in <1 s. Run it after every step that could touch fixtures (it should never start failing — that would mean a regression).

The plan is intentionally conservative (atomic transactions, dry-runs first, explicit human checkpoint before prod write) because the data being imported underpins purchase planning and stock truth — both Phase 1 and Phase 0 dependencies for GT Factory OS.
