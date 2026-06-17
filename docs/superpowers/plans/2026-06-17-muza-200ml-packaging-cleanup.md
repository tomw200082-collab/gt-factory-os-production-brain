# Muza 200ML Packaging Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-point the Muza 200ML cocktails' bottle/cap/carton off the brand-supplier `SUP-041` onto real packaging suppliers, and seed opening-stock anchors (labels 1000 each, bottle/cap/carton 0), so procurement planning is correct.

**Architecture:** One idempotent numbered SQL migration (`0254`) in `gt-factory-os`, authored in a worktree cut from `origin/main`, applied to prod via the documented manual path. Part A = master-data `UPDATE`s (reversible). Part B = `balance_anchors_current` inserts that touch STOCK TRUTH; the existing `anchor_after_insert_projection()` trigger (0009) rebases `current_balances` in-transaction. Verified read-only against prod (shadow DB is dead); parity confirmed via `rebuild_verifier()`.

**Tech Stack:** PostgreSQL (Supabase, `private_core` schema), `node` + `pg` for apply/verify, `scripts/_apply_migration.mjs` (prod-guarded applier), git worktrees.

**Spec:** `PRODUCTION/docs/superpowers/specs/2026-06-17-muza-200ml-packaging-cleanup-design.md` (Tom-approved 2026-06-17).

**Locked facts (verified read-only this session):**
- Components (in `private_core.components`): `PKG-BOTTLE-200ML`, `PKG-CAP-200ML`, `PKG-CARTON-200ML` all on `primary_supplier_id='SUP-041'` (each with exactly ONE PRIMARY `supplier_items` row, also `SUP-041`, est. costs 1.10 / 0.25 / 1.40). The 5 labels `PKG-LABEL-MUZ-{HER,JAS,NEG,PSC,QUE}-200ML` already on `SUP-022` (Miki) — untouched.
- Target suppliers (both ACTIVE): `SUP-002` Arizot 2100 (bottle+cap), `SUP-020` Eliran Kartonim (carton).
- Tom's app_user id: `0db008a9-05e3-4521-8b30-42e5d444818d`.
- None of the 8 components has a `current_balances` row or a `balance_anchors_current` row (untracked).
- Anchor INSERT/UPDATE auto-rebases `current_balances` to `anchor_qty + sum(POSTED ledger event_at > anchor_at)` via trigger `trg_balance_anchors_current_after_insert_projection`. These 8 keys have no such ledger → on-hand becomes exactly the anchor.
- `balance_anchors_current` columns: `site_id, item_type, item_id, batch_id_or_empty, anchor_qty, anchor_at, anchor_source, approved_by_user_id, approved_at, created_at, updated_at`. **No `notes` column.** `anchor_source='COUNT_APPROVAL'` is the live precedent for Tom-approved counts.
- Highest migration on `origin/main` = `0253` → this is `0254`. Migrations applied via `_apply_migration.mjs` are NOT recorded in any migrations ledger; idempotency is the SQL's own job.
- DB URL: `DATABASE_URL_POOLED` in `gt-factory-os/.env`. Read-only probes: `BEGIN; SET TRANSACTION READ ONLY; … ROLLBACK`.

**Governance:** Part B touches stock truth → boot-kernel stop condition → `factory-os-governor` PROCEED verdict required before the prod apply (Task 6 gate). Tom's written approval = the spec approval + the anchor `approved_by_user_id` stamp. Mission-scoped git/deploy authority covers commit/push/PR/apply with evidence. No frozen flags, no external-system writes, no destructive ops.

---

## File Structure

- **Create:** `gt-factory-os/db/migrations/0254_muza_200ml_packaging_split_and_seed.sql` — the whole change (Part A + Part B). One file: these rows change together and must apply atomically.
- **Create (worktree, throwaway, not committed):** `gt-factory-os/scripts/_ro.mjs` — a tiny read-only SQL runner reused for pre-flight and verification. Read-only by construction (`SET TRANSACTION READ ONLY`).
- **Modify:** none.
- **No pgTAP test** — pgTAP needs a disposable live DB; the local/shadow DB is dead. Verification is read-only SELECTs against prod with exact expected output (Tasks 1 and 7).

