---
name: plan-production-14d
description: >-
  Tom's Thursday production-planning ritual for GT Factory OS. Trigger every Thursday or when Tom says
  "בוא נתכנן ייצור", "תכנון שבועיים", "plan production", "/plan-production-14d", "ריטרו ייצור", or asks
  to review last week's production vs plan and lock the next two weeks. One batched flow: retrospective →
  tune incoming (firmed) week → plan week+2 → write drafts to production_plan → Tom fine-tunes in portal →
  firm → purchase-session drafts → quantity interview → chat approval moves POs to Doreen's placement
  queue. Objective: every tank goes where it saves the most contribution margin (₪), committed orders
  first. Reuses live engines only; hands the buying interview to the procurement-planning skill.
---

# plan-production-14d — Thursday 14-day production cockpit

Role: GT head of production planning. Engine = hypothesis; Tom = final word. Converse Hebrew; SQL/internal English. Live DB: Supabase MCP, project `rvadsozabmxkkrktwgnv`, schema `private_core`, site `GT-MAIN`.

Created per Tom written request 2026-07-03 (satisfies STEP4-SKILLS-DECISION threshold: Tom approval in writing).

## Guiding objective (§G — Tom-locked 2026-07-03)

**! כל טנק הולך למקום שבו הוא מציל הכי הרבה שקלים של תרומה בשבועיים הקרובים.**

1. **Committed > forecast.** Open LionWheel orders missed = certain loss + customer trust; forecast missed = probabilistic. Committed always wins, no math.
2. **Between two fires → money decides, ⊥ "who is at zero".** Score = `margin_risk_ils_day` × shortage-days prevented in window. On-hand only shifts WHEN loss starts, not its rate. Zero-stock + tiny demand → waits; that is the honest business answer.
3. **Constraints, not goals:** full 500 L tanks, ≤1/day, ⊥ overproduce past forecast+buffer (shelf life).

Per-base score (verified live 2026-07-03; margin data complete ∀ 10 tea bases):

```sql
-- ₪ contribution at risk per day of shortage, per base
with fg_daily as (
  select item_id, sum(forecast_qty)/14.0 as units_per_day
  from private_core.fn_forecast_daily_demand(now()::date, now()::date+13)
  group by item_id)
select i.base_bom_head_id,
       round(sum(fd.units_per_day * coalesce(e.material_margin_ils,0)),0) as margin_risk_ils_day,
       count(*) filter (where e.material_margin_ils is null or not e.cogs_complete) as fgs_no_margin_data
from fg_daily fd
join private_core.items i on i.item_id = fd.item_id
join private_core.bom_head bh on bh.bom_head_id = i.base_bom_head_id and bh.production_track='tea_tank'
left join private_core.v_fg_economics e on e.item_id = fd.item_id
group by i.base_bom_head_id order by margin_risk_ils_day desc;
```

`fgs_no_margin_data` > 0 → flag, fall back to `avg_sale_price_ils`, tell Tom. Strategic overrides (key account / delisting risk) = not in data → ask Tom, ⊥ decide.

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
| **₪ margin lost** (headline) | Σ per stocked-out FG: shortage-days × units/day × `material_margin_ils` — same unit as the planning score |
| plan vs actual per batch | `production_plan` rows last week: `planned_qty`, `status`, `completed_submission_id`; actual via `stock_ledger` `PRODUCTION_OUTPUT` |
| stockouts that happened | FG `qty_delta` events driving `current_balances`<0 during week; list item+date |
| tank utilization | actual output liters per batch (units × `items.base_fill_qty_per_unit`) vs `batch_size_l` 500 |
| forecast accuracy | `fn_forecast_daily_demand(week_start, week_end)` vs actual `FG_OUT_PICK` per top FG |

Headline sentence: "הפסדנו השבוע ~₪<X> תרומה בגלל <bases>". Conclusion per miss: "<base> אזל ב-<date> כי <cause>; בתכנון הבא: <fix>". ⊥ other invented KPI/score.

### Stage 2 — tune incoming week (already `planned`)

Per base compute BOTH: stockout date (on-hand liters + scheduled receipts vs `fn_tea_base_daily_demand_l(today, today+13)`) AND `margin_risk_ils_day` (§G query). Rank dilemmas by §G: committed orders first, then ₪/day × shortage-days-prevented. Flag: batch too late vs stockout day | slot conflict resolved against the money | batch no longer needed.
Propose exact moves/adds/cancels **with the ₪ math shown** → explicit Tom approval → apply (update `production_plan` planned rows / insert; single-scope, reversible). ⊥ apply unapproved.

### Stage 3 — plan week+2 (drafts)

Confirm once → `POST /api/planning/generate-drafts` semantics = `fn_plan_tea_production(actor)` (56d EDD, 500L tank, 1/day Sun–Thu, IL holidays) + `fn_plan_matcha_repack(actor)`. Deletes only its own prior `TEAEDD:%` drafts; `planned`/`in_production` respected as supply.
Engine sequences by EDD (lowest days-of-cover) — ⊥ margin-aware. ∴ after drafts land, run the **§G re-rank pass**: score each drafted batch + each starved base by `margin_risk_ils_day`; where scarce slots collide, propose swaps so tanks follow the money (draft edits, cheap). Present W2 board: day × base × 500L + pack split + ₪/day per base.
Saturation NOTICE (>5 tanks/wk needed) → surface starved bases **ranked by ₪/day**, ask (raise `planning.production.max_batches_per_day` for that week / add workday / accept the cheapest loss) — ⊥ change policy silently.
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
