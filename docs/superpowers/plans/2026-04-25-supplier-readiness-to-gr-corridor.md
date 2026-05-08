# Supplier Readiness → Purchase Recommendation → PO → Goods Receipt Corridor
# Closure Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the full corridor from supplier_items readiness through purchase recommendation approval, PO creation, and Goods Receipt to a first verified production-quality closure — no SQL, no DevTools, no Claude required for normal use.

**Architecture:** Four parallel lanes (W1 schema, W2 portal form, API bug fix, W4 verification) converge at Phase E (first PO test). Data entry by Tom gates Phase E. The GR leg is already structurally complete; the primary work is unblocking the supplier-readiness and recommendation-to-PO path.

**Evidence base:** Supplier Items Readiness Audit 2026-04-25 (155 supplier_items rows, live DB).

**Date authored:** 2026-04-25

---

## 1. CORRIDOR OBJECTIVE — What "Complete" Means

The corridor is complete when ALL of the following are true, with no SQL, DevTools, or Claude involvement required for any step:

| # | Condition | Verification |
|---|-----------|-------------|
| C1 | At least one component has `v_component_readiness.is_ready = true` | SQL validation query VQ-1 |
| C2 | A real planning run generates ≥ 1 purchase-type recommendation for that component | Portal: planning runs page shows purchase rec |
| C3 | A planner can approve the recommendation from the portal | Portal approval flow executes without error |
| C4 | Approved recommendation converts to a purchase_orders row (status=OPEN) | SQL VQ-3; portal PO list shows new PO |
| C5 | purchase_order_lines row exists with ordered_qty, uom, unit_price_net | SQL VQ-4 |
| C6 | GR form allows selecting the open PO | Portal GR form: PO picker shows the new PO |
| C7 | Full receipt: GR posts stock ledger entry + updates received_qty + updates line_status=CLOSED | SQL VQ-5, VQ-6 |
| C8 | Partial receipt: received_qty < ordered_qty → line_status=PARTIAL, open_qty > 0 | SQL VQ-7 |
| C9 | No posted form_submission exists without a corresponding PO row (handler bug closed) | SQL VQ-8 |
| C10 | Tom can fix any future supplier readiness gap entirely from the portal UI | Portal: all required fields editable; no admin API call needed |
| C11 | Remaining known gaps are explicitly listed and non-blocking | Gap registry updated |

**Out of scope for this corridor:**
- GR reversal decrementing received_qty (GAP-006, OPEN, separate gap)
- Supplier returns (not in v1)
- Automatic PO line pre-fill in GR form beyond PO selection (nice-to-have, Phase E verification item)

---

## 2. CURRENT BLOCKERS (Ranked)

### P0 — Blocks any purchase recommendation or PO creation today

| ID | Blocker | Root Cause | Fix Owner |
|----|---------|-----------|-----------|
| P0-1 | Zero purchase-type planning recommendations generated | v_component_readiness.is_ready = false for 162/163 components; planning engine skips them | W1 (view fix) + Tom (data confirm) |
| P0-2 | v_supplier_item_readiness treats pack_conversion=1 as "not confirmed" | Migration 0069: `case when si.pack_conversion = 1 then 'pack_conversion'` — no escape hatch | W1 migration 0084 |
| P0-3 | 27 supplier_items missing order_uom | Field not exposed in portal; admin never set it | W2 form + Tom data entry |
| P0-4 | 15 supplier_items with blank approval_status | approval_status not editable from portal form (requires POST /status endpoint, not PATCH) | W2 form + Tom data entry |
| P0-5 | Portal supplier-items edit form missing: order_uom, approval_status, std_cost_per_inv_uom controls | SupplierItemEditPage.tsx exposes only 5 soft fields | W2 form (hand-off to Admin Masters window) |
| P0-6 | po_bridge.ts transaction bug: catch block returns instead of throws | fn_convert failure commits form_submission as 'posted' with no PO created | API lane (po_bridge.ts fix) |

### P1 — Reduces planning quality but does not fully block

| ID | Blocker | Fix Owner |
|----|---------|-----------|
| P1-1 | 32 supplier_items missing std_cost_per_inv_uom | Falls back to 0 (unit_price_net=0 on PO line); PO is created but price is wrong | W2 form (add field) + Tom data entry |
| P1-2 | 40 supplier_items missing moq / lead_time_days | Planning policy fallback; suboptimal recommendations | Tom data entry (portal already editable) |
| P1-3 | GR form does not auto-pre-fill supplier/component/UOM from PO selection | GR stores po_id but portal UI must query and render PO context | W2 (UX improvement, not a blocker) |
| P1-4 | No "supplier readiness health" surface — Tom cannot see which supplier_items are blocking planning | Requires a readiness dashboard tile or inline flag on the edit page | W2 (add readiness indicator) |
| P1-5 | RAW-WATER has approval_status='INTERNAL' — unknown if intentional exclusion | Tom decision required | Tom |

### P2 — Polish, not on critical path

- Bulk edit / batch approval_status update
- Filter supplier_items by readiness status in browse page
- Pack_conversion helper text / educational UX
- Label/bottle pack size confirmation workflow

---

## 3. WINDOW OWNERSHIP PLAN

### Window 1 — DB / Schema / Migrations / Tests (W1)

**Owns:** All schema changes, view patches, migration files, pgTAP tests.