---

## Task 1: Pre-flight read-only checks (clean slate + valid IDs)

**Files:**
- Create: `gt-factory-os/scripts/_ro.mjs`

- [ ] **Step 1: Write the read-only runner**

`gt-factory-os/scripts/_ro.mjs`:

```js
#!/usr/bin/env node
// READ-ONLY SQL runner. Usage: node scripts/_ro.mjs "<SQL>"
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
const require = createRequire(process.cwd() + '/package.json');
const pg = require('pg');
const env = readFileSync('.env', 'utf8');
const url = (env.match(/^DATABASE_URL_POOLED=(.*)$/m) || [])[1].trim().replace(/^["']|["']$/g, '');
const c = new pg.Client({ connectionString: url, ssl: { rejectUnauthorized: false } });
await c.connect();
await c.query('BEGIN'); await c.query('SET TRANSACTION READ ONLY');
try { const r = await c.query(process.argv[2]); console.log(JSON.stringify(r.rows, null, 2)); }
finally { await c.query('ROLLBACK'); await c.end(); }
```

- [ ] **Step 2: Confirm target suppliers are ACTIVE**

Run:
```bash
node scripts/_ro.mjs "select supplier_id, supplier_name_short, status from private_core.suppliers where supplier_id in ('SUP-002','SUP-020','SUP-041') order by supplier_id"
```
Expected: `SUP-002` (Arizot 2100, ACTIVE), `SUP-020` (Eliran Kartonim, ACTIVE), `SUP-041` (Muza Cocktails).

- [ ] **Step 3: Confirm the 3 components + their PRIMARY supplier_items are still on SUP-041**

Run:
```bash
node scripts/_ro.mjs "select c.component_id, c.primary_supplier_id, si.supplier_id si_supplier, si.is_primary, si.std_cost_per_inv_uom::float8 cost from private_core.components c join private_core.supplier_items si on si.component_id=c.component_id and si.is_primary where c.component_id in ('PKG-BOTTLE-200ML','PKG-CAP-200ML','PKG-CARTON-200ML') order by c.component_id"
```
Expected: 3 rows, all `primary_supplier_id='SUP-041'` and `si_supplier='SUP-041'`, costs 1.10 / 0.25 / 1.40. If any is already SUP-002/SUP-020, Part A is partially applied — safe (idempotent) but note it.

- [ ] **Step 4: Confirm clean stock slate for all 8 components**

Run:
```bash
node scripts/_ro.mjs "with k(item_id) as (values ('PKG-BOTTLE-200ML'),('PKG-CAP-200ML'),('PKG-CARTON-200ML'),('PKG-LABEL-MUZ-HER-200ML'),('PKG-LABEL-MUZ-JAS-200ML'),('PKG-LABEL-MUZ-NEG-200ML'),('PKG-LABEL-MUZ-PSC-200ML'),('PKG-LABEL-MUZ-QUE-200ML')) select (select count(*) from private_core.balance_anchors_current a join k on k.item_id=a.item_id) anchors, (select count(*) from private_core.current_balances b join k on k.item_id=b.item_id) balances, (select count(*) from private_core.stock_ledger l join k on k.item_id=l.item_id and l.post_status='POSTED') posted_ledger"
```
Expected: `anchors=0, balances=0, posted_ledger=0`. (If `posted_ledger>0`, stop and re-check that no event has `event_at` after the anchor moment — would change the seeded on-hand.)

- [ ] **Step 5: Confirm Tom's user id**

Run:
```bash
node scripts/_ro.mjs "select user_id, display_name, role from private_core.app_users where user_id='0db008a9-05e3-4521-8b30-42e5d444818d'"
```
Expected: one row, Tom (admin). If the column names differ, adapt; the point is to confirm the uuid is Tom.

