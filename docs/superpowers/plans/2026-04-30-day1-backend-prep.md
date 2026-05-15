# Day-1 Backend Prep Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the two backend changes + one admin runbook step that the design doc §A.3 listed as remaining for Day-1 cutover. Tom can self-approve waste/count submissions as admin or planner; LionWheel resolver silently drops unmappable SKUs (no exception spam); 41 stale historical exceptions are bulk-closed.

**Architecture:** Three independent narrow tasks against the existing Fastify/PG/Kysely backend in `gt-factory-os/`. Two are handler edits with paired pgTAP / node:test additions; one is an admin SQL action with no code change. All three are reversible.

**Tech Stack:** Node 20 + Fastify + Zod + Kysely + PostgreSQL (Supabase managed) + pgTAP + node:test.

**Spec source:** `PRODUCTION/docs/superpowers/specs/2026-04-30-day1-cutover-and-forecast-workspace-v2-design.md` §A.3 items 1–3.

---

## File Structure

**Modify:**
- `api/src/waste-adjustments/handler.ts` — relax self-approval guard for admin/planner (lines ~430–436).
- `api/src/physical-counts/handler.ts` — same change at lines ~487–491.
- `api/src/integrations/lionwheel/poller.ts` — replace `emitException` for unmapped SKU with INFO log (lines ~405–416).

**Create:**
- `api/test/waste_adjustment_self_approval.test.ts` — node:test cases covering admin / planner self-approve = 200, operator / viewer self-approve = 409.
- `api/test/physical_count_self_approval.test.ts` — same shape against PC handler.
- `api/test/lionwheel_unmappable_silent_drop.test.ts` — node:test asserting 0 exceptions emitted on unmappable SKU + 0 demand rows + INFO log line.
- `db/tests/waste_adjustment_self_approval.test.sql` — pgTAP shape mirroring node tests against the live DB (4 cases).
- `db/tests/physical_count_self_approval.test.sql` — pgTAP shape (4 cases).

**Touch (existing tests to update if they assert old behavior):**
- `db/tests/waste_adjustment_runtime.test.sql` — if any case asserted "admin self-approve 409", flip to 200.
- `db/tests/physical_count_runtime.test.sql` — same.

**No-code admin action:**
- Bulk-close 41 stale LionWheel-triage exceptions via the `/exceptions` portal inbox UI (or single SQL UPDATE if portal is too slow). Document the action in a runbook entry, not a code change.

**Locked decisions (from spec):**
- Self-approval permitted **only when** `caller_role IN ('admin','planner')` AND `submitted_by = caller_user_id`. Operator and viewer continue to receive 409 SELF_APPROVAL_FORBIDDEN.
- LionWheel resolver: unmappable SKUs no longer emit `lionwheel_unknown_sku` exceptions. Instead, `summary.rows_unknown_sku` is still incremented and a single INFO log line per poll cycle reports `unmappable_count` + `sample_skus[5]` for diagnostics. The orders_mirror_lines row still inserts with `item_id=NULL, resolution_status='unresolved'` so it can be retroactively resolved when an alias is later approved.
- Stale-exception bulk-close: target categories `lionwheel_unknown_sku` AND `created_at < now() - interval '14 days'` (the 41 historical stale rows). New unmappable SKUs after this change won't add to the queue.

---

## Chunk 1: Self-approval handler relaxation (waste-adjustments + physical-counts)

### Task 1: Add failing self-approval test for waste-adjustments

**Files:**
- Create: `api/test/waste_adjustment_self_approval.test.ts`

- [ ] **Step 1: Read existing handler context**

  Read: `api/src/waste-adjustments/handler.ts:75-90` (role-check comment block) and `:425-440` (current 409 guard).

- [ ] **Step 2: Find an existing waste-adjustment node:test for shape reference**

  Run: `ls api/test/ | grep -i waste`
  Expected: at least one existing test file (shape to mirror).

