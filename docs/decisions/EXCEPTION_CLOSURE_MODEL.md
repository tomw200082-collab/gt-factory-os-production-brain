# GT Factory OS — Exception Closure Model

> **Authority layer:** decision proposal. **Status: `PROPOSED` — awaiting Tom ratification.**
> Until Tom merges this PR and adds a pointer from `LOCKED_DECISIONS.md`, this document is a
> proposal, not authority. It does not relax any locked decision and does not change live state.
>
> **Owner (proposed):** governance + integration-boundary lanes (W4) for emission rules;
> backend-db lane (W1) for resolution mechanisms; Tom for threshold policy.
> **Proposed:** 2026-06-23.
>
> **Cross-references (read these alongside this doc):**
> - Taxonomy + dedup + auto-resolution contract: `gt-factory-os/docs/integrations/exceptions_contract.md`
> - Auto-resolve precedent (the pattern to generalize): `gt-factory-os/api/src/jobs/freshness_check.ts`
> - Operator playbooks: `gt-factory-os/docs/runbooks/critical_exception_handling.md`
> - Portal lane routing (where rows surface): `gt-factory-os-portal/src/features/inbox/meta.ts` (`rowLane`, `rowFamily`)
> - Portal fetch + deep-link map: `gt-factory-os-portal/src/features/inbox/client.ts`

---

## 1. Why this document exists

The exceptions table (`private_core.exceptions`, migration `0010`) is the single surface every
integration, job, ledger check, form, and export audit writes to. Today the lifecycle is partly
self-healing (freshness/drift auto-resolve; SKU-alias approve auto-resolves; credit/waste/count
decisions resolve) but **incompletely** so. The result is drift: transient failures that recover
leave orphaned `open` rows, audit-only events accumulate forever, and routine-magnitude form
events reach the operator when they should auto-post.

Tom's directive (2026-06-23): *go over every exception type and decide how we solve each one
**permanently**, so that in steady state every exception resolves itself or via Tom's approval —
instead of accumulating as noise.*

This document answers that. It defines a closed set of **five closure mechanisms**, assigns every
known category to exactly one, and lists the concrete gaps (with lane ownership) that stand between
today's behaviour and a self-clearing inbox.

---

## 2. The goal (end-state)

> **A self-clearing inbox.** In steady state the count of *actionable* rows trends to zero. Only
> two of the five closure mechanisms ever surface to a human, and both are one-tap. Everything
> else clears without a human touch.

The metric of success is **steady-state actionable backlog**, watched alongside the existing
metrics in `critical_exception_handling.md §Metrics`:

| Metric | Healthy | Watch | Bad |
|---|---|---|---|
| `open`/`acknowledged` rows in the **actionable** lane, age > 48h | 0 | 1–3 | 4+ |
| `open` **transient** (B) rows older than 2 sync cycles | 0 | 1–2 | 3+ |
| `open` **info/audit** (E) rows in the table at all | 0 | — | any |

---

## 3. The five closure mechanisms (the binding model)

Every category resolves by **exactly one** mechanism. Only **C** and **D** appear in the working
(actionable) inbox; **A**, **B**, **E** live in `system_health` / `diagnostics` and never count as
operator work.

| # | Mechanism | Definition | Reaches a human? | Closure trigger |
|---|---|---|---|---|
| **A** | **Auto on healthy tick** | Condition is a live health signal; clears when the signal returns to healthy | ❌ never | next freshness/rebuild/projection tick |
| **B** | **Transient → auto-clear on next success** | A recoverable failure (auth/rate-limit/network/parse) | ❌ unless stuck | next successful poll/push/ingest for that integration |
| **C** | **Map-once → permanent** | An unrecognised key (SKU/supplier/variant) that needs a durable mapping recorded once | ✅ one-tap, once per *new* key | operator approves the mapping → auto-resolve; never recurs for that key |
| **D** | **Tom-decision → resolve** | A genuine yes/no judgement with real consequence | ✅ one-tap | the decision posts → auto-resolve in the same transaction |
| **E** | **Info / audit-only** | A record of something that happened; nothing to "resolve" | ❌ never | should not be an exception at all; if kept, auto-expire after a retention window |

### 3.1 Lane mapping (portal `rowLane`)

- **A, B** → `system_health` lane (collapsed "System & diagnostics" section).
- **E** → `diagnostics` lane.
- **C, D** → `actionable` lane (the working inbox).

The portal already routes by `rowFamily` → `rowLane`. The closure model makes the *backend
severity + category family* the source of truth so the portal routing stays correct by
construction (see §6, Gap 5).

