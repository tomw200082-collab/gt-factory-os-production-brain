# Sunday Stock-Truth Cutover Runbook
**Date of execution:** Sunday, 2026-05-10 (or next Sunday Tom counts)
**Owner:** Tom Witt
**Authored:** 2026-05-07

> This runbook is the **only** authoritative procedure for the Sunday cutover.
> Until Tom executes it, GT Factory OS is NOT decrementing stock from
> LionWheel deliveries. After this runbook completes successfully, every
> delivered LW order will decrement stock automatically within 15 minutes.

---

## 1 · What this runbook accomplishes

By the end of these steps:
- A fresh `balance_anchors_current` row exists for every stock-tracked item, set to Tom's physical count.
- `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=true` on Railway. The chain writes `FG_OUT_PICK` rows to `stock_ledger` for every LW delivery confirmed (`ROUNDTRIP_DELIVERED`/`COMPLETED`).
- The §5 pre-anchor guard automatically prevents historical (pre-count) deliveries from re-decrementing the new anchor.
- An `audit_runs` row from B.1 cron confirms the system is healthy ≤24h after cutover.

If anything goes wrong, the rollback section (step 9) restores the prior state in ≤5 minutes.

---

## 2 · Pre-cutover state (verified 2026-05-07 in this authoring session)

These facts are the substrate this runbook assumes. If any of them changed since 2026-05-07, **STOP** and re-verify before executing.

| Fact | Value | How to re-verify |
|---|---|---|
| Bridge gate | `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false` on Railway | Railway dashboard → Variables |
| Mapped LW SKUs (active) | 64 distinct, covering 877 lines/30d (83% volume) | `SELECT count(*) FROM private_core.integration_sku_map WHERE source_channel='lionwheel' AND mapping_status='active'` should be ≥64 |
| Sentinel item | `EXCLUDED-NONSTOCK` exists, `is_stock_managed=false` | `SELECT is_stock_managed FROM private_core.items WHERE item_id='EXCLUDED-NONSTOCK'` returns `false` |
| Excluded SKUs | 24 distinct, mapping_status `excluded_non_stock` or `excluded_legacy_bundle` | `SELECT mapping_status, count(*) FROM private_core.integration_sku_map WHERE source_channel='lionwheel' GROUP BY mapping_status` |
| Still-unmapped (acceptable) | 2 SKUs (`""` empty + `7290003803217` EAN), 5 lines/30d | These will emit exceptions, expected |
| Items master | `FG-SAN-BAB-RED-750ML`, `AP-DRI-PIN-1KG`, `AP-TAP-PIN-0.6` (renamed) all `status='ACTIVE'` | `SELECT item_id, status FROM private_core.items WHERE item_id IN (...)` |
| Audit cron | B.1 deployed and ≥1 successful run in `audit_runs` | `SELECT count(*) FROM private_core.audit_runs WHERE started_at > now() - interval '7 days'` ≥ 1 |
| Telegram alerts | B.2 deployed, `TELEGRAM_BOT_TOKEN`+`TELEGRAM_TOM_CHAT_ID` set | Manual `/start` test message dispatched and received before Sunday |

---

## 3 · Pre-count checklist (T-1 day, Saturday evening)

Run these the night before. They're cheap and catch ~80% of risks before count day.

### 3.1 System health probe
```bash
# From C:/Users/tomw2/Projects/gt-factory-os
NODE_TLS_REJECT_UNAUTHORIZED=0 node scripts/_check_delivery_chain.mjs 2>&1 | tail -50
```
Expect:
- `terminal_lines_7d` > 0 (deliveries are happening)
- `enriched > 0` (chain enrichment is running)
- `posted = 0` or low (bridge still closed, expected)
- `gap = 0` or matches `enriched` (lines waiting to flush)

If `enriched = 0`: chain enrichment isn't running. **STOP.** Investigate the LW poller before proceeding.

### 3.2 Audit baseline
```bash
python "C:/Users/tomw2/.claude/skills/stock-event-accuracy-audit/scripts/run_audit.py" --days 7
```
Capture the JSON or text output. Expect top-line low (chain not writing) but Layer 4 (Shopify parity via daily-inventory-agent) ≥95%. Save baseline to `PRODUCTION/.cutover/2026-05-10_pre_baseline.txt`.

