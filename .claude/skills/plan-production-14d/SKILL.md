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
4. **Bottling coexistence (Tom-locked 2026-07-04):** tank MAY run alongside item-level bottling, EXCEPT day with Muza-200ml bottling > 200 bottles (engine-enforced, migration 0278, policy key `planning.production.muza_200ml_tank_block_threshold`). Muza 200ml: **one variety per day, ≤200 bottles when tank runs**, most-urgent-by-committed-orders first. ⊥ stack 3-4 varieties on one day.
5. **Dateless committed = staged backlog (Tom 2026-07-04):** open LionWheel orders w/o `pickup_at` invisible to engine demand (projection = GREATEST(dated-committed, forecast)) — by design; Tom supplies in tranches (e.g. DET-STR 1,250: 400 supplied, next tranche following week). ! ∀ Thursday → review dateless backlog, schedule next tranche explicitly. ⊥ panic-produce full backlog at once.

Per-base score (verified live 2026-07-03; margin data complete ∀ 10 tea bases):

```sql
-- ₪ contribution at risk per day of shortage, per base.
-- Applies active planning.demand.correction_factor.<ITEM_ID> overrides (Stage 1b) — this is
-- the SINGLE choke point where factors are consumed; Stage 2 + Stage 3 reuse this query.
-- substr by fixed prefix length, NOT split on dots: item_ids may contain dots (AP-TAP-PIN-0.6).
-- fc dedup mirrors fn_compute_daily_fg_projection: DISTINCT ON keeps latest published version.
with cf as (
  select substr(key, length('planning.demand.correction_factor.')+1) as item_id,
         value::numeric as factor
  from private_core.planning_policy
  where key like 'planning.demand.correction_factor.%'),
fc as (
  select distinct on (item_id, day) item_id, day, forecast_qty
  from private_core.fn_forecast_daily_demand(now()::date, now()::date+13)
  order by item_id, day, published_at desc nulls last),
fg_daily as (
  select fc.item_id, sum(fc.forecast_qty * coalesce(cf.factor,1))/14.0 as units_per_day
  from fc left join cf on cf.item_id = fc.item_id
  group by fc.item_id)
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

### Committed-backlog overlay (§G rule 1 in SQL — run alongside the score, every stage that ranks)

! `fn_compute_daily_fg_projection` (∴ `fn_tea_base_daily_demand_l`) counts a LionWheel order ONLY
if `pickup_at IS NOT NULL` and inside the window. Verified live 2026-07-03: **47/47 open orders
(148 lines, 2,840 units) had `pickup_at` null → the engine saw ZERO committed demand.** Committed
backlog must therefore be read directly from the mirror and laid over every ranking:

```sql
-- open (unpicked) committed demand per tea base, liters
select i.base_bom_head_id,
       sum((oml.lw_qty_ordered - coalesce(oml.lw_qty_picked,0)) * i.base_fill_qty_per_unit) as backlog_l,
       sum((oml.lw_qty_ordered - coalesce(oml.lw_qty_picked,0)) * i.base_fill_qty_per_unit)
         filter (where om.pickup_at is null) as backlog_l_engine_blind,
       count(distinct om.mirror_id) as open_orders
from private_core.orders_mirror om
join private_core.orders_mirror_lines oml on oml.mirror_id = om.mirror_id
join private_core.items i on i.item_id = oml.item_id
join private_core.bom_head bh on bh.bom_head_id = i.base_bom_head_id and bh.production_track='tea_tank'
where om.retired_at is null
  and om.lw_status in ('UNASSIGNED','ASSIGNED','ACTIVE')
  and oml.resolution_status='resolved' and oml.item_id is not null
  and i.base_fill_qty_per_unit is not null and i.base_fill_qty_per_unit > 0
group by i.base_bom_head_id order by backlog_l desc;
```

Rules: (a) Stage 2 stockout-date math = on-hand + receipts vs `fn_tea_base_daily_demand_l` **+
`backlog_l_engine_blind` spread over the fortnight** — never vs forecast alone. (b) A base whose
backlog ≥ 0.5 tank is committed-first in every slot dilemma, no ₪ math (§G rule 1). (c)
Multi-tranche pattern (e.g. one commercial order arriving as several LW tasks of ~200 picked over
weeks — the Elita Ofek / BOM-BASE-DET-STR case, 625 L across 7 open tasks on 2026-07-03): the
backlog is real committed demand but ships in installments — cover it across the two weeks, ⊥
panic-schedule it into one day; if tranche pacing is unclear, ask Tom, ⊥ guess.

## Locked flow — stages, in order

```
0 gate → 1 retro → 1b forecast correction → 2 tune W1 → 3 plan W2 (drafts) → 4 ⏸ Tom tweaks → 5 firm + session → 6 procurement relay
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
| forecast accuracy | `fn_forecast_daily_demand(week_start, week_end)` vs actual `FG_OUT_PICK` per top FG; persistent deviations feed Stage 1b |