---

## 4. The closure invariant (proposed addition to change control)

> **No category may be emitted unless it declares, in `exceptions_contract.md §2`, its closure
> mechanism (A–E), its `dedupe_key` pattern, its lane, and — for D — its threshold policy.**

This extends the existing change-control rule in `exceptions_contract.md §"Change control"`
("new categories must be added to §2 before the code that writes them is merged") with the
closure declaration. A category with no closure mechanism is a noise generator by definition and
must not ship.

---

## 5. Full per-category specification

Status legend: ✅ implemented · ◐ partial · ⚠️ gap (see §6).

> **Note — taxonomy drift:** the category names below are the ones **actually emitted in code**
> (verified against `api/src/integrations/**`, `jobs/freshness_check.ts`, `boms/publish.ts`, and the
> portal `meta.ts`). Several differ from the names in `exceptions_contract.md §2` (e.g. code emits
> `shopify_unmapped_item`, contract says `shopify_missing_mapping`; code emits `supplier_price_anomaly`,
> contract says `gi_threshold_exceeded`). **Reconciling §2 to the emitted set is Gap 0.**

### 5.1 Mechanism A — auto on healthy tick (never reaches a human)

| Category | Source | Sev | dedupe_key | Closure | Today |
|---|---|---|---|---|---|
| `lionwheel_stale` `shopify_stale` `gi_stale` `rebuild_stale` `export_stale` `forecast_stale` | freshness_check | warn→crit | `<cat>:singleton` | freshness tick returns fresh → `auto_resolved` | ✅ |
| `freshness_heartbeat_stale` | job.meta | crit | singleton | external heartbeat recovers | ◐ (emits; verify auto-clear) |
| `shopify_drift` | integration.shopify | warn→crit | `shopify_drift:<item_id>` | platform re-push → diff 0 → auto-resolve | ◐ (re-push exists; confirm auto-resolve) |
| `projection_drift` | ledger.integrity | crit | `proj_drift:<balance_key>` | `rebuild_verifier` returns 0 → auto-resolve | ✅ (migration 0013 wrapper) |
| `negative_on_hand` / `stock_negative` | ledger.integrity | warn | `neg_oh:<balance_key>` | balance ≥ 0 after next insert → auto-resolve | ◐ (contract-stated; verify trigger) |

### 5.2 Mechanism B — transient, auto-clear on next success (never reaches a human unless stuck)

| Category | Source | Sev | Proposed dedupe_key | Closure | Today |
|---|---|---|---|---|---|
| `lionwheel_auth_failure` `lionwheel_auth_expired` `lionwheel_rate_limit_stuck` `lionwheel_schema_drift` `lionwheel_capped_window_gap` `lionwheel_payload_invalid_sku` `lionwheel_payload_invalid_picked_quantity` `lw_pick_enrich_failed` `lw_status_drift` | integration.lionwheel | warn/crit | `lionwheel:<class>:singleton` | next successful poll auto-resolves all open transient rows for the integration | ⚠️ **Gap 1** |
| `shopify_auth_failure` `shopify_rate_limit_stuck` `shopify_api_version_drift` `shopify_network_failure` `shopify_available_v2_unhealthy` `shopify_available_auth_fail` `shopify_available_rate_limit` `shopify_available_payload_invalid` | integration.shopify | warn/crit | `shopify:<class>:singleton` | next successful push auto-resolves | ⚠️ **Gap 1** |
| `gi_api_failure` `gi_auth_failure` `gi_rate_limit_stuck` `gi_mirror_insert_failed` `gi_price_activation_failed` | integration.green_invoice | warn/crit | `gi:<class>:singleton` | next successful ingest auto-resolves | ⚠️ **Gap 1** |

**Credential-expiry refinement:** `*_auth_expired` should be *prevented*, not reported after the
fact — a proactive pre-expiry warning (≥7 days before token expiry) routed to the digest, not an
`open` exception after the integration is already down. Genuinely stuck transients (≥3 consecutive
failures) escalate via the existing alert digest (`runAlertDigest`), **not** by accumulating in the
inbox.

### 5.3 Mechanism C — map-once → permanent (one-tap, once per new key)