- [ ] **Step 3: Write the failing test**

  Create `api/test/waste_adjustment_self_approval.test.ts` with four cases:

  ```typescript
  import { test } from "node:test";
  import assert from "node:assert/strict";
  import { request } from "./harness/request";  // or whatever the existing harness path is
  import { seedSubmission } from "./harness/waste";

  test("admin can self-approve their own waste submission (200)", async () => {
    const sub = await seedSubmission({ submitted_by_role: "admin" });
    const res = await request("POST", `/api/v1/mutations/waste-adjustments/${sub.submission_id}/approve`, {
      role: "admin",
      user_id: sub.submitted_by, // same user
      body: { idempotency_key: crypto.randomUUID() },
    });
    assert.equal(res.status, 200);
  });

  test("planner can self-approve their own waste submission (200)", async () => {
    const sub = await seedSubmission({ submitted_by_role: "planner" });
    const res = await request("POST", `/api/v1/mutations/waste-adjustments/${sub.submission_id}/approve`, {
      role: "planner",
      user_id: sub.submitted_by,
      body: { idempotency_key: crypto.randomUUID() },
    });
    assert.equal(res.status, 200);
  });

  test("operator self-approve still 409 SELF_APPROVAL_FORBIDDEN", async () => {
    const sub = await seedSubmission({ submitted_by_role: "operator" });
    const res = await request("POST", `/api/v1/mutations/waste-adjustments/${sub.submission_id}/approve`, {
      role: "operator",
      user_id: sub.submitted_by,
      body: { idempotency_key: crypto.randomUUID() },
    });
    assert.equal(res.status, 409);
    assert.equal(res.body.code, "SELF_APPROVAL_FORBIDDEN");
  });

  test("viewer self-approve 403 (role-gate, not self-approval check)", async () => {
    const sub = await seedSubmission({ submitted_by_role: "viewer" });
    const res = await request("POST", `/api/v1/mutations/waste-adjustments/${sub.submission_id}/approve`, {
      role: "viewer",
      user_id: sub.submitted_by,
      body: { idempotency_key: crypto.randomUUID() },
    });
    assert.equal(res.status, 403);
  });
  ```

  *Note: adjust seed harness import paths to match the actual `api/test/harness/*` shape.*

- [ ] **Step 4: Run test to verify cases 1+2 fail (admin/planner are blocked today)**

  Run: `cd api && npm test -- test/waste_adjustment_self_approval.test.ts`
  Expected: cases 1+2 FAIL (status 409 instead of 200), cases 3+4 PASS.

### Task 2: Edit waste-adjustments handler — relax self-approval for admin/planner

**Files:**
- Modify: `api/src/waste-adjustments/handler.ts:430-436`

- [ ] **Step 1: Read the current guard**

  The current code reads (line 430–436):
  ```typescript
  // Contract §1.1: admin is NOT exempt (Tom Q4 2026-04-17)
  if (submission.submitted_by === session.user_id) {
    return conflictResult(
      'SELF_APPROVAL_FORBIDDEN',
      `caller ${session.user_id} is the submitter; self-approval is forbidden for all roles`,
    );
  }
  ```

- [ ] **Step 2: Replace with role-aware guard**

  ```typescript
  // §A.3 #1 (2026-04-30): Tom-locked. Self-approval permitted for admin or
  // planner roles; operator and viewer continue to receive 409. Tom is the
  // sole user on Day 1, so this unblocks his daily flow without weakening
  // the guard for floor-operator promotion paths later.
  if (
    submission.submitted_by === session.user_id &&
    session.role !== 'admin' &&
    session.role !== 'planner'
  ) {
    return conflictResult(
      'SELF_APPROVAL_FORBIDDEN',
      `caller ${session.user_id} is the submitter; self-approval is forbidden for role=${session.role}`,
    );
  }
  ```

- [ ] **Step 3: Update the comment block at line 75 to reflect the new policy**

  Replace `// Role checks (contract §1.1 — admin NOT exempt from self-approval)` with:
  `// Role checks (contract §1.1 + design 2026-04-30 §A.3 #1: admin/planner may self-approve)`

