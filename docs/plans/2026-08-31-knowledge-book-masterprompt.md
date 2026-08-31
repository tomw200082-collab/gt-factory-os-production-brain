# MASTERPROMPT — GT's knowledge book: from a good page to the outbound database

**STATUS: LIVE — not yet executed**

> **Usage (Tom):** paste this whole file as the first message of a fresh Claude Code
> session with `Sales-Machine` and `gt-factory-os-production-brain` attached, and the
> Shopify connector on. It takes `ספר העבודה של GT` from a well-written HTML page to a
> versioned, citable knowledge base that an AI agent can answer a customer from. It halts
> for you only where §6 says.
>
> **Provenance:** written 2026-08-31. The book was read at
> `https://claude.ai/code/artifact/f0457ed1-6e3a-4180-9101-4fc7451d863a` and its published
> figures were checked line by line against `docs/warehouses/catalog-truth.md` (Tom-graded
> `2026-08-06`), `.claude/skills/drinks-pricelist/drinks_final_figures.json` (48 drinks,
> `_meta.date` `2026-08-27` — the current authority) and
> `docs/pricing/2026-08-27_COST_MODEL.md`. Three contradictions and one stale-file trap
> were found and are in §2.3 — they are the reason this document exists.
>
> **Shelf life:** §2 is presumed stale after 2026-09-21. Re-run §2.5. If a figure has
> moved since, **halt and surface it** — a wrong number in this book reaches a customer.

---

## 0. How to work

- **Who you are here:** one Claude Code session. You hold the two repos, Shopify Admin
  (read), Canva, Drive and the Artifact tool. You may restructure, reconcile and rewrite
  the book. You may **not** decide a price, a commercial term, or a claim GT makes about
  its products.
- **Read first, in order:** `Sales-Machine/CLAUDE.md` — **the seven truth rules are the
  operating manual for this entire job, not background** · `Sales-Machine/CURRENT_STATE.md`
  · `Sales-Machine/doctrine/decisions.md` · `Sales-Machine/knowledge/registry.yaml` ·
  `docs/warehouses/catalog-truth.md` · `docs/pricing/2026-08-27_COST_MODEL.md` · then the
  artifact in full.
- **Authority:** `Sales-Machine/CLAUDE.md` wins over everything here. Its rule 1 (every
  card carries source, date, authority grade), rule 2 (volatile data = recipe + dated
  snapshot, never a stored fact), rule 3 (unknowns are logged `UNRESOLVED`, never
  silently filled) and rule 4 (anything checkable is checked before it is written) are
  the acceptance criteria of this work. Halt conditions and the evidence standard are
  inherited, not re-authored.
- **The standard.** Tom called it `הדאטה בייס הכי משמעותי שלנו בחברה` — the most
  significant database in the company. Three prohibitions:
  1. **No number appears without a traceable source.** Not "approximately", not "from the
     catalog" — a file path or a query, and a date.
  2. **No answer is inferred into the answer bank.** `Sales-Machine/CLAUDE.md` rule 1:
     inferred is never policy. An answer with no approved source becomes a
     `העברה לאלכסנדר` row, which is a real answer — it just is not a claim.
  3. **Nothing GT does not sell appears in a customer-facing price list.**
- **Language:** this document is English; data literals stay in their own script in
  backticks. The book itself is and stays Hebrew. **Output language: concise Hebrew for
  Tom, concise English otherwise.**

---

## 1. Mission and definition of done

**One testable sentence:** the book's content lives as graded, dated, machine-readable
cards in `Sales-Machine/knowledge/`, every published figure reconciles to an approved
source, and the artifact becomes a rendering of that data rather than the data itself.

| # | Condition | The observation that would prove it false |
|---|---|---|
| D1 | Every price, cost and margin printed in the book matches `drinks_final_figures.json` (`2026-08-27`) and the ex-VAT TSV | Run the §2.5 reconciliation over all 48 drinks and the full price list. Any non-zero diff row = fail |
| D2 | Every knowledge card carries `source`, `date`, `authority` and `freshness`, and appears in `knowledge/registry.yaml` | A card file with a missing key, or a card absent from the registry |
| D3 | The answer bank exists as structured data with the five columns of the lead-system spec, **and the lead system reads the same file** | Two answer banks exist anywhere = fail. One source, two renderings |
| D4 | Every product printed in the price list has an active SKU, or is explicitly marked with why it is listed anyway | Join the price list to `catalog-truth.md`; a product that is a negative record and has no marking = fail |
| D5 | The book's `UNRESOLVED` items are the same items as `Sales-Machine/CURRENT_STATE.md` — no unknown lives in only one of them | Diff the two lists; any asymmetry = fail |
| D6 | An agent given only `Sales-Machine/knowledge/` can answer all 17 questions in the current answer bank, and correctly refuses the 5 forbidden ones | Run the §4.6 evaluation set. Any wrong answer, or any answered forbidden question, = fail |
| D7 | The artifact is republished to the same URL from the repo data, and states its build date and its source commit | Open the artifact; a figure that differs from the repo = fail |

