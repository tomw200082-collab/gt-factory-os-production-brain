# Existing-customer growth plan — method of record

**Status:** SHIPPED 2026-08-30. Data: `docs/analytics/existing-customer-growth-2026-08-30.json`.
Engine: `gt-factory-os/scripts/sales-report/{growth_plan,growth_lists,growth_scripts,verify_growth,build_growth_artifact}.py`.
Evidence: `Sales-Machine/evidence/2026-08-30-existing-customer-growth.md`.
Source masterprompt: `2026-08-30 existing customer growth masterprompt` (Tom, pasted 2026-08-30).

Volatile figures live in the artifact and in the dated JSON, never in this file.
This file is the **method** — the rules a future re-run must reproduce.

## Window and money basis

Trailing 12 months, Israel clock, `2025-09` → `2026-08` (the current month is included;
it is the freshest signal a call plan has). Every ₪ is the stored ex-VAT Shopify price,
identical to `build_facts.py`. Gross profit = ₪ × 0.809, the 48-drink average margin from
`docs/pricing/2026-08-27_COST_MODEL.md`.

## Gate: the fact table is rebuilt and reconciled before a single row is written

The five correctness gates of `Sales-Machine/recipes/sales-report.md` run first. A growth
plan built on an unreconciled fact table is a list of confident wrong numbers.

## Population

Status uses the locked definitions in
`docs/pricing/MASTER_PROMPT_customer_product_tracker.md` §4, with one implementation
detail taken from the live tracker rather than reinvented: **an "order" is a distinct
order day**. Wholesale accounts routinely book several orders on one day; counting each
separately collapses the median interval to 1–2 days and reports a customer who ordered
last week as churned. `docs/analytics/customer-product-tracker-2026-08-06.json` already
de-duplicates by day (`days_list`), and reproducing that is what keeps this plan from
publishing a competing definition of churn.

- `live` = active + at-risk. Thin-history accounts (fewer than 3 order days) are excluded
  from the opportunity engine entirely — better to miss a row than to send Tom into a call
  built on two orders.
- Distributors and wholesalers are removed from **every** peer statistic before anything
  is computed. Rule: the Shopify `distributor` tag, **or** ≥₪250K in the window at ≥10×
  the archetype median across ≥5 families. The revenue floor is what separates them from
  the largest true venue; it was checked against Shopify addresses on 2026-08-30.
  Their identification is `inferred` and Tom confirms the names.

## W1 · Archetype — derived from the account's own purchase mix

```
BAR       = SANGRIA MUZA MARGARITA COSMO ARAK + the historic cocktail/mixer buckets
SPECIALTY = MATCHA HOJICHA UBE SMOOTHIE BUBBLES
TEA       = DETOX FRESH NAMASTEA CALM REVIVE ENERGY CONSCIOUSNESS DESERTEA
            AMERICAN "ELITA STRAWBERRY DETOX" + the historic tea buckets

bar_share ≥ 0.35                       → BAR-LED
specialty_share ≥ 0.35                 → SPECIALTY-LED
tea_share ≥ 0.75 and bar_share < 0.10  → TEA-ONLY
otherwise                              → MIXED
```

The denominator is drink revenue only. Packaging, shipping, deposits and the visible
no-SKU bucket say nothing about a menu. An account within 3 points of a threshold, or
under ₪3,000 of drink revenue, is flagged `low_confidence` — a wrong confident label sends
a wrong script into a real conversation.

## W2 · Chain roll-up — three tiers of certainty, and the third is not a merge

| Tier | Basis | Treatment |
|---|---|---|
| `tag` | Shopify chain tag, taxonomy Tom-approved 2026-08-24 | merged |
| `entity` | the same legal entity name in every branch record, or a Tom-approved override | merged |
| `brand` | the same trading brand across different legal entities (franchise) | **grouped for call planning only** — one brand, one conversation. Not an identity merge, not a revenue attribution. Flagged on the row; listed for Tom under `U-010` |

Anything weaker — a shared holding-company prefix, a shared street name, a generic word
— is deliberately not grouped, and the rejected candidates are recorded in the JSON
(`meta.not_grouped`). A wrong merge hides a real gap behind another branch's orders.

## W3 · Two gap types, computed separately, ranked together

Both require at least **8 buyers** in the peer cell. A median over fewer is an anecdote.

