# T1 — The four commercial decisions: evidence brief

> **Purpose.** `T1` on the war room board costs Tom an hour and unblocks four documents
> (`#2` knowledge book, `#3` lead system, `#5` category menus, `#6` existing-customers Q4).
> This brief does the hour of work that can be done without him, so what is left is four
> yes/no answers rather than four open questions.
>
> **Status:** evidence assembled 2026-09-01. **Decisions still open — Tom is the only
> approver.** Nothing here is doctrine until he says so and it is logged in
> `Sales-Machine/doctrine/decisions.md`.

**Read with:** `docs/plans/2026-08-31-WAR-ROOM.md` (`T1`) · `Sales-Machine/doctrine/pricing-logic.md`
· `docs/ceo/reference/people_rhythm.md` (route calendar).

---

## 0. How this was measured

Every number below is computed from the live Shopify Admin API on **2026-09-01**, not from
a stored file. Authority grade: `system_verified`. Sources named per section. Three
sampling frames are used and each is stated where it applies:

| Frame | What it covers | Used for |
|---|---|---|
| **A** | Shopify sales analytics, trailing 12 months to 2026-09-01 | price realisation, discount rate, volume |
| **B** | 50 most recent fulfilled orders, `2026-08-25` → `2026-09-01` | order-to-dispatch lead time |
| **C** | 30 most recent orders, `2026-08-20` → `2026-09-01`, line by line | per-customer price dispersion |
| **D** | first order of 8 customers created since `2026-02-24` who reached ≥3 orders | starter-package composition |

Frames B, C and D are small and recent by design: they answer "what does GT do **now**",
which is the question all four decisions turn on. Where a frame is too small to carry a
conclusion, this brief says so instead of rounding up.

**One correction on the record.** The first pass at this brief was going to report that GT
cut ~17 points of discount in July 2026 and revenue rose. That is false, and the check that
killed it is in §3.1. It is written up because the same trap will catch the next reader of
the `discounts` metric.

---

## 1. Decision 1 — Starter packages

### 1.1 What GT already does

Frame D. The first order of eight customers who went on to reorder at least twice:

| Account | First order | Value | Shape |
|---|---|---|---|
| `קפה גן סיפור חולון` | `2026-02-24` | `₪1,360` | Kit + Matcha `22x18` + 2×6 1L + 6×500ml + cup |
| `קפה גן סיפור הרצליה` | `2026-02-25` | **`₪0`** | identical basket, comped |
| `קפה גן סיפור ראשון לציון` | `2026-03-02` | `₪1,534` | 3×12 500ml + Matcha `22x18` + Kit + cup |
| `סברה קפה` | `2026-03-16` | `₪1,438` | 4×4 1L + 2 sugar-free + 7 ODK |
| `ביער בייקרי קפה רמת השרון` | `2026-05-28` | **`₪0`** | 4×1L + Kit + Matcha `500g` + 4 ODK, comped |
| `קפה רימון ממילא` | `2026-06-23` | `₪2,082` | Matcha `22x18` + 4×6 1L + 4×500ml + Kit |
| `Natche` | `2026-06-25` | `₪755` | Matcha `500g` + 3 ODK + cup |
| `ג'ורנו נתניה` | `2026-07-15` | `₪896` | Ube `1kg` + 4 ODK + sangria + 2×6 500ml |

**There is already a de-facto opening kit and it is remarkably consistent.** Six of eight
first orders contain a Shizuoka matcha unit; five contain the Complete Matcha Kit; five
contain a measuring cup. Paid first orders run **`₪755`–`₪2,082`, median ≈ `₪1,400`**.

### 1.2 The three shapes the data actually shows

Not one package — three, and they map cleanly to the archetypes already in the Q4 plan:

| Shape | Contents as sold | Line total at today's list |
|---|---|---|
| **Matcha opener** (`TEA-ONLY`) | Complete Matcha Kit + Shizuoka `22x18g` or `500g` + measuring cup | `₪780` |
| **Extract opener** (`SPECIALTY-LED`) | 4 flavours × 6 × 1L + measuring cup | `₪1,580` |
| **Bar opener** (`BAR-LED` / `MIXED`) | Ube `1kg` + 4 ODK smoothies + 1 cocktail base + 2 × 6 × 500ml | `₪1,000` |

These are not invented. Each is the median basket of the accounts that stuck, priced at the
list GT charges today.

### 1.3 The finding that needs a decision more than the packages do

**Two of eight opening orders were `₪0`.** GT comps opening kits. Nothing in `doctrine/`
authorises it, no rule says who qualifies, and the Q4 playbook (`§385`) states the opposite
in Tom's own words: `אין הנחה, אין דוגמית, אין מחיר ניסיון.`

