# MASTERPROMPT — the existing-customer growth plan GT can execute next Monday

**STATUS: SHIPPED 2026-08-30.**

> Executed in full on 2026-08-30 against a fresh Shopify pull (Bulk Operation
> `8004166713585`, 33,606 objects). All five correctness gates passed; D1–D8 all met and
> machine-checked by `gt-factory-os/scripts/sales-report/verify_growth.py`.
>
> - Artifact: https://claude.ai/code/artifact/196e8803-7c72-4c83-8637-e4d821d03f44
> - Method of record: `docs/plans/2026-08-30_existing_customer_growth.md`
> - Data: `docs/analytics/existing-customer-growth-2026-08-30.json`
> - Evidence: `Sales-Machine/evidence/2026-08-30-existing-customer-growth.md`
> - Engine: `gt-factory-os/scripts/sales-report/growth_*.py`
>
> §2 was rebuilt from the re-run, as §2's own shelf-life rule directs. The re-run's
> populations and attach rates differ from the 2026-08-25 snapshot quoted below; the
> method in §4 did not depend on them. Read §2 below as the scoping session's reading,
> not as current truth — current truth is the evidence snapshot.
>
> Three findings the plan did not anticipate, recorded because they changed the output:
> the tracker's status definition only behaves if an "order" means a distinct order day;
> peer median shares sum past 100% and depth must renormalise or it punishes breadth; and
> GT's cocktail bases have no drink page and no documented preparation anywhere, so 22
> rows state that instead of inventing one (`U-014`).

> **Usage:** paste this entire file as the first message of a fresh session with the
> Shopify MCP connector, the Green Invoice credentials, the Supabase MCP connector, and
> the repos `gt-factory-os-production-brain`, `gt-factory-os` and `Sales-Machine`
> attached. It takes GT from "we have a churn radar and a naive whitespace list" to
> "a named, ranked, scripted action plan for growing revenue inside the customers we
> already have." It halts for Tom only where §6 says so; §6 is that complete list.
>
> **Provenance:** written 2026-08-30 by a session that read the live tracker artifact
> `f7c03c2f-81d1-47a8-b90f-9656bec58ab7` (data block generated `2026-08-25T13:05`,
> `as_of` 2026-08-25), re-derived every aggregate in §2 from that block, and read
> `Sales-Machine/CLAUDE.md`, `Sales-Machine/CURRENT_STATE.md`,
> `Sales-Machine/recipes/{whitespace,account-value,sales-report}.md`,
> `docs/pricing/2026-08-27_COST_MODEL.md`,
> `docs/pricing/MASTER_PROMPT_customer_product_tracker.md` and
> `docs/warehouses/catalog-truth.md`.
> Tom answered four scoping questions on 2026-08-30; his answers are §1.1.
> Authority: `gt-factory-os-production-brain/CLAUDE.md` → `EXECUTION_POLICY.md` →
> `Sales-Machine/CLAUDE.md` — cited below, never copied.
>
> **Shelf life:** §2 is presumed wrong if pasted after 2026-09-20. Re-run §2.5 first.
> If the re-run moves total 12-month revenue by more than 5%, or moves any archetype
> attach rate in §2.2 by more than 8 percentage points, **rebuild §2 from the re-run and
> keep going** — the method in §4 does not depend on the specific numbers. If the
> Shopify or Green Invoice pull fails outright, **halt and surface**: a growth plan
> built on a partial pull silently drops customers, and a customer who is missing from
> the plan is a customer nobody calls.

---

## 0. How to work

- **Who you are here:** one Claude session, running to completion. You hold read access
  to Shopify (MCP), Green Invoice (API credentials in session env), Postgres/Supabase
  (MCP, project `rvadsozabmxkkrktwgnv`, schema `private_core`), and the four repos. You
  decide the analysis, the segmentation, the ranking and the scripts alone. You decide
  nothing about price, nothing about a customer-facing send, and nothing that writes to
  a production system.
- **Read first, in this order:** `gt-factory-os-production-brain/CLAUDE.md` ·
  `Sales-Machine/CLAUDE.md` · `Sales-Machine/CURRENT_STATE.md` ·
  `Sales-Machine/recipes/whitespace.md` ·
  `docs/pricing/MASTER_PROMPT_customer_product_tracker.md` §§1–6 (the data contract for
  Shopify, Green Invoice and the VAT trap — do not re-derive it) ·
  `docs/warehouses/catalog-truth.md` (what GT actually sells) ·
  `docs/pricing/2026-08-27_COST_MODEL.md` (margin, for ranking).
