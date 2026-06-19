# Spec — Supplier-Order Draft Engine (SODE)

> **Status:** PROPOSAL / SPEC ONLY. Plan-only, authorizes no build, no migration,
> no send. For Tom's review. Companion to `docs/decisions/ADR-001-autonomous-push-and-deploy.md`
> (this is the *operational*-autonomy analogue of that *development*-autonomy ADR).
> **Date:** 2026-06-13.

## 0¾. LIVE CHECK + UX FLOW AUDIT FINDINGS (2026-06-17/19) — what's real vs. the gap

Read-only check on gt-ops-prod + a `ux-flow-architect` audit of the whole corridor:

**The engine is live and running.** A purchase session ran 2026-06-17 (status
`open`): **20 supplier PO drafts, 47 lines**, ranked by tier (`urgent`), each with
`order_by_date`, `earliest_need_date`, `covered_through_date`, and `total_cost`.
Sessions also ran 06-12 and 05-16. The approve → place → skip workflow,
per-supplier consolidation, and the PO/GR close-of-loop all exist and work.

**The two precise gaps (everything else already exists):**

1. **`order_document_text` is empty.** The column exists on `purchase_session_po`
   but `msg_len = null` on every row — the engine never composes the supplier
   message. **This is the one genuinely-new brick:** fill that column with the
   verbatim-wording order text + expected cost + price-change alert. Bounded by
   procurement-spec coverage: **18 of 200 components** have
   `supplier_catalog_wording` today (grows as the goods-receipt skill runs).

2. **The per-component dial is wired but unreachable.** `cover_day_overrides = 0`
   — Tom has never set a per-component cover-days value, because the
   `/admin/planning-policy` page shows only global scalars, has no per-component
   interface, and is v1-locked against creating new keys (audit FLOW-002 /
   FLOW-011). The "3 weeks for X, JIT for Y" capability exists in the engine but
   has no UI path. Defaults today: cover 7d, safety 0d, horizon 56d,
   consolidation 21d.

**Refined, de-duplicated build (three targeted enhancements — no new engine/table/page):**

- **A. Order-message composer (backend, the real new brick).** Compose into the
  existing empty `order_document_text`: per line, the supplier's verbatim
  `supplier_catalog_wording` + `ordering_notes`, qty in order UOM, expected unit
  cost; per draft, the total + any price-change flags; hold/flag lines with no
  spec or zero price (never guess). Ships with the §5 canary. Backend-only,
  read/compose, no send. **Recommended first build.**
