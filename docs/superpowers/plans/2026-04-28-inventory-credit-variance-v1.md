# Inventory + Credit Variance v1 — Factory OS Items Only — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade, failure-proof corridor that posts FG_OUT_PICK ledger movements from LionWheel pick truth, creates `credit_tasks` for variance, and exposes a Hebrew approval surface to Dorin with manual `gi_document_id` paste-back. Restricted to canonical Factory OS items only.

**Architecture:** Three layers — (1) hardened pick bridge with dry-run, allowlist, idempotency invariants and skipped-line info-visibility; (2) `credit_tasks` backend with audit trail and transition guards; (3) Dorin Hebrew approval UI with manual `gi_document_id` paste-back. **No** Morning API integration, **no** customer document mirror, **no** webhook listener, **no** SKU classification framework.

**Tech Stack:** Postgres 17 (Supabase pooled), Node 20 + Fastify + Zod + Kysely, Next.js 15 App Router + Tailwind + shadcn/ui + TanStack Query, Deno (Edge Function `factory_os_jobs`), pgTAP (DB tests), node:test (handler tests), Playwright (E2E sandbox).

---

## 1. Policy Lock (verbatim, non-negotiable)

Factory OS is the only product truth.

1. Only canonical `item_id` rows affect inventory, planning, purchasing, production, and credit variance.
2. External Shopify/LionWheel SKUs that do not resolve to a Factory OS `item_id` are **ignored** for v1 purposes (no ledger, no planning input, no purchase signal, no auto-credit).
3. Non-Factory-OS lines must **never** block the Pick Bridge.
4. Single exception: a bundle SKU that physically represents Factory OS items. Either (a) verify LionWheel returns picking at bottle level, OR (b) build minimal `bundle_explosion_map` for that single case. **Not beyond.**
5. The Pick Bridge filter `oml.item_id IS NOT NULL` is the canonical enforcement of policy point 1 at runtime. Any code path that bypasses this filter is a contract violation.

---

## 2. Scope

### 2.1 IN scope (v1)

| # | Component | Owner |
|---|---|---|
| 1 | Pick Bridge dry-run mode | W1 |
| 2 | Pick Bridge allowlist (per task / per day) | W1 |
| 3 | Idempotency hardening on FG_OUT_PICK + credit_task | W1 |
| 4 | Non-Factory-OS skipped-line visibility (info severity, admin-only) | W1 |
| 5 | Bundle inspection (one-time read; no runtime code) | W4 |
| 6 | Minimal `bundle_explosion_map` (only if §5 confirms LionWheel returns bundle as one line) | W1 |
| 7 | `credit_tasks` backend endpoints + transition audit | W1 |
| 8 | Dorin Hebrew approval UI (`/credits/pending`) | W2 |
| 9 | Manual `gi_document_id` paste-back flow | W2 + W1 |
| 10 | Go/No-Go gate execution | governor + Tom |

### 2.2 OUT of scope — forbidden in v1

| Forbidden | Why |
|---|---|
| Morning API auto-issue (POST 330 / 400) | Requires §10 sandbox PASS + §11 question answers; not in v1 |
| `customer_credit_drafts` 13-state machine | `credit_tasks` 4-state machine is sufficient for v1 |
| `green_invoice_documents` mirror table | No need until Morning API enters; defer to v2 |
| `document/created` webhook listener | Defer to v2 |
| Shopify ↔ Morning ↔ LionWheel customer mapping infrastructure | Manual paste-back replaces this in v1 |
| 5-type SKU classification framework | Locked to binary: `IN_FACTORY_OS` (mapped) vs `IGNORED` (unmapped) |
| Auto-credit for products outside Factory OS | Locked by policy point 2 |
| Silent bundle skipping | If bundle = Factory OS bottles, must explode (§6) or block before enabling |

---

## 3. File Structure

### 3.1 DB migrations (canonical repo: `C:/Users/tomw2/Projects/gt-factory-os/`)

| File | Responsibility |
|---|---|
| `db/migrations/0111_pick_bridge_dry_run_log.sql` | Create `pick_bridge_dry_run_log` table. Add CHECK constraints. |
| `db/migrations/0112_credit_tasks_audit.sql` | Add audit columns to `credit_tasks` + transition trigger emitting `change_log` rows. |
| `db/migrations/0113_credit_task_invariants.sql` | Add CHECK constraints (qty_missing > 0, qty_picked >= 0, etc.) + UNIQUE on `(line_mirror_id)` reaffirmed + `gi_document_id` UNIQUE-when-not-null. |
| `db/migrations/0114_bundle_explosion_map.sql` | Create `bundle_explosion_map` (only applied if §6 inspection finds tier-A — single-line bundles). |
| `db/tests/0111_pick_bridge_dry_run_log.test.sql` | pgTAP for migration 0111. |
| `db/tests/0112_credit_tasks_audit.test.sql` | pgTAP for migration 0112. |
| `db/tests/0113_credit_task_invariants.test.sql` | pgTAP for migration 0113 (boundary + violation cases). |
| `db/tests/0114_bundle_explosion_map.test.sql` | pgTAP for migration 0114 (conditional). |

### 3.2 Backend (canonical repo: `C:/Users/tomw2/Projects/gt-factory-os/`)

| File | Responsibility |
|---|---|
| `api/src/integrations/lionwheel/reconciliation.ts` | Modify: add `dry_run`, `task_allowlist`, `date_allowlist` to `ReconcilerConfig`; gate INSERTs; bundle explosion if map present. |
| `supabase/functions/factory_os_jobs/index.ts` | Modify: read `LW_PICK_BRIDGE_DRY_RUN`, `LW_PICK_BRIDGE_TASK_ALLOWLIST`, `LW_PICK_BRIDGE_DATE_ALLOWLIST` env vars; same gating logic as backend. |
| `api/src/credit-tasks/handler.ts` | Create: list/get/credit/waive/dispute handlers. |
| `api/src/credit-tasks/route.ts` | Create: Fastify route registration. |
| `api/src/credit-tasks/schemas.ts` | Create: Zod request/response schemas. |
| `api/src/credit-tasks/audit.ts` | Create: transition audit helper. |
| `api/test/credit_tasks.test.ts` | Create: node:test handler matrix (auth, role, transitions, idempotency, edge cases). |
| `api/test/lionwheel_pick_bridge_dry_run.test.ts` | Create: dry-run + allowlist behavior tests. |
| `api/test/lionwheel_pick_bridge_invariants.test.ts` | Create: invariant violation tests (negative qty, picked > ordered, etc.). |

### 3.3 Portal (sandbox: `C:/Users/tomw2/Projects/window2-portal-sandbox/`)

| File | Responsibility |
|---|---|
| `src/app/(planner)/credits/pending/page.tsx` | Create: Dorin's "זיכויים ממתינים" list page. |
| `src/app/(planner)/credits/pending/[id]/page.tsx` | Create: detail page with credit/waive/dispute actions. |
| `src/app/(planner)/credits/pending/[id]/_components/CreditApprovalDialog.tsx` | Create: dialog for `gi_document_id` paste + `notes`. |
| `src/app/(planner)/credits/pending/_components/CreditTasksList.tsx` | Create: filterable list component. |
| `src/app/(planner)/credits/pending/_components/StatusBadge.tsx` | Create: Hebrew status badge (PENDING/CREDITED/WAIVED/DISPUTED). |
| `src/app/api/credit-tasks/[...path]/route.ts` | Create: proxy to backend. |
| `src/lib/api/credit-tasks.ts` | Create: typed API client + TanStack Query hooks. |
| `src/lib/labels/credit-tasks-he.ts` | Create: locked Hebrew label register. |
| `tests/e2e/credits-pending.spec.ts` | Create: Playwright real-HTTP E2E (auth, list, credit, waive, dispute). |

### 3.4 Operational governance (PRODUCTION/docs/)

| File | Responsibility |
|---|---|
| `docs/superpowers/plans/2026-04-28-inventory-credit-variance-v1.md` | This plan. |
| `docs/inventory_credit_v1_failure_register.md` | Snapshot of §4 below — single source of truth for failure handling. |
| `docs/inventory_credit_v1_gate_log.md` | Per-gate evidence log (created during execution). |

---

## 4. Failure Register

**Format:** Failure → Detection → System behavior → User-visible surface → Recovery action → Verification gate.

### 4.1 Category A — LionWheel / Pick Bridge