Deliverables:
- Migration `0084`: Patch `v_supplier_item_readiness` — change pack_conversion check from `= 1` to `IS NULL`
- Migration `0085` (if needed): Patch `v_component_readiness` — same change (lower priority; the existing `purchase_to_inv_factor ≠ 1` escape already covers most manufactured components)
- pgTAP test: A supplier_item with pack_conversion=1, approved, order_uom set → is_ready = true after migration
- pgTAP test: A supplier_item with pack_conversion=NULL → is_ready = false
- Validation queries VQ-1 through VQ-8 (defined in Section 6)

**Does NOT own:** Portal changes, API handler changes.

### Window 2 — Canonical Portal / Production UI (W2)

**Owns:** All portal form changes for supplier-items.

> ⚠️ COLLISION GUARD: A parallel window is actively working on Admin Masters / Supplier Items UI. Do NOT implement portal changes from this plan until the parallel window completes its current work or explicitly hands off these files. See Section 4 (Collision Rules) for exact coordination protocol.

Deliverables (described as requirements in Phase C — for handoff):
- Add `order_uom` to SupplierItemEditPage.tsx
- Add `approval_status` control to SupplierItemEditPage.tsx (calls POST /status endpoint, not PATCH)
- Add `std_cost_per_inv_uom` to SupplierItemDto and SupplierItemEditPage.tsx
- Add `inventory_uom` as read-only display context in the edit form
- Add plain-language Hebrew field labels (see Phase C)
- Add readiness indicator (is_ready flag visible inline)

**Does NOT own:** DB migrations, API handler logic, po_bridge.ts.

### API / Planning Bug Lane

**Owns:** po_bridge.ts transaction rollback fix + regression test.

Deliverables:
- Restructure `api/src/planning/po_bridge.ts`: move form_submissions INSERT to after fn_convert succeeds; catch block throws not returns
- New test file `api/src/planning/po_bridge.test.ts`: regression test (see Phase F)

**Does NOT own:** Portal changes, DB migrations.

### Window 4 / Planning-Flow Verification Lane (W4)

**Owns:** End-to-end verification of the corridor after W1 + W2 + API lane are complete.

Deliverables:
- Verify planning run generates purchase recommendations (Phase E step-by-step)
- Verify approval → convert → PO
- Verify GR can reference PO
- Document first-PO verification checklist results

**Does NOT own:** Any implementation.

---

## 4. COLLISION RULES

The parallel Admin Masters window owns the following files — this plan **must not touch them** until that window signals completion:

```
portal/src/master-maintenance/supplier-items/SupplierItemEditPage.tsx
portal/src/master-maintenance/supplier-items/SupplierItemsBrowsePage.tsx
portal/src/master-maintenance/supplier-items/SupplierItemDetailPage.tsx
portal/src/shared/api-client/mock/dtos.ts  (SupplierItemDto section)
```

**Protocol when collision risk exists:**
1. This plan produces requirements (Phase C) as a written handoff document, not code
2. The parallel window reads Phase C and implements the requirements when ready
3. If the parallel window has already implemented some fields, this plan's Phase C requirements should be validated against what was implemented — not re-implemented
4. If overlap is discovered mid-execution, STOP, report to Tom, resolve ownership before continuing

**Files this plan owns exclusively:**
```
db/migrations/0084_*.sql                      (W1)
db/migrations/0085_*.sql                      (W1, if needed)
db/tests/supplier_item_readiness_tests.sql    (W1)
api/src/planning/po_bridge.ts                 (API lane)
api/src/planning/po_bridge.test.ts            (API lane, new file)
```

**Shared files (coordinate before touching):**
```
portal/src/shared/api-client/mock/dtos.ts    — SupplierItemDto only; other DTOs in this file are not in scope
```

---

## 5. STAGED EXECUTION PLAN

---

### Phase A — Contract Reconciliation

**Purpose:** Lock the field-coverage matrix so W1, W2, and API lane work from a shared contract, not assumptions.

**Key findings (already confirmed by audit — no new queries needed):**

| Field | DB column | API PATCH accepts | SupplierItemDto field | Portal edit form |
|-------|-----------|-------------------|-----------------------|-----------------|
| order_uom | ✅ supplier_items.order_uom | ✅ (mutations.ts) | ✅ orderUom | ❌ Not exposed |
| inventory_uom | ✅ supplier_items.inventory_uom | ✅ (mutations.ts) | ✅ inventoryUom | ❌ Not exposed |
| pack_conversion | ✅ supplier_items.pack_conversion | ✅ | ✅ packConversion | ✅ Exposed |
| approval_status | ✅ supplier_items.approval_status | ✅ (POST /status) | ✅ approvalStatus | ❌ Not exposed |
| std_cost_per_inv_uom | ✅ supplier_items.std_cost_per_inv_uom | ✅ (mutations.ts) | ❌ **Missing from DTO** | ❌ Not exposed |
| moq | ✅ | ✅ | ✅ moq | ✅ Exposed |
| lead_time_days | ✅ | ✅ | ✅ leadTimeDays | ✅ Exposed |

**Contract gaps requiring action:**
1. `std_cost_per_inv_uom` — missing from SupplierItemDto AND portal form (two changes needed)
2. `order_uom` — in DTO and API, missing from portal form only (one change needed)
3. `approval_status` — in DTO and API (separate /status endpoint), missing from portal form only (one change needed, different endpoint)
4. `inventory_uom` — in DTO and API, should appear as read-only context in form (one display addition)