| Category | Source | dedupe_key | Closure | Today |
|---|---|---|---|---|
| `lionwheel_unknown_sku` | integration.lionwheel | `lw_sku:<sku>` | approve alias in `/admin/sku-aliases` → `resolved`; reconciliation closes historical | ✅ |
| `shopify_unmapped_item` | integration.shopify | `shopify_unmapped_item:<sku>` | approve alias → `resolved` | ✅ |
| `shopify_variant_not_found` | integration.shopify | `shopify_variant:<sku>` | inline decision in inbox → resolve | ◐ |
| `gi_unmapped_supplier` | integration.green_invoice | `gi_supplier:<gi_supplier_id>` | set `green_invoice_supplier_id` in `/admin/suppliers` → **should auto-resolve** | ⚠️ **Gap 2** (resolve is manual today) |
| `shopify_available_mapping_missing` / `_stale` | integration.shopify | `shopify_afs:<item_id>` | record AfS mapping → auto-resolve | ⚠️ **Gap 2** (no operator mapping surface; routes to integrations health) |
| `lw_pick_data_missing` | integration.lionwheel | `lw_pick:<order_line>` | upstream pick data arrives / operator supplies → resolve | ◐ |
| `recommendation_missing_supplier_mapping` `missing_bom` | planning prep | per item | map supplier / activate BOM → auto-resolve before next run | ◐ |

**Permanent-fix amplifier:** add **fuzzy auto-suggest** so each unrecognised key arrives with a
single best-guess mapping pre-filled → the operator's action collapses to one confirm tap. Once a
key is mapped, the durable alias store guarantees it never recurs.

### 5.4 Mechanism D — Tom-decision → resolve (the only rows that should reach Tom)

| Category | Source | dedupe_key | Closure | Today |
|---|---|---|---|---|
| `lionwheel_credit_needed` | integration.lionwheel | `credit:<exception/order_line>` | `/inbox/credit/[id]` approve→`pending_gi_action`→`gi_draft_created`; reject→`resolved` | ✅ |
| `count_large_variance` | form.physical_count | `pc:<submission_id>` | approve/reject physical count → resolve | ✅ |
| `positive_adjustment` `loss_above_threshold` | form.waste_adjustment | `waste:<submission_id>` | approve/reject waste → resolve | ✅ |
| `po_line_over_receipt` | receiving | `po_over:<po_line_id>` | one-tap "accept overage" / corrective adjustment → auto-resolve | ⚠️ **Gap 3** (routes to PO list; no terminal action, no auto-resolve) |
| `supplier_price_anomaly` | price.greeninvoice | `price:<supplier_id>:<component_id>` | one-tap "accept new price" (activates price + resolves) / "reject" | ⚠️ **Gap 3** (held for review; no one-tap) |
| `lionwheel_order_note` | integration.lionwheel | `note:<order_id>` | read + acknowledge inline | ◐ |
| `gi_expense_review` | integration.green_invoice | `gi_exp:<invoice_id>` | inline triage → resolve | ◐ |
| `gi_non_ils_currency` | integration.green_invoice | `gi_fx:<invoice_id>` | review → acknowledge (v1) | ◐ |
| `alias_revoked_with_dependencies` | admin | `alias_rev:<alias_id>` | decide re-map / accept → resolve | ◐ |
| `purchase_recommendation_pending` `production_recommendation_pending` | planning | per rec | approve/reject in planning run → resolve | ✅ (approval rows) |

**Volume control is policy, not code (§7).** D rows are legitimate — the point is not to eliminate
them but to ensure (a) each is one-tap with full context inline, (b) it auto-resolves the instant
the decision posts, and (c) thresholds are tuned so only genuine outliers reach Tom.

### 5.5 Mechanism E — info / audit-only (should not be exceptions)