| # | Failure | Detection | System behavior | User-visible surface | Recovery | Gate |
|---|---|---|---|---|---|---|
| A1 | LionWheel API unavailable (HTTP 5xx, network timeout) | `fetchTaskDetail()` returns null | Skip task; emit `lw_pick_enrich_failed` exception (warning); mark `pick_enriched_at=NULL` so it retries next cycle | Exceptions inbox: "Could not fetch task detail for {lw_task_id}" | Auto-retry on next poll cycle (every job run); manual: re-run job. After 6 consecutive failures, severity escalates to critical | G1 |
| A2 | LionWheel returns malformed task payload (non-JSON / missing `task.order_items`) | `body.task?.order_items ?? []` returns empty when payload exists | Treat as zero-line task; `pick_enriched_at` is set (no retry); no FG_OUT posted | Exceptions inbox: `lw_pick_enrich_failed` if response is unparseable; `lw_pick_data_missing` per-line if `picked_quantity` absent | Manual review of LionWheel UI to confirm task state; no retry needed | G1 |
| A3 | Task is `ROUNDTRIP_DELIVERED` but no picked quantities (line.picked_quantity = null) | `row.qty_picked === null` after enrichment | Skip ledger insert; emit `lw_pick_data_missing` (warning) per-line; do NOT mark `pick_reconciled_at`; do NOT create credit_task | Exceptions inbox: "No picked_quantity for task {id} line {line_id}" | Manual investigation: was LionWheel picking module used? Or was the line added after enrichment? Resolve in LionWheel; system retries on next cycle | G1, G3 |
| A4 | Same task processed twice (concurrent or duplicate poll) | `pick_reconciled_at IS NOT NULL` filter on Phase 2 query | Phase 2 SELECT skips already-reconciled tasks; `ON CONFLICT (idempotency_key) DO NOTHING` on stock_ledger backstop | None (silent correct behavior) | None needed | G3 |
| A5 | Same order line processed twice (unit-level concurrency) | `idempotency_key = lw_fg_out_pick:{lw_task_id}:{lw_order_item_id}` UNIQUE | Second insert is no-op; `RETURNING movement_id` returns 0 rows; `result.fg_out_ledger_rows_emitted` not incremented; `oml.ledger_movement_id` already set | None | None needed | G3 |
| A6 | `picked_qty` is null after enrichment ran | Code path: `row.qty_picked === null && pick_enriched_at IS NOT NULL` | Skip ledger; emit `lw_pick_data_missing` warning; do NOT mark `pick_reconciled_at` so future enrichment can re-attempt if LionWheel updates | Admin sees per-line warning | LW data fix or manual close | G3 |
| A7 | `picked_qty` negative | `pickedQty < 0` (new invariant check, fails CHECK on stock_ledger) | Reject before INSERT; emit `lw_pick_invalid_qty` critical exception; do NOT mark line reconciled | Admin: critical exception "Negative picked qty for {task}:{line}" | Manual data fix in LionWheel; never auto-correct | G1, G3 |
| A8 | `picked_qty` non-numeric (string parsing fails) | `Number.isFinite(pickedQty)` returns false in enrichment phase | `lw_qty_picked` set to NULL (treated as A3) | A3 path | A3 path | G1 |
| A9 | `picked_qty > ordered_qty` (over-picking) | New invariant: `qty_picked <= qty_ordered` enforced before line processing | Post FG_OUT_PICK at `qty_picked` (truth wins); emit `lw_pick_overshoot` warning; do NOT create credit_task (`qty_missing < 0` is forbidden by §B5) | Admin warning: "Over-pick on {task}:{line}: ordered={x}, picked={y}" | Manual investigation: data error in LionWheel? Operator override? | G1, G3 |
| A10 | `oml.item_id IS NULL` (unresolved SKU) | Filter `AND oml.item_id IS NOT NULL` in delivered query | Line not selected; bundle path checked (§4.1.A11); else logged as info | Admin info exception (severity=info): `lw_unresolved_sku` (NOT shown to Dorin) | If real product: seed alias in `/admin/sku-aliases`. If non-product: mark `excluded_permanent` in `integration_sku_map` | G1 |
| A11 | Bundle line returned without mapping (bundle SKU, no `bundle_explosion_map` entry) | Query joins `bundle_explosion_map` LEFT JOIN; if `oml.item_id IS NULL` AND `external_sku` LIKE 'GTSET%' AND no map row → emit critical exception | NO ledger row (would silently lose bottle stock); critical exception fires; line stays unreconciled | Admin: critical exception "Bundle {sku} has no explosion mapping; pick of qty={x} skipped" | Tom must add row(s) to `bundle_explosion_map`; line will reprocess on next cycle (idempotency holds) | G2 |
| A12 | Bundle mapping creates duplicate ledger movements | New idempotency key shape: `lw_fg_out_pick:{lw_task_id}:{lw_order_item_id}:{component_item_id}` UNIQUE | Each component gets its own movement; UNIQUE prevents double-post if reconcile re-runs | None | None | G2 |
| A13 | Partial delivery updated after initial reconcile (LionWheel adjusts picked_qty post-delivery) | `pick_reconciled_at` is set; second enrichment would no-op | System does NOT detect this. Intentional v1 limitation | If LW data is later corrected, manual reversal required | Admin posts `WASTE_REVERSAL` or compensating entry on stock_ledger; document in `change_log` | G7 (operations gap) |
| A14 | Delivered task later changes status (e.g., ROUNDTRIP_DELIVERED → CANCELLED) | Periodic mirror update sets `lw_status` to non-DELIVERED | `pick_reconciled_at` still set; ledger row remains; exception emitted: `lw_post_delivery_status_change` (warning) | Admin warning per task | Manual reversal required (post-stock_ledger reversal + close credit_task as DISPUTED with reason) | G7 (operations gap) |
| A15 | Job timeout after stock_ledger INSERT but before credit_task INSERT | Transaction wraps both; ROLLBACK on error | All-or-nothing: either both committed or neither (FG_OUT_PICK and credit_task in same BEGIN/COMMIT) | None (atomicity preserved) | None needed | G1, G3 |
| A16 | Job timeout after credit_task INSERT but before marking line reconciled | Same transaction wraps `oml.ledger_movement_id` UPDATE + `credit_tasks` INSERT + `pick_reconciled_at` UPDATE | All atomic; ROLLBACK on error means none committed | None | None needed; next cycle reprocesses | G1, G3 |
| A17 | `current_stock_v2` does not update after ledger insert (trigger silently failed) | Post-insert SELECT on `current_stock_v2` shows pre-insert balance | Critical exception `projection_drift_detected`; halt subsequent cycles via break-glass | Admin: critical exception; dashboard tile flips red | Manual investigation; do not enable bridge again until trigger restored | G3, G4 |
| A18 | `rebuild_verifier()` returns non-zero after smoke | Run `rebuild_verifier()` post-smoke (G3, G4) | If non-zero: gate FAILS; bridge disabled until investigated | Admin: gate failure log | Investigate which item drifted; fix via reversal entries; re-run smoke | G3, G4 |

### 4.2 Category B — Stock truth