- **Authority:** `gt-factory-os-production-brain/CLAUDE.md` §Source of truth and
  §Authorization; `Sales-Machine/CLAUDE.md` §"The 7 truth rules" and §"Hard boundaries".
  Where this document and an authority doc disagree, the authority doc wins and this
  document is wrong.
- **Halt conditions, evidence standard, git discipline:** inherited from
  `gt-factory-os-production-brain/CLAUDE.md` §Stop conditions and §Evidence, and
  `Sales-Machine/CLAUDE.md` §"Stop conditions". Deltas specific to this work are in §8.
- **The standard.** Tom's words for the plan, verbatim (2026-08-30):
  `פעולות קונקרטיות — למי ולמה, מה לדחוף בשיחה. ממש מדוייק בצורה קיצונית ומפורט.`
  Translated into three checkable prohibitions:
  1. **No row without a named account, a named SKU, and a reason drawn from that
     account's own order history.** "Consider offering matcha" is a violation; "they
     bought `DETOX 1000ml` 14 times in 12 months and have never bought a matcha SKU"
     is not.
  2. **No dropped decimal into a promise.** Every ₪ figure on a row states which
     population it was computed from and over what window. A number whose peer group
     is not stated is a violation.
  3. **No row Tom cannot act on inside two minutes.** If the row does not say what to
     say, it is not a row.
- **Language:** this document is in English because that is the register you reason best
  in; data literals stay in their own script, in backticks, and are never translated.
  **Output language: Hebrew, concise.** Short sentences, no preamble, no restating the
  question. The plan artifact and every customer-facing script are Hebrew with
  `dir="rtl"` — they will be read on a phone in the field and spoken to Israeli
  customers. Your progress notes to Tom in chat are Hebrew too.

---

## 1. Mission and definition of done