Headline sentence: "הפסדנו השבוע ~₪<X> תרומה בגלל <bases>". Conclusion per miss: "<base> אזל ב-<date> כי <cause>; בתכנון הבא: <fix>". ⊥ other invented KPI/score.

### Stage 1b — forecast self-correction loop (every Thursday, right after retro)

Extends the Stage-1 forecast-accuracy metric into a closed loop. Representation: one
`planning_policy` row per item — `key = planning.demand.correction_factor.<ITEM_ID>`, `value` =
multiplicative factor (`1.15`, `0.85`), absent = 1.0. Multiplicative ⊥ absolute: survives the
forecast itself being republished. Consumed ONLY by the §G query above (single choke point;
advisory layer — ⊥ touch `fn_plan_tea_production` / `fn_forecast_daily_demand`). Reversible by
deleting the row.

**Order: decay pass FIRST, then detection.**

**Decay pass** — `select key, substr(key, length('planning.demand.correction_factor.')+1) as
item_id, value, description from private_core.planning_policy where key like
'planning.demand.correction_factor.%'`. Re-run the detection test below for exactly those items,
without the deviation WHERE filters. Both windows now within ±15% of the plain forecast → propose
DELETE (ask Tom; on yes `delete from private_core.planning_policy where key='<key>'`). Both
windows deviating further, same direction as the stored factor → propose UPDATE (same gated
upsert below, fresh factor). Anything else → leave as-is, report. No tracking table — this is the
entire decay mechanism.

**Detection** — two-window persistence test. Window A = day −28..−15, window B = day −14..0.
Both must independently deviate >15% in the SAME direction — filters out one anomalous fortnight
(promo, late shipment, one-off bulk order). `fn_forecast_daily_demand` over past dates = what the
currently-published forecast implies for that period (verified: reads only `status='published'`,
spreads over working days) — exactly the deviation baseline; no forecast-history retention needed.
Verified live 2026-07-03 (17 items passed; censoring guards proved essential — most downward
candidates were stock- or backlog-censored):

```sql
with fc_dedup as (
  select distinct on (item_id, day) item_id, day, forecast_qty
  from private_core.fn_forecast_daily_demand(now()::date-27, now()::date)
  order by item_id, day, published_at desc nulls last),
forecast_a as (
  select item_id, sum(forecast_qty)/14.0 as rate from fc_dedup
  where day <= now()::date-14 group by item_id),
forecast_b as (
  select item_id, sum(forecast_qty)/14.0 as rate from fc_dedup
  where day >= now()::date-13 group by item_id),
actual_a as (
  select item_id, -1.0*sum(qty_delta)/14.0 as rate
  from private_core.stock_ledger
  where item_type='FG' and post_status='POSTED' and qty_delta<0
    and movement_type='FG_OUT_PICK'
    and event_at >= now() - interval '28 days' and event_at < now() - interval '14 days'
  group by item_id),
actual_b as (
  select item_id, -1.0*sum(qty_delta)/14.0 as rate
  from private_core.stock_ledger
  where item_type='FG' and post_status='POSTED' and qty_delta<0
    and movement_type='FG_OUT_PICK'
    and event_at >= now() - interval '14 days'
  group by item_id),
fg_now as (
  select item_id, sum(calculated_on_hand)::numeric as on_hand_now
  from private_core.current_balances where item_type='FG' group by item_id),
ev as (
  select item_id, event_at, qty_delta,
         sum(qty_delta) over (partition by item_id order by event_at desc, movement_id desc
                              rows between unbounded preceding and current row) as cum_desc_incl
  from private_core.stock_ledger
  where item_type='FG' and post_status='POSTED'
    and event_at >= now() - interval '28 days'),
stocked_out as (           -- was the item at ≤0 at ANY point in the 28d window (ledger walk-back)
  select item_id from (
    select e.item_id,
           least(min(f.on_hand_now - (e.cum_desc_incl - e.qty_delta)),   -- after each event
                 min(f.on_hand_now) - sum(e.qty_delta)) as min_balance   -- at window start
    from ev e join fg_now f using (item_id) group by e.item_id
    union all
    select item_id, on_hand_now from fg_now where on_hand_now <= 0
  ) s where min_balance <= 0 group by item_id),
open_backlog as (          -- committed unpicked demand (same mirror filters as §G overlay)
  select oml.item_id,
         sum(oml.lw_qty_ordered - coalesce(oml.lw_qty_picked,0)) as backlog_units
  from private_core.orders_mirror om
  join private_core.orders_mirror_lines oml on oml.mirror_id = om.mirror_id
  where om.retired_at is null
    and om.lw_status in ('UNASSIGNED','ASSIGNED','ACTIVE')
    and oml.resolution_status='resolved' and oml.item_id is not null
  group by oml.item_id)
select aa.item_id,
       round(aa.rate,2) as actual_a, round(fa.rate,2) as forecast_a,
       round(ab.rate,2) as actual_b, round(fb.rate,2) as forecast_b,
       round((aa.rate-fa.rate)/nullif(fa.rate,0)*100,1) as dev_a_pct,
       round((ab.rate-fb.rate)/nullif(fb.rate,0)*100,1) as dev_b_pct,
       round(((fb.rate+ab.rate)/2)/nullif(fb.rate,0),2) as proposed_factor,
       (so.item_id is not null) as stock_censored,
       coalesce(ob.backlog_units,0) as open_backlog_units
from actual_a aa
join actual_b ab on ab.item_id=aa.item_id
join forecast_a fa on fa.item_id=aa.item_id
join forecast_b fb on fb.item_id=aa.item_id
left join stocked_out so on so.item_id=aa.item_id
left join open_backlog ob on ob.item_id=aa.item_id
where fa.rate>0 and fb.rate>0
  and abs((aa.rate-fa.rate)/fa.rate) > 0.15
  and abs((ab.rate-fb.rate)/fb.rate) > 0.15
  and sign(aa.rate-fa.rate) = sign(ab.rate-fb.rate)
order by abs((ab.rate-fb.rate)/fb.rate) desc;
```

