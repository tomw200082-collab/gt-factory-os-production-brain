# MASTERPROMPT — the MUZA line, fully retired from every system, with its raw materials and packaging still tracked

**STATUS: LIVE — not yet executed**

> **Usage:** paste this entire file as the first message of a fresh session with the
> Supabase MCP connector (project `rvadsozabmxkkrktwgnv`), the Shopify MCP connector, and
> the repos `gt-factory-os`, `gt-factory-os-production-brain` and `Sales-Machine`
> attached. It takes MUZA from "deactivated in one table and fully live everywhere else"
> to "archived on purpose, in the right order, with its components still counted."
> It halts for Tom only where §6 says so; §6 is that complete list.
>
> **Provenance:** written 2026-08-30. Every number in §2 was measured that day —
> Postgres through the Supabase MCP against `private_core`, Shopify through the Shopify
> MCP `graphql_query`, sales figures from the fact table rebuilt the same morning
> (Bulk Operation `8004166713585`, 33,606 objects; five correctness gates passed, see
> `Sales-Machine/evidence/2026-08-30-existing-customer-growth.md`).
> Tom's instruction, verbatim, 2026-08-30:
> `הוצאנו את כל המוזות כולל כולן מהחברה שלנו. אנחנו לא מוכרים אותן יותר.` and
> `שנמשיך לעקוב אחר המלאי חומרי גלם ואריזות אבל את המוצרים נעיף מהמערכת (נארכב) סופית.`
> Authority: `gt-factory-os-production-brain/CLAUDE.md` → `EXECUTION_POLICY.md` →
> `gt-factory-os/CLAUDE.md` — cited below, never copied.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-09-20. Re-run §2.5 first.
> If the counts moved but the shape holds, rebuild §2 from the re-run and keep going.
> **If any MUZA item has returned to `ACTIVE`, or a MUZA order was placed after
> 2026-08-30, halt and surface** — that means the retirement was reversed or is disputed,
> and this document is no longer describing the world.

## 0. How to work

- **Who you are here:** one Claude session running to completion. You hold read and
  write access to Postgres/Supabase (`private_core`), read and write access to Shopify
  through the MCP connector, and the three repos. You decide the sequencing, the SQL and
  the migration content alone. You decide nothing about writing off stock, nothing about
  which products a customer can still see, and nothing that deletes a row.
- **Read first, in this order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `gt-factory-os/CLAUDE.md` §Stock truth, §Migrations, §Shopify writes ·
  `gt-factory-os-production-brain/EXECUTION_POLICY.md` ·
  `gt-factory-os-production-brain/CURRENT_STATE.md` ·
  `docs/warehouses/catalog-truth.md` (what GT sells; MUZA is not in it and never was —
  see landmine 6).
- **Authority:** `gt-factory-os-production-brain/CLAUDE.md` §Source of truth,
  §Authorization, §Write boundaries; `gt-factory-os/CLAUDE.md` §Stock truth,
  §Migrations, §Shopify writes. Where this document and an authority doc disagree, the
  authority doc wins and this document is wrong.