**One testable sentence:** produce a ranked, evidence-backed, per-account growth plan
that tells Tom exactly which existing customers to approach, which specific SKU to push
at each, why that SKU and not another, and what to say — with 20 phone-call accounts and
a WhatsApp track for the rest.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Every live customer is classified into exactly one archetype, derived from their own purchase mix | Run the classifier over the customer set; any customer with 0 or ≥2 archetypes, or any live customer absent from the output, fails D1 |
| D2 | Every opportunity row carries all six of: account · SKU (not just family) · archetype · the peer statistic it was derived from · ₪ expected annual value · the sentence to say | Sample ten rows at random; any row missing any of the six fields fails D2 |
| D3 | Every ₪ figure is reproducible from the fact table by a query printed next to it | Re-run the printed query for five random rows; any figure that does not reproduce within ±2% fails D3 |
| D4 | Chains are ranked as one decision, not N branch rows | Search the call list for two rows that belong to one chain and carry the same SKU push; any such pair fails D4 |
| D5 | The call list is exactly 20 accounts and the WhatsApp list covers every remaining opportunity account | Count both lists; overlap, or an opportunity account in neither, fails D5 |
| D6 | Every push names the drink it becomes and how the venue prepares it | Any row whose push is a SKU with no drink and no prep line fails D6 |
| D7 | The plan is published as a Hebrew RTL artifact and its underlying data is committed as dated JSON under `docs/analytics/` | Open the artifact URL; `git log` the JSON path. A missing either fails D7 |
| D8 | Nothing was sent to any customer | `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is still `false`; no Shopify, Green Invoice or messaging write appears in the session log |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

Tom decided these on 2026-08-30. They are inputs, not questions.

| # | Decision | Consequence for you |
|---|---|---|
| S1 | **Archetype is derived automatically. No approval gate.** | Derive it from purchase mix (§4 W1). Do not build a review queue, do not ask Tom to confirm rows one by one. Publish the derivation rule so a wrong classification is visible and fixable later. |
| S2 | **Execution split: phone calls to the 20 largest opportunities, WhatsApp to everyone else.** | Two script registers, not one. The call script is a conversation with branches; the WhatsApp script is one message that survives being read without a reply. |
| S3 | **The only two levers are: (a) attach the new item to an order that is already shipping, (b) a call plus preparation guidance. No free samples. No trial price. No discount.** | Every script closes on "I'll add it to Thursday's delivery" or on "I'll show your barista how to make it." A script that closes on a price concession is a violation of S3 and must be rewritten. |
| S4 | **The three largest accounts are distributors / wholesalers, not venues.** Identify them from the fact table by the pattern in §2.3. | Exclude them from every peer statistic — they distort attach rates and ₪/buyer for the whole base. Give them a separate, short track: a product-line review, not a sales call. |

---

## 2. Ground truth — measured 2026-08-30 from the 2026-08-25 snapshot; re-verify at boot

Every number below was recomputed by this session from the tracker artifact's embedded
data block (`generated_at` `2026-08-25T13:05`). They are the *shape* of the base, not
the base itself — §2.5 regenerates them.

### 2.1 What already exists and works

- **A verified fact table pipeline.** `gt-factory-os/scripts/sales-report/` —
  `build_facts.py`, `bulk_query.graphql`, `build_report.py`, `build_gate_page.py`. Its
  method, taxonomy and five correctness gates are locked in
  `Sales-Machine/recipes/sales-report.md`; the taxonomy was Tom-approved 2026-08-24.
  **Use this pipeline. Do not build a second one.**
- **A live tracker artifact** with churn radar, movement, product concentration and a
  first-generation whitespace block. Its whitespace is the thing this plan replaces —
  see §3.1.
- **A cost model** (`docs/pricing/2026-08-27_COST_MODEL.md` §Results, verified 2026-08-27):
  48 drinks, margin range 76%–87%, average 80.9%. Treat incremental
  revenue as ≈0.8 gross profit when ranking.
- **A catalog truth file** listing what GT actually sells, including negative records —
  products that are `ACTIVE` in Shopify but are not sold
  (`docs/warehouses/catalog-truth.md`). Never push a negative record.

### 2.2 The numbers

Base, from the 2026-08-25 snapshot:

```
customers with any history                 569
customers with 12-month revenue > 0        559
12-month revenue total                     ₪5,787,830
top 144 customers (25.8%)                  80% of revenue
status split       active 254 · new 82 · thin-history 122 · at-risk 28 · churned 83
live = active + at-risk                    282   ₪4,815,457
live venues, after removing 3 distributors 279   ₪3,850,890
```

Archetypes, derived by revenue mix over the 279 live venues (rule in §4 W1):

```
archetype        n     12-mo revenue     avg/account
BAR-LED          24    ₪  697,789        ₪29,075
SPECIALTY-LED    72    ₪1,072,974        ₪14,902
TEA-ONLY        142    ₪1,189,919        ₪ 8,380
MIXED            41    ₪  890,208        ₪21,712
```

The number that reorganizes the work — **matcha, by archetype**:

```
archetype        attach rate    median ₪/buyer/yr
SPECIALTY-LED       94.4%           ₪ 7,027
MIXED               87.8%           ₪ 2,856
BAR-LED             20.8%           ₪20,068
TEA-ONLY            16.2%           ₪ 1,511
```

Family attach across the 282 live accounts, and revenue per buyer:

```
DETOX          77.3%   ₪ 4,712      SANGRIA        16.3%   ₪ 6,907
FRESH          77.3%   ₪ 2,577      MUZA           14.5%   ₪ 7,574
NAMASTEA       61.7%   ₪ 3,507      NONOMIMI(UBE)  13.8%   ₪   612
CALM           50.7%   ₪ 1,596      MARGARITA       6.4%   ₪ 4,975
MATCHA         47.2%   ₪ 6,797      TAPIOCA         3.2%   ₪ 1,718
REVIVE         39.0%   ₪ 2,725      COCKTAIL        2.1%   ₪12,067
ENERGY         36.5%   ₪ 1,448      ODK            23.4%   ₪ 1,967
CONSCIOUSNESS  34.0%   ₪ 1,277      DESERTEA       18.1%   ₪ 1,897
```

Co-purchase lift among live accounts, `P(B|A) ÷ P(B)`, minimum 20 A-buyers — the
strongest pairs:

```
MUZA    → MARGARITA   P=41.5%  base= 6.4%  lift 6.50
MUZA    → COCKTAIL    P=12.2%  base= 2.1%  lift 5.73
SANGRIA ↔ MUZA        P=56.5% / 63.4%      lift 3.89
DESERTEA→ TAPIOCA     P=11.8%  base= 3.2%  lift 3.69
ODK     ↔ NONOMIMI    P=28.8% / 48.7%      lift 2.08
MATCHA  ↔ NONOMIMI    P=24.8% / 84.6%      lift 1.79
MUZA    → REVIVE      P=70.7%  base=39.0%  lift 1.81
```

Opportunity size, two ways of counting, both computed here:

```
size-peer breadth gaps (missing family)      2,492 cells   ₪3,599,330   ← inflated, see §3.1
size-peer depth gaps (has it, under-buys)      328 cells   ₪1,291,672
archetype-conditioned breadth, ≥30% attach     783 cells   ₪  505,193   ← defensible
```

Product facts that change what you push:

- `Shizuoka Ceremonial Matcha Bag 500g` — ₪418,893 / 12 months, 174 buyers, trend +73.7%.
- `Shizuoka Ceremonial Matcha 22x18g.bags` — ₪281,784, 75 buyers, trend +355.5%.
- `Maruei Ceremonial Matcha` (both formats) — trend −92.6% and −88.6%. **This is a
  within-family substitution to Shizuoka, not customer loss.** Do not build a win-back
  around it.
- `Ube Powder 1 KG` — ₪18,280, 56 units, 38 buyers; `Nonomimi Ube Powder 500g` — ₪13,635,
  20 buyers (2026-08-25 snapshot, products block). At the ₪612/buyer/year in §2.2, ube is
  a **wedge and a signal**, not a revenue line — see §3.4.
- Six SKUs draw their entire 12-month revenue from one buyer (2026-08-25 snapshot,
  products block, `share` = 100), including a matcha can that `catalog-truth.md` records
  as a negative record per Tom 2026-08-06. Single-buyer
  concentration is a de-risking target, not a growth target.

### 2.3 What is NOT built

- **No archetype / venue-type field exists anywhere.** Not in Shopify tags, not in
  Postgres, not in `Sales-Machine/knowledge/`. You derive it (§4 W1). This is the single
  largest missing input and the reason the existing whitespace list over-promises.
- **No chain map exists as data.** `Sales-Machine/recipes/whitespace.md` requires one and
  records it as blocked on an interview that has not happened
  (`CURRENT_STATE.md`, Phase 2, "NOT STARTED"). The sales-report recipe carries an
  approved chain-tag list — reuse it, and derive the rest by the rule in §4 W2.
- **No distributor flag.** S4 tells you the three accounts exist; the fact table does not
  say so. Identify them by pattern: order count and revenue an order of magnitude above
  their archetype peers, a basket spanning most families, and no single-venue address.
  Record the identification as `inferred` per `Sales-Machine/CLAUDE.md` rule 1.
- **No ordering-contact truth.** B2B records use placeholder login emails; where the real
  ordering contact lives is open as `U-004` in `Sales-Machine/CURRENT_STATE.md`. Phone
  numbers in the tracker are the working channel. Do not assert an email is correct.

### 2.4 Known-broken, adjacent, out of scope

- **`U-009`** — an account with 58 orders and ₪0.00 `amountSpent`. Shopify's
  `customer.amountSpent` and `average_order_value` are banned by
  `Sales-Machine/recipes/sales-report.md`, section `בסיס כספי`. Compute every total from the
  fact table.
- **`U-006`** — off-Shopify revenue through Green Invoice is not fully mapped. An account
  that looks small in Shopify may not be small. Flag, do not conclude.
- **The April 2026 gap** — ₪269,006 Shopify returns against ₪138,604 Green Invoice
  credits, ₪130,402 unexplained (2026-08-25 snapshot, `exceptions.april_gap`). Tracked. Do not chase it
  here.
- **The lead pipeline** (`sales_core`, Make intake, the `/apps` sales workspace) is a
  different track and is new-customer work. Out of scope.

### 2.5 Re-verification block

Run all three. They regenerate §2.2 end to end.

```
# 1 — rebuild the fact table (month × customer × SKU). Method and the five
#     correctness gates: Sales-Machine/recipes/sales-report.md
cd gt-factory-os/scripts/sales-report && python3 build_facts.py
#     Gate 1 must close ≤0.5% against ShopifyQL total_sales for the full window.
#     Gate 5 must be 3/3 on manual re-pull. Do not proceed on a failed gate.
```

```sql
-- 2 — catalog cross-check: which sellable items have no Shopify mapping.
--     Source: gt-factory-os/CLAUDE.md §Shopify writes (the only coverage check that matters)
SELECT i.item_id FROM private_core.items i
WHERE i.status='ACTIVE' AND i.supply_method IN ('BOUGHT_FINISHED','MANUFACTURED','REPACK')
  AND NOT EXISTS (SELECT 1 FROM private_core.integration_sku_map m
    WHERE m.item_id=i.item_id AND m.source_channel='shopify'
      AND m.approval_status='approved' AND m.mapping_status='active');