Per row, in order:
1. **Downward candidate (actual < forecast) + `stock_censored`** → ⊥ propose. Surface: "possible
   demand signal but stock-censored — cannot trust yet, re-check next week". Picks can't happen
   from an empty shelf; low actuals ≠ low demand.
2. **Downward candidate + `open_backlog_units` > 0.25 × (forecast_b × 14)** → ⊥ propose. Surface
   as backlog-censored: committed demand exists, it just hasn't been picked yet (the multi-tranche
   pattern above). Proposing a cut here is exactly the wrong move.
3. **Factor outside `[0.5, 2.0]`** (clamp band) → ⊥ routine proposal. Surface as "structural
   change, needs your judgment".
4. Otherwise → ask Tom ONE question per item (⊥ bulk): "{item}: נמכר {actual_b}/יום ב-14 הימים
   האחרונים (וגם ב-14 שלפני כן), מול תחזית {forecast_b} — לתקן את קצב התכנון בפקטור {factor}?"

On yes (gated write, per-item):

```sql
insert into private_core.planning_policy (key, value, uom, description, updated_at)
values ('planning.demand.correction_factor.<item_id>', '<factor>', 'ratio',
        '<rationale>; approved by Tom in chat <date>', now())
on conflict (key) do update set value=excluded.value, description=excluded.description,
  updated_at=now();
```

On no: skip, write nothing. After any write: read the row back (verify it landed live, ⊥ assume).

### Stage 2 — tune incoming week (already `planned`)

Per base compute BOTH: stockout date (on-hand liters + scheduled receipts vs `fn_tea_base_daily_demand_l(today, today+13)` **+ the §G committed-backlog overlay** — the engine is blind to pickup_at-null orders) AND `margin_risk_ils_day` (§G query — now applies any active `planning.demand.correction_factor` overrides automatically). Rank dilemmas by §G: committed orders first, then ₪/day × shortage-days-prevented. Flag: batch too late vs stockout day | slot conflict resolved against the money | batch no longer needed.
Propose exact moves/adds/cancels **with the ₪ math shown** → explicit Tom approval → apply (update `production_plan` planned rows / insert; single-scope, reversible). ⊥ apply unapproved.

### Stage 3 — plan week+2 (drafts)

Confirm once → `POST /api/planning/generate-drafts` semantics = `fn_plan_tea_production(actor)` (56d EDD, 500L tank, 1/day Sun–Thu, IL holidays) + `fn_plan_matcha_repack(actor)`. Deletes only its own prior `TEAEDD:%` drafts; `planned`/`in_production` respected as supply.
Engine sequences by EDD (lowest days-of-cover) — ⊥ margin-aware. ∴ after drafts land, run the **§G re-rank pass**: score each drafted batch + each starved base by `margin_risk_ils_day` (the §G query now applies any active `planning.demand.correction_factor` overrides automatically) + lay the committed-backlog overlay over the board; where scarce slots collide, propose swaps so tanks follow the money (draft edits, cheap). Present W2 board: day × base × 500L + pack split + ₪/day per base.
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
| `correction_factor` insert/update/delete (`planning_policy`) | explicit per-item Tom approval in chat, present exact key/value first; ⊥ bulk, ⊥ auto-apply |
| session PO → APPROVED_TO_ORDER | per-PO Tom approval in chat |
| `fn_place_purchase_order`, other `planning_policy` writes | ⊥ (Doreen / separate Tom-gated action) |

Immutability: ⊥ UPDATE/DELETE `stock_ledger`, `purchase_orders`, audit tables. Schema drift → re-introspect, ⊥ guess. `current_balances.item_type` ∈ {RM,PKG,FG}.

## Parked (revisit, non-blocking)

- `planning.production.cover_days_buffer` — hardcoded fallback 3 in 0216, no policy row; seed to tune from UI.
- `session_day_of_week=0` fence stays correct while Doreen places Sundays.
- Cocktail/Muza line: several HIGH-criticality RM unstocked + missing BOM/supplier mappings — excluded from planning until Tom decides line status.