- **Halt conditions, evidence standard, git discipline:** inherited from
  `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and §Evidence, and
  `gt-factory-os/CLAUDE.md` §Migrations for the numbered-file bracket. Work on your
  session's designated branch, one commit per workstream, draft PR at the end. Deltas
  specific to this work are in §8.
- **The standard.** Tom's instruction has two halves and the second is the one that
  gets dropped: the products leave the system **and** the raw materials and packaging
  stay tracked. Three checkable prohibitions:
  1. **No component is archived, deactivated or hidden.** Not one. A run that ends with
     any `private_core.components` row moved out of `ACTIVE` has failed, whatever else
     it achieved.
  2. **No row is deleted and no ledger row is amended.** Archival is a status change and
     a mapping retirement, never a `DELETE`, never a `DROP`, never an `UPDATE` on
     `stock_ledger`.
  3. **No stock quantity is written without Tom's explicit number.** Nineteen units of
     finished MUZA exist. Deciding their fate is §6 B, not yours.
- **Language:** this document is in English because that is the register you reason best
  in; data literals stay in their own script, in backticks, and are never translated.
  **Output language: Hebrew, concise.** Short sentences, no preamble, no restating the
  question. Tom reads the report on a phone.

## 1. Mission and definition of done

**One testable sentence:** every MUZA product is archived in Postgres, retired from the
Shopify sync map, and archived in Shopify, while every raw material and packaging
component that MUZA used remains `ACTIVE` and countable.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Every MUZA item sits in the terminal archived state, and which state that is was decided and written down | the count query returns anything but `0` — `SELECT count(*) FROM private_core.items WHERE status='ACTIVE' AND (sku ILIKE '%MUZ%' OR item_id ILIKE '%MUZ%')` — **or** the W1 manifest names no `items_terminal_state`, **or** fewer than the §2.2 item count carry it. (The count alone already passes at boot: all 15 rows were `INACTIVE` on 2026-08-30. A condition that cannot fail is not a condition, so the recorded decision is the real test.) |
| D2 | No MUZA SKU is still mapped live to Shopify | `SELECT count(*) FROM private_core.integration_sku_map m JOIN private_core.items i USING (item_id) WHERE m.source_channel='shopify' AND m.approval_status='approved' AND m.mapping_status='active' AND (i.sku ILIKE '%MUZ%' OR i.item_id ILIKE '%MUZ%')` returns anything but `0` |
| D3 | No MUZA BOM head is `ACTIVE` | `SELECT count(*) FROM private_core.bom_head WHERE status='ACTIVE' AND (parent_name ILIKE '%muza%' OR display_family ILIKE '%muza%' OR parent_ref_id IN (SELECT item_id FROM private_core.items WHERE sku ILIKE '%MUZ%'))` returns anything but `0` |
| D4 | **Every** component MUZA used is still `ACTIVE` | the §2.5 component query returns any row whose `status` is not `ACTIVE`, or returns fewer than the count recorded in §2.2 |
| D5 | No MUZA product is purchasable on the storefront | the Shopify query in §2.5 returns any product whose `status` is `ACTIVE` and whose title or SKU matches the §2.2 list |
| D6 | The ledger is untouched and the projection still rebuilds | `rebuild_verifier()` returns anything but `0`, or the `stock_ledger` row count for MUZA items differs from the §2.2 figure |
| D7 | Nothing was deleted | `git diff` on the migration shows a `DROP`, `DELETE`, or an `UPDATE` targeting `stock_ledger` |
| D8 | The change is recorded where the next session will find it | `docs/warehouses/catalog-truth.md` has no MUZA retirement entry, or `Sales-Machine/CURRENT_STATE.md` has no dated line, or this file is not stamped |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

| # | Decision | Consequence for you |
|---|---|---|
| S1 | **MUZA is out of the company. Permanently.** Tom, 2026-08-30, in writing. | Do not model a return. Do not leave a flag that re-enables it. Do not ask whether it is temporary. |
| S2 | **Raw materials and packaging stay tracked.** Tom, same message. | Components are untouched — see the standard's prohibition 1. Their stock keeps projecting from the ledger exactly as it does today. |
| S3 | **Archive, never delete.** Inherited: `gt-factory-os/CLAUDE.md` §Migrations bans `DROP COLUMN` / `DROP TABLE` in prod; §Stock truth makes `stock_ledger` append-only. | Every step is a status change or a mapping retirement. History stays readable. |
| S4 | **The sales plan already treats MUZA as retired.** `Sales-Machine/evidence/2026-08-30-existing-customer-growth.md` — the family is out of revenue, archetypes and peer statistics, and 20 accounts carry a named replacement row. | Do not recompute the sales side. If you change the SKU list, say so; that document names its own re-run path. |

## 2. Ground truth — measured 2026-08-30; re-verify at boot

### 2.1 The fact that reorganizes this work

**MUZA is already deactivated in `private_core.items` — and live everywhere that
matters.** All 15 MUZA rows in `items` are `INACTIVE`. Meanwhile all **20 BOM heads are
`ACTIVE`**, **34 of the 46 Shopify mappings are `approved` + `active`**, **26 MUZA
products are `ACTIVE` on the storefront**, and `shopify_available_reconcile_live` is enabled, so the
reconciler writes `available` for those SKUs every five minutes on cron job 24.

So this is not "archive MUZA." It is **finish an archival that was started in one table
and abandoned before the parts that actually gate selling**. The `items.status` column is
the least load-bearing thing you will touch. This is the same shape as the documented
`0302` error in `gt-factory-os/CLAUDE.md` §Shopify writes: a flag or status that looks
decisive and has readers elsewhere.

### 2.2 The numbers

Postgres, `private_core`, measured 2026-08-30 via the Supabase MCP:

```
items matching MUZ                                15   (ACTIVE: 0)
bom_head                                          20   (ACTIVE: 20)
bom_version                                       38
bom_lines                                        336
distinct components referenced                    48
  of which used ONLY by MUZA BOMs                 35   (all ACTIVE, most carrying stock)