```

```
# 3 — Green Invoice document-type census for the window, BEFORE deciding what counts
#     as revenue. Client: gt-factory-os/api/src/integrations/greeninvoice/client.ts
#     POST /v1/documents/search — count by `type`, credit notes negative.
#     Contract and the paging rule: docs/pricing/MASTER_PROMPT_customer_product_tracker.md §2.1
```

---

## 3. What the hard part actually is

The visible deliverable is a list. The list is easy. Six things make it wrong, and each
one is a different mistake.

### 3.1 The peer group is the bug, and it is already shipped

The existing whitespace block ranks by *"customers of similar size buy this family"*.
Size is not why a venue buys a product. A restaurant with a bar and a bakery with a
counter can bill the same and share nothing on the menu.

What that costs, measured: the top of the existing whitespace list is dominated by
`SANGRIA` pushed at cafés, with peer rates of 43–54% and potentials of ₪8,522–₪25,161.
Sangria attach across all live accounts is 16.3% — the 43–54% comes from the size band,
not from anyone comparable. And the direction is not the only error; the magnitude is
worse. Per §2.2, a `TEA-ONLY` venue that adds matcha buys **₪1,511 of matcha a year**;
the same row priced off size-peers promises the all-base ₪6,797 — **4.5×** the truth.

**Consequence for ordering:** replace the peer group with archetype × size. Total
defensible opportunity drops from ₪3.6M to ₪505,193, and the *ordering* changes
completely — which is the point. A list that over-promises is worse than a short list,
because Tom spends a real call discovering the number was fiction, and stops trusting
the next one.

### 3.2 Depth beats breadth, and only depth is frictionless

Two different asks are being collapsed into one word.

- **Breadth** — "add a family you have never bought." Needs a menu decision, a barista
  who can make it, and shelf space. Slow.
- **Depth** — "you already sell this; you buy half what comparable venues buy." Needs
  nothing. No menu change, no training, no new listing. It rides the order that is
  already shipping — which is exactly lever (a) in S3.

Measured on size-peers: breadth ₪3,599,330 across 2,492 cells, depth ₪1,291,672 across
328 cells. Depth is a third of the money in an eighth of the rows, and every depth row
is a one-sentence ask.

**Consequence for ordering:** compute both. Rank depth rows above breadth rows at equal
₪, because the conversion rate is not equal and pretending it is corrupts the ranking.

### 3.3 A chain is one decision, and the list will not know that

The largest chain in the base runs 11 branches plus a central-buying entity. Their
baskets are near-identical, which is the signature of a chain-level menu, not eleven
independent choices. Two whole families are at **0 of 12** branches; two more are at
**1 of 12**. Matcha reaches almost every branch — but at roughly **half** the per-branch
matcha spend of comparable venues, which is a depth gap replicated eleven times by one
decision made once.

Three more multi-branch groups sit in the base with the same signature. One runs 15
doors on a three-family basket. One runs 4 doors on the full tea line with **zero
matcha**. One runs 9 doors with **no tea at all**.

**Consequence for ordering:** if you rank branches, the call list becomes one chain
repeated, Tom makes eleven calls to people who cannot decide, and the one person who can
is never called. Roll chains up to the deciding entity, rank the roll-up, and carry the
branch evidence *into* that one conversation — sister-branch adoption is the strongest
argument available and it only exists at the roll-up.

### 3.4 Ube is a signal, not a revenue line — and Tom asked about it directly

Ube reads like an opportunity: 13.8% attach in §2.2, so most of the base "doesn't buy
it." But at the ₪612 per buyer per year in §2.2, the whole gap is worth roughly ₪150K
gross across the entire base before any conversion assumption — and it will not convert into a venue with no use for it.

What ube actually is: 84.6% of ube buyers also buy matcha (lift 1.79) and 48.7% also buy
`ODK` purée (lift 2.08). Ube marks the venue that builds *composed, coloured,
photographed* drinks. That venue is worth far more than its ube line.

**Consequence:** treat ube two ways, never one. As a **wedge** — a low-commitment ask
into a specialty venue, where lever (b) does the work because the objection is "we don't
know what to do with it." And as a **classifier** — an account buying ube and not matcha
is a strong matcha target, and that inference is worth more than the ube order.

Say the same about `TAPIOCA` and `COCKTAIL`: tiny lines, high lift, real signal.

### 3.5 The three largest accounts are a different business

Per S4 the top three accounts are distributors. They are ₪443K, ₪261K and ₪261K — over
20% of the base — and they sit inside every peer statistic distorting it. One of them
alone produces the four largest "opportunities" on any size-peer ranking, and every one
of those is a distributor line-listing negotiation, not a sales call.

**Consequence:** exclude them from every peer statistic before computing anything, and
give them a separate one-page track: which lines they carry, which they do not, what
that is worth, and what a line review would need. Do not put them on the call list —
they would consume four of the twenty slots and none of those four is a call.

### 3.6 Without a discount, the only currency is competence

S3 removes samples, trial pricing and discounts. What remains is (a) zero friction and
(b) knowing more about the customer's business than they expect.

That is not a weaker position, but it does force the plan into a shape most cross-sell
lists never reach: **for every push, the plan must carry the drink, not the SKU.** What
it becomes on their menu, how the barista makes it, what it sells for, what it costs
them per cup. The cost model gives the last two — margin 76%–87%, average 80.9%,
`docs/pricing/2026-08-27_COST_MODEL.md`.

**Consequence:** budget real work for the drink-and-prep layer (§4 W5). A row without it
fails D6, and in the field it fails harder — "we don't know how to make it" is the
objection lever (b) exists to answer, and it cannot be answered from a SKU list.

---

## 4. Workstreams

Run W1–W3 in order; they feed each other. W4 and W5 run concurrently once W3 lands.

### W1 — Archetype classifier

Build a deterministic classifier over the fact table. Start from the revenue-mix rule
this session validated, then improve it — it is a floor, not a ceiling.

```
BAR      = SANGRIA + MUZA + MARGARITA + COCKTAIL
SPECIALTY= MATCHA + NONOMIMI + ODK + TAPIOCA
TEA      = DETOX + FRESH + NAMASTEA + CALM + REVIVE + ENERGY + CONSCIOUSNESS + DESERTEA

