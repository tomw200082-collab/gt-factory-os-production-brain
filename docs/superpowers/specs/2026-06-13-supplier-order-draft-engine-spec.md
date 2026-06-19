# Spec — Supplier-Order Draft Engine (SODE)

> **Status:** PROPOSAL / SPEC ONLY. Plan-only, authorizes no build, no migration,
> no send. For Tom's review. Companion to `docs/decisions/ADR-001-autonomous-push-and-deploy.md`
> (this is the *operational*-autonomy analogue of that *development*-autonomy ADR).
> **Date:** 2026-06-13.

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