**Approval_status endpoint is separate:**
```
POST /api/v1/mutations/supplier-items/:supplier_item_id/status
Body: { "approval_status": "approved" | "pending" | "rejected" }
```
This is NOT part of the PATCH endpoint. The W2 form must call this endpoint separately when the user changes approval_status.

**Route files (read-only, no changes):**
```
api/src/supplier-items/mutations_route.ts   — defines both PATCH and POST /status routes
api/src/supplier-items/mutations.ts         — handleSupplierItemUpdate + handleSupplierItemStatus
```

**Phase A exit:** Contract matrix above is the accepted truth. No implementation.

---

### Phase B — Readiness Logic Fix Plan

**Purpose:** Decide the exact safe change to pack_conversion readiness logic and produce the migration spec.

#### B.1 — Decision: Safe treatment of pack_conversion = 1

**Current behavior:**
- `v_supplier_item_readiness` (migration 0069): flags `pack_conversion = 1` as "not confirmed" for ALL supplier_items
- `v_component_readiness` (migration 0069): flags `pack_conversion = 1 AND purchase_to_inv_factor = 1` — has escape hatch via purchase_to_inv_factor

**Recommended fix:**
Change `v_supplier_item_readiness` to check `pack_conversion IS NULL` instead of `= 1`.

Rationale:
- The IS NULL check distinguishes "never set" from "set to 1"
- All current rows have a value (missing_pack_conversion = 0 in the null-based audit)
- Tom will confirm all pack_conversion values in Phase D before Phase E runs
- This avoids adding a `pack_conversion_confirmed` column (unnecessary schema complexity for v1)
- CLAUDE.md principle: prefer simplest architecture that won't break

**Risk:** Rows where 1 was seeded as a default without intentional confirmation. Mitigation: Phase D explicitly requires Tom to confirm pack_conversion for ambiguous rows before Phase E.

**Leave unchanged:** `v_component_readiness` existing logic is acceptable as-is. The `purchase_to_inv_factor ≠ 1` escape covers manufactured components with multi-ingredient recipes. For the first PO test (RAW-VODKA), the view will correctly become ready after the supplier_item is confirmed.

#### B.2 — Pack_conversion Tom Decision Sheet (Ambiguous Rows Only)

These rows need Tom's explicit confirmation before Phase E. For each, Tom must answer: **כמה יחידות מלאי נכנסות לכל יחידת הזמנה אחת?**

**Category 1 — Obvious 1:1 (bulk weight/volume ingredients): Tom just confirms.**
All raw ingredients with KG/L order_uom are almost certainly 1:1.
- All RAW-* with order_uom = KG or L
- Confidence: very high. Tom confirms once, no further analysis needed.

**Category 2 — Likely 1:1 but Tom should confirm (packaging cartons/cases):**

| Component | Supplier | Order UOM | Current Pack | Question |
|-----------|----------|-----------|--------------|---------|
| PKG-CARTON-* (all) | מנייר קרטונים | UNIT | 1 | מזמינים קרטון בודד או אריזת מכר? |
| PKG-BOTTLE-300/500/750ML-*/1L | צבר מריזות | UNIT | 1 | מזמינים בקבוק בודד או ארגז? |
| PKG-CAP-* | צבר מריזות | UNIT | 1 | מזמינים פקק בודד או שקית? |

**Category 3 — Ambiguous: labels, bags, specialty items — Tom MUST decide:**

| Component | Supplier | Order UOM | Current Pack | Concern |
|-----------|----------|-----------|--------------|---------|
| PKG-LABEL-* (all ~55 rows) | מיקי מדבקות | UNIT | 1 | מדבקות מגיעות בגלילים. כמה מדבקות לגליל? אם מזמינים גליל = 500 יחידות, pack=500 |
| PKG-BAG-MAT-100G/18G/500G | פרופק | UNIT | 1 | האם מזמינים שקית בודדת או קרטון? |
| PKG-TIN-MAT-30G | מנייתה מופק | UNIT | 1 | מזמינים פח בודד או ארגז? |

**Tom's answer format needed:** For each row above: "1 יחידת הזמנה = X יחידות מלאי." Where X ≠ 1, the pack_conversion field must be updated to X.

**If Tom cannot answer before Phase E:** Use RAW-VODKA for first PO test (bulk liquid, pack=1 is unambiguous). All ambiguous packaging can be resolved in a separate follow-up sprint.

#### B.3 — Migration Spec for W1

```
Migration: 0084_fix_v_supplier_item_readiness_pack_null_check.sql

Change:
  In v_supplier_item_readiness, in the missing_fields array construction:
  OLD: case when si.pack_conversion = 1 then 'pack_conversion' else null end
  NEW: case when si.pack_conversion IS NULL then 'pack_conversion' else null end

Also update the is_ready computation to be consistent.

Guard: CREATE OR REPLACE VIEW — idempotent, no data risk.

pgTAP tests required:
  1. supplier_item with pack_conversion=1, approved, order_uom set → is_ready = true
  2. supplier_item with pack_conversion=NULL → is_ready = false
  3. supplier_item with pack_conversion=1, approval_status='pending' → is_ready = false
  4. supplier_item with pack_conversion=1, order_uom=NULL → is_ready = false (order_uom missing)
```

**Migration 0085 (v_component_readiness): DEFERRED — existing logic is acceptable for first PO test. Create only if v_component_readiness.is_ready remains false after 0084 and Tom's data entry.**

**Phase B exit:** Migration spec and Tom decision sheet approved. No implementation until approved.

---