integration_sku_map rows                          46   (approved+active: 34)
planning_item_config rows                          0
stock_ledger rows                                182   (last event 2026-08-05)
current_balances with non-zero on hand             6   (19 units total)
production_plan rows                              21   (11 cancelled, 10 completed, 0 open)
feature flag shopify_available_reconcile_live   enabled
```

The 35 MUZA-only components split into two groups that need different decisions from Tom
and **no decision from you** — both stay `ACTIVE` either way:

- **20 packaging** — generic and reusable: `PKG-BOTTLE-200ML` (1,053), `PKG-CAP-200ML`
  (1,054), `PKG-CARTON-200ML` (400), `PKG-BOTTLE-MUZ-1L` (37), `PKG-CAP-MUZ-1L` (183),
  `PKG-CARTON-MUZ-1L` (36); and **13 MUZA-branded stickers** totalling roughly 7,400
  units, which cannot be used on anything else.
- **15 raw materials** — reusable spirits and syrups: `RAW-GIN` (20), `RAW-CAMPARI`
  (12.99), `RAW-TRIPLE-SEC` (2.69), `RAW-VERMOUTH-RED` (12), `RAW-VIOLET-LIQUEUR` (7.3),
  `RAW-ALCOHOL-96` (2.5), `RAW-PASSION-SEEDLESS` (80.85), and eight syrups.

Shopify, measured 2026-08-30: **26 products still `ACTIVE`**, several with large negative
inventory (`GTCC-TRO-JAP-1L` at −1,482, `GTCC-MUZ-PNMM-1L` at −653, `GTCC-MUZ-TRIL-1L` at
−476, `GTCC-JAS-JAZ-1L` at −424) and a few positive (`GTCC-MUZ-JASJ-1L` 14,
`GTMX-MUZ-MRCL-1L` 8, `GTCC-MUZ-QUE-0.2L` 4). One product carries a SKU that never sold in
the 24-month window and is easy to miss: `GTCC-MUZ-RSSP-1L`, *Muza Russian Sputnik*.

Sales, trailing twelve months `2025-09` → `2026-08`, from the fact table:

```
MUZA revenue                    ₪467,915   (7.7% of all revenue)
accounts that bought it              62   (45 of them still ordering)
of which ≥25% of their basket        21
largest single exposure         ₪237,246   — a wholesaler, 72% of its basket
```

### 2.3 What is NOT built

- **No retirement mechanism exists.** There is no "discontinued" state, no archival
  script, no precedent migration. You are writing the first one. Keep it a status change
  and a mapping retirement; do not build a framework.
- **No link from a component to "the product line that used it."** The only path is
  `bom_lines` → `bom_version` → `bom_head` → `items`. Archiving the BOM heads therefore
  makes MUZA-only components *look* orphaned to any future query that walks that path.
  Nothing today depends on it, but §4 W4 records the list so a later reader does not
  conclude they are dead.
- **No decision about the stock.** 19 finished units and ~7,400 branded stickers exist and
  no one has said what happens to them. §6 B.

### 2.4 Known-broken, adjacent, out of scope

- **Shopify negative inventory is pre-existing and not yours.** Those numbers predate this
  work. Do not "fix" them by setting inventory — `gt-factory-os/CLAUDE.md` §Shopify writes
  makes `shopify_available_reconcile` the sole live writer of `available`, and a manual
  set fights it on the next five-minute cycle.
- **`מוזה קוקטיילים בע"מ` and `MUZA COCKTAILS` are customers, not products.** They are two
  Shopify customer records under open identity question `U-010` in
  `Sales-Machine/CURRENT_STATE.md`. **Do not archive them.** They are also both churned,
  which is the churn radar's business, not this run's.
