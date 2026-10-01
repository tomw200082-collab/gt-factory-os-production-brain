# PRODUCT REVIEW HANDOFF — GT Menu Builder / Guided Sales Configurator

**From:** Session 1 (product discovery + precision design, Claude Fable 5.1), 2026-10-01.
**To:** Session 2 (independent product review, Opus 5.5), then Session 3 (implementation, Opus 5.5, only after the gates below).
**Governing instruction:** the Menu Builder masterprompt Tom pasted on 2026-10-01. Session 2 receives it again from Tom together with this file; the masterprompt's rules win over anything written here.

**State at handoff:** `PRODUCT DESIGN APPROVED — WAITING FOR SALES FOUNDATION`. `SALES FOUNDATION GATE: HOLD`. **No Menu Builder production implementation has begun** (see §12).

Everything Session 2 needs is in this folder on branch `claude/menu-builder-discovery` of `gt-factory-os-production-brain` (draft PR #241). Read in this order: `00-README.md` → `06-decision-ready-product-spec.md` → `decision-ledger.md` → `dependency-ledger.md` → `ground-truth.md` → `01`…`05` for the reasoning behind each decision → `evidence/` only when a fact needs its source.

---

## 1. The approved product spec

`06-decision-ready-product-spec.md` — 36 sections, screen-by-screen mobile flow (390 × 844 reference, 320 minimum), component behaviour, microinteractions, states, exact calculation semantics, Sales System Integration Contract, copy batch MB-01…MB-38, 22 acceptance criteria, unresolved assumptions.

Approved by Tom in writing on 2026-10-01 ("חוץ מזה אני מאשר הכל!!!") after the layered approvals recorded in `decision-ledger.md`. The spec is approved as a **design**; it does not unlock implementation (§11, §12).

The product in one paragraph: a lead (or an existing customer) opens a personal link, lands on the drinks menu with their campaign's group first, keeps or edits a curated starting set of drinks, taps through to a kit screen where GT has already worked out the smallest sellable set of products that makes every drink on the menu (aggregated once, with cups of coverage), sees recommended consumer prices and per-cup ingredient cost on request, and sends the kit through the existing draft-only lead path or the existing customer order path. The Builder itself never sends a message, never touches Shopify, never changes a price.

## 2. Decision Ledger

`decision-ledger.md` — MB-D01…MB-D12 plus MB-SPEC, each with sources, options, the decision, the reason, the strongest alternative, status, what it binds and whether Tom's word was required.

| Decision | Status at handoff |
|---|---|
| MB-D01 placement in the lead journey | **DEFERRED by Tom** (three placements open: P1 site, P2 inside the WhatsApp journey, P3 behind the personal link). Spec is placement-agnostic (DR-03). |
| MB-D02 segmentation / bypass | FINAL (Session 1): no questionnaire; context from the campaign; fast path to the catalog for people who know the products. |
| MB-D03 quantity model | FINAL (Tom): zero-question starter kit, minimum sellable units per required product, **₪800 round-up by product priority tea 1 L → tea 500 ml → the rest** (Tom's amendment, transparent note, editable after). |
| MB-D04 economics | FINAL (Tom): RRP on the card; per-cup ingredient cost and what is left per cup on one tap, with the estimate footnote; kit = cash outlay ex-VAT + VAT + total + cups; never projections or GT margins; off without identity. |
| MB-D05 recipes in selection | FINAL (Session 1, inside the approved spec): none in the Builder; the existing post-purchase path keeps delivering recipes. |
| MB-D06 discovery model | FINAL (Tom): four groups (context group first), curated pre-selected set, consequence chip, no filters/search, sticky my-menu bar, two screens. |
| MB-D07 save / resume | PROVISIONAL — SALES DEPENDENCY (DL-03, IC-1). |
| MB-D08 finish | FINAL (Tom): two layers, one action, **no 24 h branded-menu reward** (struck by Tom). |
| MB-D09 CRM contract | FINAL on shape, PROVISIONAL on Unit A mechanics (IC-2, IC-3; 24 h `call` task approved by Tom). |
| MB-D10 analytics | FINAL (Session 1): server-side append-only `builder_event`, fixed taxonomy, success measured on the lead. |
| MB-D11 architecture | FINAL (Session 1): inside `gt-factory-os/api/src/portal` under `/portal/builder…`, server-authoritative money, same token family as the portal. |
| MB-D12 V1 non-goals | FINAL (Session 1), list in `05-…` §6. |

Design requirements lifted from Tom's words: DR-01…DR-06 (`decision-ledger.md`).

## 3. Builder ↔ Sales Dependency Ledger

`dependency-ledger.md` — DL-01…DL-19, each with its source in the Sales system, status (built / merged-and-gated / draft PR / missing), the provisional assumption the design makes, and the recheck item for the FINAL SALES RECONCILIATION PASS. Four **proposed** contracts the Builder needs from the Sales system, none accepted yet:

- **IC-1** `customer_portal.lead_link.purpose` (`order` default, `builder`); `closeLinks` scoped to `order` so a Builder link survives an order.
- **IC-2** four additive `sales_core.lead_event.event_type` values (`builder_opened`, `builder_menu_completed`, `builder_kit_accepted`, `builder_help_requested`) and the trigger routing into Unit A tasks.
- **IC-3** `api_read.v_sales_builder` read model; `LeadDrawer` block "התפריט שבנה"; timeline labels; rail milestone.
- **IC-4** `builder_session_id` on `customer_portal.lead_submission` and `order_submission`.

Every row with a `draft PR` or `missing` source is a reason the gate is HOLD (§11).

## 4. Unresolved questions (open at handoff)

From spec §36, after Tom closed U-MB-1, U-MB-3 and U-MB-10 on 2026-10-01:

| Id | Question | Owner |
|---|---|---|
| U-MB-2 | The drink → product → dose table (48 rows) exists only inside recipe text and the 2026-09-29 cost model; it must be authored as data and Tom-verified before any kit is computed (DL-18). | Session 3 + Tom |
| U-MB-4 | Placement (MB-D01), and therefore which journey message carries the Builder link; the message texts are Tom's. | Tom |
| U-MB-5 | IC-1 mechanism (`purpose` column vs separate table) and the IC-2 event vocabulary are the Sales workstream's call after Unit A. | Sales session |
| U-MB-6 | Unit A's final task-trigger shape may change the `reply` / `call` routing. | Sales session |
| U-MB-7 | Cups-per-bottle claims on the site and PDFs (20 / 20–25 / 33 / 30 / 13) should agree with the Builder's derived coverage; the Builder itself needs no single figure. | Tom / docs lane |
| U-MB-8 | Whether the five lead-menu PDFs carry the 2026-09-29 figures. | menus workstream |
| U-MB-9 | Recipe defects on approved pages (p36 copied recipe, p12 name, matcha-masala 40 vs 50 ml) are the catalog owner's to fix; the Builder keys on page ids and the cost model's doses. | Tom / catalog |
| U-MB-11 | 48 drink photos exist on the Shopify CDN at 925 × 1052 (gt-site `photos.json`); self-hosting in the portal uses GT's own Canva exports. | — |
| NEW | The optional equipment add-on line `ערכת מאצ׳ה ₪170` (spec §15, copy MB-38) is a **proposal, default off, pending Tom's word**. The kit's BOM holds no matcha powder (read live: `GT-MAT-KIT` → `BOM-REPACK-MAT-KIT`). | Tom |

## 5. Assumptions the design rests on

1. Identity always comes from a personal link (lead) or the portal cookie (customer); the Builder never asks for a phone or name on the menu screen. Lead fields appear only on the kit screen, exactly as the existing lead mode asks them.
2. Prices come live from Shopify through the portal's existing `pricing.ts` rule (list for leads, last-paid family rule for customers); the Builder adds no price source and no discount logic.
3. Figures (consumer price, ingredient cost per cup, doses) come from `drinks_final_figures.json` dated 2026-09-29 and the cost model of the same date, copied into `api/src/portal/builder/figures.json` with a CI drift check; costs are ingredients-only estimates for a 350 ml ice-filled cup and are labelled as such to the customer.
4. Availability comes from the existing planner overlay `customer_portal.item_availability_current`; the Builder adds no availability source and shows the planner's return date and alternative the same way the ordering portal does (DR-05, verified in `05-…` §0: no deepening needed).
5. The ₪800 ex-VAT minimum and the pair rules are the portal's existing rules; the Builder's round-up fills the shortfall before the server re-checks, and the server stays the authority.
6. The 24 h "built a menu, did not order" task rides GT Pulse Unit A's task mechanism; if Unit A ships differently, the task shape follows Unit A, not this spec (U-MB-6).
7. Hebrew only, RTL, mobile first; every customer-facing string is in the copy batch (spec §33) and needs Tom's register approval before it ships.
8. The Builder sends nothing to the customer; any message mentioning it is an existing journey message behind the frozen outreach flag.

## 6. Rejected alternatives and why

| Rejected | Why (short) | Where argued |
|---|---|---|
| Builder as the first-message asset instead of the PDF (P2 variant A) | WhatsApp interactive messages cannot carry a URL next to the three reply buttons; the PDF opens instantly; no identity before the form so no prices. Kept as a V2 experiment. | `01-…` |
| Builder on the website without identity | No prices allowed on the site (Tom 2026-09-24), second data copy, no identity for a kit. Recorded as a possible anonymous inspiration mode later. | `01-…` |
| Builder only after the sales call | Loses the self-serve leads; the same link already reaches post-call leads through the wake-up messages. | `01-…` |
| One-question scaled kit (`כמה משקאות ביום?`) | The answer is a guess for a new menu; surplus lands in the customer's fridge as mistrust; reintroduces a form step. V1.1 experiment at most. | `02-…` |
| Menu only, no quantities (the August doctrine as written) | Loses every self-serve order and the "GT already worked it out" moment. | `02-…` |
| Cart only, no menu artifact | Drops the reward the customer is building toward. | `02-…` |
| 24 h branded-menu reward | Struck by Tom on 2026-10-01. | `decision-ledger.md` MB-D08 |
| Suggestion ladder for the ₪800 shortfall | Replaced by Tom's automatic round-up by product priority. | `02-…` amendment |
| RRP only, no cost anywhere | The lead already holds the PDF with the cost printed (D-025); the Builder would be the one surface refusing a number the others volunteer. | `03-…` |
| Projected monthly profit / ROI screen | Needs a forecast GT refuses to make; the ROI trap. | `03-…` |
| Empty start grouped by GT product | It is the catalog the lead already has; asks the customer to think in SKUs. | `04-…` |
| Wizard (venue → category → drinks), search-and-filter catalog of 48, extra presets | Form steps and shopping decisions before the menu decision; no data says a new preset is wanted. | `04-…` |
| Recipe on the detail sheet | Masterprompt §13; turns a menu decision into a cooking lesson. | MB-D05 |
| Builder as a gt-site feature | No identity, no server money, a second copy of truth; the portal already has all three. | `05-…` §5 |
| One `builder` event type with a `kind` payload instead of four types | Session 1 chose four for CHECK-constraint clarity and trigger routing; Session 2 should challenge this (§9). | `05-…` §8 |

## 7. Repositories and files consulted

All read-only. Live database reads were `SELECT` only, through the Supabase MCP, project `rvadsozabmxkkrktwgnv`.

| Repo | What was read |
|---|---|
| `gt-factory-os` | `api/src/portal/**` (`public/index.html`, `catalog.ts`, `pricing.ts`, `routes.ts`, tests), `db/migrations/0357…0362`, `supabase/functions/sales-leads-poll`, `website_lead_intake`, `factory_os_jobs`, lead-journey code paths, `api/test/*` |
| `gt-factory-os-portal` | sales corridor (`LeadDrawer`, `LeadJourneyRail`, `TaskCard` on PR #239), `/planning/portal-catalog` planner (`page.tsx`), `cockpit.ts`, `docs/portal-os/*` |
| `gt-factory-os-production-brain` | `CLAUDE.md`, `EXECUTION_POLICY.md`, `CURRENT_STATE.md`, `.claude/state/*.json`, `.claude/skills/drinks-pricelist/drinks_final_figures.json`, `docs/pricing/2026-09-29_cost_model.py`, `GT_FOOD_COST_2026-09-29.xlsx`, `docs/decisions/*`, `canva_workfiles/*` |
| `Sales-Machine` | `CLAUDE.md`, `CURRENT_STATE.md`, `doctrine/decisions.md` (D-001…D-033), `knowledge/*` (segments, sales-motion, catalog cards, answer bank), unmerged journey-doctrine PR #3, design branches |
| `gt-site` | theme sources for the lead dialog and campaign links, `tools/landing-pages/drinks.json`, `photos.json`, `show_prices` setting |
| Live DB | `sales_core.lead`, `lead_event` counts by type, `app_setting.lead_menus`, `customer_portal.lead_link`, `lead_submission`, `item_availability(_current)`, `private_core.items` + `bom_*` for `GT-MAT-KIT`, `sales_core.list_price` / `customer_price` row counts, `feature_flags` |

Verbatim reconstructions: `evidence/2026-10-01-gt-site-lead-funnel.md`, `…-customer-portal-reconstruction.md`, `…-sales-lead-backend-map.md`, `…-staff-sales-corridor.md`, `…-drinks-products-data-map.md`.

## 8. Branch and PR SHAs at handoff

| Repo | Branch | SHA |
|---|---|---|
| `gt-factory-os-production-brain` | `claude/menu-builder-discovery` (this folder, draft PR #241) | see `git log -1` on the branch; base `main` @ `93eb4b2` |
| `gt-factory-os` | `main` | `04cb0f6` |
| `gt-factory-os` | `feat/gt-pulse-a-sales-contact-loop` (draft PR #329, migration 0362) | `ff69e3c` |
| `gt-factory-os-portal` | `main` | `5e45b2d` |
| `gt-factory-os-portal` | `feat/gt-pulse-a-sales-corridor` (draft PR #239, tranche 185) | `1ba2c98` |
| `Sales-Machine` | `main` | `7fd25f8` |
| `Sales-Machine` | `design/gt-pulse-crm` | `12ab42f` (also seen as `7ee2e492`) |
| `Sales-Machine` | `status/gt-pulse-a-2026-09-30` | `5370aba` |
| `gt-site` | `main` | `5d3e69c` |

Session 2 must re-read these branches live; any of them may have moved.

## 9. External research conclusions

Session 1 did **no** external benchmarking or web research; the masterprompt's own rules and GT's systems supplied every input. Conclusions that stand in for research, all argued in `01`…`05`:

- A guided configurator earns its place only where identity and server-side money already exist; for GT that is the customer portal, not the site.
- A zero-question starter kit beats a volume questionnaire for a first order of an unknown menu; volume is learned from reorders.
- The strongest objection to the whole product is placement in a journey that already repeats itself (PDF, then interface); Tom deferred placement for exactly that reason.

What Session 2 should challenge hardest (from `05-…` §8): the `purpose` column on `lead_link` versus a separate table; four event types versus one; whether `v_sales_attention.stalled` must exclude Builder events; whether the drink table belongs in code or in a planner-editable table; and the round-up rule's behaviour on single-product menus (Tom accepted it as written).

## 10. Known Sales-system dependencies

The Builder cannot ship without these, in this order of risk:

1. **Unit A tasks** (gt-factory-os PR #329, portal PR #239, both draft, release deferred by Tom 2026-09-30): the `reply` and `call` tasks, `source_key` idempotency, the trigger on `lead_event`. DL-06, IC-2.
2. **Lead link purpose** (IC-1): without it, the Builder link dies with the first order and resume breaks. DL-03.
3. **Lead event vocabulary** (IC-2): the CHECK constraint on `lead_event.event_type` is closed; four values must be added by the Sales lane. DL-04.
4. **Staff surfaces** (IC-3): the drawer block and labels are portal work in the sales corridor, tranche-governed. DL-07, DR-06.
5. **Order attribution** (IC-4): nullable column on two `customer_portal` tables. DL-09.
6. **The journey message that carries the link**: Tom's placement decision and his words. DL-08, DL-16.
7. **Figures authority** (DL-17) and the **drink → SKU → dose table** (DL-18, U-MB-2): data work, not Sales code, but a precondition for every kit.

## 11. Sales Foundation Gate

**`SALES FOUNDATION GATE: HOLD`.**

Reason: GT Pulse Unit A is on draft PRs with release deferred; the brain's `active_mode.json` is `B-Sales-Corridor` (expires on tranche 185 closure or 2026-10-13); the next Sales session may expand the design. The FINAL SALES RECONCILIATION PASS (spec updated against the accepted Sales code first, then the gate verdict) has not run and cannot run until Unit A is accepted.

Implementation needs all three: `PRODUCT DESIGN = PASS` (reached 2026-10-01) **and** `SALES FOUNDATION GATE = PASS` (not reached) **and** Tom's explicit unlock in writing (not given).

## 12. Statement of non-implementation

No Menu Builder production implementation has begun. Session 1 wrote only Markdown under `docs/plans/2026-10-01-menu-builder/` on a branch of the brain repo. No migration, no code, no Edge Function, no deploy, no feature-flag change, no change to the lead journey, the CRM schema, GT Pulse, pricing, WhatsApp automation or portal routes. No authority document (`CURRENT_STATE.md`, `CLAUDE.md`, `EXECUTION_POLICY.md`, `Sales-Machine/doctrine/*`) was edited. All live-system access was read-only.

---

## Instructions for Session 2

1. Review the product independently: wrong assumptions, UX gaps, Sales-system conflicts, data-truth risks, implementation risks. Do not re-decide what Tom decided; challenge it with evidence and put the challenge to him.
2. Keep both ledgers current; add findings as new rows, never rewrite history.
3. Produce the review verdict the masterprompt asks for, and leave the three-gate rule untouched: `PRODUCT DESIGN = PASS` is not an unlock.
4. Do not watch PRs, schedule check-ins or create Routines unless Tom asks in that conversation (brain `CLAUDE.md` §Watching).