### Phase C — Portal Editability Closure (Handoff to Admin Masters Window)

**Purpose:** Produce exact, unambiguous requirements for the W2 form changes. The parallel window implements these; this plan does not.

#### C.1 — Required Form Fields

The following fields must be added to `portal/src/master-maintenance/supplier-items/SupplierItemEditPage.tsx`:

**Field 1: order_uom**
- Type: text input (or select with common UOM values: KG, L, UNIT, BAG)
- Label (Hebrew): **יחידת הזמנה** — יחידה שבה מזמינים מהספק (לא יחידת המלאי)
- Required: YES — show validation error if empty
- API: included in standard PATCH body `{ "order_uom": "..." }`
- Placement: immediately below or next to pack_conversion field (they are conceptually linked)
- Mobile: full-width row

**Field 2: approval_status**
- Type: select (options: pending / approved / rejected)
- Label (Hebrew): **סטטוס אישור** — האם פריט הספק מאושר לתכנון?
- Required: NO — can leave as-is (default is 'pending')
- API: NOT part of PATCH — calls `POST /api/v1/mutations/supplier-items/:id/status` with `{ "approval_status": "..." }`
- On change: optimistic update; show success toast "סטטוס עודכן"; show error if API fails
- Placement: top of form — it's a status field, visually prominent
- Styling: badge-style with color (green=approved, yellow=pending, red=rejected)

**Field 3: std_cost_per_inv_uom**
- Type: numeric input (decimal, 4dp)
- Label (Hebrew): **מחיר תקן ליחידת מלאי** — עלות ₪ ליחידת מלאי אחת (לפי יחידת מלאי, לא הזמנה)
- Required: NO — empty = 0 (acceptable for v1 planning with zero-price fallback)
- API: included in standard PATCH body `{ "std_cost_per_inv_uom": "..." }`
- Placement: in the pricing section, after pack_conversion
- Prefix: ₪ symbol
- DTO change needed: Add `stdCostPerInvUom: string | null` to `SupplierItemDto` in `portal/src/shared/api-client/mock/dtos.ts`

**Field 4: inventory_uom (read-only display)**
- Type: read-only text (not editable)
- Label (Hebrew): **יחידת מלאי** — יחידה שבה נמדד המלאי (לעיון בלבד)
- Purpose: context for Tom when setting pack_conversion — he sees "UNIT → KG × pack_conversion"
- Placement: next to pack_conversion field

**Field 5: pack_conversion — add helper text**
- Existing field, add explanatory text below it:
- Helper (Hebrew): **כמות יחידות מלאי שמגיעות עם כל יחידת הזמנה אחת. לדוגמה: אם מזמינים שק ומקבלים 20 ק"ג, הזן 20.**

#### C.2 — Readiness Indicator

Add a visual readiness badge to the supplier_item detail/edit page:
- Shows `is_ready: true/false` from the API response (if the backend returns it)
- If not returned by current API: add a read call to `v_supplier_item_readiness` per supplier_item_id, or display inline which specific fields are missing
- Label: **מוכן לתכנון** (green badge) / **חסר נתונים** (red badge with list of missing fields)

#### C.3 — Existing Fields — Keep As-Is

pack_conversion, lead_time_days, moq, payment_terms, notes are already in the form. No changes to these fields.

#### C.4 — Form Success Behavior

After a successful save:
- Show Hebrew success toast: **"נתוני פריט הספק עודכנו בהצלחה"**
- Refresh the detail view to show updated values
- If readiness status changed to is_ready=true, show: **"הפריט מוכן לתכנון ✓"**

**Phase C exit:** Requirements document handed off to Admin Masters window. That window confirms receipt and target delivery sprint.

---

### Phase D — Data Entry Plan

**Purpose:** Identify exactly what Tom must enter, in what order, and from which UI surface.

Tom must NOT enter data until:
- W1 migration 0084 is applied (readiness view fix)
- W2 form changes are live (order_uom and approval_status fields visible)

#### D.1 — Tom Can Fill From Portal (After W2 form is live)

**Priority 1: order_uom on 27 Bucket B rows**
These are immediately blocking fn_convert. Tom must set the correct order_uom for each:

| Component | Supplier | Likely order_uom | Confidence |
|-----------|----------|-----------------|------------|
| RAW-ALCOHOL-96 | טמפו משקאות | L | High |
| RAW-TRIPLE-SEC | טמפו משקאות | L | High |
| RAW-VERMOUTH-RED | טמפו משקאות | L | High |
| RAW-VIOLET-LIQUEUR | טמפו משקאות | L | High |
| RAW-TEQUILA | די מנה | L | High |
| RAW-ALMOND-SYRUP | דומינה | L or KG | Tom confirm |
| RAW-CUCUMBER-SYRUP | דומינה | L or KG | Tom confirm |
| RAW-MELON-EXTRACT | דומינה | L or KG | Tom confirm |
| PKG-JERRICAN-3.85L | גבני פלסטיק | UNIT | High (1 jerrican = 1 unit) |
| PKG-BOTTLE-200ML | מוזה קוקטיילים | UNIT | High |
| PKG-CAP-200ML | מוזה קוקטיילים | UNIT | High |
| PKG-CARTON-200ML | מוזה קוקטיילים | UNIT | High |
| PKG-LABEL-MUZ-*-200ML (5 rows) | מוזה קוקטיילים | UNIT | Confirm roll qty |
| PKG-LABEL-MAR-*-300ML (3 rows) | מיקי מדבקות | UNIT | Confirm roll qty |
| PKG-LABEL-MUZ-*-1L (5 rows) | מיקי מדבקות | UNIT | Confirm roll qty |
| PKG-LABEL-SAN-*-3850ML (2 rows) | מיקי מדבקות | UNIT | Confirm roll qty |