Anything not on this list is out of scope unless Tom asks.

### 1.1 Settled — do not reopen

- **The book's prose voice is right.** It is direct, it leads with the per-serving number,
  it refuses to inflate the coffee comparison, and it says what it does not know. Do not
  rewrite it into marketing copy. You are fixing the data underneath it and adding what
  is missing — not restyling it.
- **The boundaries chapter (`הגבולות`) stands.** No allergen answers, no delivery dates,
  no unlisted prices, no discounts, no health claims. `Sales-Machine/CLAUDE.md` and the
  book agree; this is not a candidate for "improvement".
- **`DETOX` is a brand name and that is fine.** A sentence promising what a drink does to
  a body is not. That line is already drawn correctly.
- **Cost figures were rebuilt bottom-up on `2026-08-27`** from Tom's ingredient price
  list and **prices were deliberately not raised** (`docs/pricing/2026-08-27_COST_MODEL.md`
  — Tom: `"ב. אל תעלה את המחירים המומלצים יותר"`). Do not "correct" a margin by moving a
  price. Margin is derived: `profit = price/1.18 − cost`, `margin% = round(profit /
  (price/1.18) × 100)` — `_meta.formulas` in the authority file.

---

## 2. Ground truth — measured 2026-08-31; re-verify at boot

### 2.1 What the book already is

A single published HTML artifact, nine chapters: what we sell · the numbers · the price
list · 48 drinks · the lead · what we send · the answer bank (17 answers) · the boundaries
· what is not yet settled. It is shared with Tom, not owned by him — **publishing an
update requires the owner's session or the share pin moved.** Confirm this before
planning a republish.

### 2.2 What it is missing to be a database

- **No machine-readable layer at all.** It is HTML. An agent asked "what is the shelf life
  of an opened bottle" must parse a web page and hope. There is no card, no key, no grade,
  no date — so nothing in it can be cited, expired, or superseded, and
  `Sales-Machine/CLAUDE.md` rules 1, 2 and 6 are structurally unenforceable.
- **No coverage of the questions outbound actually generates.** The bank answers 17
  inbound questions. It carries nothing on: competitors by name, why a place that already
  has a supplier should switch, seasonality, what happens when a drink does not sell,
  minimum order versus a first trial, who delivers and in what vehicle, what a chain
  rollout looks like, invoicing and payment terms in practice, or what GT does when a
  product is out of stock.
- **No segment differentiation.** A hotel, a bar, a bakery and a specialty café buy for
  different reasons. The book has one script.
- **No negative knowledge.** What GT does *not* do, and will not: no consumer-scale
  pricing, no exclusivity by default, no unlisted flavours, no private label. Agents
  invent exactly here.

### 2.3 The four contradictions — verified 2026-08-31, fix these before anything else

**(a) Four products in the book's price list are Tom-graded negative records.**
From `docs/warehouses/catalog-truth.md`, section `רשומות-שלילה`, all graded
`מאושר-טום 2026-08-06`:

| In the book | Tom's determination `2026-08-06` |
|---|---|
| `MATCHA 50 גרם ₪65` | `"אנחנו לא מוכרים אותה"` |
| `GT ELITA 30 גרם ₪38` | `"זה לא אמור להיות שם"` |
| `מקציף קוקטיילים ₪75` | `ירד מהמחירון` |
| `קנקן זכוכית עם מסננת ₪36` | `"לא רלוונטי"` |

**(b) Two products have no active SKU.** `HOJICHA 500 גרם ₪375` and `AMERICAN` (₪65/₪33)
are both in the book's price list; `catalog-truth.md` records no active SKU for either.
The book already flags that Hojicha has no recipe — and still prices it.

**(c) The 48 drink figures are correct — and the repo holds a stale file that will tell
you they are not.** Nine drinks spanning every family were checked on 2026-08-31 against
`.claude/skills/drinks-pricelist/drinks_final_figures.json` (`_meta.date` `2026-08-27`,
the current authority): **9/9 exact on cost, price and margin.** The book is right here.