- **B. Make the per-component policy reachable (Tom's "back page").** Backend
  (ARCH, FLOW-011): a mutation to set `planning.safety.component_cover_days.<id>`
  (and a JIT/Buffer preset over existing keys). Portal: a per-component section on
  the policy or component page with human names + a "see what I'd order" link
  (the live simulation, FLOW-002/003).
- **C. Surface the message on the PO + "Order message" tab (durability/audit).**
  Backend exposes `order_document_text` on the PO detail read model (ARCH,
  FLOW-005); portal adds the tab with copy + "mark as sent" note (FLOW-004).

Other audit findings are polish/standard items (FLOW-001 procurement page is
Hebrew/RTL vs the English-first contract; FLOW-006 raw `reason_code` in errors;
FLOW-008 no session-history view; FLOW-007/009/010/012). They are corridor
quality, not blockers for A–C. Full audit packet retained from the
`ux-flow-architect` run (2026-06-19).

---


## 0½. RECONCILIATION — what already exists (supersedes the "build-fresh" framing of §4, §4½, §10)

A pre-build audit of `gt-factory-os` found that **most of this already exists and
is mature.** We REUSE it and improve it; we do NOT duplicate it.

| Proposed here | Already exists | Verdict |
|---|---|---|
| `fn_generate_supplier_order_draft` (decision engine, §4) | **`fn_generate_purchase_session` v2** (0206/0235): daily-MRP projected-on-hand walk, days-of-cover floor, "need date", lot-sizing, **one PO draft per supplier** | **REUSE — do not build.** |
| `component_order_policy` table (§4½) | **`planning_policy`** keys `planning.safety.component_cover_days.<component_id>` (default 7) — read by the purchase-session engine; FG per-item `planning.safety.stock_days.<item_id>` wired in `fn_compute_fg_net_requirements_v2` (0108) | **REUSE — do not build a new table.** |
| the back-office page (§4½) | **`/admin/planning-policy`** page + API + inline-edit already in the portal | **IMPROVE ergonomics — do not build fresh.** |
| JIT vs Buffer "strategy" | expressible via existing cover/trigger days; `matcha.target_days/trigger_days` is a wired JIT-style precedent | **add a thin preset over existing keys.** |
| days-of-cover, demand rate | computed throughout (0148/0198 + projections) | **REUSE.** |
| supplier order **message** (verbatim wording + expected cost + price alert) | **does NOT exist in code** — only described in the goods-receipt skill | **THE one genuinely new brick.** |

### Revised, de-duplicated plan

1. **Decision layer = the existing purchase-session engine + `planning_policy`.**
   Tom's "3 weeks for X, JIT for Y" is set today via
   `planning.safety.component_cover_days.<id>` (and trigger/target-days for
   JIT). The dials and the engine are already live.
2. **The only new backend brick = the order-message composer:** a read-only
   function/endpoint that takes a purchase-session's per-supplier PO draft and
   renders a ready-to-send message in the supplier's **verbatim wording**
   (`component_procurement_specs.supplier_catalog_wording` + `ordering_notes`),
   with **expected cost** and **price-change alerts**. This is the goods-receipt
   skill's named-but-unbuilt payoff. It gets the canary (§5).
3. **Improve the existing `/admin/planning-policy` page** into the ergonomic
   "strategy + cover-days + live simulation" surface (§4½) — as an enhancement of
   the existing page, not a new one. (Portal lane; separate from the backend brick.)

Everything below (§1–§10) is the original design; treat §4/§4½/§10 as
**superseded by this reconciliation** wherever they describe building a new
engine or table. The principles (§5 canary, §6 phasing, §7 human-forever, §8
edge cases) still apply — now to the composer + the policy improvements.

---


## 0. One sentence

Turn "what do I order from this supplier?" from a manual question into a draft
that prepares itself — exact quantities, the supplier's own wording, expected
cost, and price-change alerts — and waits for Tom's one-tap approval; the system
does the 95%, Tom does the irreversible 5% (approve + send).

## 1. Why this is the right next autonomy step

- **Highest operational leverage.** Ordering is the recurring, error-prone task
  Tom does by hand (esp. Miki Madbekot). Getting it wrong (wrong qty, wrong
  wording, missed price change) costs real money and stockouts.
- **It is already half-built.** The goods-receipt skill's "Future ordering
  support" section is the manual version of exactly this, and the data it needs
  already exists (see §3). We are closing a loop, not starting one.
- **It is safe by construction.** Everything the engine does is internal and
  reversible (compute a draft, create an OPEN PO). The one irreversible,
  external act — sending the order to the supplier — stays a human tap, forever
  (ADR-001 L5: external-system writes are never autonomous).

## 2. The closed loop it completes

```
planning net requirements ─┐
current_balances ──────────┤
open purchase_order_lines ─┼─►  SODE draft  ──(Tom approves)──►  purchase_orders (OPEN)
supplier_items (moq/lead) ─┤        │                                   │
component_procurement_specs┘        │ (Tom sends, manual)               │ supplier ships
   (verbatim wording, price)        ▼                                   ▼
                              order message text                  invoice arrives
                                                                        │
                                  goods-receipt skill ◄─────────────────┘
                                  (posts GR vs PO, diffs price,
                                   updates specs + price_history) ──┐
                                                                    └─► feeds next draft
```

The goods-receipt skill is the **inbound** half (sales invoice → stock + spec +
price). SODE is the **outbound** half (need → order). They share
`component_procurement_specs` and `price_history`, so each order makes the next
one more accurate.

## 3. What already exists (build ON these, do not reinvent)

| Need | Existing asset |
|---|---|
| What to order (demand) | planning run net requirements (`fn_compute_component_net_purchase_v3`, `v_planning_demand`) |
| What's on hand | `private_core.current_balances` |
| Don't double-order | open `purchase_order_lines` (`line_status` OPEN/PARTIAL) |
| Supplier + order unit + MOQ + lead time | `supplier_items` (`is_primary`, `order_uom`, `pack_conversion`, `moq`, `lead_time_days`) |
| Exact supplier wording + physical spec + quirks | `component_procurement_specs` (`supplier_catalog_wording`, `spec` jsonb, `ordering_notes`) |
| Expected cost + price-change detection | `supplier_items.std_cost_per_inv_uom` + `price_history` |
| Is the line orderable at all | `v_component_readiness`, `v_supplier_item_readiness` |
| PO creation path | the recommendation→PO bridge (`fn_convert…`/`po_bridge`, `purchase_orders` + `purchase_order_lines`), and `fn_generate_purchase_session` |

So SODE is mostly **composition + a guard**, not new truth.

## 4. The engine (read-only core: `fn_generate_supplier_order_draft(supplier_id)`)

Pure function, **no side effects**, returns a structured draft:

1. **Collect candidate components** for the supplier: every component whose
   primary `supplier_items` row points at `supplier_id`.
2. **Compute need per component:** `need = max(0, demand_over_horizon +
   safety_stock − on_hand − already_on_open_PO)`, where horizon ≥ `lead_time_days`.
   Round up to `moq` and to whole `order_uom` packs via `pack_conversion`.
3. **Skip** components with `need = 0`. **Hold** (do not drop) any candidate that
   is not orderable — missing spec, missing/stale price, `is_ready = false`,
   blank `approval_status` — and list it in a `held_lines[]` section with the
   reason. (Mirrors the goods-receipt "hold the line, never guess" rule.)
4. **Compose each order line** from `component_procurement_specs`:
   `supplier_catalog_wording` verbatim + `ordering_notes` quirks (e.g. "order both
   backs as one line '2 סוגים'"), the rounded qty in `order_uom`, and the
   `expected_unit_price` from `supplier_items` / latest `price_history`.
5. **Expected total** = Σ(qty × expected price); the arithmetic must close
   (same discipline as goods-receipt: lines → net → total).
6. **Price-change flags:** if the latest known price differs from the standard
   cost, annotate the line (old → new, %) so Tom sees drift before ordering.
7. **Render** a human order message in the supplier's language/wording + a
   machine payload (component_id, qty, order_uom, expected price) for PO creation.

Output: `{ supplier, order_lines[], held_lines[], expected_total, price_flags[],
order_message_text, machine_payload }`. Nothing is written.

## 4½. Decision policy — the back-office page (the "smart" core)

What to order, and *when*, is driven by a per-component **ordering policy** that
Tom tunes from a back-office page. The unifying knob is **days of cover** +
**strategy**, so the same engine serves both "buy a day before production" and
"always keep 3 weeks".

**Per-component policy (tunable):**

| Knob | Meaning | Example |
|---|---|---|
| `strategy` | `JIT` or `BUFFER` | — |
| `target_cover_days` | how much stock to aim to have on hand | JIT ⇒ ≈ `lead_time + 1`; critical ⇒ `21` (3 weeks) |
| `safety_days` | extra cushion against demand spikes / late delivery | 2–5 |
| `criticality` | `CRITICAL` / `NORMAL` / `LOW` | drives safety + alert loudness + buy-list rank |

`lead_time_days`, `moq`, `order_uom`, `pack_conversion` come from `supplier_items`
(shown read-only on the page). **Class-level defaults + per-component override:**
set "all RM = BUFFER 14d" once, then override the critical ones to 21 and the JIT
ones to `lead+1`.

**The decision math (per component), using the live demand rate from planning:**

```
daily_demand   = planning forecast units/day over the horizon
ROP            = daily_demand × (lead_time_days + safety_days)        # reorder point
order_up_to    = daily_demand × target_cover_days                     # fill level
                 (JIT ⇒ target_cover_days = lead_time_days + buffer)
projected      = on_hand + on_open_PO − demand_until_arrival
flag_to_order  = projected < ROP
order_qty      = round_to_moq_and_pack(order_up_to − (on_hand + on_open_PO))
order_by_date  = stockout_date − lead_time_days
urgency        = f(days_until_stockout, criticality)                  # ranks the buy list
```

So a JIT component surfaces only inside its lead-time window ("buy ~a day
before"); a 21-day component surfaces well ahead and is topped up to 3 weeks;
a CRITICAL breach is ranked urgent and alerts loudly.

**The page itself** (portal admin masters surface):
- One editable row per component: strategy, target cover (days/weeks), safety
  days, criticality; read-only lead time, MOQ, **current cover (days)**, demand
  rate, **order-by date**.
- Class defaults with per-item override.
- **Live simulation:** changing any knob instantly re-renders "what would be
  flagged to order today, in what quantity, and by when" — this is the dial Tom
  plays with, and it is exactly the input the engine consumes.

**Storage:** a new `private_core.component_order_policy` table (component_id PK +
the knobs) with class-level defaults, read by `fn_generate_supplier_order_draft`.
This table *is* "the back page from which the system makes its decisions".

## 5. The guard / canary (the un-fakeable principle, per Gate A)

Every new autonomy ships with its own canary. `fn_generate_supplier_order_draft`
gets a pgTAP canary (`db/tests/9101_supplier_order_draft_canary.test.sql`) that
seeds a known supplier + components + demand and asserts:

- **No invented quantities:** every drafted qty traces to a demand/reorder input;
  a component with `need = 0` never appears.
- **Coverage, not silent drops:** a needed component with a *missing spec or
  price* appears in `held_lines` (not dropped, not guessed). A stubbed engine
  that returns an empty draft fails here.
- **Verbatim wording:** the line text equals the `supplier_catalog_wording` from
  the spec store, not a guessed/component name; `ordering_notes` quirks are
  applied (the "2 סוגים" combined-line case is a fixture).
- **MOQ / pack rounding** is correct (need 1 → ordered = MOQ; order_uom packs).
- **Don't double-order:** an open PO line for the component reduces the drafted
  qty accordingly.
- **Cost math closes** and a seeded price change is flagged.
- **The policy dial actually controls the decision** (guards a page that only
  *looks* connected): a `JIT` component is flagged only inside its lead-time
  window; a `BUFFER 21d` component is flagged when projected cover < ROP and
  ordered up to 21 days; **changing `target_cover_days` changes `order_qty`
  deterministically**; a `CRITICAL` breach is ranked urgent above a `NORMAL` one.

This canary runs in the same blocking CI gate family as Gate A.

## 6. Phasing (graduated, like the autonomy ladder)

| Phase | Capability | Side effects | Human role |
|---|---|---|---|
| **P0** | `component_order_policy` table (+ class defaults seed) and the read-only `fn_generate_supplier_order_draft` that reads it; "what would I order from X" on demand | none (read-only engine; policy seeded) | sets policy (seed/SQL at first); reads the draft |
| **P1a** | **the back-office policy page** — editable per-component dials + live "what/when/how-much" simulation | policy rows only | plays with the dials |
| **P1b** | scheduled morning drafts: an "Orders to place" inbox, one card per supplier, ranked by urgency | none (drafts persisted, not POs) | reviews each morning |
| **P2** | **one-tap Approve → creates the PO** (`purchase_orders`+lines, status OPEN) | internal, reversible | approves; **sends to supplier manually** (copy the message) |
| **P3** (later, optional) | assisted send: pre-filled WhatsApp/email with the message | draft only | **the send itself is Tom's tap — never auto-sent** |

P0–P1 are pure upside with zero risk. P2 is the real win and is still safe (PO is
internal and reversible; a wrong PO is cancelled, not money out the door). P3
never crosses into auto-sending.

## 7. What stays human forever (non-negotiable)

- **Sending the order to the supplier** (external, money-committing) — Tom's tap.
- **Approving the PO** — Tom's tap.
- **Holding/guessing:** the engine never invents a spec, price, or quantity; on
  any ambiguity it holds the line and asks.

The engine's autonomy is bounded to *preparation*. This is the same boundary as
ADR-001 L5.

## 8. Edge cases the spec must handle (the "smart" part)

- **Combined-line tricks** (Miki "X סוגים") — reproduced from `ordering_notes`.
- **Misleading supplier catalog names** (e.g. "מצ'ה 500" sticker) — use the
  supplier's wording for the order, but warn, and keep our true component name.
- **MOQ + pack conversion** — order in `order_uom`, round to MOQ and whole packs.
- **Lead-time timing** — order early enough that it arrives before stockout;
  surface "order by <date>".
- **Bundles / non-catalog SKUs** (GAP-019/020) — explicitly out of scope; flagged,
  not silently ordered.
- **Stale/zero price** (the 32 supplier_items missing `std_cost_per_inv_uom`) —
  hold the line; never order at price 0.
- **Not-ready components** (`v_component_readiness.is_ready = false`) — held with
  the readiness reason, linking to the supplier-readiness corridor work.

## 9. Dependencies / sequencing

- Builds on the supplier-readiness → recommendation → PO corridor
  (`docs/superpowers/plans/2026-04-25-supplier-readiness-to-gr-corridor.md`).
  SODE's quality is bounded by `component_procurement_specs` coverage — every
  invoice the goods-receipt skill processes enriches it, so coverage grows with
  normal use.
- No new module declaration needed: procurement / POs are existing factory-os
  scope (LOCKED_DECISIONS §receipts/POs), not a new operating-system surface.

## 10. Proposed first slice (when approved)

P0 only, as a bounded backend tranche in `gt-factory-os`:
1. `component_order_policy` table + class-default seed (the decision dials).
2. `fn_generate_supplier_order_draft(supplier_id)` (read-only) that reads the
   policy and computes need/timing per §4½.
3. The pgTAP canary (§5) + its blocking CI gate — including the policy-adherence
   assertions.
4. A read-only API endpoint `GET /api/v1/queries/supplier-order-draft/:supplier_id`.
No portal page, no PO creation, no send — the page is P1a, PO/send are P2,
each separately approved. (Policy is set by seed/SQL until the P1a page exists.)

---

**Decision for Tom:** approve the spec and the P0 slice? P0 is read-only and
safe; it makes the goods-receipt skill's promised "what do I order" instant and
trustworthy, with the canary guaranteeing it never guesses.