**Priority 2: approval_status='approved' on 15 blank-status rows**
Same 15 rows as Bucket B above that have blank approval_status. Tom sets to 'approved' for each that is a valid active supplier.

**Priority 3: std_cost_per_inv_uom on 8 cost-only-gap rows (can do anytime)**
- PKG-BAG-MAT-100G, PKG-BAG-MAT-18G, PKG-BAG-MAT-500G (פרופק)
- PKG-CARTON-300ML, PKG-CARTON-ARK-10, PKG-CARTON-MAT-22, PKG-CARTON-MAT-24, PKG-LID-MAT-30G (מנייר קרטונים / מנייתה מופק)
- RAW-CONSERVANT, RAW-OUZO-PURE (זיו כימיקלים / די מנה)

**Priority 4: moq + lead_time on 5 soft-gap rows (non-blocking)**
RAW-BERGAMOT-PURE, RAW-LIME-PURE, RAW-CLOVE, RAW-CHILI-SYRUP, RAW-PEAR-ODK-SYRUP

**RAW-WATER decision (Tom):**
approval_status = 'INTERNAL' — Tom must decide: leave as INTERNAL (permanent exclusion from planning) or change to 'approved'. If water is a planning ingredient, it must be 'approved'. If it is treated as "always in stock / not ordered from a supplier," keep INTERNAL and the planning engine correctly excludes it.

#### D.2 — Cannot Infer / Must Ask Tom

- Pack_conversion for all PKG-LABEL-* rows: roll size unknown (see Phase B.2 Tom decision sheet)
- Pack_conversion for PKG-BOTTLE-*/PKG-CAP-* rows: case/bag size unknown
- RAW-ALMOND-SYRUP, RAW-CUCUMBER-SYRUP, RAW-MELON-EXTRACT order_uom: L vs KG uncertain

#### D.3 — Can Be Loaded by Migration Only After Approval

None identified. All data entry can be done through the portal after W2 form is live.

**Phase D exit:** Tom has confirmed pack_conversion for RAW-VODKA, entered order_uom for at least one active-BOM component, and set approval_status='approved' for that component's supplier_item.

---

### Phase E — First Verified PO Test Path

**Candidate component: RAW-VODKA**

Justification:
- approval_status: approved ✓
- order_uom: L ✓ (already set)
- pack_conversion: 1 (L→L, 1:1 — unambiguous) ✓
- std_cost_per_inv_uom: complete ✓
- lead_time_days: complete ✓
- In active BOMs (cocktail products) ✓
- Supplier (Digum / משקאות): known active supplier

**Prerequisites before this phase begins:**
- [ ] W1 migration 0084 applied and pgTAP tests green
- [ ] W2 form changes live (order_uom, approval_status fields visible)
- [ ] API lane: po_bridge.ts transaction bug fixed
- [ ] Tom has confirmed RAW-VODKA pack_conversion=1 is correct
- [ ] RAW-VODKA supplier_item: approval_status='approved', order_uom='L'

**Test steps (W4 verification — no code changes):**

- [ ] **E1: Verify RAW-VODKA is_ready**
  Run VQ-1. Confirm v_supplier_item_readiness shows is_ready=true for RAW-VODKA supplier_item.

- [ ] **E2: Verify v_component_readiness**
  Run VQ-2. Confirm v_component_readiness shows is_ready=true for RAW-VODKA.

- [ ] **E3: Trigger a planning run**
  Via portal → Planning → Run planning. Confirm run completes without error.

- [ ] **E4: Verify purchase recommendation generated**
  Run VQ-2b. Confirm at least one planning_run_recommendation row exists with recommendation_type='purchase', component_id referencing a vodka component, recommendation_status='pending'.

- [ ] **E5: Approve recommendation via portal**
  Navigate to Planning → Recommendations. Find the RAW-VODKA purchase recommendation. Click Approve. Confirm status changes to 'approved'.

- [ ] **E6: Convert to PO via portal**
  Click "Create Purchase Order" (or equivalent). Confirm the convert-to-PO call succeeds.

- [ ] **E7: Verify PO row**
  Run VQ-3. Confirm purchase_orders row exists: status=OPEN, supplier_id correct, source_recommendation_id set.

- [ ] **E8: Verify PO line**
  Run VQ-4. Confirm purchase_order_lines row: ordered_qty > 0, uom='L', unit_price_net = std_cost × pack_conversion, open_qty = ordered_qty.

- [ ] **E9: Verify portal PO visibility**
  Navigate to POs list. Confirm the new PO appears with status OPEN.

- [ ] **E10: Open GR form, attach to PO**
  Navigate to Goods Receipt. Confirm RAW-VODKA PO appears in PO picker.

- [ ] **E11: Post partial receipt (do NOT execute against real stock without Tom approval)**
  ⚠️ STOP CONDITION: This step posts a real stock ledger entry. Confirm with Tom before executing.
  If Tom approves: enter received_qty < ordered_qty. Post GR. Run VQ-5, VQ-6.
  Confirm: received_qty updated, line_status=PARTIAL, open_qty > 0, stock ledger entry created.