bar_share ≥ 0.35                        → BAR-LED
specialty_share ≥ 0.35                  → SPECIALTY-LED
tea_share ≥ 0.75 and bar_share < 0.10   → TEA-ONLY
otherwise                               → MIXED
```

Improve it with evidence available in the systems, in this order of reliability:
Shopify customer tags · the trading name inside the parentheses of the company name
(`catalog-truth.md` shows GT's naming convention; the tracker masterprompt §5.3 shows
the parenthetical pattern) · `address1` for branch identity · order cadence and basket
size. **Do not use the company suffix as a signal** — `בע"מ` says nothing about a menu.

Every account lands in exactly one archetype (D1). Publish the rule and the counts.
Where the classifier is uncertain, emit `MIXED` and mark the row `low_confidence` — a
wrong confident label sends a wrong script into a real conversation.

**Acceptance:** closes D1.

### W2 — Chain roll-up

Adopt the approved chain tags from `Sales-Machine/recipes/sales-report.md`, section
`טקסונומיה` item 6, verbatim, including the manual assignments approved 2026-08-24. Extend by:
identical basket signature across accounts, shared normalized company name, shared
trading name in parentheses. Follow the matching order in
`docs/pricing/MASTER_PROMPT_customer_product_tracker.md` §5, and honour its rule —
**below full certainty, do not merge; list it as an exception.** A wrong merge hides a
real gap behind another branch's orders.