- **The `AP-DRI-PSBLAP-1` SKU** carries a Hebrew title naming MUZA Purple Kiss but sits in
  the accessories SKU range. Treat it as MUZA for archival; flag the naming oddity in the
  report rather than renaming anything.
- **The sales growth plan** is already rebuilt without MUZA and is not re-run here (S4).

### 2.5 Re-verification block

Run all three before writing anything. They regenerate §2.2.

```sql
-- 1 · Postgres state. Every count in 2.2 comes from this.
WITH muz AS (SELECT item_id, sku, status FROM private_core.items
             WHERE sku ILIKE '%MUZ%' OR item_id ILIKE '%MUZ%'),
     mh AS (SELECT bom_head_id, status FROM private_core.bom_head h
            WHERE h.parent_ref_id IN (SELECT item_id FROM muz)
               OR h.parent_name ILIKE '%muza%' OR h.display_family ILIKE '%muza%')
SELECT (SELECT count(*) FROM muz)                                              AS items,
       (SELECT count(*) FROM muz WHERE status='ACTIVE')                        AS items_active,
       (SELECT count(*) FROM mh)                                               AS bom_heads,
       (SELECT count(*) FROM mh WHERE status='ACTIVE')                         AS bom_heads_active,
       (SELECT count(*) FROM private_core.integration_sku_map
         WHERE item_id IN (SELECT item_id FROM muz))                           AS map_rows,
       (SELECT count(*) FROM private_core.integration_sku_map
         WHERE item_id IN (SELECT item_id FROM muz)
           AND approval_status='approved' AND mapping_status='active')         AS map_live,
       (SELECT count(*) FROM private_core.stock_ledger
         WHERE item_id IN (SELECT item_id FROM muz))                           AS ledger_rows,
       (SELECT coalesce(sum(calculated_on_hand),0) FROM private_core.current_balances
         WHERE item_id IN (SELECT item_id FROM muz))                           AS fg_on_hand;
-- Values observed 2026-08-30: items 15 · items_active 0 · bom_heads 20 ·
-- bom_heads_active 20 · map_rows 46 · map_live 34 · ledger_rows 182 · fg_on_hand 19.
```