- [ ] **E12: Post full receipt (Tom approval required)**
  If Tom approves: enter received_qty = remaining open_qty. Post GR. Run VQ-7.
  Confirm: line_status=CLOSED, open_qty=0.

- [ ] **E13: Verify handler bug closed**
  Run VQ-8. Confirm zero orphaned form_submissions (posted without corresponding PO).

**Phase E exit:** All E1–E9 pass without SQL. E10 confirmed (PO visible in GR form). E11–E12 pending Tom approval. E13 passes.

---

### Phase F — Handler Bug Fix (po_bridge.ts)

**File:** `api/src/planning/po_bridge.ts`
**New file:** `api/src/planning/po_bridge.test.ts`

#### F.1 — Current Bug Summary

Inside `db.transaction().execute(async (trx) => {...})` (lines 259–367):
1. A `form_submissions` row is inserted as `status='posted'` at the START of the transaction
2. `fn_convert_recommendation_to_po(...)` is called inside a try/catch
3. If the DB function raises (P0001 or P0002), the catch block RETURNS a 4xx object instead of THROWING
4. Kysely's transaction callback resolves (return) → transaction COMMITS
5. Result: `form_submissions` row committed as 'posted', no PO created

**Evidence:** 32 orphaned posted form_submissions in production referencing recommendation UUIDs that no longer exist.

#### F.2 — Fix Specification

**Change 1: Move form_submissions INSERT to after fn_convert succeeds**

The INSERT into form_submissions must happen AFTER the DB function call, not before. Move it to immediately after the `fnRes` success path, within the same transaction.

```
BEFORE (current):
  trx BEGIN
    INSERT form_submissions (status='posted')   ← committed even on failure
    try {
      fn_convert_recommendation_to_po(...)
      return ok
    } catch {
      return 409   ← transaction commits!
    }
  trx COMMIT

AFTER (fixed):
  outer try {
    trx BEGIN
      fn_convert_recommendation_to_po(...)       ← if this raises, transaction rolls back
      INSERT form_submissions (status='posted')   ← only committed on success
      return ok
    trx COMMIT
  } catch (err) {
    // translate pg error codes to 4xx HERE, outside transaction
    return 409 / 404 based on err.code + err.message
  }
```

**Change 2: Pre-check block stays unchanged**
Lines 228–257 (type/status/already-converted checks) are correct — they run OUTSIDE the transaction. Keep them.

**Change 3: loadPOSummary call**
Move the loadPOSummary call to AFTER the transaction commits (or use the main db handle, not trx). Currently called inside the transaction via trx — this is fine if kept there.

#### F.3 — Regression Test Specification

File: `api/src/planning/po_bridge.test.ts`

**Test 1: Failed conversion (non-purchase recommendation) — no posted submission**
```
Setup:
  - Insert a planning_run_recommendation with recommendation_type='production', recommendation_status='approved', supplier_id set
  - Insert the matching supplier_item with order_uom, approval_status='approved'
  - Create a mock session (role=planner)
  
Action:
  - Call handleConvertRecommendationToPO with the production recommendation's ID

Assert:
  - Returns { kind: 'conflict', status: 409, body: { reason_code: 'RECOMMENDATION_NOT_PURCHASE' } }
  - SELECT count(*) FROM private_core.form_submissions WHERE idempotency_key = <key> → 0
  - SELECT count(*) FROM private_core.purchase_orders WHERE source_recommendation_id = <rec_id> → 0
```

**Test 2: Successful conversion creates posted submission**
```
Setup: approved purchase recommendation + valid supplier_item

Action: call handleConvertRecommendationToPO

Assert:
  - Returns status 200 with po_id
  - form_submissions count = 1, status = 'posted'
  - purchase_orders count = 1
```

**Test 3: Idempotent replay**
```
Action: call handler twice with same idempotency_key

Assert:
  - Second call returns { idempotent_replay: true }
  - form_submissions count = 1 (not 2)
  - purchase_orders count = 1 (not 2)
```

**Phase F exit:** po_bridge.ts restructured. All three regression tests green. Deployed to Railway.

---

### Phase G — Production Closure Gate

**Definition of DONE for this corridor:**

All of the following must be true before declaring the corridor closed:

| Gate | Verification | Owner |
|------|-------------|-------|
| G1 | VQ-1: ≥ 1 supplier_item is_ready=true | W4 |
| G2 | VQ-2: ≥ 1 component is_ready=true | W4 |
| G3 | Planning run generates ≥ 1 purchase recommendation | W4 Phase E |
| G4 | Approval → convert → PO succeeds from portal, no SQL | W4 Phase E |
| G5 | purchase_orders + purchase_order_lines rows verified (VQ-3, VQ-4) | W4 |
| G6 | GR can reference the new PO from portal (VQ-5) | W4 Phase E |
| G7 | po_bridge regression tests green (VQ-8) | API lane |
| G8 | Tom can edit order_uom, approval_status, std_cost from portal | W2 confirmed |
| G9 | Remaining gaps explicitly listed and non-blocking | Gap registry update |

**Post-closure gap registry updates required:**
- Close GAP (new): "purchase recommendations blocked by readiness view" — closed by migration 0084
- Update GAP-006 (GR reversal): remains OPEN, mark as out-of-scope for this corridor
- Document remaining Bucket B rows (still missing order_uom) as P1 for Tom's next data-entry sprint

---

## 6. REQUIRED ARTIFACTS

### Dependency Graph