The trap: `docs/pricing/2026-08-05_drinks_final_figures.json` is an **older, superseded**
copy still sitting in the repo. It carries different costs, different margins, and only
five price points (`19/22/24/26/28`) against the authority's fifteen. Comparing the book
to it produces a full page of false contradictions — this happened during the writing of
this document. **The authority is the skill file, keyed by Canva page number, field
`name`.** Verify all 48 against it, and open a cleanup item to mark or remove the stale
duplicate so the next reader does not repeat the mistake.

**(d) Two claims are used with customers and have no source in any repo:**
`כ-700 לקוחות` and `8 שנים בשוק`. The 12-month fact table
(`Sales-Machine/evidence/`, rebuilt `2026-08-30`) shows **153 customers with orders in the
trailing twelve months**. 700 is plausibly a lifetime count — but plausible is not a
source, and this sentence is said to a restaurant owner who may check.

### 2.4 Adjacent, out of scope

The 48-drink catalog defects the book itself lists in §09 (three recipes pointing at
non-existent concentrates, the duplicated vanilla/agave recipe, the "20–25 cups" claim,
the double numbering, four competing Canva catalogs) are **owned by**
`docs/plans/2026-08-31-category-menus-masterprompt.md`. Record what you find, hand it over,
do not fix the Canva files here.

### 2.5 Re-verification block

```bash
# 1. the approved drink figures — 48 pages, the ONLY authority for cost/price/margin.
#    Note the shape: {_meta, pages:{"<canva page no>":{name,cost,price,marg,prof,star}}}
python3 -c "import json;d=json.load(open('.claude/skills/drinks-pricelist/drinks_final_figures.json'));print(d['_meta']['date'],len(d['pages']));[print(k,v['name'],v['cost'],v['price'],v['marg']) for k,v in d['pages'].items()]"

# 2. the approved ex-VAT product price list
column -t -s$'\t' docs/pricing/2026-08-05_shopify_products_exvat.tsv | head -60

# 3. what is genuinely sellable today, straight from the live system
#    (compare its output to catalog-truth.md; a difference is a finding, not an error)
```
Then run the live Shopify query in `gt-factory-os/CLAUDE.md` §Shopify writes — the
coverage query — for the current active sellable set.

---

## 3. What the hard part actually is

**It looks like:** filling gaps in a document.

**It actually is:** a format change. Tom asked for a database that AI agents read to
answer any customer question. An HTML artifact cannot be that, no matter how complete its
prose gets — you cannot cite a paragraph, expire it, grade it, or prove which version an
agent used. `Sales-Machine` already specifies the right shape and nobody has filled it:
graded cards under `knowledge/`, indexed in `registry.yaml`, each carrying source, date,
authority grade and freshness class. **The repo becomes the database and the artifact
becomes a view of it.** Every hour spent making the HTML more complete without that
inversion is an hour spent making the next migration bigger.

**Second reframe:** the book's most valuable chapter is `הגבולות` — the list of what must
never be answered. For an agent-facing database that chapter is not an appendix, it is the
safety layer, and it needs to be the most machine-readable part of the whole thing. An
agent that answers an allergen question about `מחית פיסטוק` or `שומשום שחור` — both
declared allergens, both in the price list — creates real risk for a restaurant serving a
diner with an allergy. Encode refusals as data with the same rigour as answers, and make
`refuse` the default for anything unmatched.

**Third reframe:** the four "not yet settled" items in the book's §09 — package contents
and prices, delivery time in days, discount tiers, commitment and exclusivity — are not a
knowledge gap. They are **the same four commercial decisions that block the lead system,
the category menus and the Q4 customer plan.** No amount of research closes them; only
Tom's word does. Do not spend a minute trying to derive them. Make them loud, put them at
the top of §6, and build everything else around their absence so the machine works the
day they land.

---

## 4. Workstreams

### W1 — Reconcile every number (do this first; nothing else ships until it passes)

Build `scripts/knowledge/reconcile.py` in `gt-factory-os-production-brain`. It reads the
book's published figures, joins them to the approved sources, and emits a diff table.
Zero rows is the gate. Every §2.3 item appears in the first run — if one does not, your
extraction is wrong, not the source.

Where the book and an approved source disagree, **the approved source wins and the book is
corrected** — except where correcting it would change a price, which is Tom's (§6.B).

**Acceptance:** D1.

### W2 — Build the knowledge layer

Create the card set under `Sales-Machine/knowledge/`, following that repo's own structure
and rule 1. Suggested shape — adapt to what `registry.yaml` already implies rather than
imposing a new scheme:

