# Shopify storefront — full cleanup & capability activation

> **Status:** OPEN — needs Tom. Nothing in here has been executed.
> **Opened:** 2026-08-26, from the online-presence audit.
> **Scope:** the Shopify storefront as a *commercial surface*. ⊥ factory-os core. ⊥ stock truth.
> **Pointer:** `CURRENT_STATE.md` § Open — needs Tom holds the one-line entry. This file holds the depth.

---

## 0. Why this is not cosmetic

Three costs, each independently sufficient to justify the work:

1. **61% of the live catalog cannot be fulfilled.** 74 of 122 active products sit at zero or
   negative inventory. Every shekel spent driving traffic lands a coin-flip on a dead end.
2. **Production inputs and customer private-label SKUs are publicly purchasable.** Packaging,
   raw materials, a ₪5,000 can-sealing machine, and 12 customer-specific SKUs (Elita ×10,
   Babka Bakery ×2) are listed, priced and orderable by anyone. Commercial exposure, and a
   confidentiality question on the private-label lines.
3. **URLs are disconnected from what they sell.** 52 of 122 active handles (43%) carry `copy`,
   and several name a different product entirely. Search engines read the handle.

None of this is fixable by the storefront theme. It is catalog hygiene.

---

## 1. Verified state — 2026-08-26

All figures read live from the Shopify Admin API on 2026-08-26. `authority: system_verified`.
Volatile by nature — re-run before acting, ⊥ quote as current later.

### Catalog scale
| | |
|---|---|
| Products total | 377 |
| ACTIVE | 122 |
| ARCHIVED | 253 (67%) |
| DRAFT | 2 |

### Fulfillability of the 122 ACTIVE
| | |
|---|---|
| Positive stock | 48 |
| Zero | 34 |
| **Negative (oversold)** | **40** |

Sums to 122 — filter verified reliable.

### Composition of the 122 ACTIVE
| product_type | count |
|---|---|
| Cocktail | 46 |
| `Related products` (packaging, RM, equipment) | 26 |
| *(no type set)* | 16 |
| Tea 1 l | 11 |
| Tea 0.5 l | 10 |
| Accessories | 6 |
| Tea & Infusions | 4 |
| Matcha | 2 |
| *unaccounted* | 1 |

Sums to 121/122 — one product carries a type not enumerated. Find it during the pass.

**The core product line — tea concentrates — is 25 of 122.** Everything else buries it.

### Named defects
- `Cardboard Box for 1000ml` → handle `cardboard-box-for-200ml-copy`
- `Cardboard Box for 200ml` → handle `delivery-250-copy`
- `Desert Infusion 1000ml` → handle `תמצית-צאי-מסאלה-1-ל-namastea-copy-2`
- `GT Babka Bakery Red Sangria` → handle `gt-elita-red-sangria-cocktail-750ml-copy`
- Vendor recorded two ways: `GreenTeaEveryday` and `Greentea Everyday - גרינטי`
- Product titles are English on a Hebrew-market storefront

### Method note — ⊥ trust this filter
Shopify's `has_image:true` and `has_image:false` **both return 122**. The filter is broken and
was not used. A hand sample of 30 ACTIVE products found 21 with no featured image. That is a
sample, ⊥ a count. Anyone continuing this work must count images by walking the products.

---

## 2. What Shopify already does for us — and what it doesn't

Separated by evidence grade. ⊥ collapse these into one list.

### `system_verified` — in use
| Capability | Evidence |
|---|---|
| **Draft orders** | 10,000+ COMPLETED (count capped at 10,000), **163 OPEN** |
| Discount codes | ≥5 discount nodes exist |
| Customer segments | 11 defined, incl. `WH` = `metafields.custom.client_key IS NOT NULL` → **1,172 customers** |
| Email subscribers | segment `Email subscribers` → **2,969 customers** |
| Sales channels connected | Online Store · Facebook & Instagram · Google & YouTube |

**The draft-order finding reframes the storefront.** Online checkout completed **1** order in 365
days, but draft orders number in the ten-thousands. Orders are being built by staff and invoiced —
phone, WhatsApp, direct. The storefront is not the sales channel; the draft order is. Any plan
that treats the online store as the order path is planning against a fiction.

**163 open draft orders** is its own operational item: unconverted quotes, or stale clutter.
Nobody has triaged them. Needs a decision, then a cadence.

### `system_verified` — NOT in use
| Capability | Evidence |
|---|---|
| Marketing activities | 0 |
| GT-owned product metafields | 0 — the only 3 definitions belong to apps (Google Shopping, Yotpo) |
| Email campaigns | Klaviyo: 0 flows, 0 campaigns ever sent — against 2,969 subscribers |

