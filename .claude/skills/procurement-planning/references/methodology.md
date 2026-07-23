# Procurement Methodology — the professional brain

The rigor the skill applies on top of the engine. The engine produces a number; this file is how a
world-class buyer decides whether that number is *right* and how to make it better. Consult it whenever
computing or explaining a buffer, a service level, an order quantity, or a consolidation/cash trade-off.

## Table of contents
1. The core question and the four numbers behind every order
2. Average Daily Usage (ADU) and demand variability
3. Lead time and lead-time variability
4. Statistical safety stock (the buffer floor)
5. DDMRP buffer zones (your engine's native model)
6. Mapping the math onto GT's levers (the practical bridge)
7. ABC-XYZ segmentation → which policy each component deserves
8. Lot sizing: MOQ, order multiples, EOQ, and the consolidation window
9. The senior-buyer judgment lens (beyond the math)
10. Perishability and shelf-life
11. Inventory KPIs to sanity-check any plan

---

## 1. The core question and the four numbers

Every purchase decision answers: **how much, and by when, to keep service high without tying up cash or
risking spoilage.** Four numbers drive it for each component:
- **ADU** — average daily usage (demand rate)
- **σ_D** — variability of that demand
- **DLT** — replenishment (decoupled) lead time, and **σ_LT** — its variability
- **policy** — the service level / criticality you've chosen, and the supplier's MOQ / order multiple

If any of these is wrong or missing, the order quantity is wrong. The skill's first job is therefore to
*establish these four numbers from live data* before trusting any recommendation.

---

## 2. Average Daily Usage (ADU) and demand variability

- **ADU** = average daily consumption over a window. Sources, in order of preference:
  1. Forward demand from the published forecast exploded to components (what the engine uses).
  2. Historical actual consumption from `stock_ledger` (qty_delta < 0, posted) — the truth check.
  3. A blend (recommended): forward forecast for the rate, history for the *variability*.
- **σ_D** = standard deviation of daily consumption. **Critical:** include zero-consumption days in the
  series, or you will badly understate variability for lumpy items.
- **Coefficient of Variation, CoV = σ_D / ADU.** This single number classifies demand stability:
  - CoV < 0.5 → stable (X)
  - 0.5 ≤ CoV < 1.0 → variable (Y)
  - CoV ≥ 1.0 → erratic/lumpy (Z)

A flat "days of cover" policy gives a high service level on stable items and a *poor* one on volatile
items — the whole reason to differentiate.

---

## 3. Lead time and lead-time variability

- **DLT** — use, in order: `supplier_items.lead_time_days` → `components.lead_time_days` →
  `suppliers.default_lead_time_days` → global `planning.supplier.default_lead_time_days` (14).
- **σ_LT** — compute from receipt history when it exists: per received PO line,
  `actual_lead_days = actual_first_receipt_at::date − purchase_orders.order_date`; take stddev per
  supplier/component. **Slippage** = `actual_first_receipt_at − expected_receive_date`.
- Reality at GT: receipt history is thin (few placed POs). When σ_LT can't be estimated, assume it by
  criticality/supplier reputation: reliable supplier ≈ 10–20% of DLT; unproven or import ≈ 30–50% of DLT.
- **Lead-time variability often dominates the buffer for high-volume items** — a late delivery on a
  fast-mover hurts far more than day-to-day demand noise. Don't ignore σ_LT just because it's harder to get.

---

## 4. Statistical safety stock (the buffer floor)

The professional formula when both demand and lead time vary (King's / Heizer-Render):

```
Safety Stock (units) = Z × sqrt( DLT × σ_D²  +  ADU² × σ_LT² )
Reorder Point (ROP)  = ADU × DLT  +  Safety Stock
```

- **Z** is the service-level multiplier (standard-normal quantile). Use the table below.
- Keep all terms on one time unit (days) and one UOM.
- Moving from 95%→99% raises Z from 1.645→2.33 and roughly +40% safety stock: diminishing returns.

> **GT reality check (validated live, 2026-07-16).** Applying this formula
> naively over GT's *daily* ledger consumption inflates every buffer: RM/PKG
> consumption happens in production batches (many zero days + big spikes), so
> σ_D is huge relative to ADU (CoV 1.5–5.8) and the formula suggested >7 days
> for **81 of 81** components with history — up to 96–107 days for long-lead
> items. GT's component demand is largely *plan-driven* (the engine already
> knows the firmed plan): the buffer should cover *uncertainty around the
> plan* (plan slippage, yield variance, LT variance, forecast error), not raw
> daily consumption noise. Before proposing overrides: aggregate to weekly
> buckets at minimum, prefer variability of demand-over-lead-time windows,
> fix lead-time truth first (127d items dominate the math), and differentiate
> by criticality/spend — never batch-apply the raw daily-σ output.

**Service-level → Z:**

| Cycle service level | Z |
|---|---|
| 90% | 1.28 |
| 95% | 1.65 |
| 97.5% | 1.96 |
| 98% | 2.05 |
| 99% | 2.33 |
| 99.5% | 2.58 |

**Tier the service level by criticality** (don't give every item 99%):
- A / critical (stops production, hard to source) → 98–99.5%
- B / standard → 95–97.5%
- C / cheap, easy, low-impact → 90–93%
- Expensive + slow-moving → deliberately lower (capital efficiency beats a rare stockout)

---

### 4b. Buffer suggestion read model (backend 0292, 2026-07-23)

`api_read.v_component_buffer_suggestions` computes a per-component
`suggested_cover_days` off the flat 7-day default, **differentiated down as
well as up**, with `current_cover_days`, `delta_days`, `direction`,
`review_priority`, and a `caveat`. Use it to pick the handful worth tuning in
Stage 3 — never batch-apply; apply the ones you agree with via the gated
`planning.safety.component_cover_days.<id>` override.

It uses the DDMRP-factor shortcut (methodology §6), not raw daily-σ, because the
live data won't support a statistical buffer: **the component consumption
ledger is empty** (demand is plan-driven) and **`lead_time_days` is a flat 7-day
default for 171/184 planned components** (only 13 carry a real lead: 37d, 127d).
So the honest first action is capturing **real lead times** — `lead_is_flat_default`
flags every guessed one, and the suggestion for those is criticality-centred
only (HIGH 9 / MEDIUM 7 / NULL 6). Real-lead + HIGH-criticality items go up;
unclassified short items lean down. Trust the down/up split only once lead
truth is fixed (§3).

## 5. DDMRP buffer zones (your engine's native model)

Your purchase engine is DDMRP-lite, so it helps to think in DDMRP zones. Per component:

```
Red Base    = ADU × DLT × Lead-Time-Factor (LTF)
Red Safety  = Red Base × Variability-Factor (VF)
Red Zone    = Red Base + Red Safety              (the safety buffer)
Yellow Zone = ADU × DLT                          (cover during replenishment)
Green Zone  = MAX( MOQ, ADU × order-cycle, Red Base )   (order size / frequency)

Top of Yellow (TOY) = Red + Yellow
Top of Green  (TOG) = Red + Yellow + Green
```

**Factors** (assigned by category, refined by iteration):
- **LTF** — *smaller for longer lead times* (relative variability falls with the sqrt of lead time):
  short LT ≈ 0.6–1.0, medium ≈ 0.4–0.6, long ≈ 0.2–0.4.
- **VF** — *larger for more variable demand*: low CoV ≈ 0.2–0.4, medium ≈ 0.4–0.6, high ≈ 0.6–1.0.

**Reorder trigger (net flow equation):**
```
Net Flow Position = On-Hand + On-Order − Qualified Demand (due now + qualified spikes)
```
Order when Net Flow penetrates the yellow/red zone; order quantity = **TOG − Net Flow** (order up to top
of green). Dynamic: recompute ADU regularly (e.g., rolling 28-day, refreshed weekly).

---

## 6. Mapping the math onto GT's levers (the practical bridge)

GT does not store red/yellow/green per component. It stores **days of cover** and a **consolidation
window**. Translate as follows:

- **`planning.safety.component_cover_days.<id>`** ≈ the Red Zone expressed in days:
  ```
  cover_days ≈ SafetyStock / ADU
             = Z × sqrt( DLT × σ_D² + ADU² × σ_LT² ) / ADU
  ```
  Equivalently, a DDMRP-flavoured shortcut:
  ```
  cover_days ≈ DLT × LTF × (1 + VF)          (red zone in days, since yellow≈DLT is handled by the projection)
  ```
  Use the statistical form when σ_D and σ_LT are estimable; use the DDMRP-factor form when data is thin.
  Round to a sensible integer and never below ~3 days for a critical line.
- **`planning.purchase.consolidation_window_days`** ≈ the Green Zone / order cycle in days. Raise it to cut
  ordering/delivery overhead and approach price breaks; lower it to hold less stock and free cash. Can be
  reasoned per supplier even though the global key is one value — note the intent and, if needed, stage it.
- **MOQ / order multiple** (`components.moq_purchase_uom`, `order_multiple_purchase_uom`, or
  `supplier_items.moq`) → the engine's rounding; the Green-zone MAX(MOQ, …) is already implicit.

**Worked example.** Component with ADU = 50 inv-uom/day, DLT = 10 days, σ_D = 12, σ_LT = 2 days, target
98% (Z = 2.05):
```
SS = 2.05 × sqrt(10×12² + 50²×2²) = 2.05 × sqrt(1440 + 10000) = 2.05 × 107 ≈ 219 units
cover_days = 219 / 50 ≈ 4.4 → set component_cover_days = 5 (vs the flat 7 it has today → this item is over-buffered)
ROP = 50×10 + 219 = 719 units
```
The point: the flat 7 is wrong in *both* directions across the catalogue — this is why per-component
tuning is the highest-leverage output of a session.

---

## 6b. Produce-to-stock production (backend 0289, 2026-07-23)

Production planning is **produce-to-stock, not shortage-only**.
`fn_generate_production_recommendations` always proposes the next batch for
every MANUFACTURED / REPACK item (tea bases keep their own capacity-aware
scheduler `fn_plan_tea_production`), ranked by time-to-depletion — never
"nothing to produce".

Per item, three coverage bands (days) drive an **order-up-to** model, resolved
`planning_item_config.{min,target,max}_coverage_days` >
`planning.production.{min,target,max}_coverage_days_default` (seeded 7 / 14 /
28) > 7 / 14 / 28. Powders default 10 / 21 / 45 (longer shelf life). From the
plant's **daily** projection (`fn_compute_daily_fg_projection`):
- `ADU` = horizon demand / (weeks×7); `reorder/target/max_qty` = band-days × ADU.
- Triggers when projected on-hand drops to/below `target_qty` on some day;
  `build = target_qty − projected on-hand at that day`, floored by `min_batch`,
  rounded up the batch grid (`batch_multiple` → BOM `min_run_l` → policy default
  → exact fill-to-target).
- `trigger_reason` (in `logic_trace`): `shortage` (stockout within production
  lead time), `replenish` (reaches the reorder band), `build_ahead` (below
  target, above reorder), `topup` (never-idle — soonest-to-deplete when nothing
  is below target).
- Rank the queue by `order_by_date` = depletion day − production lead time
  (ascending). `time_to_depletion_days`, the bands and the quantities all live
  in `logic_trace`.

Tuning is the same differentiate-don't-flatten discipline as component buffers
(§4): add per-item `planning_item_config` rows (min/target/max coverage,
`min_batch`, `batch_multiple`, `production_lead_time_days`) to override the
global defaults — shorten target/max for perishable FG, lengthen for
shelf-stable. Do not flatten; a handful of high-value items per session.

---

## 7. ABC-XYZ segmentation → which policy each component deserves

You cannot lavish attention on 184 components. Segment, then differentiate effort and service.

- **ABC by annual spend** (ADU × std cost × 365, or trailing 12-mo spend from `v_rm_pkg_economics`):
  A ≈ top 80% of spend, B ≈ next 15%, C ≈ last 5%. Pareto: a handful of A-items dominate cash.
- **XYZ by demand variability** (CoV from §2): X stable, Y variable, Z erratic.
- **The 9-box → policy:**

| | X (stable) | Y (variable) | Z (erratic) |
|---|---|---|---|
| **A** (high spend) | tight buffer, high service, frequent review, lean lot sizes | model carefully, higher buffer, watch closely | hardest: hold modest buffer + react fast; consider make-to-order or supplier agility |
| **B** | standard policy, automate | standard + moderate buffer | review monthly, guard against lumps |
| **C** | big lots, rarely review, low effort | simple buffer, big lots | min-max, don't overthink |

Spend the interview time on the **A-row and the Z-column**. Let C/X items ride the defaults.

---

## 8. Lot sizing: MOQ, order multiples, EOQ, and the consolidation window

- **MOQ** sets a floor; **order multiple** sets the rounding grid. The engine already rounds up. Your job
  is to judge whether MOQ-driven over-buy is acceptable: compare the over-buy's carrying + spoilage cost to
  the cost of more frequent ordering.
- **EOQ** (the classic economic lot) balances ordering cost vs carrying cost:
  `EOQ = sqrt( 2 × annual_demand × order_cost / (unit_cost × carrying_rate) )`. Treat it as a *sanity
  check* on the consolidation window, not a hard rule — for a small operator, delivery consolidation and
  cash usually matter more than textbook EOQ.
- **Period-Order-Quantity (your model)**: ordering N days of forward demand each cycle (the
  `consolidation_window_days`). Tune N up toward EOQ-equivalent days for cheap/bulky stable items, down for
  expensive/perishable ones.
- **Price breaks**: order up to a break threshold only if `(saving per unit × qty) > extra carrying cost of
  the larger quantity`.

---

## 9. The senior-buyer judgment lens (beyond the math)

What separates a planner from a procurement *manager* — apply these to every session's output:

1. **Total Cost of Ownership, not unit price.** Landed cost = price + delivery/freight + the carrying cost
   of MOQ-inflated stock + an expected risk cost (probability × impact of a stockout or quality failure).
   A higher unit price with free delivery, shorter lead time, or better terms can win.
2. **Cash and payment terms.** Ordering early/big ties up cash; terms (`payment_terms_net_days`, EOM)
   decide *when* cash actually leaves. For a small operator cash is the binding constraint — surface the
   session's cash exposure and timing, and flag any order that can safely wait without a stockout.
3. **Supplier risk & resilience.** Single-source critical items deserve a thicker buffer or a qualified
   second source. Watch open-PO slippage history (`actual` vs `expected` receipt) and overdue lines
   (zombie supply that the projection wrongly treats as arriving today).
4. **Consolidation.** Pull near-future needs from the same supplier into today's order when it saves a
   delivery, clears an MOQ, or unlocks free shipping — but only if it doesn't blow the cash or shelf-life
   budget. (`covered_through_date`, `earliest_need_date` make this visible.)
5. **Spend discipline (Pareto).** Negotiate and agonize on A-items; automate C-items. Don't spend a 30-min
   conversation saving ₪40 on a C-item.
6. **The honest trade-off.** It is rarely "right vs wrong" — it's "if we do this, we accept that." State
   the trade-off (service vs cash vs spoilage vs effort) and let Tom choose. He is operations, finance, and
   production at once, so the decision that balances all three is his to make, with the numbers in front of him.

---

## 10. Perishability and shelf-life

GT buys both shelf-stable inputs (bottles, caps, labels, tea, sugar, bags) and perishable ones (fruit,
purées, fresh/dairy inputs). The buffer/consolidation logic must respect shelf life:
- For **perishable** components, the order-up-to quantity must not exceed what will be consumed within its
  usable life. Cap the consolidation window and the buffer accordingly; favour smaller, more frequent
  orders even at higher per-unit/delivery cost. The over-buy guard
  (`auto_dismiss_if_coverage_days_above`, 90) is a backstop, not a substitute.
- For **packaging / shelf-stable** inputs, you may buy deeper to clear MOQs, hit price breaks, and cut
  delivery overhead — capital and storage are the only real limits.
- When shelf life isn't in the data, ask Tom per component during the buffer review; capture it in
  `components.notes` or `component_procurement_specs.ordering_notes` for next time.

---

## 11. Inventory KPIs to sanity-check any plan

- **Days of cover** = on-hand / ADU. The buffer is a floor on this.
- **Inventory turns** = annual usage / average inventory. Higher = leaner; watch it doesn't fall as buffers
  rise.
- **Cycle service level / fill rate** = the probability the formula is targeting; the buffer buys it.
- **Cash exposure** = sum(final_qty × unit_cost) for the session, phased by payment terms.

A good session improves service on the items that needed it *and* doesn't quietly raise total cash tied up
or create spoilage. If buffers went up across the board, something is wrong — differentiation should move
some up and some down.