For each chain emit: branch count · total 12-month revenue · the family matrix
(branch × family) · families at 0 branches · families at 1–2 branches · families present
everywhere but below archetype-median depth.

**Acceptance:** closes D4.

### W3 — The opportunity engine

Two gap types, computed separately, ranked together.

**Breadth gap** — account does not buy family `f`:

```
attach(archetype, f)  = share of that archetype's accounts buying f
median_spend(arch, f) = median annual spend on f among that archetype's buyers
size_index            = account_rev12 ÷ median(rev12 of its archetype)
EV_breadth            = attach × median_spend × size_index
```

Emit only where `attach ≥ 0.30`. Below that the family is not characteristic of the
archetype and the row is a guess wearing a number.

**Depth gap** — account buys `f` but under its archetype's norm:

```
expected  = median_share(archetype, f) × account_rev12
EV_depth  = expected − actual,  emitted where actual < 0.5 × expected
```

Rank by `EV × conversion_weight`, with `conversion_weight`: depth 1.0 · breadth into a
family with co-purchase lift ≥ 1.5 from something the account already buys 0.7 ·
breadth otherwise 0.4. These weights are an explicit modelling assumption, not a
measurement — label them as such per `Sales-Machine/CLAUDE.md` rule 1 (`inferred`), and
print them next to the ranking so a future session can correct them from outcomes.

Convert to gross profit using the 80.9% average margin
(`docs/pricing/2026-08-27_COST_MODEL.md`) so Tom's ranking is by money he keeps.

Then resolve **family → SKU**. A family is not an order. Choose the SKU by what
comparable accounts in the same archetype actually buy, prefer the 1000ml format where
the archetype's buyers do, and never propose a SKU listed as a negative record in
`docs/warehouses/catalog-truth.md`.

**Acceptance:** closes D2, D3.

### W4 — The two call lists

**Call list — exactly 20 rows.** Chains occupy one row each. Distributors are excluded
(their track is §4 W6). Each row carries:

- account · archetype · 12-month revenue · order cadence and days since last order
- what they buy now, and what they have never bought
- **the one push** — SKU, why this account, the ₪ and its peer basis
- **the opener** — one sentence naming something true about *their* orders
- **the ask** — closing on lever (a) or (b) from S3, never on price
- **two objections and the answers**, drawn from that account's own history
- **the fallback ask** if the push is refused, so the call still moves

