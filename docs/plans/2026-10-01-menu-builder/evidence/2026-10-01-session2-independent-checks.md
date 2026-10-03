# Session 2 independent checks — 2026-10-01

> Read-only. Re-derived by Session 2 from the code, the live DB (Supabase `rvadsozabmxkkrktwgnv`, `SELECT` only), live Shopify prices (read-only GraphQL) and the brain's figures. Nothing here is authority; it is the evidence behind `08-independent-review.md`.

## 1. Figures file (`.claude/skills/drinks-pricelist/drinks_final_figures.json`, `_meta.date` 2026-09-29)

- 48 pages, keys 8…64. Fields are **display strings**, not numbers: `cost "₪3.25"`, `price "₪20"`, `marg "81%"`, `prof "₪13.70 לכוס"`. The Builder's synced copy needs a strict parser.
- `prof = price/1.18 − cost` and `marg = round((price/1.18 − cost)/(price/1.18) × 100)`: **48/48 match, 0 mismatches.**
- `_meta.cost_basis`: "ex-VAT ingredients only — excludes garnish, ice, water, soda, packaging and labour". `_meta.status`: "estimated ingredient cost based on a standardized ice-filled serving".
- The figures carry no group, sub-family or product; those come from the drink table below.

## 2. Live list prices (Shopify, read-only, 2026-10-01)

Concentrate 1 L ₪65 · 500 ml ₪33 · matcha 500 g `GT-SHI-CER-500` ₪590 · ube 500 g ₪175 · purée 1 L ₪60 · matcha kit `GT-MAT-KIT` ₪170 · frother `AP-FRO-MAT` ₪100. ARCHIVED products share the SKUs `GT-HIB-LOW-1L`, `GT-LUI-LOW-1L`, `GT-MAS-CHA-1L` at ₪139 (the live portal prices the ACTIVE ₪65 variants; recorded, not chased).

## 3. Draft drink → product → dose table (U-MB-2, **not Tom-verified**)

Products from Session 1's recipe-text derivation (`2026-10-01-drinks-products-data-map.md` line 49), doses from `docs/pricing/2026-09-29_cost_model.py`. Every one of the 48 figures pages maps (asserted in the script). Known open data defects stay open: p12's name, p33 matcha-masala 40 ml (model) vs 50 ml (Canva page), p36's copied recipe.