- [ ] **Step 4: Run the new tests to verify they all pass**

  Run: `cd api && npm test -- test/waste_adjustment_self_approval.test.ts`
  Expected: all 4 cases PASS.

- [ ] **Step 5: Run the existing waste-adjustment runtime test to verify no regression**

  Run: `cd api && npm test -- test/waste_adjustments.test.ts` (or the actual filename — adjust based on `ls api/test/`)
  Expected: all existing cases PASS.

### Task 3: Repeat for physical-counts handler

**Files:**
- Create: `api/test/physical_count_self_approval.test.ts`
- Modify: `api/src/physical-counts/handler.ts:487-491`

- [ ] **Step 1: Mirror the test shape from Task 1**, swapping waste→pc and `seedSubmission` → `seedPhysicalCountSubmission` (or whatever the existing harness exposes).

- [ ] **Step 2: Run new test to verify cases 1+2 fail before edit**

  Run: `cd api && npm test -- test/physical_count_self_approval.test.ts`
  Expected: cases 1+2 FAIL.

- [ ] **Step 3: Edit handler.ts:487-491**

  Current:
  ```typescript
  // Admin NOT exempt from self-approval (Tom Q4 2026-04-17)
  if (submission.submitted_by === session.user_id) {
    return conflictResult('SELF_APPROVAL_FORBIDDEN',
      `caller ${session.user_id} is the submitter; self-approval is forbidden for all roles`);
  }
  ```

  Replace with:
  ```typescript
  // §A.3 #1 (2026-04-30): admin/planner may self-approve; operator/viewer 409.
  if (
    submission.submitted_by === session.user_id &&
    session.role !== 'admin' &&
    session.role !== 'planner'
  ) {
    return conflictResult('SELF_APPROVAL_FORBIDDEN',
      `caller ${session.user_id} is the submitter; self-approval is forbidden for role=${session.role}`);
  }
  ```

- [ ] **Step 4: Update comment at line 75**

  Replace `// Role checks (admin NOT exempt from self-approval per Tom Q4 2026-04-17)` with the same forward-looking comment as Task 2 Step 3.

- [ ] **Step 5: Run all tests pass**

  Run: `cd api && npm test -- test/physical_count_self_approval.test.ts test/physical_counts.test.ts`
  Expected: all PASS.

### Task 4: Add pgTAP coverage at the DB layer

**Files:**
- Create: `db/tests/waste_adjustment_self_approval.test.sql`
- Create: `db/tests/physical_count_self_approval.test.sql`

- [ ] **Step 1: Inspect existing pgTAP test for shape**

  Read: `db/tests/waste_adjustment_runtime.test.sql` (the existing 33-case suite).
  Identify the seed pattern + assert pattern used.

- [ ] **Step 2: Write a 4-case pgTAP file mirroring the node:test cases**

  The pgTAP cases assert against the actual SQL function or trigger that the handler ultimately calls — typically `private_core.fn_approve_waste_adjustment(...)`. Confirm function name first:

  Run: `psql -c "\df private_core.fn_*waste*approve*"`

  Then write the 4 cases (admin/planner OK; operator/viewer not OK). Use existing fixture user IDs from `db/seeds/test_users.sql` if present.

- [ ] **Step 3: Run the new pgTAP file**

  Run: `psql -f db/tests/waste_adjustment_self_approval.test.sql`
  Expected: all 4 assertions pass.

- [ ] **Step 4: Repeat for physical_count_self_approval.test.sql**

### Task 5: Commit Chunk 1

- [ ] **Step 1: Verify clean diff**

  Run: `git status` and `git diff --stat`
  Expected: 4 files modified (handlers + tests) + 4 files created (node + pgTAP tests).