```sql
-- 2 · The components that must survive. D4 reads this. Expected 2026-08-30: 35 rows,
--     every one status ACTIVE. A row that is not ACTIVE, or a missing row, fails D4.
WITH mh AS (SELECT bom_head_id FROM private_core.bom_head h
            WHERE h.parent_ref_id IN (SELECT item_id FROM private_core.items
                                      WHERE sku ILIKE '%MUZ%' OR item_id ILIKE '%MUZ%')
               OR h.parent_name ILIKE '%muza%' OR h.display_family ILIKE '%muza%'),
     use AS (SELECT final_component_id cid,
                    count(*) FILTER (WHERE bom_head_id IN (SELECT bom_head_id FROM mh)) muza,
                    count(*) FILTER (WHERE bom_head_id NOT IN (SELECT bom_head_id FROM mh)) other
             FROM private_core.bom_lines WHERE final_component_id IS NOT NULL GROUP BY 1)
SELECT c.component_id, c.component_name, c.status,
       coalesce((SELECT sum(calculated_on_hand) FROM private_core.current_balances b
                 WHERE b.item_id=c.component_id),0) AS on_hand
FROM use JOIN private_core.components c ON c.component_id=use.cid
WHERE use.muza>0 AND use.other=0 ORDER BY c.component_id;
```

```
# 3 · Shopify storefront state. D5 reads this. Run through the Shopify MCP
#     `graphql_query`. Expected 2026-08-30: 26 ACTIVE.
{ products(first: 60, query: "title:*Muza* OR title:*מוזה* OR title:*Jasmin* OR title:*Tropical*")
  { nodes { id title status variants(first:5){ nodes { sku inventoryQuantity } } } } }
```

## 3. What the hard part actually is

The visible deliverable is a status change. Five things make it wrong, and each is a
different mistake.

### 3.1 The retirement is already half-done, in the half that does not matter

`items.status='INACTIVE'` on all 15 rows reads as finished and is the weakest signal in
the system. What actually gates selling is `integration_sku_map` (34 rows still live, and
the reconciler writes `available` off them every five minutes) and Shopify's own
`status` (26 products still purchasable). **Consequence for ordering:** work outward from
the customer, not inward from the item table. Shopify and the SKU map first; `items` and
BOMs last, because they change nothing a customer can see.

### 3.2 Order matters, and the wrong order produces a live error loop

Archive the Shopify products first and the reconciler keeps trying to write `available`
for SKUs it can no longer resolve, every five minutes, until someone notices the log.
Retire the mapping first and the reconciler simply stops considering them — silent and
correct. **Consequence:** `integration_sku_map` is retired **before** Shopify status
changes, not after. This is the single sequencing decision in the whole run.

### 3.3 "Archive the product line" reads as "archive everything the product line touched"

It is the natural sweep, and it is the exact opposite of Tom's second sentence. Thirty-five
components are used *only* by MUZA BOMs. Gin, Campari, vermouth, triple sec, eight syrups,
bottles, caps and cartons — real stock, still countable, some of it reusable on other
lines. A cascade that follows `bom_lines` down and deactivates what it finds destroys the
inventory visibility Tom explicitly asked to keep. **Consequence:** the component list is
computed and *excluded* at the top of the run, before any status change is written, and
D4 re-reads it afterwards.

### 3.4 The coverage query will improve, and that improvement is fake

`gt-factory-os/CLAUDE.md` §Shopify writes carries the only coverage check that matters:
`ACTIVE` sellable items not mapped to Shopify. Archiving MUZA items removes rows from that
query's own population, so coverage goes up without a single mapping being fixed.
**Consequence:** record the coverage number **before** and **after**, and state in the
report that the delta is composition, not progress. A future session reading only the
after-number will conclude a sync gap was closed.

### 3.5 A substring match on `MUZ` misses a third of the line

Eleven of the SKUs that sold as MUZA products carry no `MUZ` in their code:
`GTCC-TRO-JAP-1L`, `GTCC-TRO-JAP-0.15L`, `GTCC-TRO-JAP-0.15Lx20`, `GTCC-JAS-JAZ-1L`,
`GTCC-JAS-JAZ-0.15L`, `GTCC-JAS-JAZ-0.15Lx20`, `AP-DRI-PSBLAP-1`, and the gift-box SKUs
that bundle them. They are the Hebrew-titled predecessors of the same drinks —
`קוקטייל טרופיקל אין גאפן (גין)` is *Tropical in Japan*, `קוקטייל גאסמין גאז (וויסקי)`
is *Jasmine Jazz*. Most have no `items` row at all and exist only in Shopify and in order
history. **Consequence:** the Shopify sweep is driven by the title query in §2.5, not by a
SKU pattern, and the report lists every SKU it touched so Tom can spot a miss.