**WhatsApp list — every remaining opportunity account.** One message, at most 45 words,
Hebrew, that reads as a supplier who noticed something rather than a campaign. It states
the observation, the suggestion, and one question that can be answered with one word. It
must survive being read with no reply — no "did you get my message" follow-up is part of
this plan.

**Acceptance:** closes D5.

### W5 — The drink-and-prep layer

For every distinct SKU that appears as a push, produce: the drink it becomes · the
preparation in 3–5 steps a barista can follow · the ingredient cost per cup and the
suggested menu price from the cost model · one sentence on why this venue's customers
order it. Source the drinks from `docs/pricing/` (the 48-drink catalogue and
`.claude/skills/drinks-pricelist/drinks_final_figures.json`). **Do not invent a drink and
do not invent a price** — if a push has no drink in the catalogue, say so on the row and
push a different SKU.

**Acceptance:** closes D6.

### W6 — The distributor track

One page, three accounts (S4). Per account: lines carried · lines not carried · what the
gap is worth at their volume · what a line review would need. Frame as a commercial
conversation, not a call script. No script, no ₪ promise — their volumes are negotiated,
not modelled.

### W7 — Publish

Hebrew RTL artifact, per `docs/pricing/MASTER_PROMPT_customer_product_tracker.md` §7 —
that section is the house standard for a Tom-facing artifact (mobile first, everything
inline, no CDN, theme-aware, sortable tables, stable title and favicon). Load the
`artifact-design` skill before writing it, and `dataviz` before any chart.

The artifact is a **worklist, not a report**: filter by archetype, by list (call /
WhatsApp), by chain; one row expands to the full script; a copy button per script.

Commit the computed data as dated JSON under
`gt-factory-os-production-brain/docs/analytics/`, and write a dated evidence snapshot to
`Sales-Machine/evidence/` per `Sales-Machine/CLAUDE.md` rule 2. **No phone numbers in
the committed JSON, the commit message, or the PR body** — see §8.

**Acceptance:** closes D7.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**

- **Sending anything to any customer.** No WhatsApp, no email, no Shopify draft order.
  The plan is written; the sending is not in this session (D8).
- **Prices, discounts, promotions.** Every customer has their own price
  (`docs/pricing/MASTER_PROMPT_customer_product_tracker.md` §1). You do not set one, and
  S3 removes price from the toolkit entirely.
- **The churn radar.** The existing tracker owns it. Use its status field; do not rebuild
  it and do not publish a competing definition of "churned".
- **New-customer work** — the lead pipeline, the `/apps` sales workspace, Make scenarios.
- **factory-os core** — `stock_ledger`, `balance_anchors`, `bom_*`, `items`,
  `components`. Read through curated views only
  (`Sales-Machine/CLAUDE.md` §"Hard boundaries").
- **The April 2026 reconciliation gap** (§2.4).
- **Fixing `U-003` pricing-tag semantics.** Note where it blocks a row; do not decode it.

---

## 6. Tom's part — the complete list, nothing else is his

**A. Confirm or correct the archetype rule after seeing the counts.** Per S1 you do not
gate on this — publish and proceed. Tom looks at four numbers and says whether the
population shape matches the customers he knows. One message, two minutes.

**B. Name the three distributors.** You identify them by the §2.3 pattern; Tom confirms
the names. Only he knows the trading relationship. Blocks W6 only — build everything
else while it is open.

