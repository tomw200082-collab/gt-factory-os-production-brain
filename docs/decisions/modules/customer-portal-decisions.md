# Tom decisions — `customer-portal`

**Status: PROPOSED — awaiting Tom's written approval (D1). Not approved; nothing in this file is in force.**

> **What this is.** The decisions log for `docs/decisions/modules/customer-portal-declaration.md`
> (`MODULE_TEMPLATE.md` §17). Opened 2026-09-24.
>
> **Sources and how D1 is given:** declaration header. This file records Tom's answer row by row.
>
> **This file is public.** It holds no customer name, phone number, price paid, Shopify customer id
> or host name, and gives counts only.

## A. Proposals awaiting D1 (masterprompt r2 §1.2)

| Item | Proposal | Status | Tom's answer (his words, date) |
|---|---|---|---|
| §1.2-1 | **The module.** The name is `customer-portal`. Its private schema `customer_portal` holds the five W2 tables (`access`, `session`, `link`, `registration`, `order_submission`), and it touches no core table. Outside its schema, the only row it writes is its own flag row in `private_core.feature_flags`. **Owner lanes:** `backend-db` (API, migration), `portal` (staff screen, tranche 179) and `integration` (the Shopify order write and the WhatsApp replies). The existing executor agents do the work under the module's scope, so no new agent files are needed. **Writes outside the schema:** (a) Shopify `draftOrderCreate` and `draftOrderComplete(paymentPending:true)`, tagged `portal`, through the backend's existing app token. (b) WhatsApp text replies through the existing order-line sender, sent only in answer to a customer's own login message, plus one order confirmation inside the 24-hour window. These are transactional, not outreach, and `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` does not govern them. (c) Nothing is written to `order_intake.wa_customer_map`. The portal keeps its own phone → customer table, backfilled from the map (§1.2-4), which grows only through staff approvals. **Nothing else is written:** not the engine, Green Invoice, LionWheel, stock or planning. | `PROPOSED 2026-09-24 — awaiting Tom` | — |
| §1.2-2 | **Exceptions to authority documents, for this module only.** (1) Customer pricing by the family rule, as the explicit confirmation `LOCKED_DECISIONS.md:326` asks for. (2) Customers log in by WhatsApp link, not Supabase magic link (`LOCKED_DECISIONS.md:98`, `EXECUTION_POLICY.md:138`). Staff auth is untouched; customers are a separate realm. (3) "System does not own customer orders" (`LOCKED_DECISIONS.md:129`) still holds: the portal keeps a submission log only, and Shopify owns the order. (4) The order engine is used through a wrapper and never edited. | `PROPOSED 2026-09-24 — awaiting Tom` | — |
| §1.2-3 | **Who counts as approved at launch.** Spec §4.3 item 3 speaks of "the existing 195 manually mapped phones". They are not manual: 194 were auto-resolved by the bot because the phone is on exactly one Shopify customer record, and only 1 row is manual. **Proposal:** those same 195 rows (194 + 1) may log in, because in each case the phone sits on that customer's own record. The 15 rows auto-resolved across several accounts, and every phone added to the map after the migration, go through registration and staff approval. **Alternative:** if Tom wants a person to approve every row, the backfill is empty, and the staff screen then needs a bulk "approve" for the single-match rows. That would be a new item for his approval. | `PROPOSED 2026-09-24 — awaiting Tom` | — |
| §1.2-4 | **The access rule, as the migration backfills it:** every map row with a `shopify_customer_id` whose note does not start with `auto-resolved from Shopify;`. | `PROPOSED 2026-09-24 — awaiting Tom` | — |
| §1.2-5 | **Launch control replaces the ≥24h soak** of `MODULE_TEMPLATE.md` §11 for this module. There is one flag, `private_core.feature_flags.customer_portal_live`, with `enabled` and `value.allowlist` (a comma-separated list of Shopify customer ids, or `*`). It is the only switch, and turning it off is the rollback. While it is off, or for a customer not on the allowlist, the portal behaves as if it did not exist: login messages fall through to the bot unchanged, and the portal APIs answer `PORTAL_CLOSED`. Before launch it may be enabled for the internal test mapping only. Pilots and `*` happen only on Tom's word. The safety evidence that replaces the soak is D3, D4 and D8, plus Tom's own first order. | `PROPOSED 2026-09-24 — awaiting Tom` | — |
| §1.2-6 | **Staff approval screen:** `/admin/portal-registrations` in `gt-factory-os-portal`, in English, for the `admin` role only. Whoever holds admin approves; today that is Tom. It also offers **"Create login link"**: a one-time link for a customer with access, which a person sends by hand. It lets pilots start even before WhatsApp sending is fixed. | `PROPOSED 2026-09-24 — awaiting Tom` | — |
| §1.2-7 | **Test access.** One-time login links may be made for the internal test mapping only: one per verification pass, so at most two. Only their hash is stored, through `apply_migration` entries named `data_portal_e2e_link_<date>_<n>`. Each link is used for D8, and its session is then revoked. This is never done for any other account. | `PROPOSED 2026-09-24 — awaiting Tom` | — |
| §1.2-8 | **Out of the catalog.** Besides 0.3 L, four `D-010(א)` items are active in Shopify but not sold: `GT-SHI-CER-30`, `GT-SHI-CER-50`, `GTCFR-GTCOC-FRO` and `AP-JUG-NEA`. They are never shown, even to a customer who bought them before. | `PROPOSED 2026-09-24 — awaiting Tom` | — |
| §1.2-9 | **Customer-facing text:** every Hebrew string in masterprompt Appendix A, exactly as written (declaration Appendix A); every Hebrew string in the design reference `index.html` except its demo line, which is removed; and the site-entry label `כניסת לקוחות`. Any other customer-facing string is not approved. Until Tom approves one, the nearest Appendix A string is used. | `PROPOSED 2026-09-24 — awaiting Tom` | — |
| §1.2-10 | **The site entry** goes into an unpublished theme copy. Publishing it is Tom's act. | `PROPOSED 2026-09-24 — awaiting Tom` | — |

