# MB-D02 · D07 · D09 · D10 · D11 · D12 — Segmentation, save/resume, CRM contract, analytics, architecture, non-goals

> Session 1 decisions, 2026-10-01, taken after MB-D08/D03/D04/D06 were approved. These are the layers under the product: mostly engineering and integration choices that follow from what Tom approved. Each is recorded with its reason; Tom was informed and stops any he disagrees with. One item is put to him as a question (§9).
> Everything that touches the Sales system is a **proposal** (masterprompt §27–§28): nothing here is implemented, and every row depends on the FINAL SALES RECONCILIATION PASS.
> Evidence: `evidence/2026-10-01-customer-portal-reconstruction.md` §1–§2, §6, §10; `evidence/2026-10-01-sales-lead-backend-map.md` §2, §4, §6, §9; `evidence/2026-10-01-staff-sales-corridor.md` §2, §7; `ground-truth.md` §2.

## 0. A fact Tom asked to check: the return date already exists end to end

Tom (2026-10-01): when a product is unavailable with an expected return date, the Builder must show it like the ordering portal does, and he was not sure a concrete date field exists on the planner side. Checked:

- `customer_portal.item_availability.back_on` is a real `date` column (migration 0357:28); the planner screen `/planning/portal-catalog` has an `<input type="date">` for it (`gt-factory-os-portal` `page.tsx:269-273`); the API validates `YYYY-MM-DD` (`routes.ts:119`); the overlay hides it once the day has passed in Asia/Jerusalem (`pricing.ts:175`); the ordering portal renders `צפי {d.M}` (`index.html:635, :805`), plus `return_note` (≤25 chars) and the planner's alternative product.

**No deepening is needed.** Requirement **DR-05**: the Builder reads the same overlay (`withAvailability`) and shows the same words in the same rule: a drink whose product is off shows `לא זמין כרגע` and, when `back_on` is set and not passed, `צפי d.M`; with an alternative product named by the planner, the drink says `בינתיים: <alternative>`. One source, one rule, two surfaces.

## 1. MB-D02 — Segmentation and bypass (decided)