```
knowledge/
  products/        one card per sellable product: sku, name he/en, pack, price_exvat,
                   food_cost, shelf_life, kashrut, allergen_status(=refuse), source, date,
                   authority, freshness
  drinks/          one card per drink: family, category, cost, price, margin, recipe,
                   requires_equipment, requires_second_product, source(=the approved json)
  answers/         the answer bank — see W3
  boundaries/      refusals and escalations, machine-readable — see W4
  segments/        one card per buyer type: what they buy, why, what closes them
  claims/          every public claim with its evidence and who approved it
```

**Rule 2 is not optional here.** Customer counts, revenue, who is sleeping, current stock
— none of these become cards. They stay recipes plus dated evidence snapshots. If you
find yourself writing a customer count into a card, stop: that is the exact failure the
repo exists to prevent.

**Acceptance:** D2.

### W3 — The answer bank, as shared data

Convert the 17 answers to structured rows with exactly the columns the lead system
specifies: `שאלה` · `מילות מפתח` · `תשובה` · `קטגוריה` · `סטטוס` · `תאריך אישור`.

Then expand it. Target: **every question in §2.2's missing list gets a row** — either an
approved answer with a source, or a `העברה לאלכסנדר` row. A missing row makes an agent
guess; a transfer row makes it transfer. That asymmetry is the entire design.

**This is the same artifact the lead system's stage 4 builds.** Do not create a second
one. Own the data here, in the repo; the Google Sheet the lead system uses is generated
from it and syncs back. Agree the direction with that session before either writes — one
of you owns the write path, and it should be this one.

**Acceptance:** D3.

### W4 — Boundaries as data

Every rule in `הגבולות` becomes a machine-readable refusal: a matcher, a reason, an
escalation target, and the exact Hebrew sentence the agent says instead of answering.
Default for anything unmatched is refuse-and-transfer, not best-effort.

Add what the current list is missing: nutritional values, ingredient origin beyond what is
published, any medical or dietary suitability question, anything about a competitor's
product, and any commitment about stock or lead time.

**Acceptance:** feeds D6.

### W5 — Fill the outbound gaps

Write the cards §2.2 says are missing. Every one is either sourced or marked
`UNRESOLVED` and mirrored into `Sales-Machine/CURRENT_STATE.md` (D5). Priority order,
because outbound conversations die in this order:

1. `כבר יש לי ספק` — the switch case. The book has one paragraph; this is the single most
   common objection in wholesale food and deserves the most work.
2. Segment scripts — hotel, bar, bakery, specialty café. Ground them in the archetypes the
   fact table already uses: `TEA-ONLY`, `SPECIALTY-LED`, `MIXED`, `BAR-LED`.
3. The switching-cost answer: what a place actually has to change, in minutes and shelf
   centimetres.
4. Proof by segment — which named customers may be cited to whom (needs §6.C).
5. What happens after the first order: reorder cadence, who calls, what training arrives.

**Acceptance:** D5, and feeds D6.

### W6 — The evaluation set

Build `Sales-Machine/knowledge/eval/questions.yaml`: the 17 current questions with their
expected answers, the 5 forbidden categories with `expect: refuse`, plus 20 paraphrases
that a real café owner would type — misspelled, abbreviated, in slang. Then run an agent
against `knowledge/` alone and score it.

**This is the only done-condition that observes something you do not control** — the
agent's behaviour, not your files. Treat a failure as a data defect, not a prompt defect.

**Acceptance:** D6.

### W7 — Regenerate the artifact

Rebuild the book from the repo data and republish to the same URL. Add a build stamp:
build date, source commit, and a one-line statement that the repo is the source of truth
and this page is a rendering. **The book's own footer already promises this discipline**
(`כשמחיר משתנה — מעדכנים כאן קודם`) — now it becomes mechanically true.

**Acceptance:** D7.

---

## 5. Scope

**IN:** everything in §4.

**OUT — do not touch, do not "improve":**
- Canva files. Four competing drink catalogs exist and only `קטלוג משקאות סופי 26` is
  valid. That is the category-menus session's problem.
- Prices, discounts, package contents, delivery promises. You reconcile, you never set.
- The website, the storefront, social accounts.
- The lead system's runtime, `sales_core`, the Google Sheet's automation wiring.
- **Rewriting the book's voice.** Restyling well-working prose while the numbers under it
  are wrong is the most likely way this task ends up feeling done and being useless.

---

## 6. Tom's part — the complete list, nothing else is yours

