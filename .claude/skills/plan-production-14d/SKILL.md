---
name: plan-production-14d
description: >-
  Tom's Thursday production-planning ritual for GT Factory OS. Trigger every Thursday or when Tom says
  "בוא נתכנן ייצור", "תכנון שבועיים", "plan production", "/plan-production-14d", "ריטרו ייצור", or asks
  to review last week's production vs plan and lock the next two weeks. One batched flow: retrospective →
  tune incoming (firmed) week → plan week+2 → write drafts to production_plan → Tom fine-tunes in portal →
  firm → purchase-session drafts → quantity interview → chat approval moves POs to Doreen's placement
  queue. Reuses live engines only; hands the buying interview to the procurement-planning skill.
---

# plan-production-14d — Thursday 14-day production cockpit

Role: GT head of production planning. Engine = hypothesis; Tom = final word. Converse Hebrew; SQL/internal English. Live DB: Supabase MCP, project `rvadsozabmxkkrktwgnv`, schema `private_core`, site `GT-MAIN`.

Created per Tom written request 2026-07-03 (satisfies STEP4-SKILLS-DECISION threshold: Tom approval in writing).

## Locked flow — 7 stages, in order

```
0 gate → 1 retro → 2 tune W1 → 3 plan W2 (drafts) → 4 ⏸ Tom tweaks → 5 firm + session → 6 procurement relay
```

! Never skip 0. ⊥ re-run generate-drafts after stage 4 begins (wipes `TEAEDD:%` drafts incl. Tom's edits on them).

### Stage 0 — integrity gate (once, read-only; shared with procurement side)

Run + present 4-row scorecard (🟢/🟡/🔴):

```sql
select private_core.rebuild_verifier();                          -- ! = 0, else HALT
select version_id, horizon_start_at, horizon_weeks, status, published_at
from private_core.forecast_versions where status='published'
order by published_at desc nulls last limit 1;                   -- ! covers [today, today+14); age >14d → 🟡 ask
select pol.po_id, pol.component_id, pol.open_qty
from private_core.purchase_order_lines pol
where pol.line_status='OPEN' and pol.open_qty>0
  and pol.expected_receive_date is null;                         -- each row = double-order trap; surface
select warnings from private_core.purchase_session
order by created_at desc limit 1;                                -- stale warnings possible: re-verify PO status before repeating them
```

Actor: resolve from `app_users` (role admin/planner, active). ⊥ hardcode UUIDs.
🔴 on gate → report, ask proceed/fix-first. ⊥ paper over.

### Stage 1 — retrospective (last week, read-only). 4 metrics, one table, one conclusion line per miss

| metric | source |
|---|---|
| plan vs actual per batch | `production_plan` rows last week: `planned_qty`, `status`, `completed_submission_id`; actual via `stock_ledger` `PRODUCTION_OUTPUT` |
| stockouts that happened | FG `qty_delta` events driving `current_balances`<0 during week; list item+date |
| tank utilization | actual output liters per batch (units × `items.base_fill_qty_per_unit`) vs `batch_size_l` 500 |
| forecast accuracy | `fn_forecast_daily_demand(week_start, week_end)` vs actual `FG_OUT_PICK` per top FG |

Conclusion format: "<base> אזל ב-<date> כי <cause>; בתכנון הבא: <fix>". ⊥ invented KPI/score.

### Stage 2 — tune incoming week (already `planned`)

Recompute per-base days-of-cover: on-hand liters (Σ `calculated_on_hand` × `base_fill_qty_per_unit`) + scheduled receipts vs `fn_tea_base_daily_demand_l(today, today+13)`. Flag: batch too late vs projected stockout day | base with no batch & <5d cover | batch no longer needed.
Propose exact moves/adds/cancels → **explicit Tom approval → apply** (update `production_plan` planned rows / insert; single-scope, reversible). ⊥ apply unapproved.

### Stage 3 — plan week+2 (drafts)

Confirm once → `POST /api/planning/generate-drafts` semantics = `fn_plan_tea_production(actor)` (56d EDD, 500L tank, 1/day Sun–Thu, IL holidays) + `fn_plan_matcha_repack(actor)`. Deletes only its own prior `TEAEDD:%` drafts; `planned`/`in_production` respected as supply.
Present W2 board: day × base × 500L + pack split. Saturation NOTICE (>5 tanks/wk needed) → surface starved bases, ask (raise `planning.production.max_batches_per_day` for that week / add workday / accept) — ⊥ change policy silently.
Sanity vs capacity: Σ tanks needed ≤ 10 per 2 weeks.

### Stage 4 — ⏸ Tom's portal pass

Tom fine-tunes drafts at `/planning/production-plan`. Wait for "סיימתי". ⊥ generate-drafts from here on.

### Stage 5 — firm + purchase session

On "סיימתי": `fn_firm_production_week(actor, week_start_W2)` (promotes drafts in [week_start, +6] → `planned`). Verify count promoted.
Then `fn_generate_purchase_session(actor, next_sunday, 'weekly')` — reads ONLY firmed plan + BF demand; read back `purchase_session.warnings` immediately.

### Stage 6 — procurement relay

Invoke **procurement-planning** skill, entering at its Stage 5 (quantity interview). Pass: session_id, stage-0 scorecard, firmed weeks summary. Its stages 0/1/4 = already satisfied; 2–3 (ABC/buffers) monthly or when flagged, not weekly.
Interview per supplier/line (qty sanity, MOQ, consolidation, cash) → Tom approves per-PO **in chat** → approve+place session PO → `fn_create_manual_po(...)` → **`APPROVED_TO_ORDER`** → Doreen's `/purchase-orders/placement-queue`. She confirms price/terms/date with supplier → `fn_place_purchase_order` (captures `expected_receive_date` — closes no-ETA trap at source).
⊥ supplier messages from this skill. ⊥ `fn_place_purchase_order` from this skill — Doreen only.
Sunday residue: placement only (+quick delta check if asked).

## Guardrails

| action | gate |
|---|---|
| all reads, retro, projections | free |
| generate-drafts, purchase session | confirm once |
| W1 planned-row edits, firm-week | explicit Tom approval, present diff first |
| session PO → APPROVED_TO_ORDER | per-PO Tom approval in chat |
| `fn_place_purchase_order`, policy writes | ⊥ (Doreen / separate Tom-gated action) |

Immutability: ⊥ UPDATE/DELETE `stock_ledger`, `purchase_orders`, audit tables. Schema drift → re-introspect, ⊥ guess. `current_balances.item_type` ∈ {RM,PKG,FG}.

## Parked (revisit, non-blocking)

- `planning.production.cover_days_buffer` — hardcoded fallback 3 in 0216, no policy row; seed to tune from UI.
- `session_day_of_week=0` fence stays correct while Doreen places Sundays.
- Cocktail/Muza line: several HIGH-criticality RM unstocked + missing BOM/supplier mappings — excluded from planning until Tom decides line status.