### 3.3 Verify Railway env vars
Open Railway → service `gt-factory-os-api` → Variables. Confirm:
- `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false` (still off)
- `DATABASE_URL_POOLED` set
- `LIONWHEEL_API_KEY` set
- `JOB_RUNNER_TOKEN` set
- `ENABLE_SHOPIFY_FG_WRITE=false` (still off — agent is still the writer)
- `TELEGRAM_BOT_TOKEN` set (for B.2 alerts)
- `TELEGRAM_TOM_CHAT_ID` set (for B.2 alerts)

If any missing, fix before Sunday.

### 3.4 GitHub Actions cron heartbeat
- Repo: `tomw200082-collab/gt-factory-os`. Tab: Actions.
- Last `LionWheel Poll` run within 15 min: ✅ healthy
- Last `Audit Daily` run within 24h: ✅ healthy (B.1 deliverable; if not yet present, B.1 hasn't deployed — fix)

### 3.5 Telegram self-test
Send `/start` to your Factory OS bot in Telegram. Expect a reply within 10 seconds confirming the bot is alive. If silent: B.2 isn't wired. Fix before Sunday.

---

## 4 · Count day (Sunday morning)

**Time required:** Tom's count process (estimate Tom-known) + ~20 min for the cutover steps below.

### 4.1 Open the count freeze (~2 minutes)
```bash
# From C:/Users/tomw2/Projects/gt-factory-os
$env:CUTOVER_OPERATOR_USER_ID = "<your-app_users-uuid>"  # PowerShell
# or: export CUTOVER_OPERATOR_USER_ID="..."  (bash)
NODE_TLS_REJECT_UNAUTHORIZED=0 node scripts/start_count_cutover.mjs
```
Expect output: JSON with `freeze_id` + `opened_at`. **Copy these to a sticky note** — you'll need them in step 4.4.

What this does: inserts a `count_freezes` row covering all items, blocking any concurrent Goods Receipt / Waste / Production submission for the duration of the count. Per CLAUDE.md "Counting v1 — uses start/submit freeze semantics".

### 4.2 Tom counts the warehouse
This is your existing process. Capture every item Tom counts in Excel at `PRODUCTION/.cutover/2026-05-10_count.xlsx` with columns:
- `item_id` (use the exact internal item_id, e.g., `FG-NAM-1L` not `GT-MAS-CHA-1L`)
- `count_qty` (the physical count in internal units — bottles, kgs, etc.)
- `notes` (optional)

Scope: **FG + RM both**. Components are static — skip them.

### 4.3 Import the count (~5 minutes)
```bash
python scripts/import_count_from_excel.py \
  --excel "PRODUCTION/.cutover/2026-05-10_count.xlsx" \
  --site-id GT-MAIN \
  --user-id <your-app_users-uuid> \
  --dry-run
```
Expect output: `valid_rows=N, malformed=0`. If malformed > 0, fix the Excel, re-run dry-run.

When dry-run is clean:
```bash
python scripts/import_count_from_excel.py \
  --excel "PRODUCTION/.cutover/2026-05-10_count.xlsx" \
  --site-id GT-MAIN \
  --user-id <your-app_users-uuid>
```
Expect every row produces a `form_submissions` row with `status='posted'`, a matching `stock_ledger COUNT_ADJUST` row, and a new `balance_anchors_current` row.

### 4.4 Verify anchors landed (~2 minutes)
```bash
python scripts/verify_count_cutover.py
```
Expects:
- `items_with_anchor` matches your imported count
- `projection_matches_anchor=true`
- `rebuild_verifier()=0`

If any of these fail: **STOP.** Do NOT flip the bridge. Investigate before continuing.

### 4.5 Set `cutover_at` + close the freeze (~1 minute)
```bash
NODE_TLS_REJECT_UNAUTHORIZED=0 node scripts/release_count_cutover.mjs
```
Expects: `cutover complete` + a `system_state.cutover_at` row + `count_freezes` row marked `consumed_cutover`.

---

## 5 · The bridge flip (T+0)

**Critical step. Read once before executing.**

### 5.1 Pre-flip sanity (~30 seconds)
```bash
# Quick gate-state check from any shell with Railway CLI:
railway variables get LIONWHEEL_FG_OUT_BRIDGE_ENABLED
# Expected: false
```

### 5.2 Flip the gate (~10 seconds)
Railway dashboard → service `gt-factory-os-api` → Variables → `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` → set value `true` → Save → Redeploy.

OR via CLI:
```bash
railway variables --set LIONWHEEL_FG_OUT_BRIDGE_ENABLED=true
railway up --detach
```

Note the deployment ID Railway returns. Save it.

### 5.3 Force one poll cycle (~30 seconds)
Don't wait 15 min for the GitHub Actions cron — fire it manually so we can verify immediately:
```bash
# Replace TOKEN with $env:JOB_RUNNER_TOKEN value
curl -X POST "https://gt-factory-os-api-production.up.railway.app/api/v1/internal/jobs/lionwheel-poll" `
  -H "Authorization: Bearer $env:JOB_RUNNER_TOKEN"
```
Expect HTTP 200 with response body showing `fg_out_ledger_rows_emitted >= 1` (or 0 if no eligible deliveries since the count freeze closed).

### 5.4 Verify flush behavior
The chain processes ALL enriched-but-unposted lines on next poll. Per Tom-locked decision (24h backfill): the §5 pre-anchor guard automatically suppresses every line whose `event_at <= anchor_at` (which is most pre-count history). Any line with `event_at > anchor_at` (i.e., post-count) gets a ledger row.

```bash
# Count FG_OUT_PICK rows posted since cutover_at
NODE_TLS_REJECT_UNAUTHORIZED=0 node -e "
import('pg').then(async ({default: pg}) => {
  const {readFileSync} = await import('fs');
  for (const l of readFileSync('.env','utf8').split(/\r?\n/)) {
    const m = l.match(/^([A-Z_][A-Z0-9_]*)=(.+)$/);
    if (m) process.env[m[1]] = m[2].replace(/^[\"']|[\"']$/g, '');
  }
  const c = new pg.Client({connectionString: process.env.DATABASE_URL_POOLED, ssl: {rejectUnauthorized: false}});
  await c.connect();
  const r = await c.query(\"SELECT count(*)::int AS n, sum(qty_delta)::float8 AS net FROM private_core.stock_ledger WHERE movement_type='FG_OUT_PICK' AND posted_at > (SELECT (value_jsonb->>'timestamp')::timestamptz FROM private_core.system_state WHERE key='cutover_at')\");
  console.log(r.rows[0]);
  await c.end();
});
"
```
Expect `n` ≥ 0 (likely 0 immediately after cutover unless deliveries already happened post-count). The number grows as new deliveries land.

### 5.5 Force the audit cron once
```bash
curl -X POST "https://gt-factory-os-api-production.up.railway.app/api/v1/internal/jobs/audit-run" `
  -H "Authorization: Bearer $env:JOB_RUNNER_TOKEN"
```
Returns `audit_run_id` + `verdict`. Expect `verdict='PASS'` or `'INCOMPLETE'` (if no deliveries yet to audit). NOT `'FAIL'`. If FAIL: investigate via dashboard or SQL.

---

## 6 · 24-hour soak (T+0 to T+24h)

Within 24h of cutover:

| Check | When | Where |
|---|---|---|
| First real `FG_OUT_PICK` ledger row appears | Within 1-3 hours of first post-count delivery | Portal → Ledger view → filter "Shipment Pick" — should see new rows with timestamps after cutover_at |
| Audit cron run at 06:00 IL produces row with verdict ∈ {PASS, INCOMPLETE} | Daily 06:00 IL | `SELECT verdict, top_line_pct FROM private_core.audit_runs ORDER BY started_at DESC LIMIT 1` |
| No Telegram FAIL alerts | Continuous | Your Telegram DM with the bot |
| `current_balances` for FG items decreases as deliveries land | Continuous | Portal → stock view → compare to morning |

If at any point verdict becomes `FAIL` or `FAIL_NEG_BALANCE`, follow the rollback (section 9) or investigate via the dashboard's stock-health page.

---

## 7 · 7-day soak (T+24h to T+7d)

This is the period before D.3 (`daily-inventory-agent` strip-down). During these 7 days:
- `daily-inventory-agent` continues writing Shopify on-hand. **Do not disable it yet.**
- factory-os writes `FG_OUT_PICK` rows but `ENABLE_SHOPIFY_FG_WRITE=false` — factory-os does NOT write to Shopify.
- This means factory-os and Shopify diverge as factory-os decrements. The agent re-syncs Shopify daily. **Acceptable** during the soak — both writers operating, factory-os in shadow mode.
- Audit Layer 4 (Shopify parity) will show progressive drift. That's expected. Don't be alarmed unless drift exceeds the daily delivery volume × 1.5.
- Audit Layer 1, 2, 5 should hold ≥99%.

After 7 stable days: proceed to chunk A.4 (continuous Shopify writer + agent strip-down). Separate runbook (TBD).

---

## 8 · Acceptance criteria (when can we close this runbook?)

Mark the runbook complete when ALL of:
- [ ] `system_state.cutover_at` is set
- [ ] `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=true` on Railway
- [ ] `count_freezes` row is `consumed_cutover`
- [ ] At least 1 `FG_OUT_PICK` row exists with `posted_at > cutover_at`
- [ ] `rebuild_verifier()=0` (matches anchor totals)
- [ ] First daily audit cron post-cutover has `verdict ∈ {PASS, INCOMPLETE}`
- [ ] No FAIL_NEG_BALANCE in any audit row in the 24h window

If all 7 are checked: cutover is successful. Tag `git tag stock-truth-cutover-2026-05-10` on `gt-factory-os`.

---

## 9 · Rollback procedure (~5 min)

If at any point post-flip the system shows wrong behavior (negative on-hand on legitimate items, audit FAIL_NEG_BALANCE, Tom's gut says "this is wrong"):

### 9.1 Close the gate
Railway → `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false` → Save → Redeploy.

### 9.2 Reverse the bad rows (if any)
The ledger is append-only. To "undo" `FG_OUT_PICK` rows posted since cutover, write `FG_OUT_PICK_REVERSAL` rows:
```sql
-- Identify the rows
SELECT movement_id, item_id, qty_delta, idempotency_key, posted_at
FROM private_core.stock_ledger
WHERE movement_type = 'FG_OUT_PICK'
  AND posted_at > (SELECT (value_jsonb->>'timestamp')::timestamptz FROM private_core.system_state WHERE key='cutover_at')
ORDER BY posted_at;

-- For each, post a reversal:
INSERT INTO private_core.stock_ledger (
  movement_type, item_id, qty_delta, source_channel, source_event_id,
  idempotency_key, post_status, event_at, posted_at, related_order_line_id, reason_code
)
SELECT
  'FG_OUT_PICK_REVERSAL',
  item_id,
  -qty_delta,  -- flip sign
  source_channel,
  source_event_id,
  idempotency_key || ':reversal:rollback_2026-05-10',
  'POSTED',
  now(),
  now(),
  related_order_line_id,
  'cutover_rollback'
FROM private_core.stock_ledger
WHERE movement_type = 'FG_OUT_PICK'
  AND posted_at > (SELECT (value_jsonb->>'timestamp')::timestamptz FROM private_core.system_state WHERE key='cutover_at');
```

### 9.3 Restore agent as sole writer
The agent should already still be running. No additional action. Verify Shopify on-hand is being written daily.

### 9.4 Investigate root cause
Do NOT re-flip the gate without understanding why the first attempt failed. The 786-row historical incident (Tom-known) is a precedent that root-cause matters.

---

## 10 · Open dependencies on Tom (BEFORE Sunday)

| Item | Action | Owner | Deadline |
|---|---|---|---|
| Telegram chat_id | Run `/telegram:configure`, capture `TELEGRAM_TOM_CHAT_ID`, set on Railway | Tom | Sat 2026-05-09 |
| Telegram bot token | Set `TELEGRAM_BOT_TOKEN` on Railway | Tom | Sat 2026-05-09 |
| `JOB_RUNNER_TOKEN` for audit cron | Confirm exists in GH secrets + Railway env | Tom or W1 | Sat 2026-05-09 |
| Railway access | Confirm Tom (or proxy) can flip env vars on Sunday | Tom | Pre-Sunday |
| Operator app_users uuid | Look up Tom's user_id in `private_core.app_users` for `--user-id` flag | Tom | Sat 2026-05-09 |
| The 2 still-unmapped SKUs (`""` + `7290003803217`) | Decide: ignore (excluded_non_stock), or seed a real mapping | Tom | Optional, not blocking |

---

## 11 · Post-cutover plan map

After Sunday's successful cutover:
- **Mon 2026-05-11 onward:** monitor audit_runs daily verdict via Telegram alerts (B.2). Open exceptions go to /admin/sku-aliases worklist (post-A.2 build).
- **2026-05-17 (T+7d):** evaluate D.3 (agent strip-down) gate. If 7 PASS verdicts in row, dispatch executor-w1 for D.3. Otherwise extend soak.
- **2026-05-17:** dispatch executor-w2 for chunks C.1-C.4 (`/dashboard/stock-health` + exceptions UI + worklists + severity banners).
- **Continuing:** A.4 (Shopify FG-write flip + agent decommission). Separate runbook.

---

*Authored 2026-05-07. To be executed Sunday 2026-05-10. Re-verify §2 facts the night before; if any have shifted, pause and reconcile.*