- [ ] **Step 2: Commit**

  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  git add api/src/waste-adjustments/handler.ts \
          api/src/physical-counts/handler.ts \
          api/test/waste_adjustment_self_approval.test.ts \
          api/test/physical_count_self_approval.test.ts \
          db/tests/waste_adjustment_self_approval.test.sql \
          db/tests/physical_count_self_approval.test.sql
  git commit -m "feat(approve): admin/planner may self-approve waste + physical-count submissions

Per design 2026-04-30 §A.3 #1. Tom is sole user on Day 1; operator/viewer
continue to receive 409 SELF_APPROVAL_FORBIDDEN. Adds:
- Role-aware guard on both handler.approve paths (waste + PC)
- 4-case node:test for each (admin/planner 200, operator 409, viewer 403)
- 4-case pgTAP for each at the SQL function layer

Existing runtime tests unchanged."
  git push
  ```

---

## Chunk 2: LionWheel resolver silent-drop

### Task 6: Add failing test for unmappable-SKU silent-drop

**Files:**
- Create: `api/test/lionwheel_unmappable_silent_drop.test.ts`

- [ ] **Step 1: Read the current emit point**

  Read: `api/src/integrations/lionwheel/poller.ts:395-416` to confirm the `emitException` call shape.

- [ ] **Step 2: Write the test**

  ```typescript
  import { test } from "node:test";
  import assert from "node:assert/strict";
  import { runPollOnce } from "./harness/lionwheel"; // existing test harness

  test("unmappable LionWheel SKU does NOT emit lionwheel_unknown_sku exception", async () => {
    // Arrange: feed a synthetic LionWheel task with one resolvable SKU and
    // one unmappable SKU. Use the existing harness's stub-API mode.
    const initialExceptions = await countExceptionsByCategory("lionwheel_unknown_sku");
    const summary = await runPollOnce({
      tasks: [
        { id: "T1", lines: [
          { id: "L1", sku: "GT-COCKTAIL-MOJITO-250ML" },  // assume seeded alias
          { id: "L2", sku: "TOTALLY-UNKNOWN-SKU-XYZ" },
        ]},
      ],
    });
    const finalExceptions = await countExceptionsByCategory("lionwheel_unknown_sku");
    assert.equal(finalExceptions, initialExceptions, "should not emit unknown-sku exception");
    assert.equal(summary.rows_unknown_sku, 1, "summary still increments");
  });

  test("unmappable SKU still inserts orders_mirror_lines row with item_id=NULL, resolution_status='unresolved'", async () => {
    await runPollOnce({ tasks: [{ id: "T2", lines: [{ id: "L3", sku: "ANOTHER-UNKNOWN" }] }] });
    const row = await sql`SELECT item_id, resolution_status
                            FROM private_core.orders_mirror_lines
                           WHERE lw_order_item_id = 'L3'`;
    assert.equal(row[0].item_id, null);
    assert.equal(row[0].resolution_status, "unresolved");
  });
  ```

- [ ] **Step 3: Run the test to verify case 1 fails (current code emits exception)**

  Run: `cd api && npm test -- test/lionwheel_unmappable_silent_drop.test.ts`
  Expected: case 1 FAIL (counts not equal — exception was emitted).

### Task 7: Edit the resolver to silent-drop + INFO log

**Files:**
- Modify: `api/src/integrations/lionwheel/poller.ts:405-416`

- [ ] **Step 1: Replace the `emitException` block**

  Current:
  ```typescript
  if (!item_id) {
    summary.rows_unknown_sku++;
    await emitException(client, {
      category: 'lionwheel_unknown_sku',
      severity: 'warning',
      source: 'integration.lionwheel',
      title: `Unknown SKU ${line.sku}`,
      detail: `lw_task_id=${task.id}, lw_order_item_id=${line.id}`,
      dedupe_key: `lw_sku:${line.sku}`,
      related_job_run_id: job_run_id,
    });
  }
  ```

  Replace with:
  ```typescript
  if (!item_id) {
    summary.rows_unknown_sku++;
    // §A.3 #2 (design 2026-04-30, Tom-locked): unmappable LionWheel SKUs
    // are dropped silently — the system is the source of truth for
    // products. No exception emitted; the orders_mirror_lines row still
    // inserts with item_id=NULL, resolution_status='unresolved' so it
    // becomes retroactively resolvable when an alias is later approved.
    // Aggregated INFO log emitted once per cycle below (after the loop)
    // so a single "5 unmappable" entry covers all instances instead of
    // N exception rows.
    summary.unmapped_sample_skus.push(line.sku);
  }
  ```

- [ ] **Step 2: Add the aggregated post-loop INFO log**

  Find where the per-task / per-cycle summary is logged (search for `summary.rows_unknown_sku` outside this block). After the loop ends, add:

  ```typescript
  if (summary.rows_unknown_sku > 0) {
    request.log.info({
      kind: 'lionwheel_unmapped_summary',
      cycle_run_id: job_run_id,
      unmappable_count: summary.rows_unknown_sku,
      sample_skus: summary.unmapped_sample_skus.slice(0, 5),
    }, `LionWheel poll: ${summary.rows_unknown_sku} line(s) had unmappable SKUs (silently dropped per design §A.3 #2)`);
  }
  ```

- [ ] **Step 3: Add `unmapped_sample_skus: string[]` to the summary type definition**

  Search for the summary type (likely `interface PollSummary` or similar at top of poller.ts). Add field:
  ```typescript
  unmapped_sample_skus: string[];
  ```
  Initialize as `[]` in the summary object construction.

- [ ] **Step 4: Run the test to verify both cases pass**

  Run: `cd api && npm test -- test/lionwheel_unmappable_silent_drop.test.ts`
  Expected: both PASS.

- [ ] **Step 5: Run existing LionWheel tests to verify no regression**

  Run: `cd api && npm test -- test/lionwheel_*.test.ts`
  Expected: all existing cases PASS.

### Task 8: Commit Chunk 2

- [ ] **Step 1: Verify diff**

  Run: `git status` and `git diff --stat`

- [ ] **Step 2: Commit**

  ```bash
  cd C:/Users/tomw2/Projects/gt-factory-os
  git add api/src/integrations/lionwheel/poller.ts \
          api/test/lionwheel_unmappable_silent_drop.test.ts
  git commit -m "feat(lionwheel): silent-drop unmappable SKUs per design §A.3 #2