**Depth** — the account buys family `f` and under-buys it:

```
expected = med_share(archetype, f) ÷ Σ_{g ∈ owned} med_share(archetype, g) × rev12
EV       = min(expected − actual, p90_spend(archetype, f) − actual)     [emit if actual < 0.5 × expected]
```

The renormalising denominator is not decoration. Peer median shares are computed over
*buyers* of each family, so they sum well past 100%: an account carrying twelve families
sits below the median on all twelve by construction. Without the denominator the engine
punishes breadth as if it were depth and manufactures nine gaps for the best customers.

**Breadth** — the account has never bought `f`, and at least 30% of its archetype has:

```
size_index = rev12 ÷ median(rev12 of the archetype)
EV         = min(attach(archetype, f) × med_spend(archetype, f) × size_index,
                 p90_spend(archetype, f))
```

The p90 cap is the honesty clause: the promise never exceeds what the 90th-percentile
comparable venue actually pays for that family. A linear `size_index` alone extrapolates a
₪1,300 median into a number no real peer has ever spent.

**Ranking:** `score = EV × conversion_weight` — depth 1.0 · breadth into a family with
co-purchase lift ≥ 1.5 from something the account already buys 0.7 · breadth otherwise 0.4.
**These weights are a modelling assumption, graded `inferred`, not a measurement.** They
are printed next to the ranking so a future session can correct them from outcomes.

**Family → SKU:** a depth ask names the SKU the account already orders — the ask is "more
of what you have". A breadth ask names the format most adopted by that archetype's buyers.
Both are filtered to SKUs present in the price list and never a negative record in
`docs/warehouses/catalog-truth.md`.

## W4 · Two registers

Call list: exactly 20 entities, one row per chain, distributors excluded. Each row carries
the opener, the push with its peer basis, the close, two objections answered from that
account's own history, and a fallback ask. WhatsApp: every remaining opportunity entity,
one message under 45 words that survives being read with no reply.

Every close lands on lever (a) — adding to a delivery that is already going out — or lever
(b) — fifteen minutes with the barista. **A close on price, a discount or a free sample is
a violation and must be rewritten** (Tom, S3, 2026-08-30).

## W5 · The drink layer

Drinks, doses, ingredient cost, recommended price and margin come from
`docs/pricing/2026-08-27_cost_model.py` and
`.claude/skills/drinks-pricelist/drinks_final_figures.json`. A family is matched to its
drinks by the botanical its SKU code names; a drink whose name does not name its botanical
unambiguously is left unassigned rather than guessed.

**Cocktail bases (SANGRIA, MUZA, MARGARITA, COSMO, BUBBLES) have no drink page and no
documented preparation.** The products catalog excludes cocktails by Tom's own scope
decision of 2026-08-05. Those rows say so on their face and name a fallback push that does
have a drink. Nothing is invented — open as `U-014`.

The dose card is the model's ingredient list per 350 ml cup, not a barista SOP. The order
of operations is not documented anywhere in GT, and this plan does not make one up.

## W6 · Distributor track

One page, no script, no ₪ promise: lines carried, lines not carried, and what a line review
would need. Their volumes are negotiated, not modelled.

## Boundaries this plan operates under

- Nothing was sent to any customer. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`.
- Read-only against Shopify, Postgres and the repos. No write to any production system.
- factory-os core untouched.
- **Contact detail never enters git.** The committed JSON carries account keys and figures
  only, and a self-check asserts it. The published artifact carries no phone numbers
  either — a hosted page with hundreds of customer numbers is data egress; the
  phone-carrying build is delivered to Tom as a local file instead.
- Churn is the existing tracker's. This plan consumes its definitions and never publishes
  a competing one.

## Re-running

```
cd gt-factory-os/scripts/sales-report
# 1 Shopify bulk operation -> raw/orders.jsonl, ShopifyQL month anchor -> shopifyql_month.json
python3 build_facts.py && python3 analyze_bridge.py     # gate 1 must PASS
python3 growth_plan.py && python3 growth_lists.py && python3 growth_scripts.py
python3 verify_growth.py                                # D1-D8, exits non-zero on any failure
GT_SCRATCH=<scratch> python3 build_growth_artifact.py               # with phones, local only
GT_SCRATCH=<scratch> GT_PHONES=0 python3 build_growth_artifact.py   # publishable build
```