## 4. Workstreams

Run W1 first; it produces the lists everything else consumes. W2 → W3 → W4 in order —
§3.2 is why. W5 and W6 run once W4 lands.

### W1 — Build and freeze the three lists

Produce, from the §2.5 queries and nothing else:

1. **`ARCHIVE_ITEMS`** — MUZA rows in `private_core.items` (expected 15), plus the
   `items_terminal_state` you chose in W4 and why. D1 reads this field.
2. **`ARCHIVE_SHOPIFY`** — Shopify products to archive, from the title query, each with
   its SKU and current status (expected 26 `ACTIVE`, plus already-`ARCHIVED` ones listed
   for completeness).
3. **`KEEP_COMPONENTS`** — the MUZA-only components (expected 35), with `status` and
   `on_hand`. This list is a **do-not-touch** list.

Write all three to `docs/analytics/2026-08-30_muza_retirement_manifest.json` in the
production brain **before** any write. Every later step names the list it is acting on.

**Acceptance:** the manifest exists and its counts match §2.5, or you halt (§8).

### W2 — Retire the Shopify SKU mappings

One numbered migration under `gt-factory-os/db/migrations/`. Read
`gt-factory-os/CLAUDE.md` §Migrations first and honour the FR1/FR2 bracket: **list the
directory immediately before writing the numbered file and again after; a new file
appearing in between is a `contract_failure` and a halt.**

Set `mapping_status` to its retired value for every `ARCHIVE_ITEMS` mapping. Discover the
allowed values from the column's own constraint or enum before writing — do not assume a
literal. Leave `approval_status` alone: it records that a human once approved the mapping,
which stays true. Ship the paired test under `db/tests/` asserting D2 returns `0`.

**Acceptance:** closes D2.

### W3 — Archive the products in Shopify

For every product in `ARCHIVE_SHOPIFY` still `ACTIVE`, set `status` to `ARCHIVED`.
This is a **customer-facing change** and needs Tom's go — §6 D. Present the full list,
get the word, then act; the mutation is `productUpdate`.

Do not touch inventory. Do not touch prices. Do not delete a product.

**Acceptance:** closes D5.

### W4 — Archive the items and the BOM heads

Same migration file as W2 or the next slot, your call, but the commit message must
enumerate both concerns if you pair them (`gt-factory-os/CLAUDE.md` §Migrations).

- `private_core.items`: the 15 rows are already `INACTIVE`. If the schema has a distinct
  archived state, move them to it; if `INACTIVE` is the terminal state, record that and
  leave them. Either way D1 must hold.
- `private_core.bom_head`: move the 20 `ACTIVE` heads out of `ACTIVE`. Versions and lines
  are history and stay exactly as they are.
- **`private_core.components`: no statement touches this table.** Add a comment in the
  migration saying so, with the reason, so the next reader does not "finish the job."

**Acceptance:** closes D1, D3, D4, D7.

### W5 — Prove the ledger and the projection are untouched

Report `stock_ledger` row count for MUZA items before and after (expected `182`, unchanged),
and `rebuild_verifier()` (expected `0`). Report the coverage query from
`gt-factory-os/CLAUDE.md` §Shopify writes before and after, with the §3.4 caveat stated in
words.

**Acceptance:** closes D6.

### W6 — Record it where the next session will look

- `docs/warehouses/catalog-truth.md` — a dated MUZA retirement entry. It already carries a
  negative-records section for `ACTIVE`-in-Shopify-but-not-sold products; this is the same
  shape at line scale. Grade it `user_confirmed` and cite Tom's 2026-08-30 instruction.