System is source of truth for products (CLAUDE.md non-negotiable).
LionWheel SKUs that don't resolve to an internal item are no longer
surfaced as exceptions — orders_mirror_lines row still inserts with
item_id=NULL, resolution_status='unresolved' so retroactive resolution
still works once an alias is approved. Single INFO log line per poll
cycle reports unmappable_count + sample_skus[5] for diagnostics.

Removes ~8/min of stale-exception noise (the 41 historical
lionwheel_unknown_sku rows are bulk-closed in a separate runbook step)."
  git push
  ```

---

## Chunk 3: Bulk-close stale exceptions (admin runbook)

### Task 9: Bulk-close 41 stale lionwheel_unknown_sku exceptions

**Files:** none (admin SQL action via portal or psql).

- [ ] **Step 1: Verify count of stale rows**

  Run via psql:
  ```sql
  SELECT count(*)
    FROM private_core.exceptions
   WHERE category = 'lionwheel_unknown_sku'
     AND status = 'open'
     AND created_at < now() - interval '14 days';
  ```

  Expected: ~41 (per design doc and CURRENT_STATE.md figure as of 2026-04-29).

- [ ] **Step 2: Bulk-close via portal** (preferred)

  Open `https://gt-factory-os-portal.vercel.app/exceptions?view=exceptions&category=lionwheel_unknown_sku` and use the bulk-select + Resolve action.