- [ ] **Step 6: Capture rebuild_verifier baseline**

Run:
```bash
node scripts/_ro.mjs "select private_core.rebuild_verifier() as parity_diff"
```
Note: `rebuild_verifier()` writes to the scratch `current_balances_shadow` table only (safe on live). Record the returned number — Task 7 must not exceed it. (Ideal baseline = 0.)

- [ ] **Step 7: No commit** — `_ro.mjs` is a throwaway helper; do not commit it.

---

## Task 2: Create the isolated worktree from origin/main

**Files:** none (workspace setup)

- [ ] **Step 1: Create the worktree + branch (REQUIRED SUB-SKILL: superpowers:using-git-worktrees)**

From `C:/Users/tomw2/Projects/gt-factory-os`:
```bash
git fetch origin --quiet
git worktree add -b feat/muza-200ml-packaging-0254 ../gt-factory-os-muza0254 origin/main
```
Expected: new worktree at `../gt-factory-os-muza0254` on branch `feat/muza-200ml-packaging-0254`, based on `origin/main`.

- [ ] **Step 2: Copy `.env` into the worktree (gitignored, needed for apply/verify)**

```bash
cp ./.env ../gt-factory-os-muza0254/.env
```
Expected: `.env` present in the worktree. Confirm `git -C ../gt-factory-os-muza0254 status --short` does NOT list `.env`.

- [ ] **Step 3: Verify the migration ledger in the worktree ends at 0253**

```bash
ls ../gt-factory-os-muza0254/db/migrations | sort | tail -3
```
Expected: highest is `0253_credit_decision_reason_optional.sql`.

---

## Task 3: Author the migration

**Files:**
- Create: `gt-factory-os-muza0254/db/migrations/0254_muza_200ml_packaging_split_and_seed.sql`

- [ ] **Step 1: Write the migration file verbatim**