- **Eligibility in V1 = whoever holds a personal link or a portal session.** No lead-type logic (exploratory / high-intent / returning) in V1: the data to segment does not exist (no venue type is collected anywhere, DL-11 gap), and the approved model already serves each type without a switch: the inspiration seeker gets the pre-selected set; the one who knows takes the fast path to the catalog (`אני כבר יודע מה להזמין`, approved with MB-D08); the returning lead reopens the link and finds the menu (D07); the existing customer gets the optional tile in the portal (MB-D06).
- **Context is the only personalisation:** the campaign/category key (DR-01), carried on the link.
- **Chains and accompanied deals** (Alex's track, August doctrine): same Builder; the salesperson builds *with* the customer on a call if they want; nothing special in V1.
- Reason: segmentation without data is guessing (Sales-Machine rule 3); every path above is already an approved product behaviour.

## 2. MB-D07 — Save, resume and identity (decided, PROVISIONAL on DL-03)

- **State lives on the server, keyed by the person**, in `customer_portal.builder_session`: `id`, `lead_id` (nullable) or `access_id` (nullable, exactly one set), `context` (lead-menu key or null), `selection` (jsonb: ordered list of drink ids), `kit_overrides` (jsonb: product → qty after the customer edited), `status` (`building` · `menu_completed` · `kit_accepted` · `ordered`), `created_at`, `updated_at`, `completed_at`. One active session per lead/customer; a new "start from scratch" archives the old row (append history, never overwrite the completed one).
- **The personal link is the resume key.** For a lead, a token link with purpose `builder` (same `randomBytes(32)` + sha256 mechanism as `lead_link`), 14 days, **reusable**, and **not closed by an order**: the order submission closes order links as today (`closeLinks`), but the Builder stays readable so the customer and the salesperson can return to the menu. Mechanism proposal: a `purpose` column on `customer_portal.lead_link` (`order` default, `builder`), `closeLinks` closing `order` only. This is a Sales-lane schema change → **integration contract item IC-1**, not built here.
- For an existing customer, the session cookie `gtp_sid` (Path `/portal`) is the identity; the Builder lives under `/portal/…` for that reason.
- **Client side:** nothing authoritative. A debounced save (250 ms, the portal's pattern) on every change; `localStorage` only for the "resumed" banner. A lost network keeps the last server state and says so.
- **After the first order:** the finish stays reachable (menu + kit, read-only, with `להזמין שוב` going to the portal once the customer exists). The salesperson's deep link to the lead shows the same.
- Reason: the masterprompt's resume requirement (§23) with the system's existing identity (link for leads, cookie for customers); no second identity, no account, no email.

## 3. MB-D09 — Sales System Integration Contract (proposal)

Relationship: **Lead → Builder → CRM → Salesperson → Recommended Cart → Order.**

| Item | Proposal | Depends on |
|---|---|---|
| Entry trigger | A `builder` link minted by the lead journey wherever Tom's placement decision puts it (MB-D01); for customers, the portal tile. | MB-D01, DL-08 |
| Identity | `lead_id` + `wa_phone` (lead) or `access_id` → `shopify_customer_id` (customer). Never typed, never inferred from the site. | DL-01, DL-02 |
| Personal link | purpose `builder`, 14 days, reusable, survives orders (IC-1). | DL-03 |
| Saved state | `customer_portal.builder_session` (§2). CRM reads it through one read model `api_read.v_sales_builder` (menu, kit, status, timestamps) — never the raw jsonb. | — |
| CRM-visible intent (lead events) | Four new `event_type`s, additive to the CHECK (0360 pattern): `builder_opened` (first open per link), `builder_menu_completed` (payload: drink ids, names, product count), `builder_kit_accepted` (payload: kit lines, total ex-VAT, rounded_up: bool), `builder_help_requested` (payload: session id, screen). The existing `draft_order` fires unchanged when the kit is sent. No event for every add/remove (that is analytics, §4). Actor `system:menu-builder`. Written directly (no `touch_first`), like `website_lead_intake`. | DL-04 (migration in the Sales lane) |
| Salesperson surfaces | `LeadDrawer`: a "התפריט שבנה" block between the Shopify snapshot and פרטים: the drinks, the kit lines with coverage, the total, the status, `נבנה לפני 2 ימים`, one link to open the Builder as the customer sees it (read-only staff view). Timeline labels for the four events (`EVENT_LABELS` + `describe()`). Under Unit A: a `LeadJourneyRail` milestone `תפריט נבנה`. Hebrew strings via the tranche register. | DL-07 (tranche after 185) |
| Tasks (Unit A) | `builder_help_requested` → task kind `reply` (same as `lj.more`), keyed `builder:help:<lead_id>:<session_id>`. `builder_menu_completed` with no `draft_order` within 24 h → task kind `call`, title `הלקוח בנה תפריט ולא הזמין`, keyed `builder:nudge:<lead_id>:<session_id>`, cancelled by `draft_order`, `lost`, `opt_out`. **Put to Tom (§9).** | DL-06 (trigger rule in 0362's successor) |
| Next-best-action | The salesperson's call opens with the menu in front of them; the outcome sheet is unchanged. If the owner logs `answered_progressing`, the existing wake-up sequence runs; wake message 1 carries the order link as today (the Builder link if Tom's placement puts it there). | DL-08 |
| Finish handoff | Send = the existing lead path (`lead_submission` → draft, `draft_order` event, confirmation, Telegram) or the customer path (`order_submission` → order). The Builder passes `lines[{key, qty, price}]` to the same functions; it never calls Shopify. | DL-09 |
| Order handoff attribution | `lead_submission` / `order_submission` gain `builder_session_id` (nullable) so an order is attributable to a menu. | DL-09 |
| Analytics attribution | `builder_session.context` + the lead's `source`/`campaign_name`; no new attribution fields. | DL-12 |
| Outreach | The Builder sends nothing. Any message that mentions the Builder is an existing journey message, behind D-005. | DL-14 |

## 4. MB-D10 — Analytics (decided)

- **One append-only table `customer_portal.builder_event`:** `session_id`, `event`, `payload`, `created_at`; written server-side from the Builder's API calls (the client posts intents, the server records what it accepted). No third-party tag, no client-only events, no GTM dependency (DL-12 gap stays a gap for now).
- **Event taxonomy (semantics fixed before code):** `open` (link or tile; payload context, resumed: bool) · `drink_view` (detail opened) · `drink_add` · `drink_remove` · `preset_cleared` · `menu_completed` (the customer tapped to the kit) · `economics_viewed` (detail with figures opened) · `kit_shown` (payload: lines, total, rounded_up, below_minimum_before) · `kit_edited` (line, from, to) · `kit_sent` (→ submission id) · `help_requested` · `fast_path` (left to the catalog) · `resumed`. `abandoned` is not an event, it is the absence of `menu_completed` after N days in a query.
- **Success is measured downstream, on the lead:** Lead → First Order (`converted`), time from `builder_opened` to `draft_order`, kit acceptance (sent kit vs shown kit, line by line), AOV of Builder orders vs non-Builder lead orders, human touches (`outreach`/`outcome` events) per converted lead, recovery (orders after a `builder:nudge` task). All of it is one query joining `builder_event`, `builder_session` and `lead_event`; a read model `api_read.v_sales_builder_funnel` serves it. No dashboard in V1.

## 5. MB-D11 — Architecture (decided)

- **Where:** inside the customer ordering portal, `gt-factory-os/api/src/portal/`, as a second page `/portal/builder/<token>` (lead) and `/portal/builder` (customer session), registered in the same `registerPortalRoutes` scope so it inherits the security headers, the Origin/JSON guard, the cookie, `customerOr401`, `pricedFor`, `withAvailability`, the pairs and minimum rules and the two submission paths. Same lane (`backend-db` / portal-public), no staff-portal change in V1 beyond the CRM proposal above.
- **Server-authoritative calculations:** `POST /portal/api/builder/<token>/kit` takes the selection and returns the kit (products, quantities, coverage, totals, round-up explanation, availability); the client never computes money or quantities. The figures, doses and the drink → product table are read server-side.
- **Data:** `api/src/portal/builder/drinks.ts` — the 48 rows (figures-file page id, Hebrew name, group, sub-family, products `[{catalog key family, dose}]`, photo id, tags) authored once from the cost model and Canva, **Tom-verified** (DL-18, NEEDS DATA); `api/src/portal/builder/figures.json` synced from the brain's `drinks_final_figures.json` with a provenance file and a check script that fails CI on drift (gt-site's `sync_figures.py --check` pattern). Pack servings derived at runtime from pack size ÷ dose.
- **Images:** the 48 drink photos self-hosted under `/portal/img/d-<id>.webp` in two sizes (CSP `img-src 'self'`), exported from the same Canva sources gt-site uses.
- **Frontend:** the portal's own stack (one HTML file, inline CSS, ES5 IIFE, shared `:root` tokens enforced by `tokens.test.ts`), Hebrew RTL, light only, the same card, stepper, sheet, bar and send state machine. No framework, no build step.
- **Tables:** `customer_portal.builder_session`, `customer_portal.builder_event`, plus `builder_session_id` on the two submission tables; the `lead_link.purpose` column and the four `lead_event` types are Sales-lane changes (IC-1, IC-2) requested through the contract.
- **Gate:** the existing `customer_portal_live` flag plus a Builder allowlist value (`value.builder_allowlist`), so the Builder can ship dark behind the live portal.
- Reason: the masterprompt's own rules (reuse authoritative infrastructure, no duplicate truth, server-authoritative money, same design family) all point at the portal; the alternative (gt-site) has no identity, no prices and a frozen intake contract.

## 6. MB-D12 — Explicit V1 non-goals (decided)

Hot or winter drinks · recipes or preparation steps in the selection flow · any volume forecast or business-type questionnaire · presets beyond the five approved sets · discount tiers or customer-specific pricing logic · the 24-hour branded-menu reward (struck by Tom) · printing or generating a menu file · any WhatsApp or email sent by the Builder · AI suggestions · filters, search, sorting controls · dark mode · English · an anonymous site mode · new staff-portal screens (only the drawer block and labels) · multi-branch or chain logic · allergen or nutrition data · per-customer food cost · GT internal margins · a dashboard.

## 7. New dependency rows

- **IC-1** `customer_portal.lead_link.purpose` (`order` | `builder`), `closeLinks` scoped to `order` — Sales lane.
- **IC-2** four `lead_event` types + trigger routing (`reply`, `call`) — Sales lane, after Unit A.
- **IC-3** `api_read.v_sales_builder` read model + `LeadDrawer` block + labels — portal tranche after 185.
- **IC-4** `lead_submission.builder_session_id`, `order_submission.builder_session_id` — Builder lane, additive.

## 8. What Session 2 should challenge hardest here

The `purpose` column on `lead_link` versus a separate `builder_link` table; four event types versus one `builder` type with a `kind` payload; whether `v_sales_attention.stalled` must exclude Builder events; whether the drink table belongs in code or in a table the planner can edit.

## 9. The one question for Tom

When a lead completes a menu and does not send the kit within 24 hours, the CRM opens a task for the lead's owner: `הלקוח בנה תפריט ולא הזמין` (kind `call`), with the menu and the kit on the lead, cancelled automatically by an order, `lost` or opt-out. No automated message is sent; the human calls. Approve, or set a different wait (or none).