| Page | Drink | GT product → dose per cup |
|---|---|---|
| 8 | חליטת היביסקוס וליים | FRESH `fresh:1l` 50 ml |
| 9 | חליטת קמומיל ותפוח | CALM `calm:1l` 50 ml |
| 10 | חליטה מדברית | DESERTEA `desertea:1l` 50 ml |
| 11 | חליטת סנצ'ה ופסיפלורה | REVIVE `revive:1l` 50 ml |
| 12 | חליטת תה ירוק וליים | DETOX `detox:1l` 50 ml |
| 13 | חליטת תה ירוק ולמון גראס | ENERGY `energy:1l` 50 ml |
| 14 | חליטת יסמין וליצ'י | CONSCIOUSNESS `consc:1l` 50 ml |
| 16 | לימונדת היביסקוס וליים | FRESH `fresh:1l` 50 ml |
| 17 | לימונדה מדברית | DESERTEA `desertea:1l` 50 ml |
| 18 | לימונדת צ'אי מסאלה | NAMASTEA `namastea:1l` 50 ml |
| 20 | חליטת אפרסק מדברית | DESERTEA `desertea:1l` 40 ml + מחית אפרסק `peach:1l` 40 ml |
| 21 | חליטת תות לואיזה | DETOX `detox:1l` 40 ml + מחית תות `strawberry:1l` 40 ml |
| 22 | חליטת מנגו סנצ'ה | REVIVE `revive:1l` 40 ml + מחית מנגו `mango:1l` 40 ml |
| 23 | חליטת תפוח היביסקוס | FRESH `fresh:1l` 40 ml |
| 25 | גזוז יסמין וליצ'י | CONSCIOUSNESS `consc:1l` 40 ml |
| 26 | גזוז מדברי ואפרסק | DESERTEA `desertea:1l` 40 ml + מחית אפרסק `peach:1l` 40 ml |
| 27 | גזוז היביסקוס ותפוח | FRESH `fresh:1l` 40 ml |
| 29 | אייס מאצ'ה קלאסי | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g |
| 30 | אייס מאצ'ה מנגו | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g + מחית מנגו `mango:1l` 40 ml |
| 31 | אייס מאצ'ה תות | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g + מחית תות `strawberry:1l` 40 ml |
| 32 | אייס מאצ'ה אפרסק | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g + מחית אפרסק `peach:1l` 40 ml |
| 33 | אייס מאצ'ה מסאלה | NAMASTEA `namastea:1l` 40 ml + מאצ׳ה 500 ג׳ `matcha:500` 1.8 g |
| 34 | מאצ'ה אגבה על הקרח | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g |
| 36 | אייס מאצ'ה וניל | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g |
| 37 | אייס מאצ'ה פיסטוק | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g |
| 38 | אייס מאצ'ה שומשום שחור | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g |
| 39 | אייס מאצ'ה קפה | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g |
| 40 | אייס מאצ'ה בננה | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g |
| 42 | מאצ'ה קוקוס אגבה | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g |
| 43 | מאצ'ה קוקוס ליצ'י | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g |
| 44 | מאצ'ה קוקוס תות | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g + מחית תות `strawberry:1l` 40 ml |
| 45 | מאצ'ה קוקוס מנגו | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g + מחית מנגו `mango:1l` 40 ml |
| 46 | מאצ'ה קוקוס אפרסק | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g + מחית אפרסק `peach:1l` 40 ml |
| 48 | אייס צ'אי מסאלה קלאסי | NAMASTEA `namastea:1l` 50 ml |
| 49 | צ'אי מסאלה על הקרח | NAMASTEA `namastea:1l` 50 ml |
| 50 | דירטי צ'אי | NAMASTEA `namastea:1l` 50 ml |
| 51 | צ'אי מסאלה תפוז וטוניק | NAMASTEA `namastea:1l` 50 ml |
| 52 | צ'אי מסאלה פינק טוניק | NAMASTEA `namastea:1l` 50 ml |
| 53 | צ'אי מסאלה ומיץ תפוזים | NAMASTEA `namastea:1l` 50 ml |
| 55 | צ'אי מסאלה קולד פואם וניל | NAMASTEA `namastea:1l` 50 ml |
| 56 | צ'אי מסאלה קולד פואם פיסטוק | NAMASTEA `namastea:1l` 50 ml |
| 57 | צ'אי תאילנדי קוקוס קולד פואם | NAMASTEA `namastea:1l` 50 ml |
| 58 | צ'אי מסאלה קולד פואם בננה | NAMASTEA `namastea:1l` 50 ml |
| 60 | אייס אובה תות | אובה 500 ג׳ `ube:500` 2 g + מחית תות `strawberry:1l` 40 ml |
| 61 | אייס אובה מנגו | אובה 500 ג׳ `ube:500` 2 g + מחית מנגו `mango:1l` 40 ml |
| 62 | אייס אובה אפרסק | אובה 500 ג׳ `ube:500` 2 g + מחית אפרסק `peach:1l` 40 ml |
| 63 | אייס אובה מסאלה | NAMASTEA `namastea:1l` 50 ml + אובה 500 ג׳ `ube:500` 2 g |
| 64 | אייס אובה מאצ'ה | מאצ׳ה 500 ג׳ `matcha:500` 1.8 g + אובה 500 ג׳ `ube:500` 2 g |

## 4. The five context sets as Builder starting kits (list prices, round-up rule as specified in `09-…` §19)

| Context set (D-026) | Products | Base kit ex-VAT | After round-up | Incl. VAT | Largest line | Note |
|---|---|---|---|---|---|---|
| `opening` (8 drinks) | 5 | ₪1,100 | ₪1,100 | ₪1,298 | מאצ׳ה 500 ג׳ ×1 = ₪590 (54%) for 2 drink(s) | — |
| `matcha` (8 drinks) | 4 | ₪960 | ₪960 | ₪1,133 | מאצ׳ה 500 ג׳ ×1 = ₪590 (61%) for 8 drink(s) | — |
| `tea` (8 drinks) | 10 | ₪1,270 | ₪1,270 | ₪1,499 | FRESH ×2 = ₪130 (10%) for 2 drink(s) | — |
| `chai` (8 drinks) | 1 | ₪130 | ₪910 | ₪1,074 | NAMASTEA ×14 = ₪910 (100%) for 8 drink(s) | raised: +12 × NAMASTEA |
| `ube` (5 drinks) | 6 | ₪1,255 | ₪1,255 | ₪1,481 | מאצ׳ה 500 ג׳ ×1 = ₪590 (47%) for 1 drink(s) | — |

Reading: the spec's acceptance criterion 6 tested only `opening`. `chai` is a one-product menu, so the ₪800 rule turns its ₪130 base into 14 bottles. `ube` spends 47% of the kit on matcha for one drink (p64). `tea` is the widest set (10 products for 8 drinks).

## 5. Small menus under the ₪800 minimum

