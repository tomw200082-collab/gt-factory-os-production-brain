# Typed Inbox + Supplier Price-Change Proposals — Design Spec

**Date authored:** 2026-05-04
**Author:** Claude (Opus 4.7) under Tom's direction
**Skill chain:** superpowers:brainstorming → superpowers:writing-plans (next)
**Status:** REV 4 — post third review pass; awaiting re-review + Tom approval

**REV 4 changes (2026-05-04 third iteration):**
- BLOCKER fix: every `supplier_items.approval_status='active'` (4 sites) replaced with `approval_status='approved'` per live data normalization in migration 0085
- §1.5.1: "Last 10 price points" lookup uses `ORDER BY event_at DESC LIMIT 10` (price_history has no status column; it's append-only)
- §1.14.3 Tier 1 action: write `SUPPLIER_PRICE_UPDATE_MANUAL` not `_AUTO` (it is planner-driven, not system; matches change_log_contract.md §3.3)
- §2.2: `tier` CHECK expanded to `('tier_1','tier_2','tier_3')` so future Tier-1 / Tier-3 audit rows can land without DDL
- §2.2: partial CHECK constraints added — `(status<>'rejected' OR rejection_reason IS NOT NULL)` and `(status NOT IN ('approved_pending_activation','activated') OR override_reason IS NULL OR override_reason IS NOT NULL)` (the second is documentation-only since override is allowed but optional)
- §2.2: explicit DEPENDS-ON note for `private_core.touch_updated_at()` function
- §1.14.1: Stage A producer call-site pinned: invoked from `factory_os_jobs/index.ts` GI ingest loop AFTER the `gi_expense_mirror` INSERT commits in the same transaction AND AFTER the existing `gi_unmapped_supplier` / `gi_non_ils_currency` checks (so we never emit `gi_expense_review` for an unmapped supplier or non-ILS expense)
- §1.14.2 form schema: `quantity_units` tooltip clarified — "כמות הרכישה ביחידות הזמנה (Order UOM של ה-supplier_item)" with worked example
- §1.14.5 / §2.5b: removed dead `pack_conversion` (column is NOT NULL DEFAULT 1)
- §1.5.1 Hebrew copy: "Confidence: HIGH" → "ביטחון: גבוה"
- New §1.16: defer/snooze lifecycle — uses `acknowledged_at` + a new `snoozed_until` column on exceptions; defer/snooze action puts the card temporarily off the default view but does NOT change `status`
- §2.7: explicit note about M5-before-M3 partial-index-vs-old-emitter window (acceptable at GT volume)
- All NIT/MINOR fixes from review 3
- Critical pivot in §1.14: Green Invoice does NOT expose structured per-line data (verified live 2026-04-21 via `green_invoice_supplier_price_contract.md` §2.4: "data.prediction is invoice-aggregate OCR, not line-item OCR"). Per-invoice-line auto-extraction is infeasible. v1 design pivots to **expense-evidence + planner-confirms-quantity flow**: every mapped-supplier expense surfaces as a To-Do card; one click opens a quick form prefilled with the supplier's supplier_items; planner enters quantity (or unit price); submission writes a `price_proposals` row and emits the Decision card. Auto-update path (Tier 1) still applies once the planner enters quantity for HIGH-confidence single-supplier_item suppliers.
- §1.12: emit-with-reopen contract uses `SELECT … FOR UPDATE` to avoid concurrency races
- §1.13 + §7: audit sentinel pattern parens fixed (OR-precedence bug)
- §1.15: added `shopify_variant_gap` Hebrew label
- §2.2: `price_proposals.gi_invoice_line_id` removed; replaced with `gi_expense_id` + `line_index_synthetic` (planner-form-set; defaults 0 for single-line invoices)
- §2.3: `shopify_variant_not_found` correctly mapped to `shopify_variant_gap` (NOT `lw_catalog_gap`)
- §2.4: change_log halt-guard now `RAISE EXCEPTION` on enum drift, not `RAISE NOTICE`
- §2.5: composite `(dedupe_key, status)` index added to preserve hot-path performance
- §2.5b NEW: `fn_gi_price_proposal_activator()` SQL body inlined
- §4.3: producer split — auto Tier-1 path runs only for single-supplier_item mapped suppliers; multi-supplier_item suppliers route to To-Do `gi_expense_review`
- §4.4: `key_facts` fallback documented for per-submission one-shot inserts
- All references to fictional `supplier_items.supplier_sku` and `supplier_items.supplier_item_name` removed; matching uses verified columns only (`supplier_id`, `component_id`, `item_id`, plus `components.component_name` / `items.item_name` for description display)
**Target environment:** GT Factory OS v1 — Inbox surface
**Audience for the surface being designed:** planner + admin only

---

## 0. Purpose

Replace the current generic Exceptions Inbox with a **typed control surface** where every operational decision arrives shaped to the decision being made. Each card type knows what data the planner needs, presents it inline at the right density, and offers action verbs that fit the type.

**Triggering use case (Tom 2026-05-04):** when a Green Invoice expense arrives from a mapped supplier, the system must surface the evidence in the Inbox so the planner can quickly turn it into a price-update proposal and approve/reject. **Reality constraint (verified 2026-04-21 via GI live API inspection):** Green Invoice's `/expenses/*` endpoints expose envelope totals only — no structured line items, no per-unit prices. The v1 flow therefore is: expense arrives → To-Do card surfaces → one-click opens a form prefilled with the supplier's supplier_items → planner enters quantity (or unit price) → submission creates a Decision card with full comparison + Approve/Edit→Approve/Reject. For mapped suppliers with EXACTLY ONE active supplier_item AND a planner-supplied quantity, the system auto-updates within Tier 1 thresholds (still under the CLAUDE.md "mapping unambiguous" guard). The same Decision-card anatomy generalizes to GR over-receipts, count approvals, waste approvals, alias mappings, etc.

**Secondary goal:** structurally fix the live complaint "every time I resolve, it comes back". Root cause: the existing emitter dedupe logic
```sql
WHERE dedupe_key=$1 AND status='open'
```
re-creates a fresh exception once the operator marks resolved. The new design uses **type-aware dedupe** that scopes correctly per card type AND adds an explicit re-open path for Warning regression cycles.

## 0.1 Scope authority

This spec governs:
- The Inbox UI (portal `/inbox/**` routes — see §1.10 + §4.4 for exact in-scope pages)
- The exceptions runtime (`api/src/exceptions/**`)
- All exception emitters (`api/src/integrations/**`, `supabase/functions/factory_os_jobs/**`, `api/src/jobs/**`, `api/src/boms/**`, `api/src/integration-sku-map/**`)
- The new GI price-change producer (new code)
- New schema artifacts: `card_type` + `subtype` columns, `price_proposals` table, dedupe index replacement
- Migration of currently-open exceptions to the typed taxonomy

This spec does NOT govern:
- The forms that submit operator events (GR, count, waste) — they continue with their existing handlers; only their post-INSERT exception rows get `card_type='decision'` populated
- Schema-foundation for stock truth (separate Gate 3 work)
- Forecasting, planning engine, dashboard control tower
- The customer-credit Decision drawer (`/inbox/credit/[id]`) — this spec ONLY adds `card_type='decision'` + `subtype='customer_credit'` to its existing emitter; the drawer chrome is unified in a follow-up spec

## 0.2 Sources consulted during brainstorming

UX / IA references:
- Nielsen Norman Group — Heuristic #1 (visibility of system status), #4 (consistency), #6 (recognition over recall); Progressive Disclosure pattern; "Dashboards & Data Visualization" report
- SAP Fiori Design Guidelines — My Inbox + Object Page pattern; Notification card pattern
- Workday Inbox + Microsoft Dynamics 365 Approvals + Microsoft Adaptive Cards
- Linear Inbox / Stripe Dashboard Disputes / Vercel Deployments / GitHub PR review queue
- Cognitive Load Theory (Sweller, 1988); Hick's Law; Rubinstein/Meyer/Evans 2001 (mode-switching cost)

Approval-workflow / supplier-price-change references:
- Coupa Supplier Information Management — 3-tier tolerance (auto / propose / anomaly); 82% approvals decided from scan-row
- SAP Ariba supplier price-list workflow — evidence + effective-date semantics
- Tipalti "Supplier Price Watch"; AvidXchange three-way match + price tolerance; NetSuite Vendor Price Levels
- Gartner ERP Procurement Best Practices 2023 — 5-15% tolerance auto-update industry standard
- APQC AP Variance Tolerance benchmark 2024 — median auto-pass = 5% absolute % OR ±$50

Data-design references:
- DDIA (Kleppmann) Ch. 7-12 — event-sourcing patterns; event-key vs state-key dedupe
- Postgres "additive enum extension" pattern — DROP+ADD CHECK with full enumeration

GT-internal:
- `CLAUDE.md` durable contract (locked decisions on stock truth, ledger, names-not-IDs, planner+admin gate, Hebrew register, Net-of-VAT)
- Live schema state (verified 2026-05-04):
  - `db/migrations/0010_exceptions.sql` — base exceptions table + 4 indexes (incl. partial dedupe index)
  - `db/migrations/0025_change_log_and_price_history.sql` — change_log + price_history append-only triggers
  - `db/migrations/0075_supplier_items_std_cost.sql` — `supplier_items.std_cost_per_inv_uom money_4dp` (the active price column)
  - `db/migrations/0123_change_log_credit_decision_actions.sql` — current change_log enum (60 actions)
  - `db/migrations/0124_exceptions_status_credit_decisions.sql` — current exceptions.status enum (7 values)
- Live emit-site inventory (verified 2026-05-04 via grep over `api/src` + `supabase/functions/factory_os_jobs/index.ts`)
- Prior cleanup spec: `docs/superpowers/specs/2026-04-27-inbox-cleanup-design.md` (executed status indeterminate at write-time; §3 of this spec includes detection + idempotency)

---

## 1. Locked design decisions

### 1.1 Architecture: Model B — fully typed Inbox

Industry has converged: SAP Fiori My Inbox, Workday Inbox, Linear, Sigma, Stripe Dashboard all use Model B (every item has a typed schema; severity is a card-level property, not a separate lane). Model B beats Model A (typed approvals only — leaves warnings homeless) and Model C (tiered lanes — creates Siberia). The codebase already moves toward typed routes (`/inbox/approvals/physical-count/[id]`, `/inbox/approvals/waste/[id]`, `/inbox/credit/[id]`).

### 1.2 Audience and operator scope

**The Inbox surface (`/inbox/**` routes, `GET /queries/exceptions` without entity filter)** is **planner + admin only**. The operator role gets HTTP 403 on these surfaces.

**Operator narrow read-access exception:** operators retain access to `GET /queries/exceptions?related_entity_type=form_submission&related_entity_id=<their_submission_id>` so the form they submitted can show its own pending state. The handler enforces ownership: returns only exceptions whose `related_entity_id` is a `form_submission` row authored by `session.user_id`. This narrow path does NOT expose the Inbox surface and does NOT permit any mutate. Form-side status indicator UI is **out-of-scope for v1**; the API surface exists so a v2 form-side status component can read it without a contract break.

### 1.3 4-tier card type taxonomy

| `card_type` | UI label | When | Primary actions | When the card disappears |
|---|---|---|---|---|
| `decision` | החלטה | Planner must approve/reject (binary or multi-option) | Approve / Edit→Approve / Reject / Defer | Immediately on action |
| `to_do` | משימה | Action required elsewhere (queue or master form) | Open in <queue> / Skip / Snooze | When underlying state changes (auto-resolve) |
| `warning` | התראה | Producer unhappy; no direct planner decision | Acknowledge / Investigate | Auto-resolve when producer recovers |
| `info` | מידע | Diagnostic events; no operator action | Dismiss → history | Immediately; hidden from default view |

Severity (`info` / `warning` / `critical`) is a per-card property rendered via icon + color; NOT a separate type or lane. The existing `exceptions.severity` column already supports this (CHECK is unchanged).

### 1.4 Decision card anatomy (universal frame)

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER                                                       │
│   type-icon · type-label · subject · severity badge · age   │
├─────────────────────────────────────────────────────────────┤
│ KEY FACTS STRIP   (3-5 name/value pairs, scan-density)      │
├─────────────────────────────────────────────────────────────┤
│ BODY (subtype-variable)                                      │
│   subtype-specific layout + inline impact preview            │
│   evidence link(s)                                           │
├─────────────────────────────────────────────────────────────┤
│ ACTION BAR                                                   │
│   primary: Approve  · secondary: Reject / Edit / Defer       │
│   audit strip: "proposed by <producer> · <timestamp>"        │
└─────────────────────────────────────────────────────────────┘
```

Two render modes:
- **List mode (scan-row)** — Header + Key Facts + primary action button. Row height 80-100px. 8-15 visible per screen.
- **Drawer mode** — full anatomy at `/inbox/approvals/<subtype>/[id]`.

### 1.5 Decision subtype body recipes

#### 1.5.1 `gi_price_proposal` — supplier price change

This Decision card is created by Stage B form-submission (§1.14.2), not directly by the GI ingest cycle. The To-Do `gi_expense_review` card is the entry point; the planner clicks once, picks the supplier_item (or accepts the prefilled single one), enters quantity, and submits — that submission emits this Decision card.

```
Header:  🏷️ שינוי מחיר ספק · מיקי מדבקות · אריזת מדבקה 30 מ"מ · 1h
Key Facts:
  [נוכחי ₪0.842]  [מוצע ₪0.891]  [+5.8% (₪+0.049)]  [ביטחון: גבוה]
─────────────────────────────────────────────────────────────
BODY:
  Comparison strip (top, center stage):
    מחיר נוכחי           מחיר מוצע          דלתא
    ₪0.842 / יח'    →    ₪0.891 / יח'    +5.8% (₪+0.049)
    Color: green if cheaper · amber if +3% < % ≤ +15% AND ₪ ≤ ₪10
           red is reserved for Tier 3 (Warning, not Decision)

  Supplier-match confidence:
    ספק:   מיקי מדבקות    ✓ gi_supplier_id matched
    רכיב:  אריזת מדבקה 30 מ"מ  ✓ supplier_item picked from dropdown
            (single-active-supplier_item supplier; auto-prefilled)
    ביטחון: גבוה (see §1.14.4 rubric)

  Quantity (planner-supplied at form):
    5,000 יח' on this invoice · ₪225.00 net = ₪0.045/יח' (mode: quantity_units)
                                                 OR
    Override: ₪0.045/יח' (mode: unit_price_net_override)

  Context:
    Last 10 price points (table or sparkline) — read from price_history ORDER BY event_at DESC LIMIT 10
    (price_history is append-only; no status column. The "current price" is the most-recent event_at row.)
    Last change: 2025-12-15 from ₪0.821 → ₪0.842
    Days since last change: 140
    Note: Active POs at the OLD price are not repriced — informational only.

  Evidence: [📄 View GI expense 12345 (PDF)]  → opens GI document via signed URL
─────────────────────────────────────────────────────────────
Actions:  [אשר]  ערוך ואשר  דחה  דחה לזמן אחר
```

#### 1.5.2 `po_line_over_receipt` — GR over-receipt approval

```
Header:  📦 עודף בקבלת סחורה · ABC Industries · GR-2541 · 2h
Key Facts: [PO #1234]  [אריזת מדבקה 30 מ"מ]  [הוזמן 500 / התקבל 600]  [+20%]
─────────────────────────────────────────────────────────────
BODY:
  Stock impact (center stage):
    אריזת מדבקה 30 מ"מ
    במלאי כעת:    1,240 יח'
    אחרי GR זה:   1,840 יח'  (+600)
  PO line: הוזמן 500 · התקבל 600 · עודף 100 (+20%)
  Why in inbox: receipt exceeds PO line by 20%, planner approval required.
─────────────────────────────────────────────────────────────
Actions:  [אשר]  דחה  דחה לזמן אחר
```

#### 1.5.3 Stock-impact-center-stage pattern reuse

The body shape generalizes to:
- `count_large_variance` (physical-count approval) — snapshot vs counted, delta
- `positive_adjustment` (waste positive adjustment) — current vs adjusted

#### 1.5.4 Other Decision subtypes (this spec scopes only chrome unification)

| existing subtype | source | this spec scope |
|---|---|---|
| `lionwheel_credit_needed` (existing `customer_credit` flow) | `api/src/integrations/lionwheel/reconciliation.ts:933` + `api/src/inbox/credit_decisions/handler.ts` | Set `card_type='decision'`, `subtype='customer_credit'` on emit. Drawer chrome unified in a follow-up spec; this spec does NOT change drawer behavior. |
| `purchase_recommendation_approval`, `production_recommendation_approval`, `manual_po_approval`, `lw_catalog_gap` | future producers | Type contract is set in this spec; implementation is deferred to writing-plans phase per producer. |

### 1.6 Warning card anatomy

```
Header:  ⚠️ Green Invoice לא מסונכרן · integration.green_invoice · 47m
Key Facts: [Stale 47m]  [Severity: warning]  [תיסגר לבד עם הסנכרון הבא]
─────────────────────────────────────────────────────────────
BODY:
  Why: GI poll has not run successfully since 12:31. Threshold: 120m.
  What you can do:
    → [בדוק חיבור ל-Green Invoice]   (deep link to /admin/integrations)
    → [הפעל poll ידני]               (deep link to /admin/jobs)
  הכרטיסייה תיסגר לבד כשהאינטגרציה תחזור לתקין.
─────────────────────────────────────────────────────────────
Actions:  [ראיתי]  בדוק
```

Differences from Decision:
- Key Facts: 2-3 (no decision to make)
- No "after my action" preview
- Action verbs: Acknowledge / Investigate
- Auto-resolve note prominently displayed

### 1.7 Acknowledge ≠ Resolve semantic

| Type | What the action does | When the card disappears |
|---|---|---|
| Decision | Approve/Reject → underlying state changes | Immediately |
| To-Do | "Open in queue" → planner works elsewhere | When underlying state changes (auto-resolve) |
| Warning | Acknowledge = "I see it" → silences urgency only | Only when producer recovers (auto-resolve) |
| Info | Dismiss → history | Immediately; hidden from default anyway |

The generic Resolve button is **removed entirely from Warning and To-Do cards**. Warnings get only Acknowledge (which does NOT close the card). To-Dos get only deep-link + Snooze. Auto-resolve is the only path that removes Warning/To-Do from the Inbox.

### 1.8 To-Do anatomy — two variants

**Variant 1 — Queue To-Do** (queue of similar items needing bulk processing):

```
Header:  ✏️ מיפוי FG לחנות · 54 פריטים פעילים · 2d
Key Facts: [Pending: 54]  [HIGH-confidence: 38]  [Updated: 1h]
─────────────────────────────────────────────────────────────
BODY:
  Why: 54 active finished-goods items have no Shopify alias.
       Without alias, stock cannot sync to the storefront.
  Suggested: 38/54 with HIGH-confidence proposal.
─────────────────────────────────────────────────────────────
Actions:  [פתח את תור המיפוי →]   דחה לזמן אחר
```

**Variant 2 — Single-task To-Do** (one action elsewhere):

```
Header:  ✏️ מיפוי שורת חשבונית · "מיקי מדבקות תווית 30 מ"מ" · 1d
Key Facts: [ספק: מיקי מדבקות]  [כמות: 5,000]  [חשבונית: 12345]
─────────────────────────────────────────────────────────────
BODY:
  GI invoice line not mapped to a canonical component.
  Map once → future invoices from this supplier with same description
  route automatically.
─────────────────────────────────────────────────────────────
Actions:  [פתח טופס מיפוי →]   דלג
```

### 1.9 Info / Diagnostic anatomy — minimal

```
Header (compact):  ℹ️ חריגה מ-100 שורות ב-LionWheel · 47 רשומות · 4h
Body: producer-emitted diagnostic. Hidden from default view.
       Visible via filter "Source: lionwheel · Severity: info".
Actions: [סגור]
```

### 1.10 Top-level IA — single unified feed

```
┌────────────────────────────────────────────────────────────────┐
│  Inbox                              [12 החלטות · 4 משימות · 2 התראות] │
│  ┌──── filters (side-pane) ─────┐  ┌──── feed ─────────────────┐│
│  │ סוג:                          │  │ 🏷️ שינוי מחיר ספק · ... 1h ││
│  │ חומרה:                        │  │ 📦 עודף בקבלת סחורה · ... 2h ││
│  │ מקור:                         │  │ ✏️ מיפוי FG · ... 1d        ││
│  │ מצב:                          │  │ ⚠️ GI לא מסונכרן · ... 47m  ││
│  │ [חיפוש...]                    │  │                            ││
│  │ [שמור סינון] [אתחל סינון]     │  │                            ││
│  └───────────────────────────────┘  └────────────────────────────┘│
└────────────────────────────────────────────────────────────────┘
```

**Default sort SQL (canonical):**

```sql
ORDER BY
  CASE card_type
    WHEN 'decision' THEN 1
    WHEN 'to_do'    THEN 2
    WHEN 'warning'  THEN 3
    WHEN 'info'     THEN 4
  END ASC,
  CASE severity
    WHEN 'critical' THEN 1
    WHEN 'warning'  THEN 2
    WHEN 'info'     THEN 3
  END ASC,
  created_at ASC  -- oldest first within (card_type, severity)
```

`info` cards are excluded from default view by filter; the sort above runs only when filter explicitly includes info.

**Top-level badge strip:** `12 החלטות · 4 משימות · 2 התראות` (counts of `status IN ('open','acknowledged') AND card_type IN ('decision','to_do','warning')`). Always visible.

**Filter side-pane** — 5 dimensions (סוג, חומרה, מקור, מצב, חיפוש) + "saved view" buttons. Default saved views:
- "פתוח" — `status IN ('open','acknowledged') AND card_type IN ('decision','to_do','warning')` (info hidden)
- "טופל" — see §1.13 History view filter

**Inbox routes — explicitly in scope:**
- `/inbox` — main feed
- `/inbox?view=history` — history tab (single-page, query-string switch — NOT a separate route)
- `/inbox/approvals/<subtype>/[id]` — Decision drawer (existing routes for `physical-count`, `waste`, `credit` retain their internal logic; gain unified chrome)
- `/inbox/approvals/gi-price-proposal/[id]` — NEW Decision drawer (this spec)

**Inbox routes — explicitly OUT of scope for v1:**
- `/inbox/queues/fg-aliases` — the To-Do "מיפוי FG לחנות" deep-links to the EXISTING `/admin/integration-sku-map` admin surface, not a new queue page.
- `/inbox/queues/gi-supplier-mapping` — the To-Do "מיפוי ספק" deep-links to the EXISTING `/admin/suppliers`.

A future spec MAY introduce dedicated `/inbox/queues/*` triage UIs; v1 reuses admin surfaces.

### 1.11 State machine

| state | meaning | which card_types use it |
|---|---|---|
| `open` | Card is pending action | all |
| `acknowledged` | Warning silenced (planner said "I see it"); card still visible but visually muted | warning only |
| `resolved` | Decision was Approved or Rejected; subaction recorded in change_log | decision only |
| `auto_resolved` | Producer detected state change / recovery | to_do, warning |
| `dismissed` | Info card sent to history | info only |
| `pending_gi_action`, `gi_draft_created`, `gi_action_failed` | Existing customer_credit lifecycle (per migration 0124) | decision (`subtype='customer_credit'`) only |

**UI macro-status compression** (planner-facing only):
- **פתוח** = internal `open`, `acknowledged`, `pending_gi_action`, `gi_action_failed`
- **טופל** = internal `resolved`, `auto_resolved`, `dismissed`, `gi_draft_created`

The internal 8 statuses persist in DB for audit. The macro-status mapping is a UI-only function in `portal/src/lib/inbox-copy.ts`.

### 1.12 Dedupe-key conventions and the re-open path

**Dedupe-on-emit changes from**
```sql
WHERE dedupe_key=$1 AND status='open'
```
**to**
```sql
WHERE dedupe_key=$1
```
(no status predicate, with the explicit re-open path defined below).

**Type-aware key shapes:**

| `card_type` | Key shape | Example | New event creates new card? |
|---|---|---|---|
| `decision` (event-scoped) | `<subtype>:<event_id>` | `gi_price_proposal:<proposal_id>` | ✓ |
| `to_do` (state-scoped) | `<subtype>:<state_id>` | `unmapped_fg_alias:<item_id>` | ✗ — same state = same card until auto-resolved |
| `warning` (producer-scoped) | `<subtype>:<producer_id>` | `lionwheel_stale:integration.lionwheel` | ✗ — same producer = same card |
| `info` (event-scoped) | `<subtype>:<event_id>` | `lw_capped_window:<job_run_id>` | ✓ |

**Per-submission one-shot inserts** (NOT subject to type-aware dedupe):
- `count_large_variance` (physical-counts/handler.ts:412)
- `positive_adjustment` and `loss_above_threshold` (waste-adjustments/handler.ts:750)

These insert with `dedupe_key=NULL` and resolve via direct `submission_id`-keyed approve/reject handlers (already implemented). This spec does NOT change their emit shape; it ONLY adds `card_type='decision'` and `subtype` columns to their INSERT. Existing dedupe predicates do not apply.

**The re-open path** — required for Warning/To-Do regression cycles:

When a producer detects a regression (state goes healthy→unhealthy, or To-Do state regresses), the emitter does NOT INSERT a fresh row. The contract is:

```sql
-- Emit-with-reopen contract (Warning + To-Do producers; runs in transaction):
BEGIN;
-- 1. Lock the existing row if any (FOR UPDATE prevents concurrent emitters double-touching).
SELECT exception_id, status
  INTO v_existing_id, v_existing_status
  FROM private_core.exceptions
 WHERE dedupe_key = $1
 FOR UPDATE;

IF NOT FOUND THEN
  -- INSERT new row
  INSERT INTO private_core.exceptions
    (category, severity, source, title, detail, raw_payload, dedupe_key,
     related_job_run_id, related_entity_type, related_entity_id, card_type, subtype)
  VALUES
    ($2, $3, $4, $5, $6, $7, $1, $8, $9, $10, $11, $12);
ELSIF v_existing_status IN ('open','acknowledged') THEN
  -- NO-OP. Already visible. Do not append re-open marker (avoids unbounded notes growth).
  -- Optional: bump updated_at to track recurrence count via a counter column (out-of-scope v1).
  NULL;
ELSE
  -- v_existing_status IN ('resolved','auto_resolved','dismissed','gi_*'): RE-OPEN.
  UPDATE private_core.exceptions
     SET status = 'open',
         resolved_by = NULL,
         resolved_at = NULL,
         acknowledged_by = NULL,
         acknowledged_at = NULL,
         -- Cap resolution_notes growth: keep last 4096 chars + new marker.
         resolution_notes = right(
           COALESCE(resolution_notes,'') || E'\n[Re-opened ' || NOW()::text || ' by producer]',
           4096),
         updated_at = NOW(),
         severity = $3,
         title = $5,
         detail = $6,
         raw_payload = $7,
         related_job_run_id = $8
   WHERE exception_id = v_existing_id;
END IF;
COMMIT;
```

The `FOR UPDATE` on the SELECT prevents concurrent emitters from both seeing `status='resolved'` and both attempting reopen. The `right(..., 4096)` cap prevents unbounded `resolution_notes` growth across many regression cycles.

`change_log` is NOT written for re-open (it is producer state, not user action). The audit signal is `resolution_notes` carrying a `[Re-opened ...]` marker plus `updated_at`.

This re-open contract applies to all Warning + To-Do emitters. Decision emitters use event-scoped keys so they have no regression path (a "re-occurrence" is a new event with a new key). Info emitters use event-scoped keys (no regression).

**Auto-resolve from existing flows continues to work:**
- `freshness_check.ts:285-295` `autoResolve` writes `status='auto_resolved' WHERE dedupe_key=$1 AND status='open'` — still correct
- `integration-sku-map/handler.ts:156-177` `autoResolveExceptionsFor` writes `WHERE status='open' AND category=ANY(...) AND dedupe_key=ANY(...)` — still correct
- The new emit-with-reopen contract handles the OPPOSITE direction (state goes back to bad) and is the missing piece

### 1.13 Audit trail / History view

**Canonical audit:** `change_log` table. This spec adds 4 new actions to the CHECK constraint via DROP+ADD using the FULL current 60-action enum (per migration 0123) plus the 4 new values. See §2.4 for the exact migration shape.

New actions:
- `INBOX_DECISION_APPROVE`
- `INBOX_DECISION_REJECT`
- `INBOX_WARNING_ACKNOWLEDGE`
- `INBOX_INFO_DISMISS`

`auto_resolved` does NOT generate a change_log row (it is producer state, not user action). The audit sentinel pattern (parens are load-bearing — OR binds wider than AND otherwise):

```sql
WHERE resolved_by IS NULL
  AND (resolution_notes LIKE 'Auto-resolved by %'
       OR resolution_notes LIKE '%[Re-opened %')
```

**History view filter:**
```sql
WHERE status IN ('resolved', 'auto_resolved', 'dismissed', 'gi_draft_created')
  AND COALESCE(resolved_at, created_at) >= NOW() - INTERVAL '90 days'
```
filterable by type / actor / source / date / subject text.

The `resolved_at`-anchored window matches the planner mental model "what got closed in the last 90 days," not "what was created in the last 90 days." Cards created earlier but resolved recently are visible.

**Retention:** rows in `exceptions` stay forever (per CLAUDE.md append-only doctrine). The 90-day cap is UI-only.

### 1.14 Producer flow — GI evidence to price proposal (REV 3 pivot)

**The reality constraint:** Green Invoice's API exposes envelope-level data only — no per-line structured items, no per-unit prices, no quantities (verified by W4 live probes 2026-04-21, captured in `green_invoice_supplier_price_contract.md` §2.1 P4 + §2.4 + §4.2). The pre-REV-3 design assumed line-level extraction; this is infeasible. REV 3 splits the flow into two stages:

**Stage A — Auto: Surface the expense as a To-Do** (no quantity from GI; planner supplies it):
- Fully automatic; runs on every GI ingest cycle
- Matches expense to supplier; if mapped, emits a `to_do:gi_expense_review` card

**Stage B — Manual-form-confirms: Convert the To-Do into a Decision** (planner clicks once):
- Planner clicks "פתח" on the To-Do
- Form opens prefilled with the supplier's supplier_items + the GI evidence (PDF link, supplier name, total amount, date)
- Planner picks the affected supplier_item from a dropdown (auto-prefilled if exactly ONE) and enters quantity (or unit_price directly)
- Submission computes pct_delta vs `supplier_items.std_cost_per_inv_uom` and routes per Tier evaluation §1.14.2
- Tier 1 → auto-update + close To-Do; Tier 2 → emit Decision card; Tier 3 → emit Warning card

For mapped suppliers with exactly ONE active supplier_item, the form is single-click (the supplier_item is preselected; planner just enters quantity and submits). For multi-supplier_item suppliers, the planner picks from the dropdown.

#### 1.14.1 Stage A — auto producer (`emitGiExpenseReview`)

**Call-site (precise):** invoked from `supabase/functions/factory_os_jobs/index.ts` inside the GI ingest loop body, AFTER:
1. The `gi_expense_mirror` INSERT has committed in the same transaction (so `gi_expense_id` is queryable).
2. The currency check (`gi_non_ils_currency` exception is emitted upstream if currency ≠ ILS; abort here on non-ILS).
3. The supplier-mapping check (`gi_unmapped_supplier` exception emitted upstream if supplier unresolved; abort here on unresolved).

The producer therefore runs only for ILS expenses with a mapped supplier. Pseudocode:

```
For each newly-mirrored gi_expense_mirror row:
  a. Verify currency = 'ILS' (else producer for `info:gi_non_ils_currency` already fired upstream; abort)
  b. Resolve supplier_id from suppliers.green_invoice_supplier_id = mirror.gi_supplier_id
     If unresolved: existing `to_do:unmapped_gi_supplier` already fired upstream; abort
  c. Count active supplier_items for this supplier:
     SELECT COUNT(*) FROM supplier_items WHERE supplier_id=$1 AND approval_status='approved'
  d. Emit `to_do:gi_expense_review` (state-scoped dedupe per §1.12) with:
     dedupe_key = `gi_expense_review:<gi_expense_id>`
     card_type='to_do'
     subtype='gi_expense_review'
     severity='info'
     related_entity_type='gi_expense_mirror'
     related_entity_id=mirror.gi_expense_id
     raw_payload->'key_facts' = {
       supplier_name: mirror.gi_supplier_name,
       supplier_id_internal: <resolved>,
       amount_excl_vat: mirror.amount_excl_vat,
       currency: mirror.currency,
       gi_document_date: mirror.gi_document_date,
       gi_document_type: mirror.gi_document_type,
       supplier_item_count: <c above>,
       prefill_supplier_item_id: <NULL if c≠1, else the lone row's supplier_item_id>
     }
  STOP. (No price logic at this stage — there is no quantity yet.)
```

The `gi_expense_review` To-Do dedupe is event-scoped on `gi_expense_id` because each GI expense is a distinct event (per the GI ingest contract §3.1 "expense.id is stable per expense"). A re-ingest of the same expense produces the same dedupe_key — no duplicate.

#### 1.14.2 Stage B — manual-form handler (`handleGiExpenseReview`)

When the planner clicks the To-Do, the form `/inbox/approvals/gi-expense-review/[gi_expense_id]/page.tsx` opens. Form schema:

```typescript
{
  supplier_item_id: uuid,        // dropdown; required; prefilled if supplier has 1 active supplier_item
  quantity_units: numeric > 0,    // input; required; tooltip:
                                  //   "כמות הרכישה ביחידות הזמנה (Order UOM של ה-supplier_item).
                                  //   דוגמה: אם הספק חייב 5,000 מדבקות והפריט מוגדר ב-Order UOM
                                  //   'יחידה' — הזן 5000. המערכת תחשב מחיר ליחידה אוטומטית
                                  //   על-בסיס סכום החשבונית."
  // OR (mutually exclusive with quantity_units):
  unit_price_net_override: numeric ≥ 0,  // input; if planner knows the unit price directly
  notes: text,                    // optional
}
```

Submission validates `XOR(quantity_units, unit_price_net_override)`. Computed values:
- If `quantity_units`: `proposed_unit_price_net = mirror.amount_excl_vat / quantity_units`
- If `unit_price_net_override`: `proposed_unit_price_net = unit_price_net_override`

Then:
- `current_unit_price_net = supplier_items.std_cost_per_inv_uom / supplier_items.pack_conversion`  (pack_conversion is NOT NULL DEFAULT 1)
- If `current_unit_price_net IS NULL OR 0`: this is a baseline-establishing event; force Tier 2 with `confidence='MEDIUM'`
- Else: compute `pct_delta = (proposed - current) / current` and `abs_delta = |proposed - current|`

Apply Tier evaluation per §1.14.3.

Submission writes (in a single transaction):
1. Insert `price_proposals` row (status depends on tier — see §1.14.3)
2. Optionally write Tier 1 auto-update (price_history + supplier_items + change_log) per §1.14.4
3. Resolve the originating `gi_expense_review` To-Do exception (`status='resolved'`)
4. Optionally emit a new Decision card (Tier 2) or Warning card (Tier 3)

#### 1.14.3 Tier evaluation — most-severe wins

Order of evaluation is **top-to-bottom; first match wins** (Tier 3 conditions are a strict severity superset by design):

```
Tier 3 (warning, no auto-update):
  IF  abs(pct_delta) > 15%
      OR abs_delta > ₪10
      OR proposed_unit_price_net ≤ 0
  THEN emit warning:supplier_price_anomaly
       dedupe_key = `supplier_price_anomaly:<supplier_id>:<supplier_item_id>:<gi_expense_id>`
       severity='warning'
       NO supplier_items.std_cost_per_inv_uom update
       NO price_proposals row
       (Original gi_expense_review To-Do is resolved with note 'Anomaly emitted')
  STOP.

Tier 2 (decision, propose for approval):
  IF  3% < abs(pct_delta) ≤ 15%  OR  abs_delta ∈ (₪0.50, ₪10]
      OR is_baseline_establishing  OR confidence < 'HIGH'
  THEN INSERT price_proposals (status='proposed')
       emit decision:gi_price_proposal
       dedupe_key = `gi_price_proposal:<proposal_id>`
       severity='info'
  STOP.

Tier 1 (auto-update):
  IF abs(pct_delta) ≤ 3% AND abs_delta ≤ ₪0.50
     AND confidence='HIGH' AND NOT is_baseline_establishing
  THEN  -- atomic block (already inside Stage B transaction):
        INSERT price_history (source='gi_invoice_auto', unit_price_net=proposed, ...)
        UPDATE supplier_items SET std_cost_per_inv_uom = proposed * pack_conversion
                                  WHERE supplier_item_id = matched_id
        INSERT change_log (action='PRICE_HISTORY_INSERT')
        INSERT change_log (action='SUPPLIER_PRICE_UPDATE_AUTO')
        -- Action semantics: AUTO = no Decision card was used (system applied
        -- silently within tolerance after planner-form supplied quantity).
        -- MANUAL = a Decision card was explicitly approved (Tier 2 / Edit→Approve).
        -- Tier 1's source='gi_invoice_auto' and action=AUTO are aligned.
        NO inbox card; the gi_expense_review To-Do is resolved with note 'Auto-updated within Tier 1'
  STOP.

Tier-1-fallback: any case not caught by the three branches above defaults to Tier 2.
```

**Boundary clarifications:**
- `abs(pct_delta) = 3.000%` AND `abs_delta = ₪0.50` → Tier 1 (≤ inclusive on both axes).
- `abs(pct_delta) = 3.001%` AND `abs_delta = ₪0.40` → Tier 2 (% axis fails Tier 1).
- `abs(pct_delta) = 15.000%` AND `abs_delta = ₪9.99` → Tier 2 (Tier 3 strict greater-than).
- `abs(pct_delta) = 15.001%` → Tier 3 regardless of ₪ axis.
- `proposed_unit_price_net = 0` → Tier 3.

#### 1.14.4 Confidence rubric (deterministic)

Computed at form-submit time and stored on `price_proposals.confidence` for audit. Inputs:
- S1: gi_supplier_id matched to suppliers row (always required to reach this step)
- S2: supplier had exactly 1 active supplier_item AND form auto-prefilled it (planner did not change selection)
- S3: planner used `quantity_units` mode (computed unit_price) vs `unit_price_net_override` mode
- S4: current price (`std_cost_per_inv_uom`) is non-null AND > 0

| S2 (single SI) | S3 (quantity mode) | S4 (current ≠ 0) | Confidence | Routing |
|---|---|---|---|---|
| ✓ | ✓ | ✓ | HIGH | Tier 1 eligible; Tier 2 default |
| ✓ | ✗ (override) | ✓ | MEDIUM | Tier 2 only (override implies planner-judgment, no auto-update) |
| ✗ (planner picked from dropdown) | any | ✓ | MEDIUM | Tier 2 only |
| any | any | ✗ (baseline) | MEDIUM (forced) | Tier 2 only |

There is no LOW confidence — the planner has actively confirmed the supplier_item via dropdown selection. Anything that would have been LOW in an auto-extraction model is a planner-supplied value at this point, which is at least MEDIUM.

#### 1.14.5 Approve / Edit→Approve / Reject flow (Decision card actions)

All three actions run in a single DB transaction.

**Approve** (Tier 2):
```sql
BEGIN;
-- (1) Mapping drift guard: verify supplier_item is still active and still belongs to this supplier
SELECT 1 FROM private_core.supplier_items si
  JOIN private_core.suppliers s ON s.supplier_id = si.supplier_id
 WHERE si.supplier_item_id = $proposal.supplier_item_id
   AND si.approval_status = 'approved'
   AND s.green_invoice_supplier_id = (
        SELECT m.gi_supplier_id FROM private_core.gi_expense_mirror m
         WHERE m.gi_expense_id = $proposal.gi_expense_id);
-- If 0 rows: ROLLBACK; handler returns 409 SUPPLIER_MAPPING_DRIFT.

-- (2) Append-only price_history row (preserves 0025 trigger)
INSERT INTO private_core.price_history
  (supplier_item_id, unit_price_net, source, event_at, posted_at,
   actor_user_id, actor_snapshot, source_document_id, notes)
VALUES
  (proposal.supplier_item_id, proposal.proposed_unit_price_net, 'gi_invoice_manual',
   NOW(), NOW(), session.user_id, session.display_name, proposal.gi_expense_id,
   format('Approved gi_price_proposal:%s', proposal.proposal_id))
RETURNING price_history_id INTO v_ph_id;

-- (3) Active price (supplier_items has no append-only trigger)
UPDATE private_core.supplier_items
   SET std_cost_per_inv_uom = proposal.proposed_unit_price_net * pack_conversion,
       updated_at = NOW()
 WHERE supplier_item_id = proposal.supplier_item_id;

-- (4) Lifecycle table
UPDATE private_core.price_proposals
   SET status='activated', activated_at=NOW(), activated_by=session.user_id,
       resulting_price_history_id = v_ph_id
 WHERE proposal_id = proposal.proposal_id;

-- (5) change_log — write three rows (PRICE_HISTORY_INSERT for the new row,
--     SUPPLIER_PRICE_UPDATE_MANUAL for the active-price change, INBOX_DECISION_APPROVE for the inbox action)
INSERT INTO private_core.change_log (entity_table, entity_id, action, actor_user_id, ...)
VALUES
  ('price_history', v_ph_id::text, 'PRICE_HISTORY_INSERT', session.user_id, ...),
  ('supplier_items', proposal.supplier_item_id::text, 'SUPPLIER_PRICE_UPDATE_MANUAL', session.user_id, ...),
  ('exceptions', exception_id::text, 'INBOX_DECISION_APPROVE', session.user_id, ...);

-- (6) Resolve inbox row
UPDATE private_core.exceptions
   SET status='resolved', resolved_by=session.user_id, resolved_at=NOW(),
       resolution_notes='Approved supplier price change.'
 WHERE exception_id = $exception_id;
COMMIT;
```

**Edit→Approve**: same as Approve but `proposed_unit_price_net` is replaced by planner-supplied `override_unit_price_net`. Required additional fields: `override_reason text NOT NULL`. Optional `effective_at timestamptz`. Conditional on `effective_at`:

```sql
IF effective_at IS NULL OR effective_at <= NOW() THEN
  -- run steps (2)-(6) above (immediate activation)
ELSE
  -- skip steps (2), (3), (5b); only update lifecycle table:
  UPDATE private_core.price_proposals
     SET status='approved_pending_activation',
         override_unit_price_net=$override_unit_price_net,
         override_reason=$override_reason,
         effective_at=$effective_at,
         activated_by=session.user_id  -- captured even though not yet activated
   WHERE proposal_id = proposal.proposal_id;
  -- Still write INBOX_DECISION_APPROVE change_log row + resolve exception per (5c) and (6)
  INSERT INTO private_core.change_log (...) VALUES (..., 'INBOX_DECISION_APPROVE', ...);
  UPDATE private_core.exceptions SET status='resolved' ... ;
END IF;
COMMIT;
```

**Reject**:
```sql
BEGIN;
UPDATE private_core.price_proposals
   SET status='rejected', rejected_at=NOW(), rejected_by=session.user_id,
       rejection_reason=$reason
 WHERE proposal_id = proposal.proposal_id;
INSERT INTO private_core.change_log (entity_table, entity_id, action, actor_user_id, ...)
VALUES ('exceptions', exception_id::text, 'INBOX_DECISION_REJECT', session.user_id, ...);
UPDATE private_core.exceptions
   SET status='resolved', resolved_by=session.user_id, resolved_at=NOW(),
       resolution_notes=concat('Rejected: ', $reason)
 WHERE exception_id = $exception_id;
COMMIT;
```

The producer's dedupe_key is `proposal_id`-scoped, so the same proposal will not re-emit. A new GI expense from the same supplier produces a new `gi_expense_review` To-Do (different `gi_expense_id`); when the planner submits the form, it produces a new `proposal_id` and a new Decision card.

#### 1.14.6 Anomaly card — event-scoped key

Tier-3 dedupe key is `supplier_price_anomaly:<supplier_id>:<supplier_item_id>:<gi_expense_id>` (event-scoped). Each anomalous expense gets its own Warning card, preserving evidence. Auto-resolves never (the underlying expense is immutable); the planner Acknowledges to silence the urgency, and the row sits in `acknowledged` status until eventually queried in the History tab. If volume becomes operational noise, a follow-up spec adds a rolled-up subtype with state-scoped dedupe.

#### 1.14.7 Future-dated `effective_at` activation job

A new pg_cron entry `gi_price_proposal_activator` runs hourly (definition in §2.5b). The job picks proposals where `status='approved_pending_activation' AND effective_at <= NOW()`, locks each row with `FOR UPDATE SKIP LOCKED`, and runs steps (2)–(5a) of §1.14.5 with `actor_user_id = NULL` and `actor_snapshot = '<system:gi_price_proposal_activator>'`. Step (6) is N/A — the inbox row was already resolved at Edit→Approve time.

**Failure surface:** if the activation handler fails (DB error, lock timeout, etc.), it emits a `warning:gi_price_activation_failed` exception with `dedupe_key=gi_price_activation_failed:<proposal_id>` and updates `price_proposals.status='activation_failed'`. The job retries on the next tick (the warning emit-with-reopen path triggers naturally). The planner can ignore (job retries) or Acknowledge to silence visual urgency. Never silently leaves a stuck proposal.

### 1.15 Hebrew copy register (UI strings)

**Card types:**

| internal | UI label |
|---|---|
| `decision` | החלטה |
| `to_do` | משימה |
| `warning` | התראה |
| `info` | מידע |

**Macro-status (UI compression, see §1.11):**

| internal status | UI label |
|---|---|
| `open`, `acknowledged`, `pending_gi_action`, `gi_action_failed` | פתוח |
| `resolved`, `auto_resolved`, `dismissed`, `gi_draft_created` | טופל |

**Action buttons:**

| card type | primary | secondary |
|---|---|---|
| Decision | אשר | ערוך ואשר · דחה · דחה לזמן אחר |
| To-Do | פתח | דלג · דחה לזמן אחר |
| Warning | ראיתי | בדוק |
| Info | סגור | — |

**Decision subtype labels:**

| `subtype` | UI label |
|---|---|
| `gi_price_proposal` | שינוי מחיר ספק |
| `po_line_over_receipt` | עודף בקבלת סחורה |
| `count_large_variance` | אישור ספירת מלאי |
| `positive_adjustment` | אישור התאמת מלאי (חיובית) |
| `loss_above_threshold` | אישור פחת מעל סף |
| `manual_po_approval` | אישור הזמנת רכש ידנית |
| `purchase_recommendation_approval` | אישור המלצת רכש |
| `production_recommendation_approval` | אישור המלצת ייצור |
| `customer_credit` (alias for `lionwheel_credit_needed`) | אישור זיכוי לקוח |
| `lw_catalog_gap` | החלטת קטלוג LionWheel |
| `shopify_variant_gap` | פער וריאנט Shopify |
| `gi_price_proposal` (already listed above; one entry only) | (see top of §1.15 list) |

**To-Do subtype labels:**

| `subtype` | UI label |
|---|---|
| `unmapped_fg_alias` | מיפוי FG לחנות |
| `unmapped_gi_supplier` | מיפוי ספק מ-Green Invoice |
| `unmapped_gi_line` | מיפוי שורת חשבונית |
| `ambiguous_supplier_mapping` | פתרון מיפוי כפול |
| `unmapped_lw_sku` | מיפוי SKU מ-LionWheel |
| `gi_expense_review` | בדיקת חשבונית מ-Green Invoice |

**Warning subtype labels:**

| `subtype` | UI label |
|---|---|
| `gi_stale` | Green Invoice לא מסונכרן |
| `lionwheel_stale` | LionWheel לא מסונכרן |
| `shopify_stale` | Shopify לא מסונכרן |
| `rebuild_stale` | אימות מלאי לא רץ |
| `export_stale` | ייצוא לילי לא רץ |
| `forecast_stale` | תחזית לא עודכנה |
| `supplier_price_anomaly` | אנומליה במחיר ספק |
| `gi_price_activation_failed` | הפעלת מחיר עתידי נכשלה |
| `gi_api_failure` | שגיאת API ב-Green Invoice |
| `gi_mirror_insert_failed` | כשל בכתיבת מראה GI |
| `lionwheel_auth_expired` | פג תוקף הזדהות LionWheel |
| `lionwheel_schema_drift` | שינוי לא צפוי במבנה LionWheel |
| `shopify_network_failure` | תקלת רשת Shopify (היסטורי) |

**Info subtype labels:**

| `subtype` | UI label |
|---|---|
| `lw_capped_window` | חריגה מ-100 שורות ב-LionWheel |
| `gi_non_ils_currency` | חשבונית במטבע שאינו ש"ח |
| `lw_pick_historical_seed` | זרעי seed היסטוריים — נסגר באופן חד-פעמי |
| `lionwheel_payload_invalid_sku` | שורה לא תקינה ב-LionWheel |
| `lionwheel_payload_invalid_picked_quantity` | כמות לקיטה לא תקינה |
| `lionwheel_order_note` | הערת הזמנה |
| `lw_pick_enrich_failed` | העשרת לקיטה נכשלה |
| `bom_version_published` | גרסת BOM פורסמה |

**Top badge strip:** `12 החלטות · 4 משימות · 2 התראות`

**Filter side-pane labels:**

| section | label |
|---|---|
| Type | סוג |
| Severity | חומרה (מידע / אזהרה / קריטי) |
| Source | מקור |
| Status | מצב (פתוח / טופל / הכל) |
| Search | חיפוש |
| Save filter | שמור סינון |
| Reset to default | אתחל סינון |
| Saved view "Default" | פתוח |
| Saved view "History" | טופל |

**Action dialogs / confirmations / toasts:**

| context | string |
|---|---|
| Approve confirmation header | אישור שינוי מחיר |
| Approve confirmation body | המחיר הנוכחי יוחלף במחיר המוצע. הפעולה תיחתם ב-audit. |
| Approve confirm button | אשר |
| Approve cancel button | ביטול |
| Edit→Approve placeholder for new price | מחיר מתוקן (₪ לפי יחידת רכש) |
| Edit→Approve placeholder for reason | סיבה לעריכה (חובה) |
| Edit→Approve placeholder for effective_at | תאריך תחילת תוקף (אופציונלי) |
| Reject placeholder for reason | סיבת הדחייה (חובה) |
| Reject confirm button | דחה |
| Defer duration options | שעה · יום · שבוע |
| Snooze duration options | יום · שבוע |
| Toast: Approved success | אושר |
| Toast: Rejected success | נדחה |
| Toast: 409 SUPPLIER_MAPPING_DRIFT | המיפוי השתנה מאז שהוצעה ההצעה. נדרש מיפוי מחדש. |
| Toast: 409 STALE_PROPOSAL | מישהו אחר כבר טיפל בהצעה זו. |
| Toast: 422 invalid input | הקלט לא תקין: <details> |
| Loading state (feed) | טוען רשימה… |
| Loading state (drawer) | טוען פרטים… |
| Empty (all clean) | הכל מטופל |
| Empty (filter no match) | אין פריטים שמתאימים לסינון |

**Auto-resolve note (Warning body):** הכרטיסייה תיסגר לבד כשהאינטגרציה תחזור לתקין.

**Names not IDs:** every UI surface shows display names (`מיקי מדבקות` / `אריזת מדבקה 30 מ"מ`). Internal IDs render small at the bottom of drawer mode only.

### 1.16 Defer / Snooze lifecycle

The Defer (Decision) and Snooze (To-Do) actions hide a card from the default view temporarily without changing its `status`. Implementation:

```sql
ALTER TABLE private_core.exceptions
  ADD COLUMN snoozed_until timestamptz;
COMMENT ON COLUMN private_core.exceptions.snoozed_until IS
  'Until this timestamp, the card is hidden from the default Inbox view. Set by Defer (Decision) or Snooze (To-Do) actions. NULL means not snoozed.';
```

Default view filter:
```sql
WHERE status IN ('open','acknowledged') AND card_type IN ('decision','to_do','warning')
  AND (snoozed_until IS NULL OR snoozed_until <= NOW())
```

Defer durations: 1 hour, 1 day, 1 week (Hebrew labels per §1.15). Snooze durations: 1 day, 1 week.

When the snooze elapses, the card naturally re-appears in the default view (the filter `snoozed_until <= NOW()` admits it). No re-emit is needed; no new row created. The `snoozed_until` column is set on a row that is otherwise unchanged (`status` stays `open`).

Defer/Snooze does NOT generate a `change_log` row (it is a UI-state hint, not a state transition that affects the underlying entity).

`auto_resolved` cards cannot be snoozed (they are already in the History tab).

---

## 2. Schema changes

All migration files are forward-only. The migration order (M1 → M2 → M3 → M4 → M5) is locked; deployment plan in §2.7 sequences code rollouts.

### 2.1 M1 — Add `card_type` and `subtype` to `private_core.exceptions`

```sql
-- 0146_exceptions_card_type_and_subtype.sql
BEGIN;
SET search_path TO private_core, public;

ALTER TABLE private_core.exceptions
  ADD COLUMN card_type text,
  ADD COLUMN subtype   text;

COMMENT ON COLUMN private_core.exceptions.card_type IS
  'Inbox card type per typed-Inbox spec 2026-05-04. Values: decision, to_do, warning, info. NOT NULL after backfill (M3).';
COMMENT ON COLUMN private_core.exceptions.subtype IS
  'Per-card-type subtype label, e.g., gi_price_proposal, unmapped_fg_alias, lionwheel_stale. Producer is source of truth.';

COMMIT;
```

The columns are added nullable so existing emit-sites do not break in-flight. M3 backfills, validates, and adds NOT NULL + CHECK constraints.

### 2.2 M2 — Create `private_core.price_proposals`

```sql
-- 0147_price_proposals.sql
BEGIN;
SET search_path TO private_core, public;

CREATE TABLE private_core.price_proposals (
  proposal_id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  supplier_item_id         uuid NOT NULL REFERENCES private_core.supplier_items(supplier_item_id),
  gi_expense_id            text NOT NULL REFERENCES private_core.gi_expense_mirror(gi_expense_id),
  -- Synthetic line index. v1 = always 0 (single proposal per expense — see §1.14).
  -- Reserved for future per-line OCR enrichment (Tom-prioritized v2 enhancement).
  line_index_synthetic     integer NOT NULL DEFAULT 0,
  -- Planner-form-supplied — the missing GI quantity (or override path).
  quantity_units           private_core.qty_8dp,           -- NULL when override mode
  unit_price_net_override  private_core.money_4dp,         -- NULL when quantity mode
  current_unit_price_net   private_core.money_4dp,         -- snapshot at submit time
  proposed_unit_price_net  private_core.money_4dp NOT NULL,
  pct_delta                private_core.ratio_8dp NOT NULL,
  abs_delta_money          private_core.money_4dp NOT NULL,
  confidence               text NOT NULL CHECK (confidence IN ('HIGH','MEDIUM')),
  tier                     text NOT NULL CHECK (tier IN ('tier_1','tier_2','tier_3')),
  status                   text NOT NULL DEFAULT 'proposed'
                           CHECK (status IN ('proposed','activated','rejected','approved_pending_activation','activation_failed')),
  override_reason          text,                       -- NOT NULL on Edit→Approve — handler enforced
  effective_at             timestamptz,                -- NULL = activate immediately on Approve
  rejection_reason         text,                       -- NOT NULL on Reject — handler enforced
  resulting_price_history_id uuid REFERENCES private_core.price_history(price_history_id),
  related_exception_id     uuid REFERENCES private_core.exceptions(exception_id),
  proposed_at              timestamptz NOT NULL DEFAULT NOW(),
  proposed_by              uuid NOT NULL,
  activated_at             timestamptz,
  activated_by             uuid,
  rejected_at              timestamptz,
  rejected_by              uuid,
  site_id                  text NOT NULL DEFAULT 'GT-MAIN',
  created_at               timestamptz NOT NULL DEFAULT NOW(),
  updated_at               timestamptz NOT NULL DEFAULT NOW(),
  -- XOR: exactly one of quantity_units / unit_price_net_override is supplied.
  CONSTRAINT price_proposals_quantity_xor
    CHECK (num_nonnulls(quantity_units, unit_price_net_override) = 1),
  -- Reject path requires reason (DB safety net beyond handler enforcement).
  CONSTRAINT price_proposals_rejection_reason_required
    CHECK (status <> 'rejected' OR rejection_reason IS NOT NULL)
);

-- DEPENDS-ON: private_core.touch_updated_at() function (defined in 0001_domains_and_schemas.sql;
-- used by 21+ existing tables — assumed present).

-- One proposal per (gi_expense_id, line_index_synthetic). v1 line_index_synthetic
-- is always 0; the unique index admits future per-line proposals without DDL change.
CREATE UNIQUE INDEX uniq_price_proposals_expense_line
  ON private_core.price_proposals(gi_expense_id, line_index_synthetic);

CREATE INDEX idx_price_proposals_status
  ON private_core.price_proposals(status)
  WHERE status IN ('proposed','approved_pending_activation','activation_failed');

CREATE INDEX idx_price_proposals_supplier_item
  ON private_core.price_proposals(supplier_item_id);

CREATE TRIGGER trg_price_proposals_touch_updated_at
  BEFORE UPDATE ON private_core.price_proposals
  FOR EACH ROW EXECUTE FUNCTION private_core.touch_updated_at();

COMMENT ON TABLE private_core.price_proposals IS
  'Lifecycle table for GI-driven supplier price-change proposals. Distinct from price_history (which is append-only canonical price ledger). Approve flow inserts a NEW price_history row; this table tracks the proposal lifecycle.';

COMMIT;
```

`price_history` retains its append-only invariant (trigger `trg_price_history_no_update` from migration 0025 unchanged). The proposal table holds the lifecycle; on Approve, a new `price_history` row is written.

### 2.3 M3 — Backfill `card_type`+`subtype`, add NOT NULL + CHECK

```sql
-- 0148_exceptions_typed_backfill.sql
BEGIN;
SET search_path TO private_core, public;

-- Idempotency guard: detect if 2026-04-27 cleanup already ran
-- (lw_pick_data_missing rows resolved → if 0 open, cleanup ran).
-- This is informational; backfill is idempotent regardless.

-- Decision categories
UPDATE private_core.exceptions SET card_type='decision', subtype='positive_adjustment'
 WHERE card_type IS NULL AND category='positive_adjustment';
UPDATE private_core.exceptions SET card_type='decision', subtype='loss_above_threshold'
 WHERE card_type IS NULL AND category='loss_above_threshold';
UPDATE private_core.exceptions SET card_type='decision', subtype='count_large_variance'
 WHERE card_type IS NULL AND category='count_large_variance';
UPDATE private_core.exceptions SET card_type='decision', subtype='customer_credit'
 WHERE card_type IS NULL AND category='lionwheel_credit_needed';
UPDATE private_core.exceptions SET card_type='decision', subtype='po_line_over_receipt'
 WHERE card_type IS NULL AND category='po_line_over_receipt';

-- To-Do categories
UPDATE private_core.exceptions SET card_type='to_do', subtype='unmapped_gi_supplier'
 WHERE card_type IS NULL AND category='gi_unmapped_supplier';
UPDATE private_core.exceptions SET card_type='to_do', subtype='unmapped_lw_sku'
 WHERE card_type IS NULL AND category='lionwheel_unknown_sku';
UPDATE private_core.exceptions SET card_type='to_do', subtype='unmapped_fg_alias'
 WHERE card_type IS NULL AND category='shopify_unmapped_item';
-- shopify_variant_not_found: dev fixtures DELETE'd by 2026-04-27 cleanup; real ones stay as decision
-- Subtype is shopify_variant_gap (NOT lw_catalog_gap — that subtype is for LionWheel-specific catalog gaps).
UPDATE private_core.exceptions SET card_type='decision', subtype='shopify_variant_gap'
 WHERE card_type IS NULL AND category='shopify_variant_not_found';

-- Warning categories
UPDATE private_core.exceptions SET card_type='warning', subtype='gi_stale'
 WHERE card_type IS NULL AND category='gi_stale';
UPDATE private_core.exceptions SET card_type='warning', subtype='lionwheel_stale'
 WHERE card_type IS NULL AND category='lionwheel_stale';
UPDATE private_core.exceptions SET card_type='warning', subtype='shopify_stale'
 WHERE card_type IS NULL AND category='shopify_stale';
UPDATE private_core.exceptions SET card_type='warning', subtype='rebuild_stale'
 WHERE card_type IS NULL AND category='rebuild_stale';
UPDATE private_core.exceptions SET card_type='warning', subtype='export_stale'
 WHERE card_type IS NULL AND category='export_stale';
UPDATE private_core.exceptions SET card_type='warning', subtype='forecast_stale'
 WHERE card_type IS NULL AND category='forecast_stale';
UPDATE private_core.exceptions SET card_type='warning', subtype='gi_api_failure'
 WHERE card_type IS NULL AND category='gi_api_failure';
UPDATE private_core.exceptions SET card_type='warning', subtype='gi_mirror_insert_failed'
 WHERE card_type IS NULL AND category='gi_mirror_insert_failed';
UPDATE private_core.exceptions SET card_type='warning', subtype='lionwheel_auth_expired'
 WHERE card_type IS NULL AND category='lionwheel_auth_expired';
UPDATE private_core.exceptions SET card_type='warning', subtype='lionwheel_schema_drift'
 WHERE card_type IS NULL AND category='lionwheel_schema_drift';
UPDATE private_core.exceptions SET card_type='warning', subtype='shopify_network_failure'
 WHERE card_type IS NULL AND category='shopify_network_failure';

-- Info categories
UPDATE private_core.exceptions SET card_type='info', subtype='lw_capped_window'
 WHERE card_type IS NULL AND category='lionwheel_capped_window_gap';
UPDATE private_core.exceptions SET card_type='info', subtype='gi_non_ils_currency'
 WHERE card_type IS NULL AND category='gi_non_ils_currency';
UPDATE private_core.exceptions SET card_type='info', subtype='lw_pick_historical_seed'
 WHERE card_type IS NULL AND category='lw_pick_data_missing';
UPDATE private_core.exceptions SET card_type='info', subtype='lionwheel_payload_invalid_sku'
 WHERE card_type IS NULL AND category='lionwheel_payload_invalid_sku';
UPDATE private_core.exceptions SET card_type='info', subtype='lionwheel_payload_invalid_picked_quantity'
 WHERE card_type IS NULL AND category='lionwheel_payload_invalid_picked_quantity';
UPDATE private_core.exceptions SET card_type='info', subtype='lionwheel_order_note'
 WHERE card_type IS NULL AND category='lionwheel_order_note';
UPDATE private_core.exceptions SET card_type='info', subtype='lw_pick_enrich_failed'
 WHERE card_type IS NULL AND category='lw_pick_enrich_failed';
UPDATE private_core.exceptions SET card_type='info', subtype='bom_version_published'
 WHERE card_type IS NULL AND category='bom_version_published';

-- Halt guard: any row still NULL is an unmapped category.
DO $$
DECLARE n_unmapped int;
BEGIN
  SELECT COUNT(*) INTO n_unmapped FROM private_core.exceptions WHERE card_type IS NULL;
  IF n_unmapped > 0 THEN
    RAISE EXCEPTION 'Backfill failed: % rows have no card_type. Inspect via: SELECT category, COUNT(*) FROM private_core.exceptions WHERE card_type IS NULL GROUP BY category;', n_unmapped;
  END IF;
END $$;

-- One-shot bulk-resolve historical buckets (idempotent; only acts on still-open rows)
UPDATE private_core.exceptions
   SET status='resolved', resolved_at=NOW(), resolution_notes='Auto-resolved by 2026-05-04 typed-Inbox migration: historical seed; producer no longer re-emits identical event IDs.'
 WHERE status='open' AND subtype='lw_pick_historical_seed';

UPDATE private_core.exceptions
   SET status='resolved', resolved_at=NOW(), resolution_notes='Auto-resolved by 2026-05-04 typed-Inbox migration: historical pre-runtime burst; superseded by Shopify runtime cache.'
 WHERE status='open' AND subtype='shopify_network_failure';

-- Add NOT NULL + CHECK
ALTER TABLE private_core.exceptions
  ALTER COLUMN card_type SET NOT NULL,
  ADD CONSTRAINT exceptions_card_type_check CHECK (card_type IN ('decision','to_do','warning','info'));

-- subtype allowed to be NULL on rows where producer has no subtype (rare; legacy planning_run rows etc.).
-- New emitters MUST populate; enforced at handler/emit time, not DB.

COMMIT;
```

### 2.4 M4 — Extend `change_log.action` enum (full enumeration)

```sql
-- 0149_change_log_inbox_actions.sql
BEGIN;
SET search_path TO private_core, public;

ALTER TABLE private_core.change_log DROP CONSTRAINT change_log_action_check;
ALTER TABLE private_core.change_log
  ADD CONSTRAINT change_log_action_check
  CHECK (action = ANY (ARRAY[
    -- ALL existing 60 actions from migration 0123 verbatim:
    'CREATE'::text,'UPDATE_QUICK'::text,'UPDATE_STRUCTURAL'::text,'SOFT_DELETE'::text,
    'FORECAST_LINE_UPSERT'::text,'FORECAST_LINE_ZERO'::text,
    'FORECAST_VERSION_PUBLISH'::text,'FORECAST_VERSION_DISCARD'::text,
    'FORECAST_VERSION_SUPERSEDE'::text,'FORECAST_FREEZE_OVERRIDE'::text,
    'PRICE_HISTORY_INSERT'::text,'SUPPLIER_PRICE_UPDATE_AUTO'::text,'SUPPLIER_PRICE_UPDATE_MANUAL'::text,
    'PLANNING_RUN_CREATE'::text,'PLANNING_RUN_RUNNING'::text,'PLANNING_RUN_COMPLETED'::text,
    'PLANNING_RUN_FAILED'::text,'PLANNING_RUN_SUPERSEDE'::text,'PLANNING_REC_STATUS_CHANGE'::text,
    'PO_CREATE'::text,'PO_UPDATE'::text,'PO_STATUS_CHANGE'::text,'PO_CANCEL'::text,
    'PO_LINE_CREATE'::text,'PO_LINE_UPDATE'::text,'POL_STATUS_CHANGE'::text,'POL_CANCEL'::text,
    'PLANNING_REC_CONVERTED_TO_PO'::text,'PRODUCTION_ACTUAL_SUBMIT'::text,
    'ITEM_CREATED'::text,'ITEM_UPDATED'::text,'ITEM_STATUS_CHANGED'::text,
    'COMPONENT_CREATED'::text,'COMPONENT_UPDATED'::text,'COMPONENT_STATUS_CHANGED'::text,
    'SUPPLIER_CREATED'::text,'SUPPLIER_UPDATED'::text,'SUPPLIER_STATUS_CHANGED'::text,
    'SUPPLIER_ITEM_CREATED'::text,'SUPPLIER_ITEM_UPDATED'::text,'SUPPLIER_ITEM_STATUS_CHANGED'::text,
    'POLICY_UPDATED'::text,'BOM_HEAD_CREATED'::text,'BOM_VERSION_CREATED'::text,
    'BOM_LINE_UPSERT'::text,'BOM_LINE_DELETED'::text,'BOM_VERSION_PUBLISHED'::text,
    'ALIAS_REJECTED'::text,'ALIAS_REVOKED'::text,'SUPPLIER_ITEM_DELETED'::text,
    'USER_ROLE_CHANGED'::text,'USER_STATUS_CHANGED'::text,
    'PRODUCTION_PLAN_CREATED'::text,'PRODUCTION_PLAN_EDITED'::text,
    'PRODUCTION_PLAN_CANCELLED'::text,'PRODUCTION_PLAN_LINKED_ACTUAL'::text,
    'PRODUCTION_PLAN_DELETED'::text,
    'HOLIDAYS_IL_CREATE'::text,'HOLIDAYS_IL_UPDATE'::text,'HOLIDAYS_IL_ARCHIVE'::text,'HOLIDAYS_IL_BULK_IMPORT'::text,
    'CREDIT_DECISION_APPROVED'::text,'CREDIT_DECISION_REJECTED'::text,
    -- 0149 — typed-Inbox actions:
    'INBOX_DECISION_APPROVE'::text,
    'INBOX_DECISION_REJECT'::text,
    'INBOX_WARNING_ACKNOWLEDGE'::text,
    'INBOX_INFO_DISMISS'::text
  ]));

COMMIT;
```

**Hard halt-guard preflight** (must run BEFORE the DROP+ADD so any drift halts the migration before it loses values):

```sql
-- Run this FIRST. If the live enum drift is detected, RAISE EXCEPTION and abort.
DO $$
DECLARE
  live_count int;
  expected_count int := 64;  -- 60 from migration 0123 + 4 INBOX_* = 64
BEGIN
  SELECT cardinality(string_to_array(
    regexp_replace(pg_get_constraintdef(oid), '.*ARRAY\[(.*)\]\)\)', '\1'),
    ','
  )) INTO live_count
    FROM pg_constraint
   WHERE conname='change_log_action_check'
     AND conrelid='private_core.change_log'::regclass;

  -- Migration 0123 had 60 actions. Expected current = 60.
  IF live_count <> 60 THEN
    RAISE EXCEPTION 'change_log enum drift: live_count=% (expected 60 from migration 0123). Migration 0149 cannot proceed safely. Inspect live enum, update this migration to enumerate the full live set + 4 INBOX_* additions, and re-apply.', live_count;
  END IF;
END $$;

-- If preflight passes, the DROP+ADD above is safe.
```

Implementation note: if a future migration between 0123 and 0149 extends the enum further, this halt-guard fires and forces the implementer to refresh the spec's enum snapshot. This is intentional — silent drop of newly-added values would invalidate every change_log row using them.

### 2.5 M5 — Status enum and dedupe index

```sql
-- 0150_exceptions_status_dismissed_and_dedupe_index.sql
BEGIN;
SET search_path TO private_core, public;

-- Add 'dismissed' to status CHECK (preserving credit-decision states from 0124).
ALTER TABLE private_core.exceptions DROP CONSTRAINT exceptions_status_check;
ALTER TABLE private_core.exceptions
  ADD CONSTRAINT exceptions_status_check
  CHECK (status = ANY (ARRAY[
    'open'::text,'acknowledged'::text,'resolved'::text,'auto_resolved'::text,
    -- 0124 credit-decision states:
    'pending_gi_action'::text,'gi_draft_created'::text,'gi_action_failed'::text,
    -- 0150 typed-Inbox addition:
    'dismissed'::text
  ]));

-- Defer/Snooze lifecycle (per §1.16): a snoozed card hides from default view
-- until snoozed_until elapses, but its status is unchanged.
ALTER TABLE private_core.exceptions
  ADD COLUMN snoozed_until timestamptz;
CREATE INDEX idx_exceptions_snoozed_until
  ON private_core.exceptions(snoozed_until)
  WHERE snoozed_until IS NOT NULL;

-- Replace partial dedupe index. Two indexes for two access patterns:
--  (a) emit-with-reopen lookup: WHERE dedupe_key=$1 (regardless of status) — needs (dedupe_key) only.
--  (b) existing autoResolve / autoResolveExceptionsFor: WHERE status='open' AND dedupe_key=$1 —
--      benefits from a (dedupe_key, status) covering index.
-- We keep both to avoid regression on the existing auto-resolve hot paths.
DROP INDEX IF EXISTS idx_exceptions_dedupe;
CREATE INDEX idx_exceptions_dedupe_key
  ON private_core.exceptions(dedupe_key)
  WHERE dedupe_key IS NOT NULL;
CREATE INDEX idx_exceptions_dedupe_status
  ON private_core.exceptions(dedupe_key, status)
  WHERE dedupe_key IS NOT NULL;

COMMIT;
```

**Performance note:** the OLD partial index `(dedupe_key) WHERE status='open'` was very small (only open rows). The new pair grows with all dedupe-keyed rows over time. For GT's volume (low thousands of resolved rows per year), this is negligible. If volume grows past ~100K resolved rows, a follow-up adds an archive partition.

### 2.5b M5b — `fn_gi_price_proposal_activator()` SQL function

```sql
-- 0150b_fn_gi_price_proposal_activator.sql
BEGIN;
SET search_path TO private_core, public;

CREATE OR REPLACE FUNCTION private_core.fn_gi_price_proposal_activator()
RETURNS TABLE(activated_count int, failed_count int)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_proposal RECORD;
  v_ph_id uuid;
  v_activated int := 0;
  v_failed int := 0;
BEGIN
  FOR v_proposal IN
    SELECT proposal_id, supplier_item_id,
           COALESCE(unit_price_net_override, proposed_unit_price_net) AS price_to_activate,
           gi_expense_id, override_reason
      FROM private_core.price_proposals
     WHERE status = 'approved_pending_activation'
       AND effective_at IS NOT NULL
       AND effective_at <= NOW()
     FOR UPDATE SKIP LOCKED
     LIMIT 100
  LOOP
    BEGIN
      -- Append-only price_history row (preserves trigger trg_price_history_no_update).
      INSERT INTO private_core.price_history
        (supplier_item_id, unit_price_net, source, event_at, posted_at,
         actor_user_id, actor_snapshot, source_document_id, notes)
      VALUES
        (v_proposal.supplier_item_id, v_proposal.price_to_activate,
         'gi_invoice_manual_activated', NOW(), NOW(),
         NULL, '<system:gi_price_proposal_activator>',
         v_proposal.gi_expense_id,
         format('Activated future-dated proposal %s; reason=%s',
                v_proposal.proposal_id, v_proposal.override_reason))
      RETURNING price_history_id INTO v_ph_id;

      -- Update active price.
      UPDATE private_core.supplier_items
         SET std_cost_per_inv_uom = v_proposal.price_to_activate * pack_conversion,
             updated_at = NOW()
       WHERE supplier_item_id = v_proposal.supplier_item_id;

      -- Lifecycle table.
      UPDATE private_core.price_proposals
         SET status='activated', activated_at=NOW(),
             resulting_price_history_id = v_ph_id
       WHERE proposal_id = v_proposal.proposal_id;

      -- change_log rows.
      INSERT INTO private_core.change_log
        (entity_table, entity_id, action, changed_fields, new_values, actor_user_id, actor_snapshot)
      VALUES
        ('price_history', v_ph_id::text, 'PRICE_HISTORY_INSERT',
         '[]'::jsonb, jsonb_build_object('proposal_id', v_proposal.proposal_id),
         NULL, '<system:gi_price_proposal_activator>'),
        ('supplier_items', v_proposal.supplier_item_id::text, 'SUPPLIER_PRICE_UPDATE_AUTO',
         jsonb_build_array('std_cost_per_inv_uom'),
         jsonb_build_object('std_cost_per_inv_uom', v_proposal.price_to_activate),
         NULL, '<system:gi_price_proposal_activator>');

      v_activated := v_activated + 1;
    EXCEPTION WHEN OTHERS THEN
      -- Mark this proposal as activation_failed and emit a warning exception.
      UPDATE private_core.price_proposals
         SET status='activation_failed'
       WHERE proposal_id = v_proposal.proposal_id;

      -- Emit-with-reopen warning (inline; same contract as §1.12).
      DECLARE
        v_existing_id uuid;
      BEGIN
        SELECT exception_id INTO v_existing_id
          FROM private_core.exceptions
         WHERE dedupe_key = format('gi_price_activation_failed:%s', v_proposal.proposal_id)
         FOR UPDATE;
        IF NOT FOUND THEN
          INSERT INTO private_core.exceptions
            (category, severity, source, title, detail, dedupe_key,
             card_type, subtype)
          VALUES
            ('gi_price_activation_failed', 'warning',
             'job.gi_price_proposal_activator',
             format('Future-dated price activation failed for proposal %s', v_proposal.proposal_id),
             SQLERRM,
             format('gi_price_activation_failed:%s', v_proposal.proposal_id),
             'warning', 'gi_price_activation_failed');
        ELSE
          UPDATE private_core.exceptions
             SET status='open',
                 resolved_by=NULL, resolved_at=NULL,
                 acknowledged_by=NULL, acknowledged_at=NULL,
                 detail=SQLERRM, updated_at=NOW(),
                 resolution_notes = right(
                   COALESCE(resolution_notes,'') || E'\n[Re-opened ' || NOW()::text || ' by activator job]',
                   4096)
           WHERE exception_id = v_existing_id;
        END IF;
      END;

      v_failed := v_failed + 1;
    END;
  END LOOP;

  RETURN QUERY SELECT v_activated, v_failed;
END;
$$;

COMMENT ON FUNCTION private_core.fn_gi_price_proposal_activator() IS
  'Hourly job: activates approved-pending-activation price proposals whose effective_at <= NOW(). Preserves price_history append-only invariant. Emits gi_price_activation_failed warning on per-proposal exception.';

COMMIT;
```

### 2.6 M6 — pg_cron registration

```sql
-- 0151_gi_price_proposal_activator_cron.sql
BEGIN;

SELECT cron.schedule(
  'gi_price_proposal_activator',
  '5 * * * *',  -- 5 minutes past every hour
  $$ SELECT * FROM private_core.fn_gi_price_proposal_activator(); $$
);

COMMIT;
```

### 2.7 Deployment sequencing

The following order is mandatory:

1. **Day 0**: Apply M1 (`0146_exceptions_card_type_and_subtype.sql`). Columns are nullable; existing emitters keep working unmodified.
2. **Day 0**: Apply M2 (`0147_price_proposals.sql`). Table is new; no existing code touches it.
3. **Day 0+1**: Code rollout — all emitters updated to populate `card_type`+`subtype`. Code is ready to land but emit-with-reopen contract not yet activated.
4. **Day 0+1**: Apply M5 (`0150_*`). Replace partial index. Old code (still in flight) queries `WHERE status='open' AND dedupe_key=$1` — covered by the new `idx_exceptions_dedupe_status (dedupe_key, status)` covering index, so no regression. New code uses the unfiltered `idx_exceptions_dedupe_key` for emit-with-reopen lookups. Also adds `snoozed_until` column + its index per §1.16.
5. **Day 0+2**: Apply M3 (`0148_exceptions_typed_backfill.sql`). Backfills all rows; halt-guard fails if any row unmapped (forces manual triage of new categories before NOT NULL is added).
6. **Day 0+2**: Apply M4 (`0149_change_log_inbox_actions.sql`).
7. **Day 0+3**: Apply M6 (`0151_*`) — pg_cron entry for future-dated activator (only if any approved-pending-activation rows exist; otherwise can be deferred).

The reason M3 lands AFTER code deploy: the backfill queries `category` (not `card_type`) and is correct for any row regardless of code version. The NOT NULL constraint at the end of M3 cannot be added before all in-flight INSERTs have switched to populating `card_type`.

---

## 3. Migration of currently-open exceptions (live count drifts)

**Live count at spec-write time is unknown.** The 2026-04-27 cleanup spec recorded 421 open at its time of writing; live count drifts. The migration M3 above (§2.3) is the canonical migration; it is idempotent and category-driven, not count-driven.

**Acceptance criterion** (replacing the brittle "421" target): post-migration verification query

```sql
SELECT card_type, COUNT(*) AS n
  FROM private_core.exceptions
 WHERE status IN ('open','acknowledged')
   AND card_type IN ('decision','to_do','warning')
 GROUP BY card_type;
```
must return rows for all 3 types AND the `info` count in default-view filter must be 0 (because info is hidden). Total operator-actionable count is the sum of the 3 types. Drift on `lionwheel_capped_window_gap` (now `info:lw_capped_window`) does not affect the operator count.

**Coordination with 2026-04-27 cleanup spec:**
- If 2026-04-27 cleanup ran first: those rows are already `resolved` with category names; M3 still backfills `card_type`+`subtype` on those rows (UPDATE matches by category, not status). Outcome: resolved+typed.
- If 2026-04-27 cleanup did NOT run: M3 includes its OWN bulk-resolves for `lw_pick_historical_seed` (was `lw_pick_data_missing`) and `shopify_network_failure`. Other dispositions from the cleanup spec (the 78 `gi_unmapped_supplier`, the 128 `lionwheel_capped_window_gap`, the 54 `shopify_unmapped_item`) are not auto-resolved — they convert into typed `to_do` / `info` cards naturally and remain open until the underlying state changes (which is correct behavior).

---

## 4. Code changes

### 4.1 Type-aware-dedupe emitters (use emit-with-reopen contract, write `card_type`+`subtype`+typed `dedupe_key`)

These emitters write `dedupe_key` and need the §1.12 emit-with-reopen contract:

| File | Function | Card type bucket |
|---|---|---|
| `api/src/integrations/lionwheel/poller.ts:567-597` | `emitException` (LW poll diagnostics) | warning / info |
| `api/src/integrations/lionwheel/reconciliation.ts` (multiple sites) | inline `INSERT private_core.exceptions` (lionwheel_*, lw_*, lionwheel_credit_needed) | varies — see §3 backfill table |
| `supabase/functions/factory_os_jobs/index.ts:190-214` | `emitException` (GI ingest) | warning (api_failure, mirror_insert_failed) and info / to_do |
| `api/src/jobs/freshness_check.ts:233-283` | `emitOrPromote` (freshness producers) | warning |
| `api/src/boms/publish.ts:505-...` | inline INSERT (`bom_version_published`) | info |
| `api/src/integration-sku-map/mutations.ts:233-...` | inline INSERT | warning (mapping conflicts) |

**Required changes** for each:
1. Replace `WHERE dedupe_key=$1 AND status='open'` with the §1.12 emit-with-reopen contract (3-branch: insert / noop / reopen).
2. Populate `card_type` and `subtype` on INSERT (and on REOPEN's UPDATE … SET).
3. Ensure `dedupe_key` shape matches the type-aware convention (event-scoped for decision/info; state-scoped for to_do; producer-scoped for warning).

### 4.2 Per-submission one-shot inserters (NOT subject to type-aware dedupe; only `card_type`+`subtype` populate)

| File | Function | card_type | subtype |
|---|---|---|---|
| `api/src/physical-counts/handler.ts:412` | `submitPhysicalCount` (large-variance pending) | `decision` | `count_large_variance` |
| `api/src/waste-adjustments/handler.ts:750-767` | submit handler (positive_adjustment, loss_above_threshold) | `decision` | per category |

These insert without `dedupe_key`; this spec ONLY adds `card_type` and `subtype` columns to their INSERT statements. Their resolve path (planner approval or rejection) is unchanged.

### 4.3 New emitter: GI price-proposal producer

New file: `api/src/integrations/green_invoice/price-proposal.ts` (or its mirror in `supabase/functions/factory_os_jobs/index.ts`). Implements §1.14 pipeline. Invoked from the existing GI invoice ingest after each line is mirrored (after the unmapped-supplier check at line 1908).

### 4.4 Handler changes — `api/src/exceptions/handler.ts`

- `roleAllowsRead` — change from `return true` to `return role === 'planner' || role === 'admin'`.
- New helper `roleAllowsScopedRead(session, query)`: returns true if `query.related_entity_type === 'form_submission'` AND a row exists in `form_submissions WHERE submission_id=query.related_entity_id AND author_user_id=session.user_id`. Operators get this scoped read.
- `handleAcknowledge` — restrict to `card_type='warning'` only; reject 409 INVALID_ACTION_FOR_TYPE for other types.
- `handleResolve` — split into:
  - `handleApprove` (decision only) — emits `INBOX_DECISION_APPROVE` + subtype-specific change_log; subtype-specific approve hooks
  - `handleReject` (decision only) — emits `INBOX_DECISION_REJECT`; rejection_reason required
  - `handleDismiss` (info only) — emits `INBOX_INFO_DISMISS`
- `handleEditApprove` — new; (decision, gi_price_proposal subtype only); requires `override_unit_price_net` + `override_reason`; optional `effective_at`
- `handleBulkResolve` — deprecated for new card_type rows; returns 422 BULK_RESOLVE_DEPRECATED for any row with `card_type IS NOT NULL`. Continues to work on legacy NULL-card_type rows during the deployment window.
- LIST response: include `card_type`, `subtype`, and a `key_facts` JSONB blob.
  - For type-aware-dedupe emitters (§4.1): producer computes and stores at emit time on `exceptions.raw_payload->'key_facts'`.
  - For per-submission one-shot emitters (§4.2): `key_facts` is **not** populated at emit time. The handler computes a fallback `key_facts` from the `raw_payload` shape on the LIST response itself, using a per-subtype mapper (`api/src/exceptions/key-facts-derivers.ts`). Mappers exist for `count_large_variance`, `positive_adjustment`, `loss_above_threshold`. The UI receives a uniform `key_facts` shape regardless of how it was produced.

### 4.5 New handlers — `api/src/inbox/gi_price_proposal/handler.ts`

Per §1.14.4: the Approve / Edit→Approve / Reject transactions, including the §1.14.4 step-(1) supplier-mapping drift guard.

### 4.6 New job — `api/src/jobs/gi_price_proposal_activator.ts`

Per §1.14.6 future-dated activation. Uses `FOR UPDATE SKIP LOCKED` for safe concurrent runs.

### 4.7 Portal — `window2-portal-sandbox/src/`

Routes (full repo paths; verify against `reference_gt_factory_paths.md`):
- `window2-portal-sandbox/src/app/(inbox)/inbox/page.tsx` — REWRITE (single feed + filter + sort + badges)
- `window2-portal-sandbox/src/app/(inbox)/inbox/approvals/gi-expense-review/[gi_expense_id]/page.tsx` — NEW Stage-B form (To-Do action target; produces a Decision card on submit)
- `window2-portal-sandbox/src/app/(inbox)/inbox/approvals/gi-price-proposal/[proposal_id]/page.tsx` — NEW Decision drawer (target of `decision:gi_price_proposal`)
- `window2-portal-sandbox/src/app/(inbox)/inbox/approvals/physical-count/[submission_id]/page.tsx` — UNIFY chrome (existing logic preserved)
- `window2-portal-sandbox/src/app/(inbox)/inbox/approvals/waste/[submission_id]/page.tsx` — UNIFY chrome
- `window2-portal-sandbox/src/app/(inbox)/inbox/credit/[exception_id]/page.tsx` — UNIFY chrome (logic unchanged)
- History tab is `?view=history` query string on `/inbox/page.tsx`, NOT a separate route.
- `/inbox/queues/*` is OUT OF SCOPE per §1.10. To-Do deep-links go to `/admin/integration-sku-map`, `/admin/suppliers`, etc.

Components (full repo paths):
- `window2-portal-sandbox/src/components/inbox/InboxCard.tsx` — universal frame (Header / KeyFacts / Body slot / ActionBar)
- `window2-portal-sandbox/src/components/inbox/bodies/PriceProposalBody.tsx`
- `window2-portal-sandbox/src/components/inbox/bodies/StockImpactBody.tsx` (reused by GR/count/waste)
- `window2-portal-sandbox/src/components/inbox/bodies/QueueToDoBody.tsx`
- `window2-portal-sandbox/src/components/inbox/bodies/SingleTaskToDoBody.tsx`
- `window2-portal-sandbox/src/components/inbox/bodies/WarningBody.tsx`
- `window2-portal-sandbox/src/components/inbox/bodies/InfoBody.tsx`
- `window2-portal-sandbox/src/components/inbox/FilterSidePane.tsx`
- `window2-portal-sandbox/src/components/inbox/TopBadgeStrip.tsx`
- `window2-portal-sandbox/src/lib/inbox-copy.ts` — Hebrew register from §1.15
- `window2-portal-sandbox/src/lib/inbox-status.ts` — macro-status compression (§1.11)

### 4.8 Planning engine read of `price_history` — guard against `proposed`/`activation_failed` lifecycle leaks

Since this spec adds `price_proposals` (not `price_history`) for proposed prices, the planning engine continues to read `price_history` only and is unaffected.

If a future read path queries `price_history.unit_price_net` to compute "current price", it MUST filter to the latest row by `event_at` (or use `supplier_items.std_cost_per_inv_uom` directly). No change to current planning code is in scope.

---

## 5. Acceptance criteria

The spec is satisfied when ALL of the following hold:

1. **Schema validity**: M1-M6 apply cleanly in order; `private_core.rebuild_verifier()` returns 0 before and after.
2. **Type contract enforced**: `private_core.exceptions.card_type IS NOT NULL` for 100% of rows; CHECK admits only the 4 values.
3. **Resolve-doesn't-stick fix**: a producer running twice over the same event yields one row (verified by integration test); a producer running over a new event (different `event_id`) yields a new row; a regression cycle (healthy→unhealthy→healthy→unhealthy) yields ONE row that flips status (open → auto_resolved → open) — NOT two rows.
4. **Audience gating**:
   - operator `GET /queries/exceptions` (no related_entity filter) → 403
   - operator `GET /queries/exceptions?related_entity_type=form_submission&related_entity_id=<own>` → 200 with their own rows only
   - operator `GET /queries/exceptions?related_entity_id=<another's>` → 403 or 404
   - operator `POST /mutations/exceptions/<id>/approve` → 403
5. **Card-type rendering**: each of the 4 card types renders its own scan-row layout and drawer; `gi_price_proposal` matches §1.5.1; `po_line_over_receipt` matches §1.5.2; warnings match §1.6.
6. **Producer flow**:
   - Stage A: every new `gi_expense_mirror` row from a mapped supplier with currency=ILS emits exactly one `to_do:gi_expense_review` card (dedupe-keyed on `gi_expense_id`). Re-ingest of the same expense does NOT duplicate.
   - Stage B Tier 1: planner submits the form for a single-supplier_item supplier in quantity-mode AND delta is within Tier 1 → `supplier_items.std_cost_per_inv_uom` updates, `price_history` row inserted (`source='gi_invoice_auto'`), `change_log` rows for `PRICE_HISTORY_INSERT` AND `SUPPLIER_PRICE_UPDATE_AUTO`, the To-Do card resolves with note 'Auto-updated', NO Decision card emitted.
   - Stage B Tier 2: planner submits → `price_proposals` row inserted (status='proposed'), `decision:gi_price_proposal` Decision card emitted with the §1.5.1 body, To-Do card resolves with note 'Proposal raised'.
   - Stage B Tier 3: planner submits with anomalous magnitude → `warning:supplier_price_anomaly` Warning card emitted (event-scoped key per §1.14.6), NO `supplier_items` update, NO `price_proposals` row, To-Do card resolves with note 'Anomaly emitted'.
   - Submitting with a multi-supplier_item supplier (S2=✗) routes to Tier 2 (no Tier 1 auto-update path), confidence=MEDIUM.
   - Submitting against a baseline-establishing supplier_item (S4=✗, current price NULL/0) routes to Tier 2, confidence=MEDIUM.
   - If supplier mapping changed between To-Do emit and form submit (planner edits dropdown to a different supplier_item): the form re-fetches; if no valid supplier_item is selectable, the form returns 422; planner-friendly error shown.
7. **Approve action**: Approve on a `gi_price_proposal` Decision card writes:
   - new `price_history` row with `source='gi_invoice_manual'`
   - updates `supplier_items.std_cost_per_inv_uom`
   - updates `price_proposals.status='activated'` + `resulting_price_history_id`
   - `change_log` rows for `PRICE_HISTORY_INSERT`, `SUPPLIER_PRICE_UPDATE_MANUAL`, AND `INBOX_DECISION_APPROVE`
   - resolves the exception
   - the supplier-mapping drift guard fires 409 if `supplier_item_id` is no longer active or no longer belongs to this supplier between propose and approve
8. **Reject action**: writes `price_proposals.status='rejected'` + `rejection_reason` (required); `change_log` `INBOX_DECISION_REJECT`; resolves exception; the same `proposal_id` does NOT re-emit. A NEW GI expense from the same supplier produces a new `gi_expense_review` To-Do (different `gi_expense_id`); the planner's next form submission produces a new `proposal_id` and a new Decision card.
9. **Edit→Approve action**: same as Approve but with `override_unit_price_net` + `override_reason`. Optional `effective_at` future date moves status to `approved_pending_activation`; hourly job activates it on schedule.
10. **Acknowledge ≠ Resolve**: clicking Acknowledge on a Warning card sets `status='acknowledged'` but the card REMAINS visible (visually muted); only auto-resolve from producer recovery removes it. Same Warning re-emission while status is `acknowledged` is no-op (does NOT create a duplicate row).
11. **Re-open path**: a Warning that previously auto_resolved AND has a fresh stale event re-flips to `status='open'` with `resolved_*` fields cleared; resolution_notes carries the `[Re-opened ...]` marker; no new row created.
12. **Hebrew labels** match §1.15 verbatim across all rendered surfaces.
13. **History view**: `?view=history` shows rows with `status IN ('resolved','auto_resolved','dismissed','gi_draft_created') AND COALESCE(resolved_at, created_at) >= NOW() - INTERVAL '90 days'`, filterable.
14. **Top badge** shows accurate counts of `status IN ('open','acknowledged') AND card_type IN ('decision','to_do','warning')`, broken down by card_type.
15. **Default sort** matches the §1.10 SQL ORDER BY.
16. **Migration verification**: post-M3 query `SELECT COUNT(*) FROM private_core.exceptions WHERE card_type IS NULL` returns 0.
17. **Bulk-resolve deprecated**: `POST /mutations/exceptions/bulk-resolve` returns 422 for any row with `card_type IS NOT NULL`.
18. **Operator form-submission scoped read**: returns the operator's own exceptions only; does not expose other operators' submissions.
19. **Customer-credit chrome unchanged**: `/inbox/credit/[id]` continues to work; only emit-site adds `card_type='decision'`+`subtype='customer_credit'`.

---

## 6. Out of scope (v1)

- Operator-facing form-side status indicator UI ("pending planner review" / "approved" / "rejected"). API surface exists per §1.2.
- Push / WebSocket real-time refresh — Inbox uses TanStack Query polling at 30s.
- Bulk approve/reject across multiple Decision cards (the existing `bulk-resolve` endpoint is DEPRECATED; will be removed in a follow-up cleanup).
- Configurable thresholds per supplier × commodity (single global tuple in v1; configurable in follow-up spec).
- Mobile / RTL adaptation — desktop LTR-with-Hebrew-content per portal default register.
- Customer-credit drawer redesign — chrome unification deferred to follow-up spec.
- Diagnostic move of `lionwheel_capped_window_gap` to a separate `integration_diagnostics` table (cleanup spec D5; v1 keeps in `exceptions` + Info hidden).
- Dedicated `/inbox/queues/*` triage UIs — v1 deep-links to existing `/admin/*` admin surfaces.
- Tier-3 anomaly state-scoped rollup — v1 uses event-scoped keys; if volume becomes a problem, follow-up adds a rolled-up subtype.
- Configurable retention beyond 90 days.
- `change_log` row for auto-resolve transitions.

---

## 7. Known limitations

- **`subtype` is text not enum**: deliberate. New subtypes can land without DDL. Producer is the source of truth.
- **`raw_payload->'key_facts'` JSONB shape is producer-specific**: each producer emits the JSONB its UI Body component reads. No global schema validation.
- **Effective-date semantics partial**: only the `gi_price_proposal` Edit→Approve flow uses `effective_at`. Planning engine still treats `supplier_items.std_cost_per_inv_uom` as point-in-time.
- **No "supersedes" link between Decision cards**: if a planner Defers a card and the producer later creates a new one for the same logical event, both cards exist. For `gi_price_proposal` this cannot happen because each `proposal_id` is a fresh row written from a single planner form submission, and the upstream `gi_expense_review` To-Do guarantees one proposal per (gi_expense_id, line_index_synthetic) via the unique index `uniq_price_proposals_expense_line`.
- **Audit reconstruction for system-driven actions**: `change_log` does not record `auto_resolved`. Audit relies on `exceptions.resolution_notes` + `resolved_by IS NULL`. Canonical SQL pattern (parens are load-bearing — OR binds wider than AND otherwise):
  ```sql
  WHERE resolved_by IS NULL
    AND (resolution_notes LIKE 'Auto-resolved by %'
         OR resolution_notes LIKE '%[Re-opened %')
  ```
- **Migration tier dependency**: M3 backfill assumes all categories from §3 have rows. New categories landing between spec write and migration time will trigger the §2.3 halt-guard, requiring spec amendment.
- **GI line description hashing**: `unmapped_gi_line` and `ambiguous_supplier_mapping` dedupe on `sha256(normalized_description)[:16]`. If a supplier later changes their description format, this is a new dedupe_key and a fresh card. Acceptable — the planner sees the change as a new mapping task.

---

## 8. Files to create / modify (preview for writing-plans)

**Schema migrations (in `gt-factory-os/db/migrations/`; numbers may shift if new migrations land between spec write and apply time):**
- `0146_exceptions_card_type_and_subtype.sql` (NEW — M1)
- `0147_price_proposals.sql` (NEW — M2)
- `0148_exceptions_typed_backfill.sql` (NEW — M3)
- `0149_change_log_inbox_actions.sql` (NEW — M4; with hard halt-guard preflight)
- `0150_exceptions_status_dismissed_and_dedupe_index.sql` (NEW — M5; two indexes for two access patterns)
- `0150b_fn_gi_price_proposal_activator.sql` (NEW — M5b; full SQL function body in §2.5b)
- `0151_gi_price_proposal_activator_cron.sql` (NEW — M6)

**Backend (`gt-factory-os/api/src/`):**
- `exceptions/handler.ts` — split handlers; role gate change; bulk-resolve deprecation
- `exceptions/schemas.ts` — extend with `card_type`, `subtype`, new actions, key_facts blob
- `exceptions/route.ts` — register new endpoints (`/approve`, `/reject`, `/dismiss`, `/edit-approve`)
- `inbox/gi_expense_review/handler.ts` — NEW (Stage-B manual-form submission per §1.14.2)
- `inbox/gi_expense_review/route.ts` — NEW
- `inbox/gi_expense_review/schemas.ts` — NEW
- `inbox/gi_price_proposal/handler.ts` — NEW (Approve/Edit→Approve/Reject transactions per §1.14.5)
- `inbox/gi_price_proposal/route.ts` — NEW
- `inbox/gi_price_proposal/schemas.ts` — NEW
- `integrations/green_invoice/expense-review-emitter.ts` — NEW (§1.14.1 Stage-A `emitGiExpenseReview` after each `gi_expense_mirror` insert)
- `exceptions/key-facts-derivers.ts` — NEW (per-subtype derivation for per-submission emitters; see §4.4)
- `integrations/lionwheel/poller.ts` — emit-with-reopen contract; card_type/subtype on emit
- `integrations/lionwheel/reconciliation.ts` — same (multiple call sites)
- `integration-sku-map/mutations.ts` — same
- `jobs/freshness_check.ts` — emit-with-reopen contract; card_type='warning'
- `jobs/gi_price_proposal_activator.ts` — NEW (§1.14.6)
- `boms/publish.ts` — emit-with-reopen contract; card_type='info'
- `physical-counts/handler.ts` — add card_type='decision'+subtype='count_large_variance' to INSERT
- `waste-adjustments/handler.ts` — same for positive_adjustment / loss_above_threshold

**Backend (`gt-factory-os/supabase/functions/`):**
- `factory_os_jobs/index.ts` — emit-with-reopen contract; add `emitGiPriceProposal` flow

**Portal (`window2-portal-sandbox/src/`):**
- `app/(inbox)/inbox/page.tsx` — rewrite (feed + filters + sort + badges + history view via query)
- `app/(inbox)/inbox/approvals/gi-price-proposal/[id]/page.tsx` — NEW
- `app/(inbox)/inbox/approvals/physical-count/[submission_id]/page.tsx` — chrome unify
- `app/(inbox)/inbox/approvals/waste/[submission_id]/page.tsx` — chrome unify
- `app/(inbox)/inbox/credit/[exception_id]/page.tsx` — chrome unify
- `components/inbox/InboxCard.tsx` (NEW)
- `components/inbox/bodies/PriceProposalBody.tsx` (NEW)
- `components/inbox/bodies/StockImpactBody.tsx` (NEW; reused for GR/count/waste)
- `components/inbox/bodies/QueueToDoBody.tsx` (NEW)
- `components/inbox/bodies/SingleTaskToDoBody.tsx` (NEW)
- `components/inbox/bodies/WarningBody.tsx` (NEW)
- `components/inbox/bodies/InfoBody.tsx` (NEW)
- `components/inbox/FilterSidePane.tsx` (NEW)
- `components/inbox/TopBadgeStrip.tsx` (NEW)
- `lib/inbox-copy.ts` (NEW — Hebrew register)
- `lib/inbox-status.ts` (NEW — macro-status compression)

**Tests (`gt-factory-os/api/test/`):**
- `exceptions/dedupe-by-type.test.ts` — NEW (proves type-aware dedupe + emit-with-reopen)
- `exceptions/role-gate.test.ts` — NEW (operator → 403; scoped read works)
- `exceptions/bulk-resolve-deprecation.test.ts` — NEW
- `integrations/gi-price-proposal-tiers.test.ts` — NEW (Tier 1/2/3 routing + confidence rubric + boundary cases)
- `integrations/gi-price-proposal-approve.test.ts` — NEW (mapping drift guard, change_log, price_history append)
- `exceptions/migration-backfill.test.ts` — NEW (halt-guard fires on unmapped category)
- `exceptions/regression-reopen.test.ts` — NEW (emit-with-reopen healthy→unhealthy→healthy→unhealthy)
- `inbox/gi-price-proposal-edit-approve.test.ts` — NEW (effective_at future-dated)

**Tests (E2E in `window2-portal-sandbox/e2e/`):**
- `inbox-decision-approve.spec.ts` — NEW
- `inbox-warning-acknowledge.spec.ts` — NEW
- `inbox-todo-deeplink.spec.ts` — NEW
- `inbox-history-view.spec.ts` — NEW
- `inbox-operator-403.spec.ts` — NEW

---

## 9. Execution gating

This spec is **not yet approved for implementation.** Required next steps in order:

1. spec-document-reviewer subagent runs over this revised file and approves.
2. Tom reviews the file and approves any changes.
3. writing-plans skill invoked to produce implementation plan in `docs/superpowers/plans/2026-05-04-inbox-typed-cards-and-price-proposals.md`.
4. Tom reviews the plan.
5. Implementation per the plan (subagent-driven-development if available; otherwise executing-plans).
6. Each task uses TDD per superpowers conventions.
7. Final verification per `superpowers:verification-before-completion`.
8. Migration tranche runs in §2.7 sequence with `rebuild_verifier()` guard at every transaction boundary.

End of design spec.