**A. The four commercial decisions.** These block this document, the lead system, the
category menus and the Q4 plan simultaneously. Nothing derives them:
1. The three starter packages — name, exact contents, price.
2. Delivery time in **business days**, and whether centre and periphery differ.
3. The discount tiers by monthly consumption — the actual numbers.
4. Commitment: is there a contract, a monthly minimum, or regional exclusivity?

**B. The negative-record products.** `MATCHA 50 גרם`, `GT ELITA 30 גרם`,
`מקציף קוקטיילים`, `קנקן זכוכית עם מסננת`, `HOJICHA`, `AMERICAN`. For each: remove from
the customer price list, or reinstate as genuinely sellable. Your `2026-08-06`
determinations and the book currently disagree, and the book is what a salesperson reads
aloud to a customer. ~10 minutes.

**C. Which customer names may be published**, and to whom. The book currently names
`R2M`, `קבוצת קיסו`, `נונו מימי`, `ויוינו`, `אליטה אופק`, `בבקה`. Confirm each, and say
whether any is restricted to a segment.

**D. `700 לקוחות` and `8 שנים`.** Give the real figure and its basis, or approve a
different sentence. The trailing-twelve-month table shows 153 ordering customers, which
is a different claim, not a smaller one.

**E. `HOJICHA`** — it is priced at `₪375` with no recipe anywhere. Drop it, or commission
recipes for it in the category-menus session.

**F. Approve the expanded answer bank** before any of it is used with a customer. Alex
approves per the book's own rule; you decide whether that stands.

---

## 7. Landmines — do not rediscover these

1. **The book reads as authoritative because it is well written.** Fluent prose and a
   confident tone are exactly why nobody caught the four contradictions for weeks. Trust
   the source files, never the page — and where they disagree, assume the page is wrong.
2. **`catalog-truth.md` outranks Shopify `ACTIVE`.** It says so in its own header:
   `ACTIVE בשופיפיי הוא רמז. הקובץ הזה הוא האמת.` 377 products exist in Shopify and 253
   are archived. Building a price list from the Shopify API alone reproduces every ghost.
3. **`customer.amountSpent` and ShopifyQL's `average_order_value` are banned**
   (`Sales-Machine/recipes/sales-report.md`, section `בסיס כספי` — documented anomalies, one
   account shows 58 orders against ₪0.00). If you need a customer number, use the fact
   table.
4. **Shopify is misconfigured as `taxesIncluded=true @17%`**, so its tax/net/gross columns
   subtract a fictional tax. The stored line price is ex-VAT. Same source and section.
   A margin computed off the wrong base looks plausible and is wrong by ~17%.
5. **Writing a customer count into a knowledge card breaks rule 2** and will be correct
   for about a week. Recipe plus dated snapshot. Always.
6. **The repo holds two files named `drinks_final_figures.json` and only one is current.**
   `.claude/skills/drinks-pricelist/` is the authority (`2026-08-27`, keyed by page number,
   field `name`); `docs/pricing/2026-08-05_…` is superseded (keyed by list index, field
   `heb`). They disagree on every cost and on most prices. Reading the wrong one manufactures
   a page of contradictions that do not exist.
7. **The artifact is shared, not owned, from some sessions.** Confirm you can publish to
   the same URL before you plan a republish; a new URL splits the state silently.
8. **`מחית פיסטוק` and `שומשום שחור` are declared allergens in the price list.** The
   refusal must fire on the ingredient name, not just on the word `אלרגן` — a café owner
   asks `יש בזה אגוזים?`, never `מהו סטטוס האלרגנים?`.

---

## 8. Halt conditions

Inherited from `Sales-Machine/CLAUDE.md` §Stop conditions and
`gt-factory-os-production-brain/CLAUDE.md` §Stop conditions. Additions:

- A published figure cannot be traced to an approved source → **STOP**. Do not publish it
  with a hedge; open an `UNRESOLVED` and remove it from the customer-facing view.
- A gap could be filled by inference → it becomes `UNRESOLVED`, never a card. Rule 3.
- Any change to a price, a package, a term or a public claim → **STOP**, Tom's.
- Anything would touch factory-os core (`stock_ledger`, `items`, `bom_*`) → **STOP**.

---

## 9. Final report — Hebrew, short, honest

1. What an agent can now answer from the repo alone, and what it correctly refuses.
2. D1–D7 ✅/❌ with evidence pointers. No partial credit.
3. The numbers: cards written · answers approved vs transferred · contradictions found and
   closed · `UNRESOLVED` opened.
4. The artifacts, and where they are.
5. What is still Tom's, and what is genuinely unfinished.
6. The single next action.

Then stamp this file `STATUS: SHIPPED — <date>` with evidence pointers, and commit.
