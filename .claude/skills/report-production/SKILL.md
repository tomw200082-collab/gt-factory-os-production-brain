---
name: report-production
description: Report finished production into GT Factory OS end to end — put the batch on the production plan for the day it was made, materialize its runs, consume the raw materials and packaging, book the finished goods, and verify the ledger afterwards. Use this WHENEVER Tom says a batch was produced or asks to record one — "תדווח ייצור", "דיווח ייצור", "ייצרנו X בקבוקים", "תכניס את הייצור של אתמול", "report production", "we made 400 bottles of Detox", "log yesterday's batch" — or any message that pairs one or more finished products with quantities in a "this was made" sense (past tense, or with a date). Also use for retroactive reporting of a batch made days ago, for repack items (matcha bags, tins, kits), and when a tank was split across several SKUs. Do NOT use for planning what to produce next (that is plan-production-14d) or for printing a batch sheet for the floor (that is production-order).
---

# Report Production

## What this is for

A batch is only real once it has moved stock. Until it is reported, the raw materials
and packaging still show as on hand, the finished goods do not exist to sell, and the
day's plan looks unproduced — so procurement over-orders, Shopify oversells, and the
morning guardian raises a false flag. This skill closes that loop in one pass.

The chain, and why each link matters:

```
plan row for the production date   ← the day's plan has to match what was actually made
        ↓
runs materialize (TANK / PACK / SINGLE)
        ↓
consumption preview                ← the gate: catches negatives and off-recipe takes
        ↓
report                             ← ONE transaction: RM + packaging out, finished goods in
        ↓
close the batch plan               ← otherwise a tank plan stays open forever
        ↓
verify against the ledger          ← 200 OK proves nothing on its own
```

## The one rule about how to write

**Post only through the live API.** Never write SQL against `stock_ledger`,
`current_balances`, `production_run` or `production_actual`.

The report handler is where the two-head BOM explosion, the pick netting, the
cap-to-on-hand rule, the run stamping and the plan link all live. Hand-rolled SQL
reproduces about eighty percent of that, and the missing twenty percent is what
silently double-consumes a tank or leaves a run un-stamped. Reads are different —
query freely for item resolution, balances and verification.

`scripts/report_production.mjs` does the whole orchestration. Use it rather than
issuing the calls by hand; it already handles idempotency, plan reuse, the preview
gate, batch closing and partial-failure reporting.

## Step 1 — Get API access

The script needs `GT_API_TOKEN`: a Supabase access token for the reporting user.

If it is not already in the environment, ask Tom for it once and reuse it for the rest
of the session (it expires after about an hour). The fastest way for him to get it, in
the portal's browser console:

```js
JSON.parse(localStorage.getItem(
  Object.keys(localStorage).find(k => k.includes('auth-token'))
)).access_token
```

Confirm the path works before doing anything else:

```bash
NODE_USE_ENV_PROXY=1 curl -sS https://gt-factory-os-api-production.up.railway.app/health
```

`NODE_USE_ENV_PROXY=1` matters only behind a proxy (Claude Code web sessions); Node's
`fetch` ignores `HTTPS_PROXY` without it and the script will look like it is hanging.

If a session has direct database access instead, that is fine for the **reads** below,
but the writes still go through the API.

## Step 2 — Resolve what was produced

Tom writes the way the floor talks: "נמסטי 502 בקבוקים 1 ליטר", "מאצ'ה 20 שקיות 0.5 קילו",
"400 של דיטוקס 1 ליטר". Turn each into a real item, and stop rather than guess when two
items could match.

```sql
select i.item_id, i.item_name, i.family, i.pack_size, i.sales_uom, i.supply_method,
       i.base_bom_head_id, i.base_fill_qty_per_unit, i.primary_bom_head_id, i.status
  from private_core.items i
 where i.status = 'ACTIVE'
   and i.supply_method in ('MANUFACTURED', 'REPACK')
   and (i.family ilike $1 or i.item_name ilike $1)
 order by i.pack_size;
```

Three things from that row decide everything downstream:

- **`sales_uom`** is the unit the report must carry. `BOTTLE`, `BAG`, `TIN`, `UNIT` —
  send anything else and the report is rejected with `UOM_MISMATCH`. Never invent it.
- **`base_bom_head_id`** set means this is a tank product: the plan row is a base batch
  and the run splits into TANK plus PACK. Null means a repack or single-head item: one
  plain plan row, one SINGLE run.
- **`base_fill_qty_per_unit`** is litres of base per pack unit — 1.0 for a 1 L bottle,
  0.5 for a 500 ml. The script sizes the tank from it.

## Step 3 — Resolve the date

Default to today. "אתמול" is yesterday, in Israel time. An explicit date wins over
everything. The production date is what the plan row is filed under and what `event_at`
records, so getting it wrong misfiles the batch in every downstream report — if the
message is genuinely ambiguous about the day, ask.

Reporting a batch made days ago is completely normal on this floor; nothing about the
flow changes. The script clamps `event_at` to just before now so a same-day report filed
in the morning is not rejected as being in the future.

## Step 4 — Dry run, then report

Write the spec and run it with `dry_run: true` first. The dry run makes no writes at
all and prints the exact consumption the report will post.

```json
{
  "date": "2026-08-24",
  "dry_run": true,
  "lines": [
    { "item_id": "FG-NAM-1L",  "qty": 502, "uom": "BOTTLE",
      "base_bom_head_id": "BOM-BASE-NAM-REG", "fill_l_per_unit": 1 },
    { "item_id": "FG-MAT-500G", "qty": 20,  "uom": "BAG" }
  ]
}
```