**C. Approve any customer-facing send.** Not part of this plan. Flagged so nobody reads
the WhatsApp list as authorization: `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is `false`
and stays `false` (`Sales-Machine/CLAUDE.md` §"Hard boundaries").

**D. Resolve an identity collision, if W2 raises one.** `U-010` in
`Sales-Machine/CURRENT_STATE.md` holds four open ones. If W2 hits a fifth, add it to
`U-010` and carry on — do not guess a merge.

Everything not listed here is yours.

---

## 7. Landmines — do not rediscover these

1. **The existing whitespace list looks authoritative and is over-promising by ~4.5×.**
   Symptom: its top rows are large, specific and ranked, so reusing them feels safe.
   Cause: peer group is size, not venue type (§3.1). Resolution: recompute from the
   archetype-conditioned formula in W3. Do not reconcile the two lists — replace.

2. **A chain will eat your call list.** Symptom: eleven similar rows with similar pushes.
   Cause: branches ranked independently (§3.3). Resolution: roll up in W2 *before*
   ranking in W3, not after.

3. **Matcha looks like it is collapsing.** Symptom: `Maruei Ceremonial Matcha` at −92.6%
   and −88.6%. Cause: within-family substitution to Shizuoka, which is up +73.7% and
   +355.5% (§2.2). Resolution: read matcha at family level. A win-back campaign here
   would target customers who never left.

4. **Shopify's own money fields will lie to you.** Symptom: `customer.amountSpent` and
   `average_order_value` are right there and easy. Cause: the store is misconfigured
   `taxesIncluded=true @17%`, and `amountSpent` has documented anomalies including 58
   orders at ₪0.00 (`U-009`). Resolution: banned by
   `Sales-Machine/recipes/sales-report.md`, section `בסיס כספי`. Compute from the fact table;
   the only valid anchor is ShopifyQL `total_sales`.

5. **Never multiply or divide by 1.18 to reconcile Shopify against Green Invoice.**
   Symptom: two sources disagree and one scaling makes them agree. Cause: the VAT
   misconfiguration makes that scaling superficially plausible. Resolution:
   `docs/pricing/MASTER_PROMPT_customer_product_tracker.md` §6 — a disagreement is a
   finding to report, not a gap to close in code. VAT in Israel is 18%.

6. **A big Shopify result silently saves to a file instead of entering context.**
   Symptom: a query "worked" but the analysis covers fewer customers than expected.
   Cause: documented harness behaviour. Resolution: work the file with Python. Always
   check `rowCount` is strictly less than the `LIMIT` you asked for; equal means
   truncated (`…tracker.md` §2.2).

7. **`ACTIVE` in Shopify does not mean GT sells it.** Symptom: a push built on a real,
   live, purchasable SKU. Cause: `catalog-truth.md` carries negative records — Tom ruled
   on 2026-08-06 that specific `ACTIVE` products are not sold. Resolution: check every
   push SKU against `docs/warehouses/catalog-truth.md` before it reaches a row.

8. **Small tail products read as big opportunities.** Symptom: 86% of the base does not
   buy ube, so the "gap" looks enormous. Cause: the gap is counted in accounts, not
   shekels —
   ube is ₪612/buyer/year (§3.4). Resolution: rank every gap by ₪ × conversion weight,
   never by attach percentage. Use the tail products as classifiers.

9. **A chain's central-buying entity distorts its own branch matrix.**
   Symptom: one "branch" carries a family at eleven times the others and misses families
   all its siblings buy. Cause: it is a central-buying or retail entity, not a venue.
   Resolution: detect it in W2 (basket unlike every sibling, revenue an order of
   magnitude above them), split it out of the branch matrix, and record the split as
   `inferred`.

10. **Thin-history accounts will manufacture fake gaps.** Symptom: an account "missing"
    nine families. Cause: the 122 thin-history accounts in §2.2 have too few orders for
    any reliable statistic (`…tracker.md` §4 — fewer than three orders ever, classified
    `אין מספיק היסטוריה`). Resolution:
    exclude them from the opportunity engine. Better to miss a row than to send Tom into
    a call built on two orders.

---

## 8. Halt conditions

Inherited set cited in §0. Additions specific to this work:

- **A correctness gate fails** — the five gates in `Sales-Machine/recipes/sales-report.md`,
  section `חמשת שערי הנכונות` → STOP. A growth plan on an unreconciled fact table is a list of confident
  wrong numbers.
- **Any customer-facing write would occur** → STOP. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`
  is `false` and this session does not flip it.
- **A merge of two accounts is below full certainty** → do not merge; record as an
  exception (§4 W2) and carry on.
- **Phone numbers, addresses or exported customer rows would enter a commit, a PR body,
  or a screenshot** → STOP. Committed JSON carries account keys and figures; the artifact
  renders contact details at view time from the same source the tracker uses. This is the
  masterprompt skill's own rule and it binds the output as much as this document.
- **A push would require a price, a discount or a free sample to work** → the push is
  wrong under S3. Replace it, or drop the row and say why.

---

## 9. Final report

In Hebrew, concise:

1. What Tom can now open and act on, end to end.
2. Each done-condition D1–D8, ✅ or ❌, with its evidence pointer. No partial credit.
3. The numbers: accounts classified per archetype · chains rolled up · opportunity rows
   emitted · total ₪ and total gross profit at stake · the 20 call rows and the ₪ they
   carry.
4. The artifacts and where they are: artifact URL · the JSON path under `docs/analytics/`
   · the evidence snapshot path under `Sales-Machine/evidence/` · the PR.
5. What is still Tom's (§6) and what is genuinely unfinished — including every
   `UNRESOLVED` you opened.
6. The single next action.

Then stamp this file `SHIPPED` with pointers, or `SUPERSEDED by <path>`, or
`ABANDONED — why`.

If anything is not ready, say so first and plainly. Per
`gt-factory-os-production-brain/CLAUDE.md` §Evidence: "it should work" is not evidence.