- [ ] **Step 3: OR bulk-close via SQL** (fallback if portal slow)

  Run via psql:
  ```sql
  UPDATE private_core.exceptions
     SET status = 'resolved',
         resolved_at = now(),
         resolved_by_snapshot = 'admin (Day-1 prep bulk-close per design §A.3 #3)',
         resolution_notes = 'Stale lionwheel_unknown_sku exception predating §A.3 #2 silent-drop change. Closed in bulk on Day-1 prep.'
   WHERE category = 'lionwheel_unknown_sku'
     AND status = 'open'
     AND created_at < now() - interval '14 days';
  ```

- [ ] **Step 4: Verify zero remaining stale rows**

  Run the count from Step 1 again.
  Expected: 0.

- [ ] **Step 5: Verify open count for `lionwheel_unknown_sku` is now zero or near-zero**

  Run:
  ```sql
  SELECT count(*) FROM private_core.exceptions
   WHERE category='lionwheel_unknown_sku' AND status='open';
  ```

  Expected: 0 (or whatever new exceptions arrived since Chunk 2 deployed and are themselves recent — but per Chunk 2 there should be no NEW rows).

### Task 10: Document the runbook step

- [ ] **Step 1: Append to PRODUCTION/docs/operations/db-ops-log.md** *(was: PRODUCTION/CURRENT_STATE.md "DB ops log" section — moved 2026-05-09 in Phase 8 Run F Wave 4 Hole 2 cleanup)*

  Add a new entry under DB ops log:
  ```markdown
  ### Day-1 prep bulk-close — applied 2026-04-30
  - **action:** UPDATE on private_core.exceptions
  - **scope:** category='lionwheel_unknown_sku' AND status='open' AND created_at < now()-14d
  - **rows affected:** ~41
  - **executed_by:** Tom (admin)
  - **method:** portal bulk-resolve OR direct SQL (Step 3 above)
  - **schema semantics changed:** NO
  - **rollback:** N/A — closed exceptions can be re-opened individually if any were not actually stale
  ```

- [ ] **Step 2: Commit the doc update**

  ```bash
  cd "C:/Users/tomw2/GTeveryday Dropbox/Data Center/Tom/AI Agents & Projects/Code Agents/PRODUCTION"
  git add CURRENT_STATE.md
  git commit -m "doc(runbook): record Day-1 stale-exception bulk-close"
  git push  # if PRODUCTION is a git repo; otherwise skip
  ```

---

## Validation — final smoke

### Task 11: End-to-end Day-1 dry run

- [ ] **Step 1: Submit a waste adjustment as admin (Tom)**

  Use portal. Verify the form submits and lands either auto-posted (delta within threshold) OR pending (delta above threshold).

- [ ] **Step 2: If pending, self-approve**

  Open `/exceptions` or `/inbox`, find the pending submission, click Approve. Verify status flips to posted; verify `stock_ledger` has the row.
  Expected: 200 OK; ledger row visible in `/stock/movement-log` within 30s.

- [ ] **Step 3: Trigger LionWheel poll** (manual or scheduled)

  Verify in API logs that you see a `lionwheel_unmapped_summary` INFO entry IF unmappable SKUs were present.
  Verify in `/exceptions` that no NEW `lionwheel_unknown_sku` rows arrive.

- [ ] **Step 4: Check `/inbox` view counts**

  Verify the Exceptions tab count has dropped by ~41 since Day-1 prep started.

- [ ] **Step 5: Mark plan complete**

  Mark this plan file's title with `(DONE 2026-04-30)` and commit.

---

## Rollback

Each chunk reverts cleanly:

| Chunk | Rollback |
|---|---|
| Chunk 1 (self-approval) | `git revert <commit>` — the role-aware guard is replaced back with the strict guard. Tests revert too. |
| Chunk 2 (LionWheel silent-drop) | `git revert <commit>` — restores `emitException` call. Existing 41 closed rows stay closed (different scope). |
| Chunk 3 (bulk-close) | Re-open specific exceptions via SQL: `UPDATE … SET status='open', resolved_at=NULL WHERE exception_id IN (…)`. |

All chunks are forward-compatible with each other; they can land in any order, but the recommended order is Chunk 1 → 2 → 3 (smallest scope of risk first).