```bash
NODE_USE_ENV_PROXY=1 GT_API_TOKEN=... node scripts/report_production.mjs spec.json
```

Read the output. If it is clean, flip `dry_run` to `false` and run it again — that
posts. Tom's standing instruction is to post without waiting for approval **when every
check is green**, so do not stall on a clean dry run; just show him the result.

Two things about the dry run are worth holding in mind, because both decide whether
"clean" means anything:

- **A first-time report cannot be previewed.** The runs only exist once the plan row
  does, and a dry run refuses to create one — so for a date with no plan yet, there is
  nothing to explode and nothing to check. The script says so (`⚠ NOT CHECKED`, status
  `dry_run_incomplete`) rather than printing an empty, reassuring result. Those lines
  are gated for real on the live pass, which still refuses to post past a blocker.
- **A blocked run is not inert.** It reports nothing and moves no stock, but the plan
  rows are written before the gate runs, so some may already exist. The script lists
  exactly which. Plan rows are intent only, so this is untidy rather than dangerous —
  re-running after the blocker clears reuses them.

Bring the blockers to Tom with the numbers, and let him decide. The blockers worth
knowing:

| Blocker | What it means | What to do |
|---|---|---|
| component would go negative | Projection says the material is not there | Real shortage, or stock arrived without a receipt. Ask which. Only Tom can authorise posting it anyway — see below |
| off-recipe take flagged | A collected quantity differs from the recipe by 2× or more | Ask what really went in, then put it in `explanation` |
| duplicate open plans | Two plan rows for the same base or item that day | Cancel one in the portal first — otherwise the other stays looking unproduced |
| no run materialized | The plan's shape does not imply a run for that item | Check the plan in the portal |
| shared component over-drawn | Two runs in the same batch each pass alone but together exceed on-hand | Real for a split tank, where both pack SKUs draw the same base and cartons. Every preview is taken before any report posts, so each sees the same on-hand; without this check the later report is silently capped and books goods the materials do not back. Split the batch across two runs of the script, or confirm the negative |

Optional per line: `scrap_qty`, `qc_brix`, `qc_ph`, `notes`, and the two
overrides — `confirm_negative: true` and `explanation: "..."`.

`confirm_negative` is Tom's call and only Tom's. It says the material really did
leave the shelf even though the projection holds none, which is usually a receipt
that was never booked rather than a phantom (Tom, 2026-07-27: bottles standing
unlabelled against a label delivery). The take then posts in full and those
components read negative until a receipt lands. Prefer booking the missing
receipt first when the goods are genuinely on site — a negative balance is a debt
the system carries in the open, not a free pass. When Tom does say to post it
anyway, set the flag and name the affected components back to him.

## Step 5 — Verify, then report back

A `201` proves the request was accepted, not that stock moved. Check the ledger:

```sql
-- what this submission actually posted
select movement_type, item_type, item_id, qty_delta::text, uom, notes
  from private_core.stock_ledger
 where source_event_id = '<submission_id>'
 order by movement_type, item_id;

-- finished goods now on hand
select item_id, sum(calculated_on_hand)::text as on_hand
  from private_core.current_balances
 where site_id = 'GT-MAIN' and item_id = any($1::text[])
 group by item_id;
```

Expect one `PRODUCTION_OUTPUT` row (positive, the finished goods), one
`PICK_CONSUMPTION` row per component (negative), and a zero-delta `PRODUCTION_SCRAP`
audit row only when scrap was reported.

If the session can write, also run `select * from private_core.rebuild_verifier();` and
report the count — it must be 0. It rebuilds a shadow table, so a read-only session
cannot run it; say that plainly rather than implying the check passed.

Then tell Tom, in Hebrew: what was booked, the consumption totals, before/after stock
for anything that got tight, the plan rows created or adjusted, and any note the script
raised.

## What the system does on its own — do not fight it

These caused real confusion before; knowing them saves a wrong "fix".

- **A PACK run explodes as if it were SINGLE.** Reporting 502 bottles consumes base
  liquid *and* packaging scaled to those 502 bottles — not to the tank. Charging the
  whole tank to the first SKU reported would over-consume by half on a split batch.
- **Never report a TANK run.** It has no finished product and answers
  `RUN_NOT_REPORTABLE`. Its liquids are swept into the first PACK report of the plan and
  stamped, so later PACK reports of the same plan cannot take them twice.
- **The base BOM's output quantity is not the tank size.** `BOM-BASE-NAM-REG` yields
  480 L per recipe; a 502 L batch scales every line by 502/480. The script never touches
  this — the handler does it.
- **`batch_size_l` is fixed once the plan row exists** and cannot be patched alongside
  the split. It does not drive consumption, so a mismatch between it and the bottles
  reported is cosmetic. The script says so and moves on.
- **BOM lines in `PENDING` status are consumed too**, not just `ACTIVE` ones. That is
  deliberate.
- **Re-running is safe.** Every mutation carries a fixed idempotency key, and a run that
  is already `REPORTED` is skipped rather than posted twice.

## Never

- Never write SQL to `stock_ledger` or any projection, and never post a correction as an
  `UPDATE` or `DELETE` — the ledger is append-only and corrections are reversal rows
  (`api/src/production-actuals/reverse-handler.ts`).
- Never invent a quantity, a UOM, or a date. If the message is ambiguous, ask.
- Never post past a blocker on your own judgement. A negative projection is Tom's call.
- Never report a batch twice to "make sure it went in" — check the run's status instead.