## B. Decided in Phase A, 2026-09-24 (masterprompt §1.1). Not reopened here.

Every row cites the spec section and date. The last column says exactly how the decision was made:
in Tom's own words (quoted verbatim), by "no objection recorded", or as a fact stated to Tom.

| # | Decision | Record | How it was decided |
|---|---|---|---|
| S1 | v1 is the simplest possible. | spec §4 row 3, §4.2 (2026-09-24) | In Tom's words (his Q3 answer; the spec's quote ends in "…"): `אנחנו צריכים קודם לעשות את זה הכי פשוט ובייסיק שאפשר- better done than perfect. לגבי הזמנה שלא עוברת את המינימום- פשוט לא לאשר ולצרף כפתור של יצירת קשר בווצאפ במקרה של בקשה חריגה או משהו כזה. בעניין של המחירים- פשוט תציג מחירים בדף עצמו ואז לקוח שחושב שמגיע לו מחיר אחר יוכל פשוט ליצור קשר, אנחנו נעשה את הכי טוב שלנו אבל ברגע שהכל מוצג ללקוח אין בעיה כי הוא מבין כמה צריך לשלם…` |
| S2 | Every portal order is a real Shopify order, placed as a draft, then completed, and tagged `portal`. There is no draft path for customers and no exceptions queue. | spec §4.2 (2026-09-24) | The spec's reading of Tom's Q3 answer ("Tom changed it to simpler", spec §4 row 3). It replaces the earlier "an exception becomes a draft" design. |
| S3 | Below the minimum, sending is blocked and a WhatsApp contact button is shown. | spec §4 row 3, §4.2 (2026-09-24) | In Tom's words, part of the S1 quote: `לגבי הזמנה שלא עוברת את המינימום- פשוט לא לאשר ולצרף כפתור של יצירת קשר בווצאפ במקרה של בקשה חריגה או משהו כזה.` |
| S4 | The minimum is ₪800 ex-VAT, on the numbers stored in Shopify. | spec §4 row 1, §2 W0-VAT (2026-09-24); Sales-Machine `doctrine/decisions.md` D-015 (2026-08-31) | The ₪800 ex-VAT figure is D-015's. That the stored numbers are ex-VAT was answered from the systems and put to Tom as a stated fact on 2026-09-24; he may overrule it (spec §4 row 1). |
| S5 | Prices are shown, not adjudicated. A customer who disputes a price contacts GT. | spec §4 row 3, §4.2 (2026-09-24) | In Tom's words, part of the S1 quote: `בעניין של המחירים- פשוט תציג מחירים בדף עצמו ואז לקוח שחושב שמגיע לו מחיר אחר יוכל פשוט ליצור קשר` |
| S6 | There are three price families: TEA_1L (11 SKUs), TEA_05 (11) and ODK_1L (3). Each gives one price per customer: the paid price on that customer's most recent line in the family. A family the customer never bought shows its list price. Every other catalog SKU is priced at the customer's exact last paid price, otherwise the list price. When the newest order holds two prices in one family, the first family line in that order sets the price. | spec §4 row 2, §4.1 (2026-09-24); the two-prices rule is in spec §4.2 | In Tom's words (Q2, "approved with one change"): `אין תמצית 300 מל אל תכניס אותה. חוץ מזה מסכים ומאשר. 3 קטגוריות למחיר + מחירים משתנים פה לקוח של מאצ׳ה וכו׳ כל שאר המוצרים שנמצאים בקטלוג מוצרים בקאנבה`. The two-prices rule follows his Q3 simplification (spec §4.2). |
| S7 | 0.3 L is out: not shown, prefilled or orderable. | spec §4 row 2, §4.1 (2026-09-24) | In Tom's words: `אין תמצית 300 מל` |
| S8 | The catalog is the 40 SKUs in brain `docs/warehouses/catalog-truth.md` (the Canva catalog, as corrected by D-010), plus items the customer already buys outside it. Those items are shown to that customer only, at their exact last paid price. | spec §4.1 (2026-09-24) | In Tom's Q2 words (S6). Showing out-of-catalog history items is the spec's reading of `חוץ מזה מסכים ומאשר`. The spec records that reading so Tom can overrule it (spec §4.1). |
| S9 | Login: the customer sends a ready WhatsApp message to the order line, and the system replies with a one-time link sent to that phone. The device then stays signed in. | spec §4 row 4, §4.3 item 2 (2026-09-24) | In Tom's words: `תוודא ב100% שזה אפשרי ופשוט`. The spec records the verified form (spec §2 W0-6b). It works only once WhatsApp sending is fixed (M1). The exception it makes to the locked staff auth model is proposal §1.2-2. |
| S10 | Registration: GT approves every new customer by picking their Shopify customer. | spec §4 row 4, §4.3 item 3 (2026-09-24) | In Tom's words: `צריך לפתח מנגנון הרשמה פשוט שאנחנו נאשר בו כל לקוח`. The same spec item says "the existing 195 manually mapped phones count as approved". That premise is wrong: 194 of those rows were auto-resolved by the bot, and 1 is manual. So who may log in at launch is reopened as proposal §1.2-3. |
| S11 | Billing is unchanged in v1. Green Invoice, LionWheel and route-print-pack see an ordinary order, and the distributor billing switch is a separate project. | spec §4.3 item 1 (2026-09-24) | No objection recorded. The spec takes it as decided under Tom's standing rule, "I'll stop you if I disagree" (spec §4 row 4). |
| S12 | No credit check in v1. | spec §4.3 item 4 (2026-09-24) | In Tom's words: `מאשר את 4` |
| S13 | Hosting is inside the existing API, behind its own subdomain; the host name is in the private spec. | spec §4.3 item 6 (2026-09-24) | In Tom's words: `מעולה. אנחנו צריכים לסדר את כל הדומיינים האלו` |
| S14 | Confirmation is on screen, plus WhatsApp. | spec §4.3 item 5 (2026-09-24) | In Tom's words: `בוא נעשה שיישלח מייל או ווצאפ`. WhatsApp was chosen because B2B customers mostly have no email (spec §4.3 item 5). In v1 it is sent only inside the 24-hour window (§1.2-1(b)); the template needed for later confirmations does not block launch (masterprompt §6). |
| S15 | Later, not in v1: personal signed links and promotions. | spec §4.3 item 7 (2026-09-24) | No objection recorded (spec §4 row 4). Masterprompt §1.1 also lists delivery dates, payment and KPIs as later, but spec §4 records no words of Tom's for those three. |
| S16 | Working rule: open items are parked and resolved one by one at the end, and there is no compromise on UI/UX. | spec §4.4 (2026-09-24) | In Tom's words: `בוא כרגע נשאיר את כל הדברים פתוחים ונערום אותם, לבסוף נכין רשימה מסודרת ונפתור אחד אחד בצורה מקצועית ומושלמת. התוצר הסופי שרצוי מפה הוא דף ממש ממש מקצועי, יפה ונגיש ונוח מבחינת uxui עם הdna של המותג. לא מתפשרים על הuiux!` |

## C. Tom's switches after D1 (masterprompt §6). Each is open and is Tom's act.

No secret value appears here or in any file (declaration §8). The steps, host names and variable
names are in the private masterprompt §6.

| # | Switch | Status |
|---|---|---|
| M1 | Fix WhatsApp sending: a configuration change on the API service. It blocks login and every bot reply. Side effect: the bot's existing catalog pointer starts reaching customers. | open |
| M2 | Domain: point the portal's subdomain at the API service, then set the portal's public-URL variable. | open |
| M3 | Who goes live: `pilots: <names>` or `everyone`. The session writes the allowlist. | open |
| M4 | The first real order, placed by Tom as the internal test account. It needs Tom's written go (declaration §11). | open |
| M5 | Publish the theme copy that carries the site entry (after M2 and M4). | open |

## D. UNRESOLVED — for Tom

U1–U8: declaration §17.3.

## Log

| Date | Entry |
|---|---|
| 2026-09-24 | Opened as PROPOSED. Transcribed from masterprompt r2 §1.1, §1.2 and §6, and from spec §4.1–§4.4 and §5. No item is approved. U1–U8 were opened. |