- `Sales-Machine/CURRENT_STATE.md` — one dated line plus any `UNRESOLVED` you open.
- The manifest from W1, committed.
- **Stamp this file** `SHIPPED` with pointers, or `SUPERSEDED by <path>`, or
  `ABANDONED — why`.

**Acceptance:** closes D8.

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**

- **`private_core.components`, `component_aliases`, `component_procurement_specs`,
  `supplier_items`.** The whole point of the second half of the instruction.
- **`stock_ledger`, `balance_anchors`, `current_balances`, projections.** Append-only;
  corrections by reversal row only; never a direct mutation
  (`gt-factory-os/CLAUDE.md` §Stock truth).
- **The finished MUZA stock (`fg_on_hand` 19 on 2026-08-30, §2.5 query 1) and the ~7,400
  branded stickers (§2.2).** §6 B.
- **Shopify inventory quantities and prices.** §2.4.
- **The customer records `מוזה קוקטיילים בע"מ` and `MUZA COCKTAILS`.** §2.4.
- **Frozen flags and code sentinels** — `SHOPIFY_FG_SYNC_LIVE_ADAPTER_WIRED`,
  `SHOPIFY_FULFILLMENT_BRIDGE_LIVE_ADAPTER_WIRED`, `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`,
  `LIONWHEEL_FG_OUT_BRIDGE_ENABLED`. None of them needs to move for this work.
- **The sales growth plan.** Already rebuilt without MUZA (S4).
- **Any other product line.** If a query returns something that is not MUZA, the query is
  wrong; fix the query, do not widen the scope.

## 6. Tom's part — the complete list, nothing else is his

**A. Confirm the three lists are right and complete.** You build them in W1 and show him
the counts and the SKUs — in particular the eleven Hebrew-named legacy SKUs from §3.5 and
`GTCC-MUZ-RSSP-1L`, which never sold. Only he knows whether something is missing. Two
minutes. Blocks W2.

**B. Decide what happens to the stock.** The `fg_on_hand` figure measured on 2026-08-30
(§2.5 query 1), the roughly 7,400 MUZA-branded stickers in §2.2, and the reusable spirits
and syrups beside them. Sell through, write off, or hold. Only he can
say, and a write-off posts to the ledger, which needs his number. **This blocks nothing
else** — build everything else while it is open, and leave the balances exactly as they
are.

**C. Decide whether the two MUZA customer records stay.** `מוזה קוקטיילים בע"מ` and
`MUZA COCKTAILS` (§2.4). They are customers, not products, and both are churned. Adds to
`U-010` either way.

**D. Approve the Shopify archival before it runs.** 26 products stop being visible to
customers. Customer-facing and irreversible in practice, so it needs his word
(`gt-factory-os-production-brain/CLAUDE.md` §Authorization). Show the list, get the go.

Everything not listed here is yours.

## 7. Landmines — do not rediscover these

1. **`items.status='INACTIVE'` looks like the job is done.** Symptom: the first query you
   run says zero MUZA items are active, and the work appears finished. Cause: the item
   status gates nothing a customer sees (§3.1). Resolution: check
   `integration_sku_map.mapping_status` and Shopify `status` before concluding anything.
   This is the documented `0302` mistake in `gt-factory-os/CLAUDE.md` §Shopify writes,
   recurring in a new place.

2. **Archiving Shopify before retiring the mapping starts a five-minute error loop.**
   Symptom: `shopify_available_reconcile` failures appear on cron job 24 shortly after
   your change. Cause: the reconciler resolves SKUs from `integration_sku_map` and keeps
   trying (§3.2). Resolution: W2 strictly before W3.