| # | Failure | Detection | System behavior | User-visible surface | Recovery | Gate |
|---|---|---|---|---|---|---|
| B1 | Stock goes negative after FG_OUT_PICK | Trigger on stock_ledger INSERT computes new `current_stock_v2.balance`; if `< 0` → emit `stock_ledger_invariant_violation` critical exception (does NOT block insert per existing semantics, but flags) | INSERT succeeds (audit trail preserved); exception fires; admin notified | Admin: critical exception "RAW-X stock went negative after FG_OUT_PICK {movement_id}" | Manual investigation: was a count overdue? Should bridge pause? Tom decides whether to post compensating ADJUSTMENT or accept | G3, G4 |
| B2 | Item is `inactive` but still mapped (`integration_sku_map.approval_status=approved` + `items.status='INACTIVE'`) | Pre-INSERT query checks `items.status` ; if not `ACTIVE` → emit `lw_pick_inactive_item` warning; skip ledger | Skip ledger; do NOT create credit_task; line remains unreconciled until item reactivated or alias removed | Admin warning per line | Either reactivate item OR remove the alias mapping; line auto-reprocesses on next cycle | G3 |
| B3 | Item is not stock-tracked but receives movement (e.g., `items.is_stock_tracked = false` if column added later) | v1: NOT enforced (column doesn't exist). Documented as deferred invariant | All Factory OS items are stock-tracked in v1 | None | If column added in v2, add CHECK | G7 (deferred) |
| B4 | Duplicate idempotency_key (same key, attempted twice) | `idempotency_key UNIQUE` on stock_ledger | INSERT fails with constraint violation → caught; treat as no-op (already posted) | None | None | G1, G3 |
| B5 | `event_at` / `captured_at` / date allowlist mismatch (e.g., task captured today but allowlist says yesterday) | `LW_PICK_BRIDGE_DATE_ALLOWLIST` filter: `om.captured_at::date = $allowlist_date` | Lines outside allowlist are not selected; processed on later cycles when allowlist is widened | Admin: dry-run log shows which lines were filtered out by date | None — intentional behavior | G3, G4 |
| B6 | Dry-run writes real stock by mistake (gate failure) | Test invariant: with `dry_run=true`, `stock_ledger` count before == count after | Critical: if dry-run posts real rows, the entire enable plan is suspect | Admin sees test failure | Investigation; do not enable bridge for production until fixed | G1 |
| B7 | Allowlist empty accidentally causes full production run | Code rule: if both `task_allowlist` AND `date_allowlist` are empty AND `LW_PICK_BRIDGE_ENABLED=true` AND `LW_PICK_BRIDGE_DRY_RUN=false` → full production run; require explicit env var `LW_PICK_BRIDGE_FULL_PRODUCTION=true` to enable this combination | Without `FULL_PRODUCTION=true`: bridge refuses to run; emits `pick_bridge_misconfig` critical exception with reason "no allowlist + full production not explicit" | Admin: critical config exception on every cycle until fixed | Set `FULL_PRODUCTION=true` (deliberate cutover) OR set allowlist | G7 |
| B8 | Skipped lines shown to Dorin and create noise | `lw_unresolved_sku` exception severity = `info`; Dorin's exceptions inbox filters severity ≥ `warning` by default | Dorin sees only operationally-actionable exceptions | None | None | G5 |
| B9 | Non-Factory-OS lines silently hidden from admin monitoring | Severity = `info` is filtered from default view but available with explicit "Show all severities" toggle; Dashboard tile "Unresolved LionWheel SKUs (this week)" | Admin sees count tile; Tom can drill in | Admin tile click-through to filtered exception list | G7 |

### 4.3 Category C — Credit task

| # | Failure | Detection | System behavior | User-visible surface | Recovery | Gate |
|---|---|---|---|---|---|---|
| C1 | Credit_task created without order reference | NOT NULL on `mirror_id` and `wp_order_id` (CHECK: `wp_order_id IS NOT NULL OR notes LIKE 'manual:%'`) | INSERT fails; reconciler logs error; line remains unreconciled (transaction rollback) | Admin: critical `credit_task_invariant_failed` exception | Investigate orders_mirror data integrity | G1, G3 |
| C2 | Credit_task created without customer display name | `wp_order_id` resolves to `orders_mirror.recipient_name` (or NULL); UI shows "לא ידוע" if NULL | Allowed (NULL recipient_name is real data); does not block | Dorin's screen shows "לקוח לא ידוע" | Manual: Dorin tags via `notes`; future: customer mapping admin (v2) | G5 |
| C3 | Duplicate credit_task for same order line | `UNIQUE (line_mirror_id)` on credit_tasks (already in 0089) | Second INSERT no-op (`ON CONFLICT DO NOTHING`); first task wins | None | None | G3 |
| C4 | `qty_missing = 0` but task created | CHECK constraint: `qty_missing > 0` (new in 0113) | INSERT fails; line marked reconciled without credit_task (correct); no exception | None | None | G3 |
| C5 | `picked_qty > ordered_qty` creates negative credit | CHECK constraint: `qty_picked <= qty_ordered` (new in 0113); reconciler also checks before insert | INSERT skipped on over-pick; A9 path fires | Admin warning | A9 path | G3 |
| C6 | Estimated amount uses missing/null price | API resolver: `items.last_price_per_unit_inc_vat` LEFT JOIN; if NULL → estimated_amount = NULL; UI shows "—" with tooltip "אין מחיר אחרון לאומדן" | Display "—"; allow Dorin to credit anyway (manual amount in Morning UI) | Dorin sees missing-price indicator | Tom sets price in admin; or Dorin manually computes in Morning | G5 |
| C7 | Dorin credits task but `gi_document_id` blank | Backend Zod: `gi_document_id: z.string().min(1)`; UI: required field | API rejects with 400; UI shows "חובה למלא מספר חשבונית" | Inline form error | None — invariant | G5 |
| C8 | Invalid `gi_document_id` format | Zod regex (Tom-locked v1: any non-empty string; v2 may add format) | v1: any string accepted; intentional liberal accept (Morning's IDs are not strictly typed) | None | Manual correction via UPDATE if pasted wrong (admin only) | G5 |
| C9 | Same `gi_document_id` pasted into two tasks | UNIQUE INDEX `credit_tasks_gi_document_id_unique` WHERE `gi_document_id IS NOT NULL` (new in 0113) | Second credit attempt fails with 409 Conflict; UI shows "מספר חשבונית כבר משויך לזיכוי אחר" | Dialog error | Dorin pastes correct ID, OR opens existing task in dispute | G5 |
| C10 | Dorin waives task without reason | Backend Zod: `reason: z.string().min(1)`; UI required field | API 400; UI inline error | Form error | None | G5 |
| C11 | Disputed task disappears from workflow | Default Dorin view filters `status IN ('PENDING')`; "Disputed" tab shows DISPUTED separately; SLA: disputed > 7 days emits `credit_task_dispute_stale` warning | Dorin sees disputed count badge; can switch tab | Resolve dispute by transitioning to CREDITED or WAIVED | G5, G7 |
| C12 | Status transition not audited | Trigger on credit_tasks UPDATE writes to `change_log` (new in 0112): record `old_status`, `new_status`, `changed_by`, `changed_at`, `notes_at_transition` | Every transition has audit row | Audit visible in admin (future) | None | G3 |
| C13 | User without role admin/planner can close credit task | Fastify route guard: `requireRole(['admin', 'planner'])` | API 403; UI shows "אין לך הרשאה" | API rejection | Tom assigns correct role to Dorin | G5 |

### 4.4 Category D — Dorin UI

| # | Failure | Detection | System behavior | User-visible surface | Recovery | Gate |
|---|---|---|---|---|---|---|
| D1 | Screen exists but Dorin cannot find it | UX review: nav entry "זיכויים ממתינים" with badge count of PENDING; appears in main sidebar; Tom-locked location | If badge > 0, sidebar shows red dot | Dorin sees nav item every time she logs in | None — nav lock | G5 |
| D2 | No search/filter by order/customer/product | UX requirement: search input filters across `wp_order_id`, `recipient_name`, `item_name_he` | Live filter on each keystroke (debounced 300ms) | Search bar at top of list | None | G5 |
| D3 | Source/freshness missing | Each row shows: delivered_at timestamp + "לפני X שעות" relative; >48h shows orange flag | Per-row freshness indicator | Visual color cue | None | G5 |
| D4 | "Estimated amount" looks like final amount | UI label: "סכום מוצע (אומדן)"; gray text; tooltip: "אומדן בלבד — הסכום הסופי בחשבונית הזיכוי ב-Morning" | Visual + textual distinction | Dorin trained on this distinction | None | G5 |
| D5 | Mobile layout unusable | Card view < 768px width; hits all critical actions; Playwright mobile viewport test | Card components on mobile, table on desktop | Mobile usability tested | None | G5 |
| D6 | Success toast appears but no durable confirmation/history | After credit/waive/dispute action: status badge updates immediately; row moves to filtered tab; audit row in `change_log` queryable from admin | Visual confirmation + DB-level durable audit | Audit visible in admin | None | G5 |
| D7 | Technical labels leak into UI | Locked Hebrew label register `src/lib/labels/credit-tasks-he.ts` with verbatim translations; lint rule fails on non-registered strings in UI components | Build fails if unregistered string detected | Localization complete | Add Hebrew label to register | G5 |
| D8 | Status visually unclear | Color + label + icon for each status: PENDING (yellow), CREDITED (green ✓), WAIVED (gray), DISPUTED (orange ⚠) | Clear differentiation | None | None | G5 |
| D9 | No "what do I do now?" action | Each row has primary action button: PENDING → "אשר וצור זיכוי" / DISPUTED → "פתח לבדיקה"; secondary actions in overflow menu | Primary CTA always visible | None | None | G5 |

### 4.5 Category E — PO / GR / Production side-effect failures

These are pre-existing system invariants that the credit corridor must NOT regress.

| # | Failure | Detection | System behavior | User-visible surface | Recovery | Gate |
|---|---|---|---|---|---|---|
| E1 | GR without PO works but no traceability | Existing: `goods_receipts.po_id IS NULL` allowed; `change_log` row written; `notes` field captures supplier/reason | Audit trail in change_log; admin can find by `notes LIKE` | Admin sees "PO-less GR" in submission history | None — by design | G7 |
| E2 | GR linked to PO updates stock but not PO `received_qty` | Existing trigger `trg_po_received_qty_increment` on stock_ledger GR_POSTED rows where `po_id IS NOT NULL` | Both atomic | None | None | G7 |
| E3 | Partial receipt falsely closes PO | Existing trigger: PO status moves to RECEIVED only when `received_qty >= ordered_qty` per line summed | Verified by pgTAP in PO corridor (migration 0049-0057) | None | None | G7 |
| E4 | Production actual consumes RM from wrong BOM version | Existing: `bom_version_id` pinned at form-open; stored on `production_actual` row; consumption rows use pinned version (not active) | Form snapshots BOM at open; pgTAP coverage | None | None | G7 |
| E5 | Production scrap semantics unclear to operator | Existing GAP-011 (open) — operator training required; not a v1 corridor concern | Form copy: "פסולת מורידה רק תוצרת — צריכת חומרי גלם לא מושפעת" | Tom-locked Hebrew copy in production-actual form | Operator training session (out of scope of this plan) | G7 (open gap) |
| E6 | Production output posts but BOM consumption fails | Transaction wraps both inserts; ROLLBACK on either failure (existing) | Atomic | None | None | G7 |
| E7 | Count adjustment overwrites truth without approval where threshold exceeded | Existing: `physical_counts` handler enforces threshold via `auto_post_threshold` policy; large discrepancies → exception + approval | Approval required above threshold | None | None | G7 |

### 4.6 Category F — Deployment / operations

| # | Failure | Detection | System behavior | User-visible surface | Recovery | Gate |
|---|---|---|---|---|---|---|
| F1 | Env flags misconfigured (e.g., `LW_PICK_BRIDGE_ENABLED=trueX`) | Boolean parse: `env.toLowerCase() === 'true'`; anything else = false; emit `pick_bridge_config_warning` if value present but not literal "true" or "false" | Defaults to `false`; warning logged | Admin warning at job start | Fix env var | G7 |
| F2 | `dry_run=true` AND `enabled=true` conflict | Resolution rule: `dry_run` wins; behavior: do not POST stock | Documented + tested | Job summary shows "DRY-RUN MODE" header | None | G1 |
| F3 | Edge Function deployed but old env still active | Per-deploy verification: deploy checks env vars match expected snapshot | If mismatch: alert posted to admin via `deployment_drift_detected` exception | Admin alert | Re-set env var via supabase functions secrets | G7 |
| F4 | Scheduled job cadence too slow / aggressive | Tom-locked cadence: `pg_cron` runs `lionwheel_poll` every 30 min; tunable via `pg_cron.schedule()` | Documented in `docs/integrations/lionwheel_mirror_contract.md` | None | Admin tunes via SQL | G7 |
| F5 | Logs not visible from portal | New page `/admin/jobs/runs` shows recent `jobs_runs` rows with summary; details clickable | jobs_runs already populated; UI pending | Admin can debug | Build admin/jobs page (out of v1, deferred to v1.5) | G7 (open) |
| F6 | No rollback switch | Break-glass already exists: `is_break_glass()` checked at job start; sets all jobs to skip; OR per-job env: `LW_PICK_BRIDGE_ENABLED=false` → bridge stops on next cycle | Break-glass tile on dashboard | Tom flips break-glass | G7 |
| F7 | No post-cutover observation dashboard | Dashboard tile pre-existing: "Pick Bridge — Last 24h" showing rows posted, credit_tasks created, exceptions fired; freshness < 1h | Dashboard refreshes every 5 min | Admin monitors | G7 |
| F8 | No owner for failed jobs | Tom-locked: failed `jobs_runs` (status='failed') → exception `job_run_failed` (warning) → exceptions inbox alerts admin (Tom) via daily digest | Daily digest email at 08:00 | Tom resolves | G7 |

---

## 5. DB Invariants

### 5.1 New invariants in this corridor

```sql
-- Migration 0113: credit_task_invariants

ALTER TABLE private_core.credit_tasks
  ADD CONSTRAINT credit_tasks_qty_missing_positive
    CHECK (qty_missing > 0);

ALTER TABLE private_core.credit_tasks
  ADD CONSTRAINT credit_tasks_qty_picked_nonnegative
    CHECK (qty_picked >= 0);

ALTER TABLE private_core.credit_tasks
  ADD CONSTRAINT credit_tasks_qty_ordered_positive
    CHECK (qty_ordered > 0);

ALTER TABLE private_core.credit_tasks
  ADD CONSTRAINT credit_tasks_picked_le_ordered
    CHECK (qty_picked <= qty_ordered);

ALTER TABLE private_core.credit_tasks
  ADD CONSTRAINT credit_tasks_qty_missing_arithmetic
    CHECK (qty_missing = qty_ordered - qty_picked);

CREATE UNIQUE INDEX credit_tasks_gi_document_id_unique
  ON private_core.credit_tasks (gi_document_id)
  WHERE gi_document_id IS NOT NULL;

ALTER TABLE private_core.credit_tasks
  ADD CONSTRAINT credit_tasks_gi_document_id_when_credited
    CHECK ((status = 'CREDITED' AND gi_document_id IS NOT NULL AND gi_matched_at IS NOT NULL)
        OR (status <> 'CREDITED'));

ALTER TABLE private_core.credit_tasks
  ADD CONSTRAINT credit_tasks_waive_reason_when_waived
    CHECK ((status = 'WAIVED' AND notes IS NOT NULL AND length(trim(notes)) > 0)
        OR (status <> 'WAIVED'));

ALTER TABLE private_core.credit_tasks
  ADD CONSTRAINT credit_tasks_closed_when_terminal
    CHECK ((status IN ('CREDITED','WAIVED') AND closed_at IS NOT NULL AND closed_by IS NOT NULL)
        OR (status NOT IN ('CREDITED','WAIVED')));
```

### 5.2 Audit trigger (migration 0112)

```sql
CREATE OR REPLACE FUNCTION private_core.fn_credit_task_audit()
RETURNS TRIGGER AS $$
BEGIN
  IF (OLD.status IS DISTINCT FROM NEW.status)
     OR (OLD.gi_document_id IS DISTINCT FROM NEW.gi_document_id)
     OR (OLD.notes IS DISTINCT FROM NEW.notes) THEN
    INSERT INTO private_core.change_log
      (entity_type, entity_id, field_name, old_value, new_value, changed_by, changed_at)
    VALUES
      ('credit_task', NEW.credit_task_id::text, 'status',
       OLD.status, NEW.status, NEW.closed_by, now()),
      ('credit_task', NEW.credit_task_id::text, 'gi_document_id',
       OLD.gi_document_id, NEW.gi_document_id, NEW.closed_by, now()),
      ('credit_task', NEW.credit_task_id::text, 'notes',
       OLD.notes, NEW.notes, NEW.closed_by, now());
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_credit_task_audit
  AFTER UPDATE ON private_core.credit_tasks
  FOR EACH ROW EXECUTE FUNCTION private_core.fn_credit_task_audit();
```

### 5.3 Stock ledger pre-existing invariants (must remain green)

- `idempotency_key` UNIQUE on `stock_ledger`
- `qty_delta != 0`
- `event_at` NOT NULL
- `posted_at` NOT NULL
- `movement_type` ENUM CHECK
- Trigger `trg_stock_ledger_to_current_balances` updates `current_stock_v2` synchronously
- Trigger `trg_stock_ledger_gr_reversal_po_decrement` (migration 0082, applied)

### 5.4 Bundle explosion invariants (migration 0114, conditional)

```sql
CREATE TABLE private_core.bundle_explosion_map (
  bundle_external_sku  text        NOT NULL,
  factory_os_item_id   text        NOT NULL REFERENCES private_core.items(item_id),
  qty_per_bundle       numeric(24,8) NOT NULL,
  active_from          timestamptz NOT NULL DEFAULT now(),
  active_to            timestamptz,
  created_by           uuid,
  created_at           timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (bundle_external_sku, factory_os_item_id, active_from),
  CHECK (qty_per_bundle > 0),
  CHECK (active_to IS NULL OR active_to > active_from)
);

CREATE INDEX idx_bundle_explosion_active
  ON private_core.bundle_explosion_map (bundle_external_sku)
  WHERE active_to IS NULL;
```

### 5.5 pick_bridge_dry_run_log (migration 0111)

```sql
CREATE TABLE private_core.pick_bridge_dry_run_log (
  log_id              uuid          PRIMARY KEY DEFAULT gen_random_uuid(),
  job_run_id          uuid          NOT NULL,
  cycle_at            timestamptz   NOT NULL DEFAULT now(),
  lw_task_id          text          NOT NULL,
  lw_order_item_id    text          NOT NULL,
  item_id             text          NOT NULL,           -- always Factory OS canonical
  bundle_external_sku text,                              -- non-null if explosion path
  qty_ordered         numeric(24,8) NOT NULL,
  qty_picked          numeric(24,8) NOT NULL,
  qty_missing         numeric(24,8) NOT NULL,
  would_post_movement boolean       NOT NULL,
  would_create_credit boolean       NOT NULL,
  reason_code         text          NOT NULL,           -- 'normal_pick' | 'over_pick' | 'zero_pick' | 'bundle_explode' | 'inactive_item' | 'no_pick_data'
  config_snapshot     jsonb         NOT NULL            -- env at cycle: dry_run, allowlist, enabled
);

CREATE INDEX idx_pick_bridge_dry_run_cycle
  ON private_core.pick_bridge_dry_run_log (cycle_at DESC);
```

### 5.6 rebuild_verifier (existing)

After every smoke gate (G3, G4): `SELECT rebuild_verifier()` MUST return `0`. Non-zero halts the gate.

---

## 6. Endpoint Contract

### 6.1 Base path: `/api/v1`

All endpoints require Supabase JWT via `Authorization: Bearer <token>`. `app_users.role` resolved from JWT `sub` claim.

### 6.2 `GET /api/v1/queries/credit-tasks`

**Query params:**
- `status` (optional, repeatable): `PENDING` | `CREDITED` | `WAIVED` | `DISPUTED`. Default: `PENDING`.
- `since` (optional, ISO timestamp): include only tasks where `created_at >= since`.
- `q` (optional, string): substring match against `wp_order_id`, `recipient_name`, `item_name_he`.
- `limit` (default 50, max 200), `offset` (default 0).

**Auth:** Role IN (`admin`, `planner`).

**Response 200:**

```json
{
  "rows": [
    {
      "credit_task_id": "uuid",
      "status": "PENDING",
      "wp_order_id": "WP-12345",
      "lw_task_id": "98765",
      "mirror_id": "uuid",
      "line_mirror_id": "uuid",
      "customer_display_name": "ABC חברה בע״מ",
      "item_id": "MUZA-APPZ-1L",
      "item_name_he": "מוזה אפלצינז",
      "qty_ordered": "10",
      "qty_picked": "8",
      "qty_missing": "2",
      "estimated_credit_amount_inc_vat": "92.50",
      "currency": "ILS",
      "delivered_at": "2026-04-27T14:23:00Z",
      "freshness_hours": 18.5,
      "freshness_flag": "fresh",
      "gi_document_id": null,
      "gi_matched_at": null,
      "notes": null,
      "created_at": "2026-04-27T15:00:00Z",
      "updated_at": "2026-04-27T15:00:00Z",
      "closed_at": null,
      "closed_by_display_name": null
    }
  ],
  "total": 14,
  "limit": 50,
  "offset": 0
}
```

**Notes:**
- `customer_display_name`: from `orders_mirror.recipient_name` LEFT JOIN; null → "לקוח לא ידוע" rendered by UI.
- `estimated_credit_amount_inc_vat`: computed as `qty_missing × items.last_price_per_unit_inc_vat`; null if price absent.
- `freshness_flag`: `fresh` (< 24h), `aging` (24-48h), `stale` (>= 48h).

### 6.3 `GET /api/v1/queries/credit-tasks/:id`

**Auth:** Role IN (`admin`, `planner`).

**Response 200:** Same shape as a list row, plus:

```json
{
  "credit_task_id": "uuid",
  ...all list-row fields...,
  "audit_history": [
    {
      "changed_at": "2026-04-27T16:00:00Z",
      "changed_by_display_name": "Dorin",
      "field_name": "status",
      "old_value": "PENDING",
      "new_value": "CREDITED"
    }
  ],
  "lw_task_url": "https://members.lionwheel.com/tasks/98765",
  "raw_lw_payload": null
}
```

**Response 404:** if id not found.

### 6.4 `POST /api/v1/mutations/credit-tasks/:id/credit`

**Auth:** Role IN (`admin`, `planner`).

**Request:**

```json
{
  "gi_document_id": "GI-2026-001234",
  "notes": null
}
```

**Validation (Zod):**
- `gi_document_id`: `z.string().min(1).max(120)`
- `notes`: `z.string().max(2000).nullable().optional()`

**Pre-conditions:**
- Task `status = 'PENDING'`
- Task not already credited (UNIQUE on `gi_document_id`)

**On success (200):**

```json
{
  "credit_task_id": "uuid",
  "status": "CREDITED",
  "gi_document_id": "GI-2026-001234",
  "gi_matched_at": "2026-04-28T10:00:00Z",
  "closed_at": "2026-04-28T10:00:00Z",
  "closed_by": "uuid",
  "closed_by_display_name": "Dorin"
}
```

**Errors:**
- 400: missing/invalid `gi_document_id`
- 403: insufficient role
- 404: task not found
- 409: task not in `PENDING` state OR `gi_document_id` already used

### 6.5 `POST /api/v1/mutations/credit-tasks/:id/waive`

**Request:**

```json
{
  "reason": "מחיר נמוך מדי לזיכוי — נספג"
}
```

**Validation:**
- `reason`: `z.string().min(1).max(2000)` (REQUIRED — cannot waive without reason; per failure C10)

**On success (200):** Same shape as credit, but `status='WAIVED'`, `gi_document_id=null`, `notes=reason`.

### 6.6 `POST /api/v1/mutations/credit-tasks/:id/dispute`

**Request:**

```json
{
  "notes": "Maxim מאשר שמסר את כל הכמות; פער טכני ב-LionWheel"
}
```

**Validation:**
- `notes`: `z.string().min(1).max(2000)` (REQUIRED)

**On success (200):** `status='DISPUTED'`, `notes=notes`. Note: DISPUTED is non-terminal; task stays in workflow until resolved.

### 6.7 `GET /api/v1/queries/admin/pick-bridge-dry-run`

**Query params:**
- `since` (ISO ts, default: 24h ago)
- `limit` (default 100)

**Auth:** Role = `admin` only.

**Response 200:**

```json
{
  "rows": [
    {
      "log_id": "uuid",
      "cycle_at": "2026-04-28T08:00:00Z",
      "lw_task_id": "98765",
      "item_id": "MUZA-APPZ-1L",
      "qty_ordered": "10",
      "qty_picked": "8",
      "qty_missing": "2",
      "would_post_movement": true,
      "would_create_credit": true,
      "reason_code": "normal_pick",
      "bundle_external_sku": null,
      "config_snapshot": {
        "dry_run": true,
        "enabled": true,
        "task_allowlist": [],
        "date_allowlist": null,
        "full_production": false
      }
    }
  ],
  "summary": {
    "cycle_count": 4,
    "would_post_total": 18,
    "would_credit_total": 5,
    "skipped_reasons": {
      "no_pick_data": 1,
      "inactive_item": 0,
      "over_pick": 0
    }
  }
}
```

### 6.8 Backend route registration

```typescript
// api/src/credit-tasks/route.ts
fastify.get('/api/v1/queries/credit-tasks', { preHandler: requireRole(['admin','planner']) }, listHandler);
fastify.get('/api/v1/queries/credit-tasks/:id', { preHandler: requireRole(['admin','planner']) }, getHandler);
fastify.post('/api/v1/mutations/credit-tasks/:id/credit', { preHandler: requireRole(['admin','planner']) }, creditHandler);
fastify.post('/api/v1/mutations/credit-tasks/:id/waive', { preHandler: requireRole(['admin','planner']) }, waiveHandler);
fastify.post('/api/v1/mutations/credit-tasks/:id/dispute', { preHandler: requireRole(['admin','planner']) }, disputeHandler);
fastify.get('/api/v1/queries/admin/pick-bridge-dry-run', { preHandler: requireRole(['admin']) }, dryRunReadHandler);
```

---

## 7. UI Acceptance Criteria

### 7.1 Route locked

- **Path:** `/credits/pending`
- **Title (Hebrew):** "זיכויים ממתינים"
- **Subtitle (Hebrew):** "פערים בליקוט שדורשים אישור או הוספת מספר חשבונית זיכוי"
- **Sidebar nav entry:** "זיכויים" (with PENDING count badge)

### 7.2 Locked Hebrew labels (in `src/lib/labels/credit-tasks-he.ts`)

```typescript
export const CREDIT_LABELS_HE = {
  page_title: 'זיכויים ממתינים',
  page_subtitle: 'פערים בליקוט שדורשים אישור או הוספת מספר חשבונית זיכוי',
  status: {
    PENDING: 'ממתין לאישור',
    CREDITED: 'בוצע זיכוי',
    WAIVED: 'ויתור',
    DISPUTED: 'בבדיקה',
  },
  cols: {
    customer: 'לקוח',
    order_id: 'מס׳ הזמנה',
    item: 'פריט',
    ordered: 'הוזמן',
    picked: 'לוקט',
    missing: 'חוסר',
    estimated: 'סכום מוצע (אומדן)',
    delivered_at: 'תאריך מסירה',
    status: 'סטטוס',
    actions: 'פעולות',
  },
  actions: {
    credit: 'אשר וצור זיכוי',
    waive: 'ותר',
    dispute: 'שלח לבדיקה',
  },
  dialog: {
    credit_title: 'יצירת זיכוי',
    gi_document_id_label: 'מספר חשבונית זיכוי מ-Morning',
    gi_document_id_placeholder: 'הדבק כאן את המספר אחרי שהפקת את החשבונית',
    notes_label: 'הערות (אופציונלי)',
    confirm: 'אשר',
    cancel: 'ביטול',
    waive_title: 'ויתור על זיכוי',
    waive_reason_label: 'סיבת ויתור (חובה)',
    waive_reason_placeholder: 'לדוגמה: סכום נמוך מדי, לקוח ויתר',
    dispute_title: 'שליחה לבדיקה',
    dispute_notes_label: 'הערה (חובה)',
  },
  errors: {
    gi_document_id_required: 'חובה למלא מספר חשבונית',
    gi_document_id_already_used: 'מספר חשבונית כבר משויך לזיכוי אחר',
    waive_reason_required: 'חובה למלא סיבת ויתור',
    dispute_notes_required: 'חובה למלא הערה',
    not_pending: 'לא ניתן לבצע פעולה — הסטטוס אינו ממתין לאישור',
    forbidden: 'אין לך הרשאה',
    unknown: 'שגיאה לא צפויה. נסה שוב.',
  },
  empty: {
    no_pending: 'אין כרגע זיכויים ממתינים לאישור.',
    no_results: 'לא נמצאו תוצאות עם המסננים האלו.',
  },
  freshness: {
    fresh: 'טרי',
    aging: 'התקרר',
    stale: 'התיישן',
  },
  unknown_customer: 'לקוח לא ידוע',
  no_price: '—',
  no_price_tooltip: 'אין מחיר אחרון לאומדן — חשב ידנית ב-Morning',
  estimated_tooltip: 'אומדן בלבד — הסכום הסופי בחשבונית הזיכוי ב-Morning',
} as const;
```

### 7.3 List page (`/credits/pending`)

| Requirement | Details |
|---|---|
| Default filter | `status=PENDING` |
| Tabs | "ממתין" (default) / "בוצע" / "ויתור" / "בבדיקה" — count badge per tab |
| Search bar | Live filter on order id / customer / product (debounced 300ms) |
| Date filter | "מ-" / "עד-" (date pickers) |
| Sort | Default: oldest first (fairness); column-click toggleable |
| Empty state | Hebrew message + illustration |
| Loading state | Skeleton rows |
| Error state | "לא הצלחנו לטעון. נסה שוב" + retry button |
| Mobile | Below 768px: card view, one card per row, primary action button visible |

### 7.4 Per-row content (desktop table)

| Column | Source | Format |
|---|---|---|
| לקוח | `customer_display_name` | text; "לקוח לא ידוע" if null (italic gray) |
| מס׳ הזמנה | `wp_order_id` | clickable → opens LionWheel UI in new tab |
| פריט | `item_name_he` | text |
| הוזמן | `qty_ordered` | numeric, 0 decimals if integer |
| לוקט | `qty_picked` | numeric, 0 decimals if integer |
| חוסר | `qty_missing` | numeric, bold |
| סכום מוצע (אומדן) | `estimated_credit_amount_inc_vat` | NIS format with currency suffix; "—" if null + tooltip |
| תאריך מסירה | `delivered_at` + `freshness_flag` | "27/04 14:23" + colored chip (fresh=green / aging=yellow / stale=orange) |
| סטטוס | `status` | colored badge per §4.4 D8 |
| פעולות | per status | primary CTA visible |

### 7.5 Detail page (`/credits/pending/[id]`)

| Section | Content |
|---|---|
| Header | Customer, order id (LW link), item, ordered/picked/missing/estimated, status badge |
| Variance card | Visual breakdown: ordered (gray bar) vs picked (green bar) vs missing (red bar) |
| Source freshness panel | LionWheel delivery time, last reconcile time, raw LW task id |
| Audit timeline | All `change_log` rows for this task in chronological order, with actor name |
| Actions | Same buttons as list row, plus "חזור לרשימה" |

### 7.6 Action dialogs (modals)

#### Credit dialog
- Title: "יצירת זיכוי"
- Body: shows ordered, picked, missing, estimated amount (read-only)
- Required field: "מספר חשבונית זיכוי מ-Morning" (text input)
- Optional field: "הערות"
- Buttons: "אשר" (primary) / "ביטול"
- After "אשר": API call → on success, close dialog, toast "הזיכוי נשמר", row updates to CREDITED + moves tabs

#### Waive dialog
- Title: "ויתור על זיכוי"
- Body: shows missing amount (warning text: "אישור ויתור — לא ייווצר זיכוי")
- Required field: "סיבת ויתור"
- Buttons: "אשר ויתור" (warning color) / "ביטול"

#### Dispute dialog
- Title: "שליחה לבדיקה"
- Body: explanatory text "ההזמנה תועבר לטאב 'בבדיקה'. ניתן לחזור אליה ולפעול בהמשך"
- Required field: "הערה"
- Buttons: "שלח" / "ביטול"

### 7.7 Acceptance test scenarios (Playwright `tests/e2e/credits-pending.spec.ts`)

| Scenario | Expected |
|---|---|
| Anonymous user visits /credits/pending | 307 → /login |
| Operator role visits | 403 |
| Admin/planner visits empty state | "אין כרגע זיכויים ממתינים" message |
| Admin views list with 5 PENDING tasks | Table renders 5 rows, badge shows "5" |
| Admin uses search "MUZA" | Filtered to MUZA items only |
| Admin clicks order id | New tab opens LionWheel URL |
| Admin clicks "אשר וצור זיכוי" → empty gi_document_id | Inline error "חובה למלא מספר חשבונית" |
| Admin completes credit dialog | Success toast, row moves to CREDITED tab |
| Admin attempts to credit twice with same `gi_document_id` | API 409, dialog shows "מספר חשבונית כבר משויך" |
| Admin clicks "ותר" without reason | Dialog blocks submit |
| Admin completes waive | Status WAIVED, row moves to ויתור tab |
| Admin disputes a task | Status DISPUTED, row in בבדיקה tab |
| Mobile viewport 375px wide | Card layout, primary CTA visible per card |
| Stale task (delivered > 48h ago) | Orange freshness chip |

---

## 8. Dry-Run Report Shape

### 8.1 Per-cycle output

Every `reconcileAfterPoll()` invocation with `dry_run=true` writes one row per affected line to `pick_bridge_dry_run_log`, plus one summary row in `jobs_runs.summary`.

### 8.2 jobs_runs.summary (cycle-level)

```json
{
  "job_name": "lionwheel_poll",
  "cycle_at": "2026-04-28T08:00:00Z",
  "mode": "DRY_RUN",
  "config": {
    "enabled": true,
    "dry_run": true,
    "task_allowlist": ["98765"],
    "date_allowlist": null,
    "full_production": false
  },
  "lines_evaluated": 12,
  "would_post_fg_out_pick": 8,
  "would_create_credit_task": 3,
  "skipped": {
    "unresolved_sku": 4,
    "no_pick_data": 0,
    "inactive_item": 0,
    "bundle_no_mapping": 0,
    "over_pick": 0
  },
  "items_affected_unique_count": 5,
  "total_qty_would_decrement": "120.50",
  "potential_credit_lines": 3,
  "potential_credit_estimated_total_inc_vat": "287.40"
}
```

### 8.3 Per-line dry-run rows (table `pick_bridge_dry_run_log`)

See §5.5. One row per (`lw_task_id`, `lw_order_item_id`, `item_id`) tuple that was evaluated in this cycle.

### 8.4 Admin-facing surface

Endpoint `GET /api/v1/queries/admin/pick-bridge-dry-run` returns last 24h of cycles. Renders in admin page (deferred to v1.5; v1 reads via SQL or admin endpoint manually).

### 8.5 Interpretation guide for G1 PASS

A dry-run report is "G1 PASS" if:

- ≥10 cycles ran with no SQL errors
- `lines_evaluated` is non-zero across cycles (i.e., real LW data was processed)
- `would_post_fg_out_pick` shows expected order of magnitude (Tom-judgment, baseline ≥ 5 lines/day for typical week)
- `skipped.unresolved_sku` count corresponds to known unresolved aliases (sanity check against `/admin/sku-aliases`)
- `skipped.no_pick_data` is 0 OR matches known LW data quality issues
- Zero `stock_ledger` rows inserted (verify: row count before == row count after, scoped by movement_type='FG_OUT_PICK' and posted_at >= cycle_start)
- Zero `credit_tasks` rows inserted

If any check fails: G1 = FAIL. Investigate before promoting to G2.

---

## 9. Go/No-Go Gates Checklist

### G1 — Dry-Run PASS

**Setup:**
- `LW_PICK_BRIDGE_ENABLED=true`
- `LW_PICK_BRIDGE_DRY_RUN=true`
- Allowlists empty
- Migrations 0111, 0112, 0113 applied
- Backend deployed with dry-run gating

**Run:** Let `pg_cron` execute `lionwheel_poll` ≥10 cycles (≥5 hours wall-clock if 30-min cadence).

**PASS criteria (ALL required):**
- [ ] Zero `stock_ledger` rows with `movement_type='FG_OUT_PICK'` posted during dry-run window
- [ ] Zero new `credit_tasks` rows during dry-run window
- [ ] ≥10 rows in `pick_bridge_dry_run_log` with `cycle_at` in window
- [ ] No SQL errors in `jobs_runs` (status='succeeded' for every cycle)
- [ ] `pick_bridge_dry_run_log.reason_code` distribution makes sense (Tom verifies)
- [ ] Skipped count for `unresolved_sku` matches manual count from `/admin/sku-aliases` (sanity)
- [ ] `rebuild_verifier()` returns 0
- [ ] Pre-existing operations (GR, Waste, Production Actual) still post correctly (regression check: post one of each manually, verify ledger writes)

**Sign-off:** governor + Tom.

### G2 — Bundle decision PASS

**Setup:** W4 inspection complete (one-time fetch of `/tasks/show/{lw_task_id}` for a known GTSET-containing order).

**Decision tree:**

**(a) If LionWheel returns bundle as exploded bottle lines** (each component as own line with FG SKU):
- [ ] Document evidence (sample payload saved in `docs/integrations/lionwheel_bundle_inspection_2026-04-XX.md`)
- [ ] No `bundle_explosion_map` migration needed
- [ ] Mark migration 0114 as N/A
- **G2 PASS**

**(b) If LionWheel returns bundle as single line** (GTSET SKU, single `picked_quantity`):
- [ ] Tom provides composition for all 9 GTSETs (CSV or direct entry)
- [ ] Migration 0114 applied
- [ ] `bundle_explosion_map` seeded with 27+ rows (avg 3 components per bundle)
- [ ] Reconciliation code updated to detect bundles + emit N rows per bundle
- [ ] Idempotency key extended: `lw_fg_out_pick:{task}:{line}:{component}`
- [ ] pgTAP test for bundle explosion (3 cases: simple bundle, partial bundle picked, missing mapping → critical exception)
- [ ] Dry-run cycle of bundle order shows correct N-line explosion in `pick_bridge_dry_run_log`
- **G2 PASS**

**Sign-off:** Tom (composition data) + W1 (code/migration) + governor.

### G3 — Single task smoke PASS

**Setup:**
- G1 + G2 complete
- `LW_PICK_BRIDGE_DRY_RUN=false`
- `LW_PICK_BRIDGE_TASK_ALLOWLIST=<single_known_task_id>` (Tom selects a recently-delivered low-risk task)
- `LW_PICK_BRIDGE_ENABLED=true`

**Run:** One `lionwheel_poll` cycle (or wait for cron).

**PASS criteria (ALL required):**
- [ ] Exactly N `stock_ledger` rows posted with `movement_type='FG_OUT_PICK'` (where N = number of mapped lines in the task)
- [ ] Each row has correct `idempotency_key` shape
- [ ] `current_stock_v2` decremented by sum of `qty_picked` per item (verify by SELECT before/after)
- [ ] `credit_tasks` created for any line where `picked < ordered` (verify count)
- [ ] `orders_mirror.pick_reconciled_at` set
- [ ] `orders_mirror_lines.ledger_movement_id` set per line
- [ ] `rebuild_verifier()` returns 0
- [ ] No critical exceptions emitted
- [ ] Replay test: re-run cycle → idempotent (no new rows)
- [ ] Same task, different line in different ordering: idempotency key collision check

**Sign-off:** governor + Tom.

### G4 — Full-day smoke PASS

**Setup:**
- G3 PASS
- `LW_PICK_BRIDGE_TASK_ALLOWLIST=` (clear)
- `LW_PICK_BRIDGE_DATE_ALLOWLIST=YYYY-MM-DD` (Tom picks a recent past day with known task volume)

**Run:** Wait one full poll cycle.

**PASS criteria (ALL required):**
- [ ] Number of FG_OUT_PICK rows matches expected (Tom calculates from LW UI)
- [ ] All affected `current_stock_v2` rows match expected delta
- [ ] `credit_tasks` count matches expected variance count
- [ ] `rebuild_verifier()` returns 0
- [ ] No critical exceptions
- [ ] Re-run cycle → idempotent
- [ ] Tom spot-checks 3 random tasks: `qty_picked` in ledger row matches LW UI
- [ ] No regressions on GR/Waste/Production paths

**Sign-off:** governor + Tom.

### G5 — Dorin UI sign-off PASS

**Setup:**
- G4 PASS (real `credit_tasks` exist for Dorin to look at)
- Backend endpoints (§6) deployed
- Portal `/credits/pending` deployed

**Test session:** Tom + Dorin live at terminal.

**PASS criteria (ALL required):**
- [ ] Dorin finds `/credits/pending` from sidebar within 10 seconds without help
- [ ] Dorin understands the meaning of each column without explanation (translation OK if needed)
- [ ] Dorin opens a PENDING task; understands ordered/picked/missing instantly
- [ ] Dorin successfully credits a real task (paste-back from Morning) end-to-end
- [ ] Status updates immediately, row moves to CREDITED tab
- [ ] Dorin successfully waives a task with reason
- [ ] Dorin successfully disputes a task
- [ ] Dorin attempts to credit twice with same `gi_document_id`: error message clear, no system damage
- [ ] Mobile viewport check: Dorin can perform credit action on phone
- [ ] All Hebrew labels match register; no leaked English/technical strings
- [ ] Dorin says: "כן, אני מוכנה להשתמש בזה יומיום" (Hebrew approval)

**Sign-off:** Dorin (verbal + written acknowledgment) + Tom + governor.

### G6 — Manual Morning paste-back PASS

**Setup:** G5 PASS.

**Test:** Tom or Dorin issues a real credit invoice in Morning UI for one PENDING task.

**PASS criteria (ALL required):**
- [ ] Morning credit invoice created successfully (Dorin's existing flow)
- [ ] `gi_document_id` from Morning copied to portal credit dialog
- [ ] Submit → API returns 200
- [ ] `credit_tasks.status='CREDITED'`, `gi_document_id` saved, `gi_matched_at` set
- [ ] `change_log` row written for the transition
- [ ] No silent errors in any layer
- [ ] Customer receives credit invoice from Morning (verify via Morning UI / customer email)

**Sign-off:** Tom + Dorin.

### G7 — 7-day allowlist observation PASS

**Setup:** G6 PASS. Bridge running with `DATE_ALLOWLIST` rolling daily (Tom updates env each day) OR with `TASK_ALLOWLIST` covering 50+ tasks/day.

**PASS criteria (ALL required, observed over 7 consecutive days):**
- [ ] Zero unexplained ledger rows
- [ ] Zero stock projection drifts (`rebuild_verifier()` = 0 every day at 23:00)
- [ ] Zero PRODUCTION-impact regressions (GR / Waste / Production Actual paths green)
- [ ] All credit_tasks created have valid customer + item + qty_missing
- [ ] Dorin processes ≥1 credit per day (or zero days with no variance, demonstrating NULL flow OK)
- [ ] No critical exceptions of categories A11 (bundle), B1 (negative stock), B6 (dry-run leak), B7 (misconfig), C1 (orphan task)
- [ ] No more than 3 warning exceptions per day in pick bridge category
- [ ] Tom subjectively comfortable: "the system is doing what I think it's doing" (Tom-Lens calibration)

**Sign-off:** Tom (final cutover decision).

### G8 — Production cutover (post-G7)

**Setup:**
- Clear `LW_PICK_BRIDGE_DATE_ALLOWLIST` and `LW_PICK_BRIDGE_TASK_ALLOWLIST`
- Set `LW_PICK_BRIDGE_FULL_PRODUCTION=true`
- `LW_PICK_BRIDGE_ENABLED=true`, `LW_PICK_BRIDGE_DRY_RUN=false`

**Verification immediately post-cutover:**
- [ ] First post-cutover cycle runs and produces expected ledger writes (admin spot-check)
- [ ] Dashboard tile "Pick Bridge — Last 24h" shows non-zero values
- [ ] No critical exceptions
- [ ] `rebuild_verifier()` = 0

**This is the production-ready milestone.** RUNTIME_READY signal can be emitted: `RUNTIME_READY(InventoryCreditVarianceV1)`.

---

## 10. Implementation Sequence

### Phase 1 — W1: Plan-update + DB invariants + dry-run/allowlist code

#### Task 1.1: Verify pre-existing pick bridge filter

**Files:**
- Read: `api/src/integrations/lionwheel/reconciliation.ts:200-220`
- Read: `supabase/functions/factory_os_jobs/index.ts:850-870`

- [ ] **Step 1.1.1:** Confirm `oml.item_id IS NOT NULL` filter present in both files. If absent in either → BLOCKER, escalate.
- [ ] **Step 1.1.2:** Document evidence in `docs/inventory_credit_v1_gate_log.md` with line numbers and snippets.

#### Task 1.2: Migration 0111 — `pick_bridge_dry_run_log`

**Files:**
- Create: `db/migrations/0111_pick_bridge_dry_run_log.sql`
- Create: `db/tests/0111_pick_bridge_dry_run_log.test.sql`

- [ ] **Step 1.2.1:** Write pgTAP failing test (table exists, columns + types match §5.5, indexes present). Expected: FAIL.
- [ ] **Step 1.2.2:** Write migration per §5.5.
- [ ] **Step 1.2.3:** Apply migration to live DB (pooled). Verify tap test passes (≥6/6 assertions green).
- [ ] **Step 1.2.4:** Commit: `feat(db): 0111 pick_bridge_dry_run_log table`.

#### Task 1.3: Migration 0112 — credit_tasks audit trigger

- [ ] **Step 1.3.1:** Write pgTAP failing test (trigger fires on UPDATE, change_log row created). Expected: FAIL.
- [ ] **Step 1.3.2:** Write migration per §5.2.
- [ ] **Step 1.3.3:** Apply + verify pgTAP green (≥4/4).
- [ ] **Step 1.3.4:** Commit: `feat(db): 0112 credit_tasks audit trigger`.

#### Task 1.4: Migration 0113 — credit_task invariants

- [ ] **Step 1.4.1:** Write pgTAP failing test for each CHECK constraint (boundary + violation cases). Expected: FAIL.
- [ ] **Step 1.4.2:** Write migration per §5.1.
- [ ] **Step 1.4.3:** Apply + verify pgTAP green (≥10/10 covering all 7 CHECK constraints + UNIQUE).
- [ ] **Step 1.4.4:** Verify existing credit_tasks rows (from 0089) still satisfy new CHECKs (none should violate; if any do → fix data first).
- [ ] **Step 1.4.5:** Commit: `feat(db): 0113 credit_tasks invariant constraints`.

#### Task 1.5: Reconciliation.ts — config additions

**Files:** Modify `api/src/integrations/lionwheel/reconciliation.ts`.

- [ ] **Step 1.5.1:** Add fields to `ReconcilerConfig`: `dry_run: boolean`, `task_allowlist: string[]`, `date_allowlist: string | null`, `full_production: boolean`. Update `DEFAULT_RECONCILER_CONFIG` defaults: `dry_run=false`, `task_allowlist=[]`, `date_allowlist=null`, `full_production=false`.
- [ ] **Step 1.5.2:** Update Phase 2 SELECT to apply allowlist filters when non-empty.
- [ ] **Step 1.5.3:** Add config validation: if `enabled=true && dry_run=false && allowlists empty && full_production=false` → return early with `pick_bridge_misconfig` critical exception.
- [ ] **Step 1.5.4:** Wrap each INSERT (stock_ledger, credit_tasks) in conditional: if `dry_run=true` → write to `pick_bridge_dry_run_log` instead.
- [ ] **Step 1.5.5:** Update result accounting: separate counters for dry-run vs real.
- [ ] **Step 1.5.6:** Commit: `feat(lw): pick bridge dry-run + allowlist`.

#### Task 1.6: Reconciliation.ts — invariant pre-checks

- [ ] **Step 1.6.1:** Add per-line guard: `if (pickedQty < 0)` → emit `lw_pick_invalid_qty` critical, skip line.
- [ ] **Step 1.6.2:** Add per-line guard: `if (pickedQty > orderedQty)` → emit `lw_pick_overshoot` warning, post FG_OUT_PICK at `pickedQty`, do NOT create credit_task (qty_missing would be negative).
- [ ] **Step 1.6.3:** Add per-line guard: SELECT `items.status` before insert; if not `ACTIVE` → emit `lw_pick_inactive_item` warning, skip.
- [ ] **Step 1.6.4:** Commit: `feat(lw): pick bridge invariant pre-checks`.

#### Task 1.7: Edge Function (`factory_os_jobs/index.ts`) — mirror config

- [ ] **Step 1.7.1:** Add env var reads: `LW_PICK_BRIDGE_DRY_RUN`, `LW_PICK_BRIDGE_TASK_ALLOWLIST` (comma-split), `LW_PICK_BRIDGE_DATE_ALLOWLIST`, `LW_PICK_BRIDGE_FULL_PRODUCTION`.
- [ ] **Step 1.7.2:** Apply identical gating logic as `reconciliation.ts` (DRY by extracting shared helper if reasonable; otherwise mirror carefully).
- [ ] **Step 1.7.3:** Test deploy to Supabase functions; verify env vars read correctly via `supabase functions logs`.
- [ ] **Step 1.7.4:** Commit: `feat(edge): pick bridge dry-run + allowlist`.

#### Task 1.8: Skipped-line severity downgrade

- [ ] **Step 1.8.1:** Modify `lw_pick_enrich_failed` and `lw_pick_data_missing` to severity=`info` for the unresolved-SKU subset; keep `warning` only for hard failures.
- [ ] **Step 1.8.2:** Verify exceptions inbox default filter (`severity >= warning`) hides info-level rows.
- [ ] **Step 1.8.3:** Commit: `feat(lw): downgrade unresolved SKU severity to info`.

#### Task 1.9: Test matrix `lionwheel_pick_bridge_dry_run.test.ts`

- [ ] **Step 1.9.1:** Test: with `dry_run=true`, no ledger rows inserted (use real DB; assert count delta = 0).
- [ ] **Step 1.9.2:** Test: with `dry_run=true`, rows written to `pick_bridge_dry_run_log` with correct shape.
- [ ] **Step 1.9.3:** Test: with `task_allowlist=[X]`, only task X processed.
- [ ] **Step 1.9.4:** Test: with `date_allowlist='YYYY-MM-DD'`, only matching captured_at dates processed.
- [ ] **Step 1.9.5:** Test: misconfig (no allowlist + no full_production) → exception fired, no rows.
- [ ] **Step 1.9.6:** Test: `dry_run=true && enabled=true` → dry-run wins (no rows posted).
- [ ] **Step 1.9.7:** Run all 6 tests; all green.
- [ ] **Step 1.9.8:** Commit: `test(lw): pick bridge dry-run + allowlist matrix`.

#### Task 1.10: Test matrix `lionwheel_pick_bridge_invariants.test.ts`

- [ ] **Step 1.10.1:** Test: negative pickedQty → critical exception, no insert.
- [ ] **Step 1.10.2:** Test: pickedQty > orderedQty → FG_OUT_PICK posted at pickedQty, no credit_task.
- [ ] **Step 1.10.3:** Test: items.status='INACTIVE' → warning, no insert.
- [ ] **Step 1.10.4:** Test: idempotency replay → no double rows.
- [ ] **Step 1.10.5:** Run all 4 tests; green.
- [ ] **Step 1.10.6:** Commit: `test(lw): pick bridge invariant matrix`.

#### Task 1.11: Deploy backend + edge function to Railway/Supabase staging

- [ ] **Step 1.11.1:** Push `gt-factory-os/main`; Railway auto-deploys.
- [ ] **Step 1.11.2:** Verify `GET /health` HTTP 200.
- [ ] **Step 1.11.3:** Deploy edge function: `supabase functions deploy factory_os_jobs`.
- [ ] **Step 1.11.4:** Set env vars: `LW_PICK_BRIDGE_ENABLED=true`, `LW_PICK_BRIDGE_DRY_RUN=true`, allowlists empty.
- [ ] **Step 1.11.5:** Wait for next `pg_cron` cycle (≤30 min).
- [ ] **Step 1.11.6:** Verify dry-run log rows appear; commit gate-log entry "G1 entered".

### Phase 2 — W4 bundle inspection (no runtime code)

#### Task 2.1: Inspect LionWheel bundle payload

**Files:**
- Create: `docs/integrations/lionwheel_bundle_inspection_2026-04-XX.md`

- [ ] **Step 2.1.1:** Identify a recent delivered task that contained a GTSET bundle. Use `orders_mirror.lw_status='ROUNDTRIP_DELIVERED'` + `orders_mirror_lines` JOIN where some `external_sku LIKE 'GTSET%'`.
- [ ] **Step 2.1.2:** Fetch `https://members.lionwheel.com/api/v1/tasks/show/{lw_task_id}.json?key={API_KEY}` (use sandbox or PROD with read-only).
- [ ] **Step 2.1.3:** Save raw JSON to inspection doc.
- [ ] **Step 2.1.4:** Document tier: tier-A (single line, GTSET SKU + integer picked_quantity) OR tier-B (already exploded — multiple lines per bundle, each with FG SKU).
- [ ] **Step 2.1.5:** If tier-A: list all 9 unique GTSET SKUs Tom needs to map.
- [ ] **Step 2.1.6:** If tier-B: confirm at least 3 sample bundles all expand correctly; G2 path is "no migration needed".
- [ ] **Step 2.1.7:** Commit: `docs(lw): bundle inspection 2026-04-XX`.

### Phase 3 — W1: bundle mapping (only if tier-A)

#### Task 3.1 (conditional, tier-A only): Migration 0114

- [ ] **Step 3.1.1:** pgTAP failing test for `bundle_explosion_map` shape per §5.4.
- [ ] **Step 3.1.2:** Write migration 0114 per §5.4.
- [ ] **Step 3.1.3:** Apply + verify pgTAP green.
- [ ] **Step 3.1.4:** Tom provides composition (CSV or admin entry); seed at least 9 bundle rows.
- [ ] **Step 3.1.5:** Update `reconciliation.ts` (and edge function) to query `bundle_explosion_map` for unresolved bundle SKUs; emit N FG_OUT_PICK rows + 1 credit_task per component (if missing).
- [ ] **Step 3.1.6:** Update idempotency key shape: include `component_item_id`.
- [ ] **Step 3.1.7:** Add critical exception path: bundle SKU detected but no map row → `lw_bundle_no_mapping`.
- [ ] **Step 3.1.8:** pgTAP/node:test for bundle explosion (3 cases: simple, partial-pick, missing-mapping).
- [ ] **Step 3.1.9:** Commit: `feat(lw): bundle explosion via bundle_explosion_map`.

### Phase 4 — W1: credit_tasks endpoints

#### Task 4.1: Schemas

**Files:**
- Create: `api/src/credit-tasks/schemas.ts`

- [ ] **Step 4.1.1:** Write Zod schemas for request bodies (credit/waive/dispute) + response shapes per §6.
- [ ] **Step 4.1.2:** Export TypeScript types.
- [ ] **Step 4.1.3:** Commit: `feat(api): credit-tasks zod schemas`.

#### Task 4.2: Handler — list + get

**Files:**
- Create: `api/src/credit-tasks/handler.ts`
- Create: `api/test/credit_tasks.test.ts`

- [ ] **Step 4.2.1:** Write failing test: GET list returns rows for PENDING; respects auth/role.
- [ ] **Step 4.2.2:** Implement `listHandler` with pagination + filters per §6.2.
- [ ] **Step 4.2.3:** Verify test green.
- [ ] **Step 4.2.4:** Write failing test: GET detail returns single row + audit_history.
- [ ] **Step 4.2.5:** Implement `getHandler`.
- [ ] **Step 4.2.6:** Verify green.
- [ ] **Step 4.2.7:** Commit: `feat(api): credit-tasks list+get`.

#### Task 4.3: Handler — credit

- [ ] **Step 4.3.1:** Failing test: POST /credit with valid body transitions PENDING→CREDITED.
- [ ] **Step 4.3.2:** Failing test: missing gi_document_id → 400.
- [ ] **Step 4.3.3:** Failing test: not in PENDING → 409.
- [ ] **Step 4.3.4:** Failing test: duplicate gi_document_id → 409.
- [ ] **Step 4.3.5:** Failing test: insufficient role → 403.
- [ ] **Step 4.3.6:** Implement `creditHandler` with all guards.
- [ ] **Step 4.3.7:** Verify all 5 tests green.
- [ ] **Step 4.3.8:** Commit: `feat(api): credit-tasks credit endpoint`.

#### Task 4.4: Handler — waive

- [ ] **Step 4.4.1:** Failing test: POST /waive with reason → WAIVED.
- [ ] **Step 4.4.2:** Failing test: missing reason → 400.
- [ ] **Step 4.4.3:** Failing test: not in PENDING → 409.
- [ ] **Step 4.4.4:** Implement.
- [ ] **Step 4.4.5:** Verify green.
- [ ] **Step 4.4.6:** Commit: `feat(api): credit-tasks waive endpoint`.

#### Task 4.5: Handler — dispute

- [ ] **Step 4.5.1:** Failing test: POST /dispute with notes → DISPUTED.
- [ ] **Step 4.5.2:** Failing test: missing notes → 400.
- [ ] **Step 4.5.3:** Implement.
- [ ] **Step 4.5.4:** Verify green.
- [ ] **Step 4.5.5:** Commit: `feat(api): credit-tasks dispute endpoint`.

#### Task 4.6: Audit verification

- [ ] **Step 4.6.1:** Failing test: each transition writes change_log row.
- [ ] **Step 4.6.2:** Verify trigger from 0112 fires on each handler call.
- [ ] **Step 4.6.3:** Commit: `test(api): credit-tasks audit chain`.

#### Task 4.7: Admin dry-run read endpoint

- [ ] **Step 4.7.1:** Failing test: GET /admin/pick-bridge-dry-run returns rows + summary.
- [ ] **Step 4.7.2:** Failing test: non-admin → 403.
- [ ] **Step 4.7.3:** Implement.
- [ ] **Step 4.7.4:** Verify green.
- [ ] **Step 4.7.5:** Commit: `feat(api): admin dry-run read`.

#### Task 4.8: Route registration + deploy

- [ ] **Step 4.8.1:** Wire all 6 routes in `route.ts`.
- [ ] **Step 4.8.2:** Run full backend test suite; verify zero regressions.
- [ ] **Step 4.8.3:** Push to main; Railway deploys.
- [ ] **Step 4.8.4:** Live smoke: `curl` each endpoint with real JWT; verify 200 / 401 / 403 expected.
- [ ] **Step 4.8.5:** Commit: `feat(api): credit-tasks routes wired`.

### Phase 5 — W2: Dorin UI

This phase requires explicit RUNTIME_READY signal from W1 first. Per `EXECUTION_POLICY.md`, W2 enters Mode B for this single named form.

#### Task 5.1: W1 emit signal

- [ ] **Step 5.1.1:** W1 writes `RUNTIME_READY(InventoryCreditVarianceV1-Backend)` to `.claude/state/runtime_ready.json`.
- [ ] **Step 5.1.2:** Tom approves W2 Mode B dispatch.

#### Task 5.2: W2 — Hebrew label register

**Files:** Create `src/lib/labels/credit-tasks-he.ts`.

- [ ] **Step 5.2.1:** Write per §7.2 verbatim.
- [ ] **Step 5.2.2:** Add ESLint rule: no string literals matching Hebrew regex outside the register.
- [ ] **Step 5.2.3:** Commit.

#### Task 5.3: W2 — API client + hooks

**Files:** Create `src/lib/api/credit-tasks.ts`.

- [ ] **Step 5.3.1:** TanStack Query hooks: `useCreditTasks(filters)`, `useCreditTask(id)`, `useCreditTaskCredit(id)`, `useCreditTaskWaive(id)`, `useCreditTaskDispute(id)`.
- [ ] **Step 5.3.2:** Strict TypeScript types from backend Zod schemas.
- [ ] **Step 5.3.3:** Commit.

#### Task 5.4: W2 — List page

**Files:** Create `src/app/(planner)/credits/pending/page.tsx` + components.

- [ ] **Step 5.4.1:** Implement per §7.3, §7.4.
- [ ] **Step 5.4.2:** Mobile responsive.
- [ ] **Step 5.4.3:** Loading/error/empty states.
- [ ] **Step 5.4.4:** Status tabs with badges.
- [ ] **Step 5.4.5:** Commit.

#### Task 5.5: W2 — Detail page

**Files:** Create `src/app/(planner)/credits/pending/[id]/page.tsx`.

- [ ] **Step 5.5.1:** Implement per §7.5.
- [ ] **Step 5.5.2:** Audit timeline component.
- [ ] **Step 5.5.3:** Commit.

#### Task 5.6: W2 — Action dialogs

- [ ] **Step 5.6.1:** Credit dialog per §7.6.
- [ ] **Step 5.6.2:** Waive dialog.
- [ ] **Step 5.6.3:** Dispute dialog.
- [ ] **Step 5.6.4:** Form validation matches backend Zod.
- [ ] **Step 5.6.5:** Toast notifications on success.
- [ ] **Step 5.6.6:** Inline errors per `errors` register.
- [ ] **Step 5.6.7:** Commit.

#### Task 5.7: W2 — Sidebar nav entry

**Files:** Modify portal sidebar manifest.

- [ ] **Step 5.7.1:** Add "זיכויים" entry with PENDING count badge.
- [ ] **Step 5.7.2:** Commit.

#### Task 5.8: Playwright E2E

**Files:** Create `tests/e2e/credits-pending.spec.ts`.

- [ ] **Step 5.8.1:** Implement all 14 scenarios per §7.7.
- [ ] **Step 5.8.2:** Run against live backend; all green.
- [ ] **Step 5.8.3:** Commit.

#### Task 5.9: Deploy + Mode B exit

- [ ] **Step 5.9.1:** Build clean (`pnpm build`).
- [ ] **Step 5.9.2:** Push to portal main; Vercel deploys.
- [ ] **Step 5.9.3:** Live verify `/credits/pending` 307→/login (auth gate).
- [ ] **Step 5.9.4:** W2 emits Mode B exit signal.

### Phase 6 — Operational gates

#### Task 6.1: G1 (dry-run)

- [ ] Per §9 G1 checklist.
- [ ] Update gate log.

#### Task 6.2: G2 (bundle decision)

- [ ] Per §9 G2 checklist.
- [ ] Update gate log.

#### Task 6.3: G3 (single task smoke)

- [ ] Per §9 G3 checklist.
- [ ] Update gate log.

#### Task 6.4: G4 (full-day smoke)

- [ ] Per §9 G4 checklist.
- [ ] Update gate log.

#### Task 6.5: G5 (Dorin UI sign-off)

- [ ] Per §9 G5 checklist with Dorin live.
- [ ] Update gate log.

#### Task 6.6: G6 (manual paste-back)

- [ ] Per §9 G6 checklist.
- [ ] Update gate log.

#### Task 6.7: G7 (7-day observation)

- [ ] Per §9 G7 checklist over 7 days.
- [ ] Daily gate-log update.

#### Task 6.8: G8 (production cutover)

- [ ] Set `LW_PICK_BRIDGE_FULL_PRODUCTION=true`.
- [ ] Clear allowlists.
- [ ] Verify first cycle.
- [ ] Emit `RUNTIME_READY(InventoryCreditVarianceV1)`.
- [ ] Update CURRENT_STATE.md with closure entry.

---

## 11. Verification Standard

For every task, every gate, every claim of completion, the report must distinguish:

| Section | Meaning |
|---|---|
| **What is proven** | Direct evidence: pgTAP green count, HTTP response captured, ledger row queried + asserted, smoke test passed with verified output |
| **What is inferred** | Reasonable assumptions based on system design (e.g., "trigger fires synchronously per existing schema"). Must be flagged so reviewers know to verify if doubted |
| **What failed** | Anything attempted that did not meet criteria; do not omit or rephrase |
| **What was skipped** | Intentional skips, documented (e.g., "F5 admin/jobs dashboard deferred to v1.5") |
| **What user can see** | Operator/Dorin/admin-visible surface. UI rendering ≠ proof; operator-completed action == proof |
| **What rollback exists** | Specific revert path: which migration reverses, which env var disables, which break-glass triggers |

**False-green guards:**
- "Tests pass" ≠ feature works. Pass criteria for v1: a real Dorin closes a real credit_task created by real LW data, and the change reaches `change_log`.
- "API returns 200" ≠ correct. Verify the DB state after the call.
- "Migration applied" ≠ invariant holds. Run violation tests.
- "RUNTIME_READY emitted" ≠ Gate PASS. Gate PASS is per §9 checklist with Tom's sign-off.

**Tom-Lens calibration applied:**
- A. **Small things that will hurt later:** documented per failure register (categories A-F).
- B. **Tom Tax:** dialog UX requires no SQL knowledge; CSV import for bundle composition (if tier-A) is bulk-pasteable; gate logs are queryable, not just logged to console; admin can disable bridge with single env var (no redeploy required if Supabase secrets used).

---

## 12. Rollback Plan

### 12.1 Per-migration rollback

| Migration | Rollback approach | Side effects |
|---|---|---|
| 0111 (`pick_bridge_dry_run_log`) | DROP TABLE | None — no FKs from this table |
| 0112 (audit trigger) | DROP TRIGGER + FUNCTION | Future credit_tasks updates won't audit; existing change_log rows remain |
| 0113 (invariants) | ALTER TABLE DROP CONSTRAINT (×7) + DROP INDEX | Existing data may contain newly-illegal values; verify before re-applying |
| 0114 (bundle map, conditional) | DROP TABLE; revert reconciliation code | If applied, FG_OUT_PICK rows from bundle explosion remain in ledger; reverse via WASTE_REVERSAL if data error |

### 12.2 Per-feature kill-switches

| Switch | Effect | Lag |
|---|---|---|
| `LW_PICK_BRIDGE_ENABLED=false` | Bridge stops on next cycle (≤30 min) | ≤30 min |
| `LW_PICK_BRIDGE_DRY_RUN=true` | Bridge logs but does not post (≤30 min) | ≤30 min |
| `is_break_glass()=true` (existing global) | All jobs skip (LW poll, GI poll, Shopify, freshness) | Immediate next cycle |
| Disable portal route | Add `redirect()` from `/credits/pending` to `/login` with banner | Immediate redeploy |

### 12.3 Data corrections

If FG_OUT_PICK rows posted incorrectly:
1. Identify by `idempotency_key LIKE 'lw_fg_out_pick:%'` + `posted_at` window.
2. Post compensating reversal: same balance_key, opposite `qty_delta`, `movement_type='WASTE_REVERSAL'`, `notes='Reverses {original_movement_id}: {reason}'`.
3. Verify `current_stock_v2` returns to expected value.
4. Verify `rebuild_verifier()` = 0.

If credit_tasks created incorrectly:
1. UPDATE status='WAIVED', notes='Auto-created in error: {reason}', closed_by=admin, closed_at=now().
2. Audit trigger writes change_log row.

### 12.4 Full corridor rollback

If post-G8 issues require pulling the plug:
1. Set `LW_PICK_BRIDGE_ENABLED=false` (immediate stop).
2. Operate in manual mode (current state pre-cutover).
3. Reverse migrations in order: 0114 → 0113 → 0112 → 0111 (sequenced; 0112 audit trigger drop is non-destructive).
4. Revert reconciliation.ts + factory_os_jobs/index.ts to pre-corridor commit.
5. Document incident in `docs/lessons_learned.md`.

---

## 13. Open / deferred items (out of v1 by design)

These are documented here so future versions (v1.5, v2) inherit the right context.

| Item | Severity | Deferral reason | Re-evaluate at |
|---|---|---|---|
| Morning API auto-issue for type 305 | P1 | Requires §10.1 sandbox PASS + §11 questions 1/2/3/6/7 | After v1 stable 4 weeks |
| Morning API auto-issue for type 320 | P1 | Requires §10.2 sandbox PASS + §11 question 8 | After 305 path proven |
| `customer_credit_drafts` 13-state machine | P2 | Replaced by simpler `credit_tasks` 4-state in v1 | If v1 limits hit |
| `green_invoice_documents` mirror | P2 | Not needed without Morning auto-issue | v2 |
| `document/created` webhook | P2 | Not needed without mirror | v2 |
| Shopify ↔ Morning customer mapping admin | P2 | Manual paste-back replaces in v1 | v2 |
| 5-type SKU classification framework | P3 | Binary IN/IGNORED sufficient | Indefinite |
| Bundle composition admin UI | P3 | CSV seed sufficient if 9 bundles | If bundle catalog grows |
| Admin/jobs dashboard live page | P2 | Logs accessible via SQL in v1 | v1.5 |
| Late-pick / late-deliver alert SLAs | P2 | Tom-deferred until volume known | After v1 cutover |
| Production scrap operator training | P2 | GAP-011, pre-existing | Operator rollout |

---

## 14. Plan boundary

This plan does NOT cover:
- Production Actual / Goods Receipt / Waste Adjustment / Physical Count form changes (existing systems).
- Planning engine logic (Gate 5 closed).
- Forecast workspace (Gate 4).
- Any code path that would require Morning API authentication.
- Any code path that would require subscribing to Morning webhooks.
- Bundle SKU catalog management UI.
- Customer-master maintenance.

If during execution any of these surface as blockers, **HALT and re-plan**. Do not silently expand scope.

---

## 15. Document change log

| Date | Author | Change |
|---|---|---|
| 2026-04-28 | Tom + Claude | Plan authored after Tom-locked policy: Factory OS = single product truth; non-Factory-OS SKUs ignored except bundles. Production-grade Failure Register format applied per Tom's spec. Six deliverables included: Failure Register, DB invariants, endpoint contract, UI acceptance, dry-run shape, Go/No-Go gates. |