### `inferred` — worth evaluating, ⊥ verified from here
Not checkable through the API surface available in this session. Each needs a look in the admin
before it is claimed as a gap:

Shopify Email · Shopify Forms · Shopify Flow · Search & Discovery (filters, recommendations) ·
Bundles · Translate & Adapt (Hebrew/English) · automated collections by rule · customer-account
configuration · abandoned-checkout recovery · Markets · gift cards (read blocked — no
`read_gift_cards` scope) · the plan's own feature ceiling (`planName: Shopify`, ⊥ Plus — so
native B2B company profiles and price lists are **not** available on the current plan; confirm
before designing around them)

---

## 3. Hard boundary — inventory is ⊥ fixable in Shopify

`CLAUDE.md` § Source of truth: *Shopify FG inventory — sync target; **we are authoritative**;
the reconciler overwrites Shopify `available` every 5 min from our truth (Tom 2026-08-01).*

Therefore the 40 negative-inventory products are **⊥ a Shopify data-entry problem**. Either

- the negatives are our own truth arriving through the reconciler → fix at source, ⊥ in Shopify; or
- those products sit outside the reconciler's scope → then *why*, and what is writing them?

**Typing corrected numbers into Shopify would be overwritten within 5 minutes and would
falsify stock truth in the meantime.** Any executor touching this must establish which case
applies before changing a single quantity.

**Open question for the same reason:** does un-publishing or archiving a product change what the
FG reconciler syncs? Must be answered before any bulk status change, or the cleanup silently
alters the sync surface.

---

## 4. Decisions only Tom can make

Work ⊥ start before these are answered. Each blocks a different part of the pass.

1. **What is the storefront for?** Consumer, business, or both on separate paths? The whole
   catalog shape follows from this. (Tom 2026-08-26 stated both audiences matter equally —
   that is a marketing stance; this asks the narrower question of what the *store* sells.)
2. **Do production inputs stay listed at all?** Packaging, RM and equipment are presumably there
   so staff can add them to draft orders. If so they must be hidden from the storefront while
   staying available in admin — ⊥ deleted.
3. **Private-label SKUs (Elita, Babka Bakery) — public or not?** Confidentiality question first,
   commercial second. Likely needs the customers' word.
4. **The 253 archived products — keep archived, or delete?** Archived is safe and reversible.
   Deletion is not. Recommend keeping unless there is a reason.
5. **One email tool or two?** Klaviyo is installed and completely unused; Shopify Email is
   included in the plan. Running both is a tax. Pick one before building anything.
6. **The 163 open draft orders — chase or close?**

---

## 5. Sequence

Strictly ordered. Each step is a gate on the next.

1. Answer §4. ⊥ proceed without it.
2. Resolve §3 — establish the inventory ownership case, in writing.
3. **Freeze a full export first.** All 377 products with every field, to file, before any change.
   Reversibility is the whole safety net here.
4. Hide-not-delete pass: production inputs and private-label SKUs off the storefront.
5. Fulfillability pass: the 74 at zero/negative — publish only what can actually ship.
6. Taxonomy pass: real `product_type` on all 122, one vendor spelling, Hebrew titles.
7. Handle pass: fix the misleading handles. **Every change needs a 301** — see the
   redirect precedent set 2026-08-26 (3 redirects created for dead blog links).
8. Media pass: count images properly (§1 method note), then fill the gaps.
9. Only then: activate the capabilities in §2 that survived evaluation.

Steps 4–8 are bulk operations on a customer-facing surface. `CLAUDE.md` § Authorization puts
mass and customer-facing writes behind Tom's explicit go, stated per batch — ⊥ a blanket approval.

---

## 6. Cross-references

- **Sales-Machine `U-003`** — tag semantics for `pl` / `client_key` metafields is UNRESOLVED
  there. This audit found `client_key` carries **1,172 customers** via the `WH` segment. The two
  items are the same unknown seen from two sides; resolve once, record in both.
- **Online-presence roadmap** (artifact, 2026-08-26) — phase «חנות שופיפיי» carries the
  operator-facing task list. This file is the governance record; that one is the working surface.
- **`docs/decisions/modules/sales-declaration.md`** — the sales module's isolation rules bind any
  agent that later automates this.

---

## 7. Evidence standard for closing this

Per `CLAUDE.md` § Evidence, a PASS on this work states: products changed (by id) · before/after
export diff · redirects created · reconciler behaviour re-verified after any status change ·
which §4 decisions Tom gave in writing · rollback path.