3. **A `MUZ` substring match misses eleven SKUs.** Symptom: the archival looks complete
   and `קוקטייל טרופיקל אין גאפן` is still on sale. Cause: the Hebrew-titled predecessors
   carry no `MUZ` in their SKU and most have no `items` row (§3.5). Resolution: drive the
   Shopify sweep from the title query in §2.5 and list every SKU touched.

4. **Cascading down `bom_lines` deactivates 35 components.** Symptom: a tidy-looking
   archival that also removes gin, Campari and 7,400 stickers from inventory tracking.
   Cause: MUZA is the only consumer of those components, so any "unused component" sweep
   catches them (§3.3). Resolution: compute `KEEP_COMPONENTS` first, exclude explicitly,
   and re-read it after (D4).

5. **The coverage number improves and means nothing.** Symptom: `items` not mapped to
   Shopify drops, and it reads as a sync fix. Cause: archived items leave the query's
   population (§3.4). Resolution: report before and after with the caveat in words.

6. **`catalog-truth.md` never listed MUZA, so it looks like nothing to update.** Symptom:
   you search the warehouse file, find no MUZA section, and skip W6. Cause: the file
   covers tea extracts, matcha and powders, purées and accessories — cocktails were
   deliberately excluded from the products catalog by Tom on 2026-08-05
   (`docs/pricing/2026-08-05_products_pricelist_page.md`). Resolution: add the retirement
   as a dated record anyway. Its absence is exactly why the next session will not know.

7. **Shopify's negative inventory invites a "fix".** Symptom: `−1,482` on a product you
   are archiving, and a `set-inventory` call one keystroke away. Cause: pre-existing
   oversell, unrelated to this work; `available` is owned by the reconciler
   (`gt-factory-os/CLAUDE.md` §Shopify writes). Resolution: leave it, report it.

8. **`מוזה קוקטיילים בע"מ` matches every MUZA search you run.** Symptom: a customer record
   appears in a product query and looks like a stray item. Cause: it is a customer, under
   `U-010` (§2.4). Resolution: never archive a customer here.

## 8. Halt conditions

Inherited set cited in §0. Additions specific to this work:

- **Any statement would `DELETE`, `DROP`, or `UPDATE` `stock_ledger`** → STOP. Archival is
  a status change; corrections are reversal rows and are not part of this run.
- **Any statement would change a `private_core.components` row** → STOP. This directly
  violates Tom's instruction and the standard's first prohibition.
- **`rebuild_verifier()` returns non-zero at any point** → STOP, do not continue, surface
  with the value.
- **A MUZA item is found `ACTIVE`, or a MUZA order was placed after 2026-08-30** → STOP.
  The retirement is disputed or reversed, and this document no longer describes the world.
- **The migration slot changed between listing and writing** → `contract_failure`, halt
  (`gt-factory-os/CLAUDE.md` §Migrations).
- **The Shopify archival would run without Tom's word** → STOP. §6 D.
- **A stock quantity would be written without Tom's number** → STOP. §6 B.

## 9. Final report

In Hebrew, concise:

1. What is now true that was not true this morning, end to end.
2. Each done-condition D1–D8, ✅ or ❌, with the query output that proves it. No partial
   credit.
3. The numbers: items archived · mappings retired · BOM heads archived · Shopify products
   archived · **components touched (must be 0)** · ledger rows before and after ·
   `rebuild_verifier()` · coverage before and after with the §3.4 caveat.
4. The artifacts: the manifest path · the migration and its test · the PR · the
   `catalog-truth.md` entry · the `CURRENT_STATE.md` line.
5. What is still Tom's (§6) and what is genuinely unfinished, including every `UNRESOLVED`
   opened — the stock decision (§6 B) will still be open unless he answered it.
6. The single next action.

Then stamp this file `SHIPPED` with pointers, or `SUPERSEDED by <path>`, or
`ABANDONED — why`.

If anything is not ready, say so first and plainly. Per
`gt-factory-os-production-brain/CLAUDE.md` §Evidence: "it should work" is not evidence.