| Category | Emitted at | Verdict |
|---|---|---|
| `bom_version_published` | `boms/publish.ts:510` | move to `activity_log`; if kept, info + auto-expire |
| `gi_draft_created` | credit/GI lifecycle | lifecycle *state*, not an exception — keep on `credit_decisions.state` only |
| `ledger_at_anchor_review` `lw_pick_at_anchor_review` `lw_pick_pre_anchor_skipped` | reconciliation | audit records → `activity_log`; if kept, auto-expire |
| `inventory_movement_proposal` | planning/stock | proposal, not anomaly → its own surface, not exceptions |
| `form_duplicate_idempotency` | form dedup | info; auto-expire (it's a no-op confirmation) |
| `retroactive_write_before_anchor` | ledger.integrity | keep as **warning** (real integrity signal), not info |

**Permanent fix:** audit-only events belong in `activity_log`, not `exceptions`. Emitting them as
exceptions is a category error that manufactures permanent noise. For any that must stay (e.g. for
dashboard counting), add a daily **retention sweep** that flips `info`-severity rows older than the
retention window (proposed: 30 days) to `auto_resolved`.

---

## 6. The gaps (engineering backlog, with lane ownership)

| # | Gap | Fix | Lane | Needs Tom |
|---|---|---|---|---|
| **0** | `exceptions_contract.md §2` taxonomy is stale vs emitted categories | Reconcile §2 to the verified emitted set; add closure column | W4 (docs/contracts) | ratify §2 rewrite |
| **1** | Transient (B) failures never auto-clear on recovery | On every successful poll/push/ingest, run the freshness-style `autoResolve()` over open transient rows for that integration; switch transient dedupe to per-class singleton | W1 (api) | no (additive) |
| **2** | Map (C) gaps for GI supplier + Shopify AfS don't auto-resolve on mapping | Wire supplier-map + AfS-map writes to auto-resolve matching open rows (mirror the sku-map handler) | W1 (api) + portal (surface) | no |
| **3** | Decision (D) gaps: `po_line_over_receipt` + `supplier_price_anomaly` have no one-tap terminal action | Add inline accept/reject that posts the decision and auto-resolves | W1 (api) + portal (UX) | thresholds for price-anomaly |
| **4** | Info (E) rows accumulate forever | Move audit events to `activity_log`; add retention sweep for any kept info rows | W1 (api) + W4 (jobs) | ratify retention window |
| **5** | No backend guarantee that severity/family → portal lane | Emit a `lane` hint (or lock severity per category) so portal routing can't drift | W4 (contract) + portal | no |

All five are **backend / contract lanes** (`gt-factory-os`, W1/W4) plus thin portal surfacing.
None are authored here. Per the boot kernel, each requires Tom's explicit approval to merge, and
**no autonomous push to production**.

---

## 7. Threshold calibration — the master policy lever (Tom)

The single biggest noise reducer is tuning the auto-post thresholds so routine, trustworthy
events auto-post **without** emitting a D exception. These live in `planning_policy` and are
Tom's to set. Proposed starting values (to be ratified, not assumed):

| Policy | Governs | Today | Proposed start | Effect |
|---|---|---|---|---|
| `waste_auto_post_threshold` | `loss_above_threshold` | (current value) | small loss auto-posts; only large losses → approval | fewer D rows |
| physical-count auto-post band | `count_large_variance` | (current value) | counts within ±X% or ±N units auto-post | fewer D rows |
| positive-adjustment policy | `positive_adjustment` | always approval | optional: auto-post tiny "found stock" under N units | fewer D rows |
| price-change threshold | `supplier_price_anomaly` | (current value) | only changes > Y% held for accept/reject | fewer D rows |

These four numbers are the highest-leverage, zero-code change in the whole plan. They are listed
as **open questions** in §9 for Tom to fill.

---

## 8. Phased rollout

1. **Phase 0 — Policy (Tom, immediate, no code):** ratify the four thresholds in §7. Biggest
   noise drop, instant.
2. **Phase 1 — Transient auto-clear (Gap 1, W1):** generalise the freshness `autoResolve()` to all
   integrations on success. Removes the largest source of orphaned `open` rows.
3. **Phase 2 — Audit-out + retention (Gaps 4, W1/W4):** move E events to `activity_log`; add the
   retention sweep.
4. **Phase 3 — Complete C/D terminal actions (Gaps 2, 3):** GI-supplier + AfS auto-resolve; PO
   over-receipt + price-anomaly one-tap.
5. **Phase 4 — Hardening (Gaps 0, 5):** reconcile the taxonomy; lock severity/lane per category.

Each phase is independently shippable and independently reduces backlog.

---

## 9. Open questions for Tom

1. **Thresholds (§7):** the four values. Without these, Phase 0 can't land.
2. **Retention window (§5.5 / Gap 4):** 30 days for info-severity auto-expire — OK?
3. **Audit-out (§5.5):** confirm `bom_version_published`, anchor-review, and pre-anchor-skipped
   should move to `activity_log` (i.e. they're not things you ever want to "action").
4. **Authority promotion:** on ratification, should this become a pointer from `LOCKED_DECISIONS.md`
   (durable authority) or stay a decision record under `docs/decisions/`?

---

## 10. Change control

On ratification: reconcile `exceptions_contract.md §2` (Gap 0), then this model's closure
invariant (§4) governs every future category. No new category ships without declaring its
mechanism (A–E), dedupe_key, lane, and — for D — threshold policy.

---

*This is a proposal. It changes no code and no live state. Ratification = Tom merges this PR.*