```
Phase A (Contract reconciliation) — no dependencies
     │
     ├──▶ Phase B (Readiness view fix) → W1 migration 0084
     │         │
     │         ▼ (after 0084 applied + Tom confirms pack=1 for RAW-VODKA)
     │
     ├──▶ Phase C (Portal form requirements) → W2 handoff
     │         │
     │         ▼ (after W2 form live + Tom data entry)
     │
     ├──▶ Phase F (po_bridge.ts bug fix) → API lane (parallel to B+C)
     │
     └──▶ Phase D (Data entry plan) — Tom action (after B + C both complete)
                   │
                   ▼
             Phase E (First PO test — W4 verification)
                   │
                   ▼
             Phase G (Closure gate)
```

Phases B, C, and F are fully parallel.
Phase D starts only after B (view fix deployed) + C (portal form live).
Phase E starts only after D (data entered) + F (bug fixed).

### Window Ownership Summary

| Phase | Owner | Dependencies |
|-------|-------|-------------|
| A | Plan (read-only) | None |
| B | W1 | A |
| C | W2 (after parallel window clears) | A |
| D | Tom (data entry) | B + C |
| E | W4 (verification) | D + F |
| F | API lane | A |
| G | W4 + Tom | E + F |

### Exact Files / Routes Involved

**W1 (creates new files):**
```
db/migrations/0084_fix_v_supplier_item_readiness_pack_null_check.sql
db/migrations/0085_fix_v_component_readiness_pack_null_check.sql    (if needed)
db/tests/supplier_item_readiness_tests.sql                           (new pgTAP file)
```

**W2 (modifies — coordinate with parallel window):**
```
portal/src/master-maintenance/supplier-items/SupplierItemEditPage.tsx
portal/src/shared/api-client/mock/dtos.ts                            (SupplierItemDto only)
```

**API lane (modifies):**
```
api/src/planning/po_bridge.ts
api/src/planning/po_bridge.test.ts                                   (new file)
```

**Read-only reference (do not modify):**
```
api/src/supplier-items/mutations.ts                                  (PATCH + POST /status handlers)
api/src/supplier-items/mutations_route.ts                            (route definitions)
db/migrations/0069_v_component_bom_supplier_item_readiness.sql       (view being replaced)
db/migrations/0050_purchase_order_lines.sql                          (received_qty definition)
```

### Exact DB Objects Involved

| Object | Schema | Type | Action |
|--------|--------|------|--------|
| v_supplier_item_readiness | private_core | VIEW | Patched by migration 0084 |
| v_component_readiness | private_core | VIEW | Patched by migration 0085 (if needed) |
| supplier_items | private_core | TABLE | Data updated by Tom via portal |
| fn_convert_recommendation_to_po | private_core | FUNCTION | No changes (0083 patch already applied) |
| purchase_orders | private_core | TABLE | Receives new rows from conversion |
| purchase_order_lines | private_core | TABLE | Receives new rows; received_qty updated by GR trigger |
| form_submissions | private_core | TABLE | Behavior corrected by po_bridge.ts fix |
| stock_ledger | private_core | TABLE | Written by GR trigger (Phase E, requires Tom approval) |
| planning_run_recommendations | private_core | TABLE | Purchase recs generated here |

### Validation Queries

```sql
-- VQ-1: Supplier item readiness for RAW-VODKA
SELECT si.supplier_item_id, v.is_ready, v.missing_fields
FROM private_core.v_supplier_item_readiness v
JOIN private_core.supplier_items si ON si.supplier_item_id = v.supplier_item_id
WHERE si.component_id = 'RAW-VODKA';
-- Expected after fix: is_ready=true, missing_fields=[]

-- VQ-2: Component readiness
SELECT component_id, is_ready, missing_fields
FROM private_core.v_component_readiness
WHERE component_id = 'RAW-VODKA';
-- Expected: is_ready=true

-- VQ-2b: Purchase recommendations from latest planning run
SELECT recommendation_type, recommendation_status, component_id, recommended_qty
FROM private_core.planning_run_recommendations
WHERE run_id = (SELECT run_id FROM private_core.planning_runs ORDER BY created_at DESC LIMIT 1)
  AND recommendation_type = 'purchase';
-- Expected: ≥1 row with recommendation_type='purchase'

-- VQ-3: PO row after conversion
SELECT po_id, status, supplier_id, source_recommendation_id, order_date
FROM private_core.purchase_orders
WHERE source_recommendation_id = '<approved_rec_id>'::uuid;
-- Expected: 1 row, status='OPEN'

-- VQ-4: PO line
SELECT po_line_id, component_id, ordered_qty, uom, unit_price_net, open_qty, line_status
FROM private_core.purchase_order_lines
WHERE po_id = '<po_id>';
-- Expected: 1 row, ordered_qty > 0, open_qty = ordered_qty, line_status='OPEN'

-- VQ-5: GR references PO (after partial receipt)
SELECT gr.goods_receipt_id, grl.po_line_id, grl.received_qty, grl.component_id
FROM private_core.goods_receipts gr
JOIN private_core.goods_receipt_lines grl ON grl.goods_receipt_id = gr.goods_receipt_id
WHERE gr.po_id = '<po_id>';
-- Expected: 1+ rows with received_qty > 0

-- VQ-6: PO line state after partial receipt
SELECT received_qty, open_qty, line_status
FROM private_core.purchase_order_lines
WHERE po_id = '<po_id>';
-- Expected: received_qty > 0, received_qty < ordered_qty, line_status='PARTIAL', open_qty > 0

-- VQ-7: PO line state after full receipt
SELECT received_qty, open_qty, line_status
FROM private_core.purchase_order_lines
WHERE po_id = '<po_id>';
-- Expected: open_qty = 0, line_status='CLOSED'

-- VQ-8: Handler bug — no orphaned posted submissions
SELECT fs.submission_id, fs.status, fs.idempotency_key, po.po_id
FROM private_core.form_submissions fs
LEFT JOIN private_core.purchase_orders po
  ON po.source_recommendation_id = (fs.raw_payload->>'recommendation_id')::uuid
WHERE fs.form_type = 'planning_rec_convert_to_po'
  AND fs.status = 'posted'
  AND po.po_id IS NULL;
-- Expected after bug fix: 0 rows
-- Current expected: 32 rows (known orphans from testing; these are historical, not new)
```