Comping may well be the right move — both comped accounts reordered. But the playbook and
the practice contradict each other, and every session writing customer-facing copy has to
pick one. **That is the decision, and it is bigger than the package contents.**

### 1.4 Recommendation

Adopt the three shapes above at list price, and settle the comp question explicitly:
a comped opener is allowed **only** for a multi-site account where the first site is a
proof-of-concept for the chain — which is exactly what both `₪0` orders were
(`גן סיפור` 7 sites, `ביער` 2+ sites). Single-site accounts pay. That rule fits the
evidence and does not contradict the playbook line, because a chain pilot is not a
`דוגמית`.

**If Tom says nothing:** sessions keep guessing, and #5's landing pages either publish a
package that does not exist or publish nothing.

---

## 2. Decision 2 — Delivery time in business days

### 2.1 What the warehouse actually does

Frame B, n=50, order created → fulfilment created (dispatch, not doorstep):

- median **`21.6 h`** · mean `26.9 h` · p90 `53.8 h` · max `91.6 h`
- **82%** dispatched within **1 business day**; **100%** within **2**
- Israeli work week (Sun–Thu) applied; Fri/Sat excluded

The warehouse is not the constraint. It clears essentially everything inside two business
days, and four in five orders inside one.

### 2.2 What the route calendar does

`docs/ceo/reference/people_rhythm.md`: `ראשון · שני · חמישי — מרכז · שלישי — צפון · רביעי — דרום`.

Centre gets three route days a week. North gets one. South gets one. **The honest promise
is therefore regional, and a single national number is either a lie in the north or an
undersell in the centre:**

| Region | Route days | Worst case order → delivery | Safe public promise |
|---|---|---|---|
| Centre | Sun · Mon · Thu | 3 days (Mon afternoon → Thu) | **`עד 2 ימי עסקים`** |
| North | Tue | 7 days (Tue afternoon → next Tue) | **`אספקה בימי שלישי`** |
| South | Wed | 7 days (Wed afternoon → next Wed) | **`אספקה בימי רביעי`** |

### 2.3 Recommendation

Publish **`עד 2 ימי עסקים במרכז`**, and name the day for north and south rather than a
day-count. Naming the day is a *stronger* promise than "3–5 days" — it is a standing
appointment, and it is the truth. Add one cut-off hour so it is falsifiable; the data
supports **`הזמנה עד 12:00`** comfortably.

**Not verified here:** dispatch is not delivery. LionWheel holds delivery truth and was not
queried for this brief. If Tom wants the promise stated as *delivery* rather than
*dispatch*, that check runs first. → `UNRESOLVED U-016`.

**If Tom says nothing:** #3 cannot answer the single most common question a lead asks, and
#4 and #5 publish nothing about delivery at all.

---

## 3. Decision 3 — Discount tiers by consumption

This is the one where the data changes the question.

### 3.1 The trap, and why the obvious reading is wrong

Shopify's `discounts` metric collapsed in July 2026:

| Month | Gross | Discounts | % of gross |
|---|---|---|---|
| `2025-09` … `2026-06` | — | — | **14%–20%**, mean ≈ 17% |
| `2026-07` | `₪777,760` | `₪65,929` | 8.5% |
| `2026-08` | `₪1,178,853` | `₪3,865` | **0.33%** |

Read alone, that says GT stopped discounting. It did not. **The realised price per unit did
not move:**

| SKU | Net ₪/unit, `2026-06` | Net ₪/unit, `2026-08` | Change |
|---|---|---|---|
| `DETOX 1000ml` | `₪43.21` | `₪42.90` | −0.7% |
| `FRESH 1000ml` | `₪43.68` | `₪43.81` | +0.3% |
| `NAMASTEA 1000ml` | `₪43.66` | `₪42.40` | −2.9% |
| `DETOX Sugar-Free 1000ml` | `₪44.63` | `₪44.16` | −1.1% |
| `CALM 1000ml` | `₪46.52` | `₪44.72` | −3.9% |
| `ENERGY 1000ml` | `₪48.56` | `₪46.99` | −3.2% |
| `Shizuoka Matcha 500g` | `₪399.16` | `₪398.59` | −0.1% |

The customer pays the same. What changed is that the discount is now typed into the **line
price** instead of appearing as a discount line. Same money, different bookkeeping. Anyone
reporting off the `discounts` metric across July 2026 will report a margin gain that did not
happen.

### 3.2 What is actually true: nine prices for one litre

Frame C — the same `1000ml` extract, sold in the twelve days to 2026-09-01:

| Price / 1L | vs `₪65` list | Accounts seen at this price |
|---|---|---|
| `₪41.85` | −35.6% | `נונומימי נס ציונה` · `נונו ג'ירף מודיעין` |
| `₪44.40` | −31.7% | `בני ציון הבימה` (קבוצת נורדוי) |
| `₪47.00` | −27.7% | `וויקס.קום` (קמפוס) |
| `₪54.00` | −16.9% | `בבקה צהלה` · `בבקה מיקדו סנטר` |
| `₪54.90` | −15.5% | `קפה מרי` · `קפה מרי באר יעקב` |
| `₪58.50` | −10.0% | `קפה ללוש נס ציונה` · `סיטי בולונזרי` |
| `₪60.45` | −7.0% | `ביער בייקרי` |
| `₪61.00` | −6.2% | `Bake & Bread` · `ביסקוטי ראש העין` |
| `₪65.00` | 0% | `קפה נוק` · `גאפן גאפן` · `אמה קפה` · `נולי` · `רוז עוגות` |

The `500ml` shows seven price points (`₪21.39` → `₪33.00`); Shizuoka `500g` shows six
(`₪325` → `₪590`); the Complete Matcha Kit is sold at both `₪150` and `₪170` while its
Shopify `compareAtPrice` says `₪100`; the measuring cup is sold at `₪0`, `₪15` and `₪20`.

**Shopify holds `0` B2B companies and `0` price lists.** There is no tier machinery. Every
one of these prices is typed by hand, per order, from memory.

### 3.3 The sentence that decides it

> `קפה נוק` — 47 orders, `₪50,302` lifetime — pays **`₪65.00`**.
> `קפה מרי באר יעקב` — 4 orders, `₪4,840` lifetime — pays **`₪54.90`**.

**The discount does not track consumption. It tracks who negotiated.** That is the finding.
"Discount tiers by consumption" is not a new policy to design — it is a correction to a
structure that already exists and rewards the wrong thing.

### 3.4 The size of the prize

Trailing 12 months, the 1L extract line (10 SKUs):

- **`56,055` litres** sold · net **`₪2,426,485`** · realised **`₪43.29`/litre** (`₪43.2876`)
- at `₪65` list that volume would be `₪3,643,575` — the discount structure is worth
  **`₪1,217,090`/yr**

That full gap is not recoverable and should not be chased. The useful unit is smaller:

| Move | Annual value at current volume |
|---|---|
| **+`₪1`/litre across the line** | **`₪56,055`** |
| average `₪43.29` → `₪45.00` | `₪95,990` |
| average `₪43.29` → `₪47.00` | `₪208,100` |

For scale: the whole existing-customer Q4 target is `₪200,125` of new annualised run-rate.
**Moving the average realised litre from `₪43.29` to `₪47.00` is worth the same as the
entire Q4 growth plan** — from customers GT already has, with no new conversations.

That is not a recommendation to do it. It is the number that says this decision deserves
the hour more than the other three.

### 3.5 A second finding, free

Realised `500ml` price is **`₪22.31`** — `₪44.62` per litre — against the 1L's `₪43.29`.
**The half-litre earns GT a 3% per-litre premium for double the bottles, caps, labels and
picking.** Whatever the tier structure becomes, the 500ml format is under-priced relative
to its own cost to serve.

### 3.6 Recommendation

Three tiers, set at prices that already exist in the book so that most accounts do not move:

| Tier | Qualifier (rolling 12m) | 1L | 500ml |
|---|---|---|---|
| `בסיס` | under `₪25,000` | `₪61` | `₪31` |
| `מועדף` | `₪25,000`–`₪75,000` | `₪56` | `₪29` |
| `רשת` | over `₪75,000`, or 3+ sites | `₪48` | `₪25` |

Sequencing matters more than the numbers. **Never re-price a live account downward and
upward in the same conversation.** Apply the tier to every new account from day one; move
existing accounts only at their next natural review, and only upward toward their tier — the
accounts below their tier (`₪41.85` on a `₪48` tier) are the ones to leave alone until Tom
decides individually.

**If Tom says nothing:** `U-003` stays open, which means #4 cannot publish a price on the
website at all — because any published number tells `קפה נוק` it has been paying 33% over
what `נונומימי` pays. **This is why the website price question is blocked, and it is not a
copywriting problem.**

---

## 4. Decision 4 — Commitment and exclusivity

### 4.1 What can and cannot be said from data

GT has no contracts, no minimums and no exclusivity today — nothing in `doctrine/` records
any, and Shopify holds no B2B agreement structure to carry one. So there is no empirical
base to extrapolate from. **This brief will not invent one.**

What the data does establish is the leverage question underneath it:

- Reorder behaviour is already extremely sticky — the 87–98% monthly returning rate in
  `Sales-Machine/CLAUDE.md`, and the Frame D accounts reordering 3–15 times within months
  of a first order.
- Concentration is real: `אליטה אופק` (`₪864,864` lifetime, 179 orders) and the
  `מימי / נונומימי` group (`₪821,471` + `₪229,691` + `₪144,772` + `₪106,904` + `₪95,523`
  + `₪89,648` + `₪66,280` + `₪51,537` across sites) are the two relationships whose loss
  would be structural rather than painful.

### 4.2 Recommendation

**Do not introduce commitment or exclusivity in Q4.** Reasoning, plainly:

1. GT's retention is already near-ceiling. A commitment clause buys almost nothing it does
   not already have, and costs the one thing it is short of — reasons for a customer to say
   yes quickly.
2. The tier structure in §3.6 *is* the commitment mechanism, and a better one: it rewards
   consumption after the fact instead of demanding a promise up front. `רשת` pricing for
   3+ sites is an exclusivity incentive that needs no contract.
3. Introducing both a price correction and a commitment ask in the same quarter puts two
   uncomfortable conversations into every account at once. **§3 is worth `₪208,100`.
   Exclusivity is worth an unknown. Do not spend the first on the second.**

**If Tom disagrees** and wants a commitment track, the smallest version that does not risk
the base: offer `רשת` pricing to a 2-site account *in exchange for* the third site, with no
paper. That is a commitment in substance and a favour in form.

---

## 5. What Tom is being asked

Four answers. Each is yes / no / change-it:

| | Decision | Recommended answer |
|---|---|---|
| **D1** | Three starter shapes at list (§1.2); comped opener allowed **only** as a chain pilot | ☐ |
| **D2** | `עד 2 ימי עסקים` centre · named day north (`שלישי`) and south (`רביעי`) · cut-off `12:00` | ☐ |
| **D3** | Three tiers `₪61` / `₪56` / `₪48` (§3.6); new accounts immediately, existing only upward at next review | ☐ |
| **D4** | No commitment or exclusivity in Q4; the tier is the mechanism | ☐ |

---

## 6. UNRESOLVED opened by this brief

| ID | Item | Owner |
|---|---|---|
| `U-016` | Dispatch ≠ delivery. Lead times here are order → fulfilment. Delivery truth is in LionWheel and was not queried. Needed before any *delivery* promise is published | a session with LionWheel read |
| `U-017` | `2026-08-09`: `מימי ואזה חנויות` placed two orders totalling **`₪472,500`** (`17,000` + `18,000` line items, `₪13.50`/unit, 0.3 L bottles). The same week carries **`₪437,692`** of sales reversals. Whether these are the same money is unverified. This is the largest single financial event in the trailing year and it is unexplained | Tom |
| `U-018` | The 0.3 L Hebrew-named SKUs (`תמצית היביסקוס וליים 0.3 ל` and three siblings) sold `19,650` units in the trailing year at `₪13.50` list. They are a retail line, not HoReCa, and appear in no doctrine, no catalog and no menu | Tom |
| `U-019` | Complete Matcha Kit sells at `₪150` and `₪170` with a Shopify `compareAtPrice` of `₪100` — the compare-at is **below** both. Any storefront that renders it will show a negative saving | #4 |
| `U-020` | A product with an empty title sold `7,738` units for `₪138,399` in the trailing year — deleted or unnamed SKU carrying real revenue | `gt-catalog-truth` |

---

## 7. Evidence statement

**Files changed:** this file only. **Checks run:** 11 live queries against Shopify Admin
(2 analytics, 6 GraphQL, 3 REST-equivalent listings) + 1 computed lead-time analysis over
n=50. **Sources cited:** Shopify Admin API `2026-09-01`; `docs/ceo/reference/people_rhythm.md`;
`docs/pricing/2026-08-27_COST_MODEL.md`; `Sales-Machine/doctrine/decisions.md`;
`docs/plans/2026-08-31-existing-customers-q4-masterprompt.md`. **Authority grades:** all
Shopify figures `system_verified`; the tier proposal in §3.6 and the recommendations in
§1.4, §2.3 and §4.2 are `inferred` and **are not policy until Tom approves them**.
**UNRESOLVED opened:** `U-016`–`U-020`. **Closed:** none. **Tom approvals required:** all
four decisions in §5. **Stock truth:** untouched — no factory-os core table was read or
written. **Customer-facing writes:** none; `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` remains
`false`.

**Contact details are deliberately absent.** Company names appear because Tom cannot act on
"Account A"; no email, phone or personal name of any customer is recorded here.

---

**Prepared:** 2026-09-01, war-room session. **Decides:** nobody but Tom.