| Selection | Base | After round-up | Kit |
|---|---|---|---|
| חליטת היביסקוס וליים | ₪130 | ₪910 | FRESH ×14 (≈280 כוסות) |
| חליטת היביסקוס וליים, לימונדת היביסקוס וליים, גזוז היביסקוס ותפוח | ₪130 | ₪910 | FRESH ×14 (≈280 כוסות) |
| אייס צ'אי מסאלה קלאסי, צ'אי מסאלה על הקרח | ₪130 | ₪910 | NAMASTEA ×14 (≈280 כוסות) |
| אייס מאצ'ה קלאסי | ₪590 | ₪1180 | מאצ׳ה 500 ג׳ ×2 (≈554 כוסות) |
| אייס מאצ'ה קלאסי, מאצ'ה אגבה על הקרח | ₪590 | ₪1180 | מאצ׳ה 500 ג׳ ×2 (≈554 כוסות) |
| אייס מאצ'ה תות | ₪710 | ₪830 | מאצ׳ה 500 ג׳ ×1 (≈277 כוסות) · מחית תות ×4 (≈100 כוסות) |
| אייס אובה תות | ₪295 | ₪885 | אובה 500 ג׳ ×3 (≈750 כוסות) · מחית תות ×6 (≈150 כוסות) |
| אייס אובה מסאלה | ₪305 | ₪825 | NAMASTEA ×10 (≈200 כוסות) · אובה 500 ג׳ ×1 (≈250 כוסות) |
| אייס אובה מאצ'ה | ₪765 | ₪940 | מאצ׳ה 500 ג׳ ×1 (≈277 כוסות) · אובה 500 ג׳ ×2 (≈500 כוסות) |

Shelf life (Sales-Machine `knowledge/claims/public-claims.yaml#shelf_life`, approved, Tom 2026-08-31): concentrates one year closed without refrigeration, three months refrigerated after opening; powders two years. The surplus is cash tied up, not spoilage, for concentrates and powders. Purée shelf life is not in any approved claim.

## 6. Live DB and code facts used by the review

| Fact | Value | Source |
|---|---|---|
| Leads by status | new 146 · working 38 · won 5 · lost 72 | `sales_core.lead` |
| `lj.order` taps → live lead links → lead orders | 4 → 2 → **0** | `lead_event` `button_tap`, `customer_portal.lead_link`, `lead_submission` |
| Portal customer orders | 4 `created` | `customer_portal.order_submission` |
| `sales_core.task`, `task_event`, `lead_wait` | **exist in production**, 0 rows; trigger `lead_event_task` and `lead_task_owner` attached; index `task_one_open_reply_per_lead` (D17 of the 2026-10-01 closure design); `app_setting.activity_required = {"enabled": false}`; no 0362 row in `supabase_migrations.schema_migrations` | catalog queries |
| PR #329 / #239 | open, **draft**, unmerged; heads `9d423c1` / `4b94597` | GitHub |
| `lead_event.event_type` CHECK | 19 values incl. `draft_order`, `button_tap`, `kit_sent` (content kit, unrelated to the starter kit) | `pg_constraint` |
| `v_sales_attention.stalled` | `max(any lead_event.created_at) < now() − 14 days`; 616 automated `reminder_sent` rows already reset it | `pg_get_viewdef` |
| `customer_portal_live` | `enabled=true`, `{"allowlist":"*"}`; the lead routes check `enabled` only | `feature_flags`, `routes.ts:308,319` |
| Lead link | 14 days, reusable until the first draft; `closeLinks` sets `used_at` on **every** link of the lead (`lead.ts:220,295`); every wake-up step mints a fresh link (`wake.ts:204`) | code |
| API process | one Fastify app hosts the portal **and** all Factory OS routes (stock, goods receipts, production, planning) | `api/src/server.ts` |
| Ordering-page bar | shows the running subtotal and the minimum meter: `לפני מע״מ · מינימום ₪800` / `לפני מע״מ · עברתם את המינימום` | `index.html:579-582, 1120-1138` |
| Ordering-page card | `<article>` with separate controls, not a button | `index.html:812-826` |
| Approved help reply | `TEXT.moreInfo` "בשמחה! נתקשר אליכם בהקדם לשיחה קצרה. בינתיים, כאן תמצאו תשובות לכל השאלות החשובות שלכם…" + `FAQ_BUTTON` `שאלות ותשובות` | `lead_texts.ts:32,46` |
| PDF economics term | "נשאר לך" = "המחיר פחות מע״מ, פחות עלות הרכיבים. גם האחוז … מחושב כך." | `drinks-pricelist/build.py:150-158` |
| Sales module scope | Amendment A (approved 2026-08-17) covers the customer journey incl. the interactive catalog (stage 4); no new-module declaration is needed | brain `docs/decisions/modules/sales-declaration.md` |
| D-018 (CONFIRMED) | "Neither the price of the opening menu nor the food cost per drink is ever stated by the system" | Sales-Machine `doctrine/decisions.md` |
| Outreach flag | the Sales workstream reports `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED=true` on Railway and 4 real `first_menu` sends (status branch `ac43857`) | Sales-Machine `status/gt-pulse-a-2026-09-30` |