### First-PO Verification Checklist

```
[ ] VQ-1 passes for RAW-VODKA supplier_item
[ ] VQ-2 passes for RAW-VODKA component
[ ] Planning run completed from portal (no SQL)
[ ] VQ-2b shows ≥ 1 purchase recommendation
[ ] Recommendation approved in portal (no SQL)
[ ] Convert-to-PO clicked in portal — 200 returned
[ ] VQ-3 passes — purchase_orders row exists, status=OPEN
[ ] VQ-4 passes — purchase_order_lines row exists with correct data
[ ] PO visible in portal POs list
[ ] GR form shows the new PO in PO picker
[ ] VQ-8 passes — 0 new orphaned posted submissions
[ ] ⚠️ E11 (partial receipt ledger write) — pending Tom approval
[ ] ⚠️ E12 (full receipt) — pending Tom approval
```

### Handoff to Admin Masters Window

The following are requirements for the Admin Masters window to implement. This plan does not implement these.

**File to modify:** `portal/src/master-maintenance/supplier-items/SupplierItemEditPage.tsx`

Required additions:
1. `order_uom` text/select input — label: "יחידת הזמנה" — maps to PATCH `order_uom`
2. `approval_status` select (pending/approved/rejected) — label: "סטטוס אישור" — calls POST `/status` endpoint separately from PATCH
3. `std_cost_per_inv_uom` numeric input — label: "מחיר תקן ליחידת מלאי" — maps to PATCH `std_cost_per_inv_uom`
4. `inventory_uom` read-only display — label: "יחידת מלאי" — display only, not editable
5. pack_conversion helper text (Hebrew explanation, see Phase C)

**File to modify:** `portal/src/shared/api-client/mock/dtos.ts`

Required addition: Add `stdCostPerInvUom: string | null` to `SupplierItemDto` interface.

**Note:** `orderUom`, `inventoryUom`, and `approvalStatus` are ALREADY in `SupplierItemDto`. They only need to be wired to form controls, not added to the DTO. Only `stdCostPerInvUom` needs a DTO addition.

**Sequencing:** The Admin Masters window should complete this work before Phase D begins (Tom's data entry sprint). Target: before next planning cycle.

---

## 7. DO NOT TOUCH LIST

The following must NOT be modified during this corridor's execution:

```
# Live production data
private_core.supplier_items                   (Tom edits via portal only, not script)
private_core.stock_ledger                     (GR test posts require Tom approval)
private_core.planning_run_recommendations     (no fake recommendations)
private_core.purchase_orders                  (no fake POs)

# Parallel window ownership (defer until they clear)
portal/src/master-maintenance/supplier-items/SupplierItemEditPage.tsx
portal/src/master-maintenance/supplier-items/SupplierItemsBrowsePage.tsx
portal/src/master-maintenance/supplier-items/SupplierItemDetailPage.tsx

# GR reversal logic (separate gap, GAP-006)
# Any trigger that updates received_qty from reversals

# Migration 0083 (fn_convert patch — already correct)
db/migrations/0083_fn_convert_rec_to_po_std_cost_price.sql

# Migration 0069 (being replaced, not modified)
db/migrations/0069_v_component_bom_supplier_item_readiness.sql

# PO status lifecycle logic (not in scope)
# Supplier returns (not in v1)
```

---

## 8. STOP CONDITIONS

Stop and report to Tom before continuing if any of the following is true:

| # | Stop Condition | Why |
|---|---------------|-----|
| S1 | Parallel window has modified SupplierItemEditPage.tsx in a way that conflicts with Phase C requirements | Resolve ownership before proceeding |
| S2 | After migration 0084 is applied, v_component_readiness still shows is_ready=false for RAW-VODKA | The v_component_readiness view may also need patching (migration 0085); requires W1 decision |
| S3 | pack_conversion=1 for any packaging item (bottles, caps, labels) is confirmed to be WRONG by Tom | pack_conversion values must be corrected before Phase E; first PO test must shift to an unambiguous component |
| S4 | Phase E Step E11/E12 (GR posting) — do not execute without explicit Tom approval | These write real stock ledger entries |
| S5 | Planning run in Phase E generates unexpected side effects (e.g., production recommendations triggering something) | Verify planning run is read-safe before executing |
| S6 | po_bridge.ts restructure in Phase F causes any existing posted form_submission to be re-evaluated | Historical orphaned rows should not be modified by the fix |
| S7 | SupplierItemDto already has `stdCostPerInvUom` in a version pushed by the parallel window | Check before adding to avoid duplicate DTO field |

---

*Plan authored: 2026-04-25. Evidence base: Supplier Items Readiness Audit 2026-04-25. No implementation performed.*
