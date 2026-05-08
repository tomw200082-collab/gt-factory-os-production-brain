# LionWheel Remaining Unresolved — Decision Surface (Tom-actionable)

**Date:** 2026-05-02 (Asia/Jerusalem) — cycle 21 W1.
**Owner:** executor-w1.
**Purpose:** Tom-decision-ready surface for the 90 unresolved `orders_mirror_lines` rows / 27 distinct SKUs / 325 unit qty remaining after cycle 19 W1 LionWheel runtime closure (signal #30) + cycle 20 math reconciliation.

**Read this with:**
- `gt-factory-os/docs/integrations/lionwheel_remaining_unresolved_breakdown_2026-05-02.md` (cycle 20 W4 — class definitions + counts)
- `gt-factory-os/docs/lionwheel_unresolved_math_reconciliation_2026-05-02.md` (cycle 20 W1 — sum reconciliation)
- `gt-factory-os/docs/integrations/lionwheel_remaining_tom_decisions_2026-05-02.md` (cycle 19 W4 — Tom-blocking IDs LWR-1 / LWR-3 / LWR-4)
- `gt-factory-os/docs/integrations/lionwheel_normalization_runtime_contract.md` (cycle 17 + cycle-19 §13 appendix)
- `gt-factory-os/docs/integrations/lionwheel_bundle_map_contract.md` (cycle 18)

**Boundaries respected:**
- READ-ONLY against live DB (Supabase pooler `aws-1-eu-central-1.pooler.supabase.com:5432`, project `rvadsozabmxkkrktwgnv`, PG17). Zero writes.
- Backend handlers UNCHANGED. `api/src/integrations/lionwheel/*.ts` UNCHANGED (cycle 19 carve-out expired).
- Planned-inflow endpoint UNCHANGED — W2 has not reported an API gap.
- A3 LOCKED (`v_planning_demand`), A4 LOCKED (`fn_compute_fg_net_requirements`), `stock_ledger` LOCKED, MC-U2 DISABLED.
- No new `RUNTIME_READY` signal emitted; this is a decision-grade audit, not contract closure.
- No invented mappings. Every candidate suggestion is sourced from `private_core.items` substring/token probe; no guess assertion is made.

**Live counts confirmed (server_now=2026-05-02 19:01:35 IL):**

| Total unresolved | Distinct SKUs | Total qty |
| --- | --- | --- |
| 90 | 27 | 325.00 |

| Class | SKUs | Rows | Qty |
| --- | ---: | ---: | ---: |
| Bundle (LWR-1) | 9 | 44 | 47.00 |
| Non-catalog (LWR-3) | 7 | 25 | 218.00 |
| Ambiguous (LWR-4) | 10 | 20 | 59.00 |
| Malformed | 1 | 1 | 1.00 |
| **Total** | **27** | **90** | **325.00** |

Sum check: 44+25+20+1 = 90 ✓ ; 9+7+10+1 = 27 ✓ ; 47+218+59+1 = 325 ✓.

**Note on the 65→59 ambiguous-qty drift vs `lionwheel_remaining_unresolved_breakdown_2026-05-02.md` §4.2:** the cycle-20 breakdown pack stated `ambiguous_qty=65`. Live re-run today shows `59`. The 6-unit difference is consistent with one or more cycle-19 back-fill rows being post-aliased and deducted between the cycle-20 pack authoring and today's snapshot. No category change; no math error in the breakdown pack — just a moving snapshot. This artifact uses the live 59.

---

## §1 Bundles (LWR-1) — 9 SKUs / 44 rows / 47 qty

**Tom decision needed (LWR-1):** rule on bundle policy. Three options per cycle-19 decisions pack §2:
- **Option A (W4-recommended default):** decompose via `private_core.bundle_map` at the curated planning-demand layer; raw mirror preserves bundle SKU verbatim; Tom authors per-bundle composition.
- **Option B:** parent alias — treat each bundle as a standalone purchasable item via `integration_sku_map`.
- **Option C:** status quo / unresolved-visible-only.

**Tom default per dispatch:** Option A (wait for curated bundle_map).

Rows below are sorted by row count desc.

### §1.1 GTSET-LOW-6FLAV-SALE
- **Total rows:** 17 / **Total qty:** 17.00 / **Distinct orders:** 17
- **lw_name:** "מארז טעימות ב-6 טעמים מופחת סוכר במבצע" (6-flavor low-sugar sample box on sale)
- **Sample order codes:** `6579839`, `6585640`, `6589035`
- **Date range:** order_created `2026-04-18 → 2026-04-18`; pickup_at NOT POPULATED on any row
- **Likely business meaning:** 6-bottle reduced-sugar sample/gift box. Decomposes to 6 distinct FG bottles (likely from the FG-CAL/FG-DET/FG-DES/FG-FRE/FG-ENE/FG-MAT family — Tom-known).
- **bundle_map needs:** 6 component item_ids × 1 each = 6 rows in `bundle_map` (composition unknown to W1 — Tom-authoritative).
- **W4 recommendation:** Option A (bundle_map at curated layer).
- **Tom default per dispatch:** A (wait for curated bundle_map).

### §1.2 GTSET-FREE-3FLAV-SALE
- **Total rows:** 7 / **Total qty:** 10.00 / **Distinct orders:** 7
- **lw_name:** "מארז טעימות ב-3 טעמים ללא סוכר במבצע" (3-flavor no-sugar sample box on sale)
- **Sample order codes:** `6586171`, `6592981`, `6597033`
- **Date range:** `2026-04-18 → 2026-04-18`; no pickup_at
- **Likely business meaning:** 3-bottle no-sugar sample box. Decomposes to 3 FG bottles. Some orders carry qty>1 (10 units across 7 orders → average 1.43 boxes/order).
- **bundle_map needs:** 3 component item_ids × 1 each per box.
- **W4 recommendation:** Option A.
- **Tom default per dispatch:** A.

### §1.3 GTSET-FREE-DETOX-X4
- **Total rows:** 4 / **Total qty:** 4.00 / **Distinct orders:** 4
- **lw_name:** "מארז MONTHLY DETOX PACK ללא סוכר במבצע" (monthly DETOX pack no-sugar on sale)
- **Sample order codes:** `6605397`, `6607848`, `6632568`
- **Date range:** `2026-04-18 → 2026-04-18`; no pickup_at
- **Likely business meaning:** Monthly DETOX pack. 4× FG-DET items (no-sugar variant). Likely composes to 4× FG-DET-1L-NS or FG-DET-500ML-NS — Tom-known.
- **bundle_map needs:** 1 component item × 4 qty (or 4 × 1 if mixed sizes).
- **W4 recommendation:** Option A.
- **Tom default per dispatch:** A.

### §1.4 GTSET-FREE-FRESH-DETOX
- **Total rows:** 4 / **Total qty:** 4.00 / **Distinct orders:** 4
- **lw_name:** "מארז FRESH&DETOX ללא סוכר במבצע" (FRESH+DETOX pack no-sugar on sale)
- **Sample order codes:** `6608062`, `6612120`, `6724970`
- **Date range:** `2026-04-18 → 2026-04-18`; no pickup_at
- **Likely business meaning:** Fresh + Detox combination pack (no-sugar). Likely 2× FG-FRE + 2× FG-DET no-sugar variants.
- **bundle_map needs:** ≥ 2 component item_ids × qty.
- **W4 recommendation:** Option A.
- **Tom default per dispatch:** A.

### §1.5 GTSET-LOW-3FLAV-SALE
- **Total rows:** 4 / **Total qty:** 4.00 / **Distinct orders:** 4
- **lw_name:** "מארז טעימות ב-3 טעמים מופחת סוכר במבצע" (3-flavor low-sugar sample box on sale)
- **Sample order codes:** `6602453`, `6603595`, `6691236`
- **Date range:** `2026-04-18 → 2026-04-18`; no pickup_at
- **Likely business meaning:** 3-bottle reduced-sugar sample box. Sibling SKU to §1.2 (no-sugar variant). Decomposes to 3 FG bottles.
- **bundle_map needs:** 3 component item_ids × 1 each.
- **W4 recommendation:** Option A.
- **Tom default per dispatch:** A.

### §1.6 GTSET-LOW-3FLAV-PREMI
- **Total rows:** 3 / **Total qty:** 3.00 / **Distinct orders:** 3
- **lw_name:** "מארז טעימות ב-3 טעמים פרימיום מופחת סוכר במבצע" (3-flavor PREMIUM low-sugar sample box on sale)
- **Sample order codes:** `6627163`, `6632755`, `6783809`
- **Date range:** `2026-04-18 → 2026-04-18`; no pickup_at
- **Likely business meaning:** 3-bottle PREMIUM reduced-sugar sample box. Different SKU set than §1.5 (premium tier).
- **bundle_map needs:** 3 component item_ids × 1 each.
- **W4 recommendation:** Option A.
- **Tom default per dispatch:** A.

### §1.7 GTSET-LOW-DETOX-X4
- **Total rows:** 3 / **Total qty:** 3.00 / **Distinct orders:** 3
- **lw_name:** "מארז MONTHLY DETOX PACK במבצע" (monthly DETOX pack on sale, low-sugar)
- **Sample order codes:** `6608564`, `6724565`, `6768379`
- **Date range:** `2026-04-18 → 2026-04-18`; no pickup_at
- **Likely business meaning:** Monthly DETOX pack — sibling to §1.3 in the LOW-sugar (not no-sugar) variant. 4× FG-DET-* items.
- **bundle_map needs:** 1-2 component item_ids × 4 qty.
- **W4 recommendation:** Option A.
- **Tom default per dispatch:** A.

### §1.8 GTSET-LOW-JASMI-SENCH
- **Total rows:** 1 / **Total qty:** 1.00 / **Distinct orders:** 1
- **lw_name:** "מארז BRAIN BOOSTER במבצע" (BRAIN BOOSTER pack on sale)
- **Sample order codes:** `6595524`
- **Date range:** `2026-04-18 → 2026-04-18`; no pickup_at
- **Likely business meaning:** "Brain Booster" pack — likely Jasmine + Sencha tea variant. Composition unknown to W1.
- **bundle_map needs:** ≥ 1 component item_id (likely 2 — jasmine + sencha bottles).
- **W4 recommendation:** Option A.
- **Tom default per dispatch:** A.

### §1.9 GTSET-LOW-ENERG-DETOX
- **Total rows:** 1 / **Total qty:** 1.00 / **Distinct orders:** 1
- **lw_name:** "מארז ENERGY&DETOX במבצע" (ENERGY+DETOX pack on sale, low-sugar)
- **Sample order codes:** `6676336`
- **Date range:** `2026-04-18 → 2026-04-18`; no pickup_at
- **Likely business meaning:** Energy + Detox combination pack. Likely 2 component items.
- **bundle_map needs:** ≥ 2 component item_ids × qty.
- **W4 recommendation:** Option A.
- **Tom default per dispatch:** A.

### §1 Subtotal
- Distinct SKUs: **9** ✓
- Rows: **17+7+4+4+4+3+3+1+1 = 44** ✓
- Qty: **17+10+4+4+4+3+3+1+1 = 47** ✓

**Common observations across §1:**
- All 9 bundle SKUs were `order_created_at = 2026-04-18` — single batch ingest day.
- Zero rows have `pickup_at` populated. The picker discipline soak from `lionwheel_chain_repair_plan_2026-04-30.md` is still in flight; bundle SKUs are not yet exhibiting fresh inflows.
- All Hebrew names follow the pattern "מארז ... במבצע" ("box ... on sale"). This confirms the LionWheel side is treating these as standalone listing SKUs, not auto-decomposed at source.
- W1 cannot author composition — bundle composition (which constituent FGs) is operational governance only Tom owns.

---

## §2 Non-catalog (LWR-3) — 7 SKUs / 25 rows / 218 qty

**Tom decision needed (LWR-3):** per-SKU disposition. Three actions per cycle-19 decisions pack §3:
- **(A) Admit** — create canonical `items` row + alias map row.
- **(B) Keep visibility-only** — exception remains open; no admission. (W4-recommended default per cycle-17 §5.1.)
- **(C) Reject** — `integration_sku_map` row with `approval_status = 'rejected'`; future occurrences resolve to null silently.

**Tom default per dispatch:** B (keep visibility-only unless explicit map).

### §2.1 GT-GLA-CUP
- **Total rows:** 9 / **Total qty:** 11.00 / **Distinct orders:** 9
- **lw_name:** "Measuring Cup"
- **Sample order codes:** `24096912`, `24117299`, `24125088`
- **Date range:** order_created `2026-04-19 → 2026-04-29` (recurring across 11 days)
- **Why classified non-catalog:** "Measuring Cup" is a kitchen accessory, not a beverage. No `GT-GLA-*` items in catalog (catalog has FG-/ADD-/RM-/PKG- prefixes for beverage components). Recurrence over 11 days indicates this is a stock-managed accessory line on the LionWheel side.
- **Stock-managed?** Likely YES on LionWheel (recurrence pattern). Not stock-managed on platform — no items row exists.
- **Recommended action per-SKU:** **(B) keep visibility-only.** GT operations does not produce or stock measuring cups; if this is a re-sold accessory, Tom can decide later whether to admit (A) for inventory tracking purposes.
- **Tom default per dispatch:** B.

### §2.2 GT-PUE-FRE-1L
- **Total rows:** 5 / **Total qty:** 6.00 / **Distinct orders:** 5
- **lw_name:** "תה פואר ולימון ללא סוכר" (Pu'er and Lemon tea no-sugar)
- **Sample order codes:** `6577920`, `6597033`, `6600964`
- **Date range:** order_created `2026-04-18 → 2026-04-18` (single batch — no recurrence after 04-18)
- **Why classified non-catalog:** No `GT-PUE-*` items in catalog. The cycle-17 audit flagged this as "likely defunct PUE-Fresh line" — single-day appearance pattern supports defunct/legacy interpretation.
- **Stock-managed?** Probably no longer (single-day appearance). Could be a discontinued product still listed on LionWheel.
- **Recommended action per-SKU:** **(B) keep visibility-only** OR **(C) reject** if Tom confirms discontinued. Either is valid; reject is cleaner if confirmed defunct.
- **Tom default per dispatch:** B.

### §2.3 GT-MAT-KIT
- **Total rows:** 4 / **Total qty:** 4.00 / **Distinct orders:** 4
- **lw_name:** "Complete Matcha Kit"
- **Sample order codes:** `24269209`, `24294263`, `24295859`
- **Date range:** order_created `2026-04-27 → 2026-04-29` (recent recurrence)
- **Why classified non-catalog:** "Kit" is bundle-like with no component definition. No matching items row.
- **Stock-managed?** Unclear — recent recurrence suggests stock-managed on LionWheel side, but kit composition is unknown.
- **Recommended action per-SKU:** **(B) keep visibility-only** until Tom decides whether to (A) admit as a new bundle SKU (which then routes to LWR-1 / bundle_map flow), or (A) admit as a standalone catalog item.
- **Tom default per dispatch:** B.

### §2.4 GTMN-PIK-254
- **Total rows:** 4 / **Total qty:** 84.00 / **Distinct orders:** 4
- **lw_name:** "Pikadon 254"
- **Sample order codes:** `24073351`, `24326256`, `24329498`
- **Date range:** order_created `2026-04-19 → 2026-04-29` (recurring)
- **Why classified non-catalog:** No `GTMN-*` prefix in catalog. The "254" suffix and "Pikadon" name suggest a promotional/legacy item. **Highest-qty non-catalog row at 84 units** — bulk shipping pattern.
- **Stock-managed?** Likely YES (recurring + bulk qty pattern). High operational priority for Tom-decision: 84 unaccounted units is the largest single-SKU underplanning opportunity in this entire 90-row population.
- **Recommended action per-SKU:** **(B) keep visibility-only** initially; **escalate to Tom for (A) admit decision** because 84 units is operationally significant.
- **Tom default per dispatch:** B (with operational flag — see §6).

### §2.5 GT-GLA-MAT-PRINT
- **Total rows:** 1 / **Total qty:** 100.00 / **Distinct orders:** 1
- **lw_name:** "Matcha GT Printed Cup with Lid"
- **Sample order codes:** `24213747`
- **Date range:** order_created `2026-04-26 → 2026-04-26` (single-order)
- **Why classified non-catalog:** Printed accessory cup. Single 100-unit shipment indicates a one-off bulk order (possibly a B2B/wholesale customer or marketing-merch order).
- **Stock-managed?** Possibly — but single occurrence suggests one-off rather than recurring.
- **Recommended action per-SKU:** **(B) keep visibility-only.** If Tom confirms one-off, can also (C) reject. The 100-unit qty is high but is likely an accessory not subject to FG planning math.
- **Tom default per dispatch:** B.

### §2.6 GTEL-BAB-RED-0.75L
- **Total rows:** 1 / **Total qty:** 12.00 / **Distinct orders:** 1
- **lw_name:** "GT Babka Bakery Red Sangria Cocktail 750ml"
- **Sample order codes:** `24254076`
- **Date range:** order_created `2026-04-27 → 2026-04-27` (single order)
- **Why classified non-catalog:** No `GTEL-*` prefix. The "Babka Bakery" name suggests a co-branded product (GT × Babka Bakery). 12-unit bulk single-order pattern matches B2B/wholesale partnership delivery.
- **Stock-managed?** Possibly co-branded SKU — would require Tom-clarification on partnership status.
- **Recommended action per-SKU:** **(B) keep visibility-only.** If co-brand is active, Tom can (A) admit. If discontinued partnership, (C) reject.
- **Tom default per dispatch:** B.

### §2.7 7290003803217
- **Total rows:** 1 / **Total qty:** 1.00 / **Distinct orders:** 1
- **lw_name:** "מגרדת לזכוכית וקרמיקה" (glass and ceramic scraper)
- **Sample order codes:** `6714255`
- **Date range:** order_created `2026-04-18 → 2026-04-18` (single order)
- **Why classified non-catalog:** This is a **barcode (EAN-13 GS1 Israel prefix `729`)** populated as a SKU — not a GT-defined SKU. The lw_name confirms it's an accessory unrelated to GT product line ("glass scraper"). Likely a marketplace catalog leakage (a generic third-party item appearing in a GT order).
- **Stock-managed?** No — this is third-party stock, not GT stock.
- **Recommended action per-SKU:** **(C) reject** — barcode-as-SKU should never resolve to a GT items row. A rejected `integration_sku_map` entry would also serve as audit trail.
- **Tom default per dispatch:** B (but C is the more correct disposition long-term).

### §2 Subtotal
- Distinct SKUs: **7** ✓
- Rows: **9+5+4+4+1+1+1 = 25** ✓
- Qty: **11+6+4+84+100+12+1 = 218** ✓

**Common observations across §2:**
- §2.4 (GTMN-PIK-254 at 84 qty) and §2.5 (GT-GLA-MAT-PRINT at 100 qty) account for **184 of the 218 qty** — 84% of non-catalog volume is in 2 SKUs.
- §2.7 is unambiguously rejectable (barcode-as-SKU); the other 6 require Tom inspection.
- All non-catalog SKUs have `pickup_at = null` — same picker-discipline gap as §1.

---

## §3 Ambiguous (LWR-4) — 10 SKUs / 20 rows / 59 qty

**Tom decision needed (LWR-4):** per-candidate approval at `/admin/sku-aliases`. Three actions per cycle-19 decisions pack §4:
- **(A) Approve** — pick a specific candidate `item_id` and approve via `integration_sku_map` row (`approval_status='approved'`).
- **(B) Leave as exception** — no admission until further info (W4-recommended default).
- **(C) Reject** — `integration_sku_map` row with `approval_status='rejected'` if confirmed malformed/test data.

**Tom default per dispatch:** B (leave as exception unless deterministic).

**Confidence scoring legend:**
- `0.95+` deterministic — pattern + name + size all match a single existing item; ready to approve.
- `0.7–0.94` strong — pattern + partial name match; one candidate clearly leads but a name discrepancy exists.
- `0.4–0.69` moderate — token match but multiple candidates plausible OR name does not precisely fit.
- `<0.4` weak — substring match only; likely false-positive.

### §3.1 GTCC-MUZ-APPZ-1L
- **lw_name:** "Muza Apple Zest Cocktail 1000ml"
- **Total rows:** 4 / **Total qty:** 10.00 / **Distinct orders:** 4
- **Sample order codes:** `24124411`, `24124989`, `24126058`
- **Date range:** order_created `2026-04-20 → 2026-04-29` (recurring)
- **Candidate matches:**
  | Candidate | Confidence | Rationale |
  | --- | ---: | --- |
  | (none — no `ADD-MUZ-APP*` or `ADD-MUZ-*APPLE*` in catalog) | — | Apple Zest is not present in any of the 7 ADD-MUZ-*-1L catalog items |
- **Recommended action per-SKU:** **(B) leave as exception.** No deterministic candidate. New flavor / typo / discontinued — Tom-only call.
- **Tom default per dispatch:** B.

### §3.2 GTCC-MUZ-SMAR-1L
- **lw_name:** "Muza Spicy Margarita Cocktail 1000ml"
- **Total rows:** 4 / **Total qty:** 13.00 / **Distinct orders:** 4
- **Sample order codes:** `24124989`, `24125789`, `24267387`
- **Date range:** `2026-04-20 → 2026-04-29` (recurring)
- **Candidate matches:**
  | Candidate | Confidence | Rationale |
  | --- | ---: | --- |
  | `ADD-MUZ-MRCL-1L` (MUZA CLASSIC MARGARITA MIXER 1L) | 0.50 | Both are 1L Muza Margarita mixers, but "SMAR" likely = "Spicy MARgarita" while MRCL = "Margarita CLassic". **Different products by flavor profile** — should NOT auto-map. |
  | `FG-MAR-CLA-300ML` / `FG-MAR-PEA-300ML` / `FG-MAR-STR-300ML` | <0.30 | These are 0.3L finished cocktails, not 1L mixers. Wrong size + wrong supply method. |
- **Recommended action per-SKU:** **(B) leave as exception.** Spicy Margarita variant not in catalog. Tom-decide: admit new Spicy variant or treat as misnamed Classic.
- **Tom default per dispatch:** B.

### §3.3 GTCC-MUZ-TROJ-1L
- **lw_name:** "Muza Tropical in Japan Cocktail 1000ml"
- **Total rows:** 3 / **Total qty:** 13.00 / **Distinct orders:** 3
- **Sample order codes:** `24125789`, `24260733`, `24314996`
- **Date range:** `2026-04-20 → 2026-04-29` (recurring)
- **Candidate matches:**
  | Candidate | Confidence | Rationale |
  | --- | ---: | --- |
  | `ADD-MUZ-TRIL-1L` (MUZA TROPICAL ISRAELI MIXER 1L) | 0.55 | Both are "Tropical" + "MUZ" + "1L". But TROJ = "Tropical in Japan" vs TRIL = "Tropical Israeli" — **different geographic flavor variants by name**. Could be either (a) same product renamed Japan→Israeli (catalog rename) or (b) genuinely two different SKUs. Tom-decide. |
- **Recommended action per-SKU:** **(B) leave as exception** until Tom confirms whether `ADD-MUZ-TRIL-1L` was a rename of "Tropical in Japan" or a separate product.
- **Tom default per dispatch:** B.

### §3.4 GTCC-MUZ-PSSP-1L
- **lw_name:** "Muza Passion Spritz Cocktail 1000ml"
- **Total rows:** 2 / **Total qty:** 5.00 / **Distinct orders:** 2
- **Sample order codes:** `24125789`, `24126058`
- **Date range:** `2026-04-20 → 2026-04-20` (2-day window)
- **Candidate matches:**
  | Candidate | Confidence | Rationale |
  | --- | ---: | --- |
  | `FG-MUZ-PSC-200ML` (MUZA PASSION SPRITZ COCKTAIL 0.2L) | 0.65 | **Same flavor name (Passion Spritz)** but different size (0.2L vs 1L) and different role (FG cocktail vs ADD mixer). The `GTCC-MUZ-*-1L` pattern points to a 1L mixer that does not exist for Passion Spritz. |
- **Recommended action per-SKU:** **(B) leave as exception.** Strong name match but role mismatch (FG vs ADD/mixer). If Tom confirms a 1L mixer should exist for Passion Spritz, **(A) admit** new ADD-MUZ-PSC-1L item; otherwise leave.
- **Tom default per dispatch:** B.

### §3.5 GTCC-MUZ-ANBL-1L
- **lw_name:** "Muza Anise Bliss Cocktail 1000ml"
- **Total rows:** 2 / **Total qty:** 5.00 / **Distinct orders:** 2
- **Sample order codes:** `24124989`, `24125789`
- **Date range:** `2026-04-20 → 2026-04-20`
- **Candidate matches:**
  | Candidate | Confidence | Rationale |
  | --- | ---: | --- |
  | `ADD-MUZ-HER-1L` (MUZA HERBAL MULE BLISS MIXER 1L) | 0.45 | Both contain "Bliss" + "MUZ" + "1L". But HER = Herbal Mule, ANBL = Anise Bliss — **different flavors**. Substring overlap only on "Bliss". |
  | `ADD-GAR-ANISE` (STAR ANISE GARNISH) | 0.30 | Anise match but wrong role (garnish, not mixer) and wrong size. |
- **Recommended action per-SKU:** **(B) leave as exception.** No clean match. Anise Bliss is a likely-new flavor.
- **Tom default per dispatch:** B.

### §3.6 GTCC-MUZ-BLBR-1L
- **lw_name:** "Muza Blueberry Breeze Cocktail 1000ml"
- **Total rows:** 1 / **Total qty:** 6.00 / **Distinct orders:** 1
- **Sample order codes:** `24125789`
- **Date range:** `2026-04-20 → 2026-04-20`
- **Candidate matches:**
  | Candidate | Confidence | Rationale |
  | --- | ---: | --- |
  | `ADD-TAP-BLU-3400G` (TAPIOCA BLUEBERRY 3.4KG) | 0.20 | "Blueberry" token match but wrong product family (tapioca pearls, not mixer) and wrong size. |
- **Recommended action per-SKU:** **(B) leave as exception.** No `ADD-MUZ-BLU*` mixer in catalog; new flavor likely.
- **Tom default per dispatch:** B.

### §3.7 GTCC-MUZ-CHRBL-1L
- **lw_name:** "Muza Cherry Bloom Cocktail 1000ml"
- **Total rows:** 1 / **Total qty:** 3.00 / **Distinct orders:** 1
- **Sample order codes:** `24260733`
- **Date range:** `2026-04-27 → 2026-04-27`
- **Candidate matches:**
  | Candidate | Confidence | Rationale |
  | --- | ---: | --- |
  | (none — no `ADD-MUZ-CHR*` or `ADD-MUZ-*CHERRY*` or `ADD-MUZ-*BLOOM*` in catalog) | — | Cherry Bloom variant not present in any ADD-MUZ-*-1L catalog item. |
- **Recommended action per-SKU:** **(B) leave as exception.** New flavor likely.
- **Tom default per dispatch:** B.

### §3.8 AP-DRI-PIN
- **lw_name:** "Dried Pineapple 1000g"
- **Total rows:** 1 / **Total qty:** 1.00 / **Distinct orders:** 1
- **Sample order codes:** `24260733`
- **Date range:** `2026-04-27 → 2026-04-27`
- **Candidate matches:**
  | Candidate | Confidence | Rationale |
  | --- | ---: | --- |
  | (none — no `ADD-GAR-PIN-DRY` in catalog) | — | The cycle-19 W1 back-fill closed AP-DRI-ORA→ADD-GAR-ORA-DRY and AP-DRI-ROS→ADD-GAR-ROSE-DRY, but **no Pineapple variant exists in the ADD-GAR-*-DRY family**. |
  | `ADD-TAP-PIN-3400G` (TAPIOCA PINEAPPLE 3.4KG) | 0.25 | "Pineapple" + "Pin" match but wrong family (tapioca pearls, not dried garnish) and wrong size (3.4kg vs 1kg). |
- **Recommended action per-SKU:** **(B) leave as exception.** Either Tom (A) admits a new `ADD-GAR-PIN-DRY` item (consistent with the AP-DRI-* family pattern), or leaves as exception.
- **Tom default per dispatch:** B.

### §3.9 AP-FRO-MAT
- **lw_name:** "Matcha Frother"
- **Total rows:** 1 / **Total qty:** 1.00 / **Distinct orders:** 1
- **Sample order codes:** `24219159`
- **Date range:** `2026-04-26 → 2026-04-26`
- **Candidate matches:**
  | Candidate | Confidence | Rationale |
  | --- | ---: | --- |
  | (none — `ADD-FRO-*` family does not exist in catalog) | — | "Frother" is a kitchen accessory, not a beverage component. |
- **Recommended action per-SKU:** **(B) leave as exception** OR (debate-worthy) **reclassify as non-catalog** (LWR-3) since "Frother" is an accessory like §2.1 GT-GLA-CUP. Currently classified ambiguous because of the `AP-` prefix rule — this is a classifier limitation, not a real ambiguity.
- **Tom default per dispatch:** B.

### §3.10 AP-TAP-PIN
- **lw_name:** "Pineapple Tapioca Pearls 1300g"
- **Total rows:** 1 / **Total qty:** 2.00 / **Distinct orders:** 1
- **Sample order codes:** `24213747`
- **Date range:** `2026-04-26 → 2026-04-26`
- **Candidate matches:**
  | Candidate | Confidence | Rationale |
  | --- | ---: | --- |
  | `ADD-TAP-PIN-3400G` (TAPIOCA PINEAPPLE 3.4KG) | **0.80** | **Same product (Pineapple Tapioca Pearls)** but different pack size (1.3kg requested vs 3.4kg catalog). Likely a smaller retail pack of the same SKU. |
- **Recommended action per-SKU:** **(A) consider approving** → `ADD-TAP-PIN-3400G` IF Tom confirms 1.3kg and 3.4kg are the same product in different pack sizes (which would imply a UOM/pack-size conversion at the alias layer). OR **(B) leave as exception** until Tom decides whether to (A) admit a new `ADD-TAP-PIN-1300G` item (cleaner — preserves pack-size semantics).
- **Tom default per dispatch:** B (cleaner — admit new SKU rather than alias to a different pack size).

### §3 Subtotal
- Distinct SKUs: **10** ✓
- Rows: **4+4+3+2+2+1+1+1+1+1 = 20** ✓
- Qty: **10+13+13+5+5+6+3+1+1+2 = 59** ✓

**Common observations across §3:**
- 7 of 10 ambiguous SKUs are `GTCC-MUZ-*-1L` Muza cocktail mixer variants. Tom has actively curated 5 ADD-MUZ-*-1L catalog items already (BZSM, HER, JASM, MRCL, PNMM, PRPL, TRIL — wait, that's 7 actually counting from §1 catalog probe). The LionWheel side appears to be selling a wider Muza flavor lineup than the platform catalog supports. This is consistent with a "catalog catching up to LionWheel" pattern rather than data drift.
- 2 of 10 (`AP-FRO-MAT`, `AP-TAP-PIN`) are arguably misclassified into ambiguous because of the `AP-` prefix rule; they're closer to non-catalog or pack-size variant.
- 1 of 10 (`AP-DRI-PIN`) is a clean opportunity for a new `ADD-GAR-PIN-DRY` admit if Tom rules.

---

## §4 Malformed — 1 row / 1 SKU

### §4.1 Single empty-string SKU row (historical, preserved)
- **line_mirror_id:** `f3212ae9-a01e-473a-a0cf-a51df110587f`
- **lw_sku:** `''` (empty string)
- **lw_name:** "מקציף חשמלי" (electric whisk/frother)
- **lw_qty_ordered:** 1.00
- **mirror_id:** (parent order — not enumerated; sample order code below)
- **Sample order code:** `24117299`
- **Order created at:** `2026-04-20 12:15:02 IL`
- **pickup_at:** null
- **resolution_status:** `unresolved`
- **item_id:** null

**Status:** **PRESERVED historical**. Per cycle-17 §6 + cycle-19 carve-out, this single row is the audit trail for the malformed-line class. Future occurrences are rejected at parse time per cycle-19 commit `3ac1964` empty-string SKU handling.

**Recommendation:** **leave as-is** unless Tom wants cleanup. Cleanup would require a bespoke data-only DELETE script (with audit-trail row in `change_log`) — not justified for a single visibility-only row that is operationally inert.

**Tom default per dispatch:** leave-as-is.

---

## §5 Admin route map — where Tom acts

### §5.1 SKU alias surface — `/admin/sku-aliases`
**Path:** `c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(admin)/admin/sku-aliases/page.tsx`

**What it supports today:**
- Channel tab selector via `?channel=lionwheel|shopify` URL query parameter (default = lionwheel).
- Lists all unmapped external SKUs (sourced from `/api/exceptions?category=lionwheel_unknown_sku&status=open&limit=500`) — this is exactly the inbox needed for LWR-4 ambiguous-resolution decisions.
- Per-SKU dropdown to pick an internal `items.item_id`.
- BATCH approve via `POST /api/integration-sku-map/approve` — closes both the alias mapping AND the related exceptions in one action.
- Read-only audit list of already-approved aliases.

**What it does NOT support today (would be future enhancement, not blocking):**
- No URL-query deep-link to a specific external SKU. Tom must scroll/scan the inbox manually. **Future enhancement:** add `?source_sku=<sku>` URL parameter that auto-scrolls + highlights the matching row.
- No "mark as reject" action — only approve. To reject a SKU (LWR-3 path C, LWR-4 path C), Tom currently must (a) leave as exception AND (b) author the reject mapping via direct DB or admin panel that does not exist. **Future enhancement:** add reject button to approval surface.
- No per-row link from `/exceptions` or `/planning/blockers` "fix this" → `/admin/sku-aliases?source_sku=...`. **Future enhancement:** wire `resolveExceptionDeepLink()` for `lionwheel_unknown_sku` to land on `/admin/sku-aliases?channel=lionwheel&source_sku=<sku>`.

### §5.2 Items master — `/admin/masters/items` (admit path)
**Path:** `c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(admin)/admin/masters/items/` (multiple files; full path enumeration not required for this surface).

**What it supports:**
- Admin can author a new `items` row (LWR-3 path A, LWR-4 path A admit). New item must be paired with an alias map row at `/admin/sku-aliases`.

### §5.3 Exception inbox — `/exceptions?category=lionwheel_unknown_sku`
**Path:** consumer of `/api/exceptions` query endpoint.

**What it supports:**
- Filter to `category=lionwheel_unknown_sku` to see all unmapped-SKU exceptions (open count snapshot today: 28 — see §6.4 W4 reconciler note).
- "Acknowledge" / "Resolve" inline actions per exception (per gate-3 closure).

### §5.4 Planning blockers — `/planning/blockers`
**Path:** consumer of `/api/v1/queries/planning/blockers` endpoint.

**What it supports:**
- LionWheel unmapped-SKU rows surface here as planning blockers when a planning run is active. Currently no run pulls these in (per §7 boundary statement — no live-on-LionWheel-mirror-driven run yet).

### §5.5 Bundle map — proposed at `/admin/bundles` (LWR-1 Option A path)
**Status:** NOT YET BUILT.

**Per cycle-18 lionwheel_bundle_map_contract.md:** Once Tom rules LWR-1 Option A, a fresh dispatch creates `private_core.bundle_map` table + curated `api_read.v_bundle_decomposed_demand` view + W2 admin surface `/admin/bundles` for per-bundle composition authoring. Until LWR-1 lands, §1 has no admin surface.

### §5.6 Per-row deep-link summary (today + future)

| LW SKU | Today (manual scroll) | Future (deep-link enhancement) |
| --- | --- | --- |
| GTCC-MUZ-* (7) | `/admin/sku-aliases?channel=lionwheel` (scroll to find) | `/admin/sku-aliases?channel=lionwheel&source_sku=<sku>` |
| AP-* (3) | same | same |
| GT-* / GTMN-* / GTEL-* / 7290003803217 (7) | same | same |
| GTSET-* (9) | none (no admin surface) | `/admin/bundles` (post LWR-1 Option A + bundle_map) |
| empty-string (1) | n/a (no action recommended) | n/a |

---

## §6 Unblock leverage table

| Decision | Unblocks rows | Unblocks SKUs | Unblocks qty | Implementation cost |
| --- | ---: | ---: | ---: | --- |
| **LWR-1 Option A** (bundle_map) | 44 | 9 | 47 | W1 + W4 cycle: bundle_map migration + curated view + `/admin/bundles` admin UI + Tom authors composition per-bundle |
| **LWR-3 per-SKU disposition** (admit/dismiss/reject) | 25 | 7 | 218 | per-SKU admin action (no engineering); §2.4 GTMN-PIK-254 alone unblocks 84 qty |
| **LWR-4 per-candidate approval** | 20 | 10 | 59 | per-SKU admin action (no engineering); 0 deterministic candidates means each is Tom-decide-only |
| Malformed cleanup | 1 | 1 | 1 | optional cleanup script — not recommended |
| **Total** | **90** | **27** | **325** | recoverable via Tom decisions (no engineering blocker except LWR-1 Option A) |

**Operational priority ranking (Tom Tax — daily friction lens):**
1. **LWR-3 single highest-leverage row:** §2.4 GTMN-PIK-254 (84 qty across 4 recurring orders) — single decision unblocks 26% of the entire 325-qty population.
2. **LWR-1 single highest-leverage row:** §1.1 GTSET-LOW-6FLAV-SALE (17 rows / 17 qty) — but blocked on Option A authoring path.
3. **LWR-4 single highest-leverage row:** §3.10 AP-TAP-PIN (only deterministic-candidate-with-name-match in §3, but pack-size discrepancy means cleaner admit-as-new-item path).
4. **LWR-3 reject-eligible:** §2.7 7290003803217 (barcode-as-SKU; cleanly rejectable by EAN-13 pattern).

**§6.1 W4 reconciler open-exception count gap:** Live snapshot shows **28 open `lionwheel_unknown_sku` exceptions** but only **27 distinct unresolved SKUs** in the mirror line population. The 1-exception delta likely reflects either (a) the malformed empty-string row firing an exception under `lionwheel_schema_drift` instead (which would not match the count), or (b) an open exception for a SKU whose mirror lines have all since resolved. This is a W4 reconciler housekeeping concern — surfaced for visibility, not blocking any LWR-1/3/4 decision.

---

## §7 Boundary statement

- **LionWheel demand-side:** 14 of 104 historical rows resolved cycles 18-19 (cycle-18 JASM/PNMM alias creation + cycle-19 W1 historical back-fill of JASM 2 + PNMM 9 + AP-DRI-ORA 2 + AP-DRI-ROS 1 = 14 rows). 90 rows remain on the Tom-decision surface enumerated above.
- **Stock truth on stock-side bridge MC-U2:** still **DISABLED** per A4 LOCK. No LionWheel-driven demand currently affects `current_balances`, `stock_ledger`, or any planning-engine projection.
- **Planning math impact:** zero corruption. Per `lionwheel_remaining_unresolved_breakdown_2026-05-02.md` §7.2: the 90 rows are **default-excluded-but-visible**. No autonomous catalog growth, no autonomous decomposition, no autonomous reconciliation.
- **Operator visibility impact:** all 90 rows surface at `/exceptions?category=lionwheel_unknown_sku` and at `/planning/blockers`. The ambiguous and bundle subsets also fire `lionwheel_unknown_sku` exceptions per cycle-17 §3.2 + §4 + §5.2.
- **What ships when LWR-1/3/4 close:** demand recovery for up to 325 qty across 27 distinct SKUs once Tom rules. Three rulings recover three populations independently — no ordering dependency between them.
- **What does NOT ship from this artifact:** no `RUNTIME_READY` signal; no migration; no view body change; no portal authoring; no API change; no `bundle_map` table (gated on LWR-1 Option A ruling + fresh dispatch).

**Forbidden phrasing per dispatch:** this document does not assert "production-ready", "Gate 3 closed", "stock truth closed", or "LionWheel chain complete". The cycle-21 outcome is: a Tom-decision-ready surface with concrete data per-SKU, sourced from live DB, with explicit honest gaps documented where business meaning is Tom-only knowledge.

---

## §8 Files referenced

**Inspection scripts (created cycle 21, gt-factory-os/scripts/):**
- `_w1_lionwheel_decision_surface_inspect.mjs` — main per-SKU detail probe (live DB read-only).
- `_w1_lionwheel_decision_surface_inspect2.mjs` — broader candidate match probe across `private_core.items` for §3 ambiguous SKUs.

**Live-DB connection used:** `DATABASE_URL_POOLED` from `gt-factory-os/.env` → Supabase pooler `aws-1-eu-central-1.pooler.supabase.com:5432`, project `rvadsozabmxkkrktwgnv`, PG17. Read-only. Zero writes.

**Portal admin surface inspected (read-only header check):** `c:/Users/tomw2/Projects/window2-portal-sandbox/src/app/(admin)/admin/sku-aliases/page.tsx` (no edits).

**Cycle 17/19/20 prior outputs cross-referenced:**
- `PRODUCTION/docs/qa/lionwheel_unresolved_demand_audit_2026-05-02.md`
- `PRODUCTION/docs/qa/lionwheel_alias_review_candidates_2026-05-02.csv`
- `gt-factory-os/docs/lionwheel_unresolved_math_reconciliation_2026-05-02.md`
- `gt-factory-os/docs/integrations/lionwheel_remaining_unresolved_breakdown_2026-05-02.md`
- `gt-factory-os/docs/integrations/lionwheel_remaining_tom_decisions_2026-05-02.md`

**End of decision surface.**