```sql
-- ===========================================================================
-- 0254_muza_200ml_packaging_split_and_seed.sql
-- ===========================================================================
-- Muza 200ML cocktail packaging cleanup. Tom-approved 2026-06-17.
-- Spec: PRODUCTION/docs/superpowers/specs/2026-06-17-muza-200ml-packaging-cleanup-design.md
--
-- Idempotent (safe to re-run). No DDL, no stock_ledger rows, no BOM/recipe
-- change, no price change.
--
-- Part A — un-bundle bottle/cap/carton off the brand-supplier SUP-041
--   ("Muza Cocktails") onto real packaging suppliers, matching the 1L line:
--     PKG-BOTTLE-200ML, PKG-CAP-200ML -> SUP-002 (Arizot 2100)
--     PKG-CARTON-200ML                -> SUP-020 (Eliran Kartonim)
--   Updates components.primary_supplier_id and the single PRIMARY
--   supplier_items row per component. Placeholder est. costs kept (price
--   pass is later). Labels (SUP-022 Miki) and SUP-041's Muza-FG links: untouched.
--
-- Part B — opening-stock anchors (TOUCHES STOCK TRUTH). The AFTER INSERT/UPDATE
--   trigger anchor_after_insert_projection() (0009) rebases current_balances to
--   anchor_qty + sum(POSTED ledger with event_at > anchor_at). These 8 keys have
--   no such ledger, so on-hand becomes exactly the anchor:
--     5 labels = 1000 each ; bottle/cap/carton = 0 each.
--   balance_anchors_current has NO notes column — rationale lives in this header.
--   anchor_at = now() (the count moment, 2026-06-17); approver = Tom.
-- ===========================================================================

begin;

set search_path to private_core, public;

-- ---- Part A: re-point suppliers (only rows still on SUP-041 are touched) ----
update private_core.components
   set primary_supplier_id = 'SUP-002', updated_at = now()
 where component_id in ('PKG-BOTTLE-200ML','PKG-CAP-200ML')
   and primary_supplier_id = 'SUP-041';

update private_core.components
   set primary_supplier_id = 'SUP-020', updated_at = now()
 where component_id = 'PKG-CARTON-200ML'
   and primary_supplier_id = 'SUP-041';

update private_core.supplier_items
   set supplier_id  = 'SUP-002',
       source_basis = 'Muza 200ML packaging un-bundled 2026-06-17: bottle/cap moved off brand SUP-041 to Arizot 2100 (matches 1L mixer line).',
       notes        = 'Re-pointed from Muza Cocktails (SUP-041) to Arizot 2100. Est. cost kept as placeholder pending real quote.',
       updated_at   = now()
 where component_id in ('PKG-BOTTLE-200ML','PKG-CAP-200ML')
   and is_primary = true
   and supplier_id = 'SUP-041';

update private_core.supplier_items
   set supplier_id  = 'SUP-020',
       source_basis = 'Muza 200ML packaging un-bundled 2026-06-17: carton moved off brand SUP-041 to Eliran Kartonim (default carton supplier).',
       notes        = 'Re-pointed from Muza Cocktails (SUP-041) to Eliran Kartonim. Est. cost kept as placeholder pending real quote.',
       updated_at   = now()
 where component_id = 'PKG-CARTON-200ML'
   and is_primary = true
   and supplier_id = 'SUP-041';

-- ---- Part B: opening-stock anchors (trigger rebases current_balances) ----
insert into private_core.balance_anchors_current
  (site_id, item_type, item_id, batch_id_or_empty,
   anchor_qty, anchor_at, anchor_source, approved_by_user_id, approved_at)
values
  ('GT-MAIN','PKG','PKG-LABEL-MUZ-HER-200ML','', 1000, now(), 'COUNT_APPROVAL', '0db008a9-05e3-4521-8b30-42e5d444818d', now()),
  ('GT-MAIN','PKG','PKG-LABEL-MUZ-JAS-200ML','', 1000, now(), 'COUNT_APPROVAL', '0db008a9-05e3-4521-8b30-42e5d444818d', now()),
  ('GT-MAIN','PKG','PKG-LABEL-MUZ-NEG-200ML','', 1000, now(), 'COUNT_APPROVAL', '0db008a9-05e3-4521-8b30-42e5d444818d', now()),
  ('GT-MAIN','PKG','PKG-LABEL-MUZ-PSC-200ML','', 1000, now(), 'COUNT_APPROVAL', '0db008a9-05e3-4521-8b30-42e5d444818d', now()),
  ('GT-MAIN','PKG','PKG-LABEL-MUZ-QUE-200ML','', 1000, now(), 'COUNT_APPROVAL', '0db008a9-05e3-4521-8b30-42e5d444818d', now()),
  ('GT-MAIN','PKG','PKG-BOTTLE-200ML','',           0, now(), 'COUNT_APPROVAL', '0db008a9-05e3-4521-8b30-42e5d444818d', now()),
  ('GT-MAIN','PKG','PKG-CAP-200ML','',              0, now(), 'COUNT_APPROVAL', '0db008a9-05e3-4521-8b30-42e5d444818d', now()),
  ('GT-MAIN','PKG','PKG-CARTON-200ML','',           0, now(), 'COUNT_APPROVAL', '0db008a9-05e3-4521-8b30-42e5d444818d', now())
on conflict (site_id, item_type, item_id, batch_id_or_empty) do update set
  anchor_qty          = excluded.anchor_qty,
  anchor_at           = excluded.anchor_at,
  anchor_source       = excluded.anchor_source,
  approved_by_user_id = excluded.approved_by_user_id,
  approved_at         = excluded.approved_at,
  updated_at          = now();

commit;

-- ===========================================================================
-- End of 0254_muza_200ml_packaging_split_and_seed.sql
-- ===========================================================================
```

- [ ] **Step 2: Sanity-check the file parses (offline, no DB)**

