# Menu Builder — Ground Truth (reconstructed 2026-10-01)

> The map Session 1 built before any product question was put to Tom. Every claim cites its source; the verbatim exploration reports are in `evidence/`.
> **Design-phase artifact. Not an authority doc.** Re-verify every live number before relying on it (recipes in §8).
> Heads read: gt-factory-os `04cb0f6` (#328) · gt-factory-os-portal `5e45b2d` (#238) · brain `93eb4b2` · Sales-Machine `7fd25f8` (#37) · gt-site `5d3e69c` (#34). Live DB: Supabase `rvadsozabmxkkrktwgnv`, read-only, 2026-10-01 ~05:30 UTC.

## 1. The lead → first-order journey as it runs today

| Step | What happens | Where it lives | Status |
|---|---|---|---|
| 1 Arrive | (a) gteveryday.com: 19 CTAs open one lead dialog (business question → 4 fields → thanks → five WhatsApp pills). (b) Facebook lead-ad form → Make → `/ingest`. (c) Campaign link `?c=matcha\|tea\|ube\|chai\|menu` opens the dialog on arrival and leaves one pill. (d) A direct WhatsApp message to the lead line `054-758-8132`. (e) Instagram DM / Messenger: parked (U-054). | gt-site `theme/sections/gt-home.liquid:286-328`, `website_lead_intake` v10; `sales-leads-poll` `/ingest` | PROD |
| 2 Lead row | One write path `sales_core.ingest_lead()`; one open lead per phone (0361, advisory lock, repeat contact joins the oldest open lead); `(source, external_id)` idempotent; org matched by shopify id > phone > email > domain; **no intake path sets `assignee`**. | gt-factory-os 0318–0361 | PROD |
| 3 First automated message | Lead line recognises one of five ready texts (`היי, אני מעוניין ב…`). Recognised → the line's **PDF menu** (≤8 drinks, FOOD COST printed) + body + footer + **three reply buttons** `אני רוצה להזמין` · `רוצה לשמוע עוד` · `תודה, לא כרגע`. Not recognised → one general reply with a FAQ link (once per phone per 30 days). The fifth site line `בניית תפריט משקאות עשיר ורווחי לעסק` maps to the **opening** menu. | `api/src/order-intake/sales/journey.ts`, `lead_texts.ts`; `sales_core.app_setting.lead_menus` (5 PDFs on the Shopify CDN, dated 2026-09-29) | PROD-GATED: `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED=false` → dry run except `lead_journey_test_phones`; live rows `delivered`/`read` on the lead line 2026-09-30 (`first_menu` ×5, `order_link` ×2, `more_info` ×2, `customer_link` ×2) |
| 4 Buttons | `lj.order` → **personal ordering link** `/portal/lead/<token>` (14 days, reusable until one order; a known customer gets `/portal/` instead). `lj.more` → "we'll call" + FAQ link + Telegram to the owner. `lj.not_now` → thanks, `lost` (`לא כרגע`), opt-out. Any later free text → desk task + at most one `free_text_reply`/day (#328). | `journey.ts:153-185`; `customer_portal.lead_link` (2 rows live) | PROD-GATED |
| 5 Lead order | The same ordering page in **lead mode**: 40-SKU catalog, **list prices ex-VAT**, planner availability, bottles in pairs, ₪800 ex-VAT minimum, three fields (business, city, contact). Submission → `customer_portal.lead_submission` → Shopify **draft** tagged `lead` with `customAttributes {lead_id, business_name, city, contact_name, wa_phone}` → **never completed by the system** (D-029) → `lead_event draft_order` → confirmation (free-form inside 23.5 h, else utility template) → Telegram «טיוטת הזמנה חדשה מליד». All links of the lead close. | `api/src/portal/lead.ts`, `routes.ts:306-326` | PROD (0 lead submissions yet) |
| 6 Human | Owner by default Tom; Avi/Alex for chains (lead-response SOP §1). SLA 24 h; Today queue cap 15. Outcome `answered_progressing` + next touch starts the **wake-up sequence**: ≤4 marketing templates (1: PDF again + order link ≥2 h after the call; 2: FAQ link, morning of follow-up 1; 3 and 4: order link, mornings of follow-ups 2 and 3; 4 = soft close). Stops on order, any reply on either line, `הסר`, `lost`; 48 h spacing; Sun–Thu 10:00–11:30 / 15:00–17:00; `holidays_il`. | `wake.ts`; cron `lead_wake_sequence` */15 → Railway `/internal/jobs/lead-wake`; templates `gt_lead_wake_1..4` (Meta approval status unknown, U-052) | PROD-GATED (eligibility needs a *delivered real* first message) |
| 7 Customer | Staff create the customer (Shopify + Green Invoice, skill `customer-setup-shopify-gi`), complete the draft → Green Invoice 305 in 5–11 s → LionWheel task. Daily job `convert_lead()` is the **sole writer of `won`** (first Shopify order at/after the lead). | `sales-leads-poll` daily 04:00; 0348 | PROD |
| 8 Reorder | Customer portal: WhatsApp A1 → 10-min link → 180-day cookie; own prices from last 40 orders (family rule); reorder cards; draft→complete tagged `portal`. | `api/src/portal/*`, flag `customer_portal_live` on, allowlist `*` since 2026-09-25 | PROD (4 orders) |

**Live funnel numbers (2026-10-01):** 261 leads: `new` 147 (142 are the 2026-08-10 historical import, deliberately untouched), `working` 38, `won` 5, `lost` 71. Sources: `import_meta_export` 188, `facebook` 50, `website_form` 19, `whatsapp_unattributed` 4. Lead line: 68 events / 19 messages in 30 days (all since 2026-09-29). Order line: 6,480 events / 3,368 messages in 30 days. `sales_core.task`: absent (0362 not applied).

**What the lead actually experiences between "interested" and "ordered" today:** a static PDF of ≤8 drinks with economics, and then an order link into a list of 40 raw products with prices. The translation "the drinks I want → the bottles I must buy, how many, what it costs me" happens in the lead's head or on the sales call. That is the gap the Builder is meant to close.

## 2. The future Sales-system journey (GT Pulse), as approved and as built

- **Program design** (Tom-approved 2026-09-29, `Sales-Machine` `design/gt-pulse-crm` `docs/superpowers/specs/2026-09-29-gt-pulse-crm-program-design.md`): the CRM customer is the business; Units A (contact loop + tasks) → B (business + full order history) → C (retention and expansion) → D (GT Pulse visual: lead rail, business cycle, contact compass, event river, basket map) → E (AI drafting). Only Unit A has an execution plan.
- **Unit A spec** (`2026-09-29-sales-activity-task-loop-design.md`): `sales_core.task` (target lead|org, closed kind enum, owner, due, `source_key` idempotency, `task_event` audit); atomic activity command (note ≥5 chars + one action + date, or `ממתין ללקוח` with a review date); staff email's only primary action `פתח את הליד`; deep link survives login; owner isolation; wait guard at the wake send boundary; Today / Leads / Attention all leave the legacy `/outcome` path before `activity_required` is enabled.
- **Built, held:** backend draft PR #329 (`feat/gt-pulse-a-sales-contact-loop` @ `ff69e3c`, migration 0362, 19 files; exact-head CI green: 0362 pgTAP 79/79, lead/wake DB 19/19, API 11/11, legacy 14/14, mail 38/38) and portal draft PR #239 (`feat/gt-pulse-a-sales-corridor` @ `1ba2c98`, tranche 185, 53 files; unit 1,525/1,525). **Release explicitly deferred by Tom (2026-09-30).** Open gates: connected staging Auth→browser→API→DB proof (two paid Supabase branches failed at migration `0090`), WebKit keyboard proof, connected five-lens UX gate, final-head review, production 0362, count-specific backfill approval. Brain `active_mode.json`: `B-Sales-Corridor`, tranche 185, expires at closure or 2026-10-13.
- **Next Sales session** (`Sales-Machine` `status/gt-pulse-a-2026-09-30` `docs/plans/2026-09-30-gt-pulse-preproduction-claude-code-masterprompt.md`): Grill with Docs + brainstorming with Tom → possibly **expanded design** → implement on the same two draft PRs → connected UX gate → simplify → verify → `READY_FOR_PRODUCTION_DECISION`. **Scope may grow after Tom's interview**; the Builder must not assume Unit A's final shape until that session reports.
- **Event → task routing in 0362** (`tg_lead_event_task`): `created` → `contact_first` (or `contact_resolution` when no phone/email); `note{kind:repeat_contact}` with `source`+`external_id` → `reply`; `button_tap{button_id:'lj.more'}` with `wamid` → `reply`; `draft_order{idem_key}` → `draft_followup`; `status_change→lost`, `opt_out`, `converted`, `won` → cancel open tasks and deactivate `lead_wait`; `lost→undo` restores. Owner follows `lead.assignee` (`tg_lead_task_owner`). This is the hook a Builder event would use.

## 3. The customer ordering portal (the design and runtime the Builder must belong to)

Verbatim detail: `evidence/2026-10-01-customer-portal-reconstruction.md`. The facts that bind a sibling product:

- **One file, no framework:** `api/src/portal/public/index.html` (1,584 lines, inline CSS + ES5 IIFE, `innerHTML` templates); entry pages share `panel.css`; token parity enforced by `tokens.test.ts`. Mounted in the Fastify API on Railway (`registerPortalRoutes`, `server.ts:118`); `order.gteveryday.com` wired as `PORTAL_HOST` but DNS not moved.
- **Identity:** cookie `gtp_sid` with `Path=/portal`, 180 days; CSP `connect-src 'self'`, `img-src 'self' data:` → a sibling that shares identity must live under `/portal/…` on the same host and self-host images. Lead mode = `/portal/lead/<token>` (the same page, boot line string-replaced; coupling to `index.html:12`).
- **Catalog is code:** 40 SKUs in `catalog.ts` (11 teas × 2 sizes, 7 matcha/powders, 3 ODK purées, 8 accessories; `EXCLUDED_SKUS` never shown); presentation list `P` in `index.html:645-683` (flavour `bg`/`c`, sizes, `six` = bottle); images self-hosted WebP exported from Canva (`l-`, `h-`, `p-`, `o-`, `a-` prefixes, full + `-320`). Availability overlay from `customer_portal.item_availability_current` (planner-set, append-only).
- **Pricing:** Shopify only (`pricing.ts`): list = `productVariant.price` (10-min cache); customer = last 40 non-cancelled orders, **family rule** (TEA_1L, TEA_05, ODK_1L take the newest family line's price for every flavour), others exact last paid, else list; leads = list prices. **Ex-VAT numbers; never ×/÷ 1.18; VAT line 18%; minimum ₪800 ex-VAT** (`BELOW_MINIMUM`); pairs for tea 1 L, tea 500 ml and ODK (`NOT_IN_PAIRS`), matcha exempt; price drift → `409 PRICE_CHANGED`.
- **Order handoff:** `order_submission` (idem key) → `draftOrderCalculate` double-VAT guard → `draftOrderCreate` (tags `portal`, `pk-<idem>`) → `draftOrderComplete(paymentPending)`; leads stop at the draft. Replays, stale `submitting` rows, 202 `CREATED_NOT_COMPLETED`, Telegram alerts.
- **Client state:** no server cart; `localStorage` `gtp_cart_v1` per account (14 days), `gtp_last_v1` (24 h duplicate guard), pending state replays with the same idem key.
- **Design DNA:** paper `#FBF8F2`, card `#F3EFE6`, ink `#20241F`, brand `#3E6E34`/`#2B4F24`, terra `#9A5433`; Heebo (self-hosted, variable) + "GT Latin" (Bebas Neue) for product names only; radii 12/16/24/999 (sheet 26, bar 22); shadows `--sh-1..3` + radial floor instead of drop-shadow; easings `--ease/--out/--spring`; grid "2 or 4, never 3"; product card anatomy (flavour disc, bottle hop on add, ✓ badge, fixed 76 px price/control area); stepper 44 px (pairs step 2, carton +6); cart tiers 560/1100 px (bottom sheet / drawer / sticky side cart); send state machine idle→sending→pending→done with replays at 5/15/45/120/150 s; light scheme only; `he`/`rtl` everywhere, logical properties, `.num` LTR-isolated; axe-clean, 44 px targets, skip links, live regions; LCP ≤1,300 ms budget (measured 1,156), CLS 0, 151 KB.
- **Locked decisions a sibling must respect:** spec §4.1–4.5 and UX gate §4 decisions 1–15 (cart client-side 14 days, logout clears, reorder merges by max, no toasts while cart visible, catalogue-first loading, light only, cart as `<aside>` not `<dialog>`, GT Latin names only, 560/1100 tiers, every amount states its VAT basis); availability words; pairs; `customer_portal` write boundary; approved Hebrew only (`portal_copy_check.mjs`).

## 4. The staff sales corridor (where Sales would see the Builder)

Verbatim detail: `evidence/2026-10-01-staff-sales-corridor.md`. What binds the Builder's CRM handoff:

- **Surfaces on main:** `/sales/today` (queue derived from `v_sales_today`: conversion → returning customer → due follow-up → new lead, daily cap 15 on new leads only), `/sales/leads` (+ `LeadDrawer`, the only full lead view), `/sales/orgs`, `/sales/attention` (overdue / unowned / stalled + activity feed), `/sales/settings`. One gate `sales:execute` (`sales_rep`, `planner`, `admin`); no manager role on main. Hebrew RTL, own `s-*` token set (`sales-tokens.css`, Rubik, teal accent), no shadcn.
- **No task entity, no "send link" action, no customer-facing send** on main; every outbound is `tel:` / `wa.me` / `mailto:` with the outcome sheet on return. `next_touch_at` is the only promise field.
- **Timeline renders `lead_event` by `EVENT_LABELS`**; seven backend types (`draft_order`, `auto_message`, `button_tap`, `opt_out`, `qualified`, `kit_sent`, `question_logged`) have no Hebrew label and print as raw tokens. A lead's draft order from the WhatsApp link therefore shows as the token `draft_order` today.
- **Zero-portal-change path for Builder intent:** a `note` event whose `payload.note` is readable Hebrew with structured JSON beside it (precedent: `website_lead_intake` writes `{note, form:{…}}`, actor `system:website_form`) renders in the drawer, the org card and the Attention feed. A new `event_type` needs the backend CHECK widened (0360 pattern) plus `EVENT_LABELS` and `describe()` entries, and under Unit A a routing rule in `tg_lead_event_task`.
- **Natural places for the built menu:** `LeadDrawer` between the Shopify snapshot and פרטים; the timeline; under Unit A the `TaskCard` reason ("למה עכשיו") and a `LeadJourneyRail` milestone. Today never fetches events, so anything on the Today card needs a `v_sales_today` column.
- **Tranche 185 corridor (PR #239) owns `(sales)/**`, `api/sales/**`, middleware, login/callback, safe-redirect and tests; one pan-form amendment at a time** → any Builder change to staff screens must follow that tranche, never run beside it.
- Governance drift to carry into the Review Handoff: `route-manifest.json` lacks planner and `/sales/attention`; `baseline.json` has no sales routes (sentinel blind); `registry.md` stale on 173/184; deep links lose `?lead=` on the login bounce (fixed only on the PR #239 branch).

## 5. Data ground truth (drinks, products, yields, food cost, prices)

Verbatim detail: `evidence/2026-10-01-drinks-products-data-map.md`. Classification the Builder must build on:

| Data element | Canonical source | Status | Builder consequence |
|---|---|---|---|
| Drink list, stable ID, name (he), food cost per cup, RRP, margin, profit | brain `.claude/skills/drinks-pricelist/drinks_final_figures.json` (`_meta.date` 2026-09-29; 48 drinks, 10 families, all cold; page keys `8…64`) | **CANONICAL**, but the file calls its costs *estimates* (ingredients only, standardized ice-filled 350 ml serving, unmeasured pours, retail-derived milk/cream prices) | Read at runtime from one server-side copy; never from a card or the site; label economics as estimates |
| Per-drink doses (GT and non-GT ingredients) | `docs/pricing/2026-09-29_cost_model.py` + `GT_FOOD_COST_2026-09-29.xlsx` (`פירוט עלות`) | **CANONICAL** (concentrate 50 ml in 21 drinks, 40 ml in 8; matcha 1.8 g; ube 2 g; purée 40 ml) | The BOM→cart aggregation input |
| Drink → GT SKU | **none structured**; derivable from gt-site `tools/landing-pages/drinks.json` `steps` and brain `canva_workfiles/recipes.json` `eng` | UNKNOWN / DERIVED | A Tom-verified drink→SKU table is a **NEEDS DATA** item; 32 drinks need one GT product, 16 need two |
| What GT sells, list prices | brain `docs/warehouses/catalog-truth.md` (40 sellable SKUs + 4 not sold) · runtime Shopify `variant.price` via `api/src/portal/pricing.ts` · dated TSV `2026-08-05_shopify_products_exvat.tsv` | **CANONICAL** | Product truth = the portal catalog (`catalog.ts` 40 keys), priced by the portal pricer |
| Yield per pack | Sales-Machine `knowledge/products/catalog.yaml` `servings_per_unit` (tea 1 L = 20 × 50 ml, 0.5 L = 10; matcha 500 g = 277 × 1.8 g; ube 0.5 kg = 250, 1 kg = 500; ODK = 25 × 40 ml; sachets / hojicha / kit null) | DERIVED (`doc_confirmed`) | Derive as pack ÷ dose at runtime; publish one approved number per product (U-021 open) |
| Preparation steps | Canva `DAHTYkRvEnM`; transcriptions in gt-site `drinks.json` and Sales-Machine `recipes.yaml serve` | CANONICAL external / DERIVED | Post-purchase delivery, not selection (masterprompt §13) |
| Drink images | gt-site `tools/landing-pages/photos.json` → Shopify Files `gtd-<id>.webp` 925×1052 | DERIVED (only source) | Self-host under `/portal/img` (CSP `img-src 'self'`) |
| Category / family | five taxonomies (Sales-Machine 3; 10 catalog families; site 9 groups + 4 landing pages; 5 lead menus; `campaign_map` 4) | DERIVED | The Builder picks one customer-facing taxonomy (MB-D06) |
| Availability, pairs, ₪800, excluded SKUs | `customer_portal.item_availability_current`; `catalog.ts`; `build-cart.ts` | CANONICAL (code) | Reuse, never re-implement |
| VAT presentation, shelf life | `commercial-terms.md` §1; `claims#shelf_life` | CANONICAL (`user_confirmed`) | Copy rules |
| GT internal COGS/margin (`v_fg_unit_economics`) | gt-factory-os | not for customers | Never surface |

**Stale copies (do not read):** Sales-Machine `knowledge/drinks/{catalog,recipes}.yaml` (2026-08-27 figures, review overdue), gt-site `data/drinks_final_figures.json` and `COLS` (08-27; English site 08-05), the drive pack; 38/48 drinks differ from the current file; the card reconciler only accepts a 2026-08-27 figures file.

**Gaps the Builder must not fill by invention:** consumption volume per café; opening-order quantities / starter packages (D-013, TOM-A.1); hot/winter drinks; recipes for HOJICHA, AMERICAN, sachets, kit, sugar-free variants; flavour add-in quantities; measured cups/ice; non-GT ingredient invoices; per-customer food cost; English names; a drink→SKU table; allergens/nutrition; one approved yield per product; a Tom rule on which economics a self-serve surface may show.

**Conflicts to settle before the Builder shows a number:** cups per bottle (20 / 20–25 / 33 / 30 / 13), drinks per NAMASTEA bottle (11 vs 13), matcha masala dose (40 vs 50 ml), p36 recipe copied from p38, name drift (p12; ASCII `'` vs `׳`), opening-menu prices in `commercial-terms.md` §2 stale, D-018 vs D-025 vs `show_prices:false` vs the approved answer that states ₪3.25.

## 6. Decisions that already shape the Builder (Tom, in writing)

| Date | Decision | Consequence for the Builder |
|---|---|---|
| 2026-08-04 (Sales-Machine PR #3, **unmerged**; cited by the approved sales declaration Amendment A) | Journey stage 4 "interactive catalog": the restaurant chooses drinks; sells through the customer's P&L (FOOD COST, RRP, margin); **a drink whose product is out of stock is never offered as available**. Stage 5: output = **product types + full recipe per drink, no quantities**; link = Shopify checkout/draft. Basket = our products only (D-009). Pricing = public Shopify (D-008). 24-hour incentive: order within 24 h of the link → the chosen menu branded with the customer's logo, print-ready, free (D-011). | The Builder *is* stages 4–5. "No quantities" conflicts with the 2026-10-01 masterprompt §21 and with D-013 (2026-08-31) leaving quantities open — a Tom decision (MB-D03). |
| 2026-08-31 | D-012 every business price ex-VAT and labelled; RRP incl. VAT. D-013 one recommended opening menu, not three packages; "the deck prices drinks, not the order". D-015 ₪800 minimum per order, no contract. D-016 discount tiers deliberately open (transfer row). D-018 **the system never states the opening menu's price or food cost per drink in conversation.** | Economics copy (MB-D04). |
| 2026-09-24 | No prices anywhere on gteveryday.com. | A site-hosted Builder cannot show ₪. |
| 2026-09-28 | D-025 menus keep FOOD COST; D-026 ≤8 drinks per PDF, fifth line → opening menu; D-027 no bot, event-fired messages only; D-028 three buttons and their paths (personal ordering link, no sign-up, list prices, ₪800, three fields); D-029 lead order = Shopify draft never completed by the system; D-031 wake-up sequence; D-033 **only the first message has buttons; later messages carry at most one link button; everyone waiting for a call is led to the FAQ; no behind-the-scenes talk; no promised call time**; D-034 no `פרסומת` word. Texts approved byte for byte (U-051). | Any Builder entry that needs a new button or text reopens these. |
| 2026-09-28 | Bottles in pairs (tea both sizes, ODK), server-enforced. | Starter cart rounding. |
| 2026-09-29 | Ice-aware 48-drink pricing applied; 78% minimum ingredient margin; Canva menus regenerated. | Figures file is the only economics source. |
| 2026-09-30 | GT Pulse Unit A release deferred; existing Supabase project + existing portal only; deeper product design deliberately open for the next Sales session. | Sales Foundation Gate is HOLD. |

## 7. Conflicts and unknowns

See `decision-ledger.md` C-01…C-08. Additional unknowns found in code:

- `set_lead_status` has no from-status guard (a `won` lead can be moved back); `opt_out_at` is in no `api_read` view; three phone→customer maps (`wa_customer_map`, `customer_portal.access`, `org.shopify_customer_id`) with nothing reconciling them; lead draft has no Shopify customer, so conversion depends on staff attaching one Shopify can find by phone/email.
- `v_sales_attention.stalled` counts **any** event as activity — automated Builder events would reset the stall clock unless excluded.
- `customer_portal.lead_link` closes **all** links of a lead once an order is drafted; a Builder that lives behind the same token must handle "link gone" after the first order.
- `lead_journey_force_template` is read but never seeded.
- The customer portal catalog is code (40 SKUs); `private_core.items` has 62 ACTIVE sellable items (59 Shopify-mapped). The Builder's product truth must be the portal catalog (what a customer can buy), not `items`.

## 8. Recipes (re-run before relying on §1 numbers)

```sql
select status, count(*) from sales_core.lead group by 1;
select source, count(*) from sales_core.lead group by 1;
select event_type, count(*), max(created_at) from sales_core.lead_event group by 1 order by 2 desc;
select raw_payload->>'phone_number_id' pnid, count(*), count(*) filter (where type='message'), max(created_at)
  from order_intake.wa_event_log where created_at > now() - interval '30 days' group by 1;
select coalesce(split_part(status,':',1),'?'), raw_payload->>'phone_number_id', count(*), max(created_at)
  from order_intake.wa_event_log where direction='outbound' group by 1,2;
select key from sales_core.app_setting; select value from sales_core.app_setting where key='lead_menus';
select to_regclass('sales_core.task');
select flag_key, enabled, value from private_core.feature_flags where flag_key in ('customer_portal_live');
select count(*) from customer_portal.lead_link; select count(*) from customer_portal.lead_submission; select count(*) from customer_portal.order_submission;
```