```bash
node -e "const s=require('fs').readFileSync('../gt-factory-os-muza0254/db/migrations/0254_muza_200ml_packaging_split_and_seed.sql','utf8'); if(!/begin;[\s\S]*commit;/.test(s)) throw new Error('missing begin/commit'); console.log('OK length', s.length)"
```
Expected: `OK length <n>`.

- [ ] **Step 3: Commit the migration to the feature branch**

```bash
git -C ../gt-factory-os-muza0254 add db/migrations/0254_muza_200ml_packaging_split_and_seed.sql
git -C ../gt-factory-os-muza0254 commit -m "feat(db): 0254 Muza 200ML packaging — un-bundle bottle/cap/carton off SUP-041 + seed opening-stock anchors

Bottle/cap -> SUP-002 (Arizot 2100), carton -> SUP-020 (Eliran Kartonim);
labels untouched (already Miki). Anchors: labels 1000 each, bottle/cap/carton 0.
Idempotent. Touches stock truth; Tom-approved 2026-06-17.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Adversarial review of the migration (ultracode)

**Files:** none (review only)

- [ ] **Step 1: Run an adversarial review pass on the SQL**

Dispatch independent reviewers (Workflow or parallel agents), each trying to REFUTE one dimension; treat a finding as real only if it holds up:
  1. **Append-only / stock-truth:** no `UPDATE`/`DELETE` on `stock_ledger`; `current_balances` never edited directly; anchors are the only stock-truth write.
  2. **Idempotency:** re-running changes nothing after first apply (UPDATEs gated on `supplier_id='SUP-041'`; anchors `ON CONFLICT DO UPDATE` to same values).
  3. **Correctness of IDs/values:** supplier IDs valid+ACTIVE; `item_type='PKG'`; `batch_id_or_empty=''`; anchor qtys 1000×5 / 0×3; Tom uuid correct.
  4. **Projection:** the anchor trigger rebases `current_balances`; no orphan `current_balances` row left without an anchor; `rebuild_verifier()` will stay at baseline.
  5. **Blast radius:** only the 8 named keys / 3 components touched; SUP-041's Muza-FG links and the labels' Miki links untouched; no DDL.

Expected: no surviving finding. Fix any real issue in the migration and re-commit before proceeding.

---

## Task 5: Governance gate + push/PR

**Files:** none

- [ ] **Step 1: factory-os-governor verdict (stock-truth gate)**

Present the decision packet (spec + migration + pre-flight evidence from Task 1) to `factory-os-governor`. Required verdict: **PROCEED** (or PROCEED_WITH_CONSTRAINTS). If HOLD → stop and route to Tom.

- [ ] **Step 2: Push the branch and open a PR**

```bash
git -C ../gt-factory-os-muza0254 push -u origin feat/muza-200ml-packaging-0254
gh --repo <gt-factory-os remote> pr create --base main --head feat/muza-200ml-packaging-0254 --title "0254 Muza 200ML packaging: un-bundle suppliers + seed opening stock" --body "<summary + link to spec + pre-flight evidence>"
```
Expected: PR created. (Apply-to-prod is manual and separate; merge to main keeps repo↔live aligned — Task 8.)

---

## Task 6: Apply to production (manual, guarded)

**Files:** none (executes the migration)

- [ ] **Step 1: Apply with the production guard**

From the worktree `../gt-factory-os-muza0254` (so `.env` + script resolve there):
```bash
MIGRATION_ALLOW_PRODUCTION=confirmed node scripts/_apply_migration.mjs db/migrations/0254_muza_200ml_packaging_split_and_seed.sql
```
Expected: the script prints the PRODUCTION warning, then `SUCCESS — … committed in <ms>ms`. If it prints `FAILED:` with a code, stop and read the error; do not retry blindly.

---

## Task 7: Verify against production (read-only)

**Files:** none (uses `scripts/_ro.mjs` from Task 1, copied into the worktree)

- [ ] **Step 1: Suppliers re-pointed**

```bash
node scripts/_ro.mjs "select c.component_id, c.primary_supplier_id, si.supplier_id si_supplier from private_core.components c join private_core.supplier_items si on si.component_id=c.component_id and si.is_primary where c.component_id in ('PKG-BOTTLE-200ML','PKG-CAP-200ML','PKG-CARTON-200ML') order by c.component_id"
```
Expected: bottle→SUP-002/SUP-002, cap→SUP-002/SUP-002, carton→SUP-020/SUP-020.

- [ ] **Step 2: No packaging component left on SUP-041**

```bash
node scripts/_ro.mjs "select component_id from private_core.components where primary_supplier_id='SUP-041'"
```
Expected: `[]` (empty).

- [ ] **Step 3: Anchors present with Tom approval**

```bash
node scripts/_ro.mjs "select item_id, anchor_qty::float8 q, anchor_source, approved_by_user_id from private_core.balance_anchors_current where item_id like 'PKG-%200ML' order by item_id"
```
Expected: 8 rows; labels `q=1000`, bottle/cap/carton `q=0`; all `anchor_source='COUNT_APPROVAL'`, `approved_by_user_id='0db008a9-...'`.

- [ ] **Step 4: current_balances rebuilt to the anchors (the real win)**

```bash
node scripts/_ro.mjs "select item_id, calculated_on_hand::float8 oh from private_core.current_balances where item_id like 'PKG-%200ML' order by item_id"
```
Expected: 8 rows; 5 labels `oh=1000`; bottle/cap/carton `oh=0`.

- [ ] **Step 5: Parity gate unchanged**

```bash
node scripts/_ro.mjs "select private_core.rebuild_verifier() as parity_diff"
```
Expected: equals the Task-1 baseline (ideally `0`). If it increased, stop and investigate — the seed introduced drift.

- [ ] **Step 6: No ledger written**

```bash
node scripts/_ro.mjs "select count(*) n from private_core.stock_ledger where item_id like 'PKG-%200ML'"
```
Expected: `n=0`.

- [ ] **Step 7: Record evidence (N/N)** — paste the 6 results into the PR / handoff: suppliers 3/3, SUP-041 0/0, anchors 8/8, balances 8/8 (1000×5, 0×3), parity = baseline, ledger 0. No DB write to `current_balances`/`stock_ledger` by hand.

---

## Task 8: Merge + close out

**Files:** none

- [ ] **Step 1: Merge the PR to main** (keeps repo↔live aligned; the migration already ran on prod, but `main` must carry `0254`).

```bash
gh --repo <gt-factory-os remote> pr merge feat/muza-200ml-packaging-0254 --squash --delete-branch
```
Expected: merged; Railway auto-deploy of the API is a no-op for this data migration (no code change).

- [ ] **Step 2: Remove the worktree**

```bash
git worktree remove ../gt-factory-os-muza0254
```
Expected: worktree gone (its `.env` and throwaway `_ro.mjs` go with it).

- [ ] **Step 3: Report to Tom** with the Task-7 evidence and the two deferred follow-ups (real bottle/cap/carton counts; price/cost pass; optional carton-ratio confirm).

---

## Self-Review (run after writing)

- **Spec coverage:** Part A re-point (Task 3) ✓; labels untouched ✓; anchors 1000/0 (Task 3) ✓; system-native anchor mechanism, not balance edit ✓; costs/names/`label_size_id`/BOM/ledger untouched ✓; governance gate (Task 5) ✓; read-only verification incl. parity (Task 7) ✓; the 3 open flags carried to Task 8 report ✓.
- **Placeholder scan:** the only `<…>` tokens are the gt-factory-os remote name and PR body in Tasks 5/8 (environment-specific, filled at run time) — acceptable. All SQL/IDs/quantities are literal.
- **Type/name consistency:** column names match the verified schema (`balance_anchors_current` has no `notes`; `supplier_items` uses `is_primary`, `source_basis`, `std_cost_per_inv_uom`; `current_balances.calculated_on_hand`). Migration number `0254` consistent across tasks.
