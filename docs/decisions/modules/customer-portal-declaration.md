# Module Declaration — `customer-portal`

**Status: APPROVED (content: Tom, in writing, 2026-09-25, spec §4.5) — file confirmation pending**

> **Drafted:** 2026-09-24. This is the first half of D1: `MODULE_TEMPLATE.md` filled in by
> transcription only, for Tom to read and decide on.
>
> **Transcribed from** two private files in `gt-factory-os`. They are cited by path and section, and
> no customer data is copied from them.
> - The overnight masterprompt,
>   `gt-factory-os/docs/superpowers/plans/2026-09-24-customer-portal-overnight-masterprompt.md`,
>   **revision r2** (`gt-factory-os` main `3a8a968`, PR #287). r2 is the red-team revision of r1
>   (PR #285). Where the two differ, this file follows r2. By the masterprompt's own rule, a
>   revision may correct r1 but can never widen what Tom approves (W0 step 1). The difference that
>   matters most here: under r2 the portal never writes the bot's customer map (§8).
> - The design spec, `gt-factory-os/docs/superpowers/specs/2026-09-24-customer-portal-design.md`
>   (main): §4.1–§4.4 hold Tom's dated Phase-A decisions in his own words, and §5 lists the conflicts
>   with authority documents.
>
> **How D1 is given.** Tom decides each proposal in `customer-portal-decisions.md` in his own written
> words, with a date: he approves it, says what to change, or rejects it. A changed item follows his
> change. An item he rejects or does not address is not built (masterprompt §1.2). His words are
> recorded privately, in spec §4.5 (masterprompt header). This file approves nothing. Pasting the
> masterprompt is not an approval either (masterprompt header).
>
> **Since D1** (2026-09-25, spec §4.5), the router routes this module by rules 1/2/4/5 of
> `AI_BRAIN_ROUTER.md` §3, per-module isolation from §8's allowed paths. No code, schema, agent,
> command or UX surface has been built for it yet (`CLAUDE.md` §New modules; `MODULE_TEMPLATE.md`
> hard rule).
>
> **This file is public.** It holds no customer name, phone number, price paid, Shopify customer id
> or host name, and gives counts only. The private spec holds the detail.
>
> **Owner of the declaration process:** `factory-os-governor`. **Approver:** Tom.

---

## 0. Summary for Tom

### 0.1 What D1 asks Tom to decide: masterprompt r2 §1.2, items 1–10

| Item | Proposal | Where in this file |
|---|---|---|
| §1.2-1 | **The module.** The name is `customer-portal`. Its private schema `customer_portal` holds five tables, and the module touches no core table. Outside that schema it writes one row only: its own flag row. Three lanes (`backend-db`, `portal`, `integration`) do the work with the existing executor agents, so no new agent files are needed. Three writes happen outside the schema: (a) the Shopify order; (b) transactional WhatsApp replies; (c) nothing is written to the bot's map. | §1, §3, §5, §8, §12 |
| §1.2-2 | **Exceptions to authority documents, for this module only:** customer pricing by the family rule; customers log in by a WhatsApp link; the portal keeps a log while Shopify owns the order; the order engine is used through a wrapper and never edited. | §0.3 |
| §1.2-3 | **Who may log in at launch:** 195 map rows. These are the 194 rows whose phone is on exactly one Shopify customer record, plus the 1 manual row. The 15 multi-match rows, and every phone added later, go through registration and staff approval. | §4, §5 |
| §1.2-4 | **The backfill rule** that puts §1.2-3 into the database. | §5 |
| §1.2-5 | **Launch control.** A single flag, `customer_portal_live`, replaces the ≥24h soak. Turning it off is the rollback. | §11, §16 |
| §1.2-6 | **Staff approval screen** `/admin/portal-registrations`: in English, `admin` only, with "Create login link". | §10.2 |
| §1.2-7 | **Test access:** at most two one-time login links, for the internal test mapping only. | §14 |
| §1.2-8 | **Never shown:** 0.3 L, and four SKUs that are active in Shopify but not sold. | §4 |
| §1.2-9 | **Customer-facing Hebrew:** Appendix A word for word; the design reference's strings, without its demo line; and the site-entry label. | §10, Appendix A |
| §1.2-10 | **Site entry:** it goes into an unpublished theme copy. Publishing it is Tom's act. | §10.3, §17.2 |

### 0.2 Already decided in Phase A (2026-09-24). Not reopened here.

S1–S16: `customer-portal-decisions.md` Part B, each with Tom's words and its spec citation. Two rest
on "no objection", not his words: S11 (billing) and S15 (the "later" list).

### 0.3 Exceptions to authority documents

| # | Authority line | What the module does | Source | Status |
|---|---|---|---|---|
| X1 | `LOCKED_DECISIONS.md:326`: "Do not add customer pricing unless explicitly confirmed" | Prices each customer by the family rule (§4) | masterprompt §1.2-2. In Phase A, Tom approved the pricing rule itself (spec §4 row 2, §4.1). | exception approved 2026-09-25 (spec §4.5) |
| X2 | `LOCKED_DECISIONS.md:97-101`: "Supabase magic-link email auth" (`:98`); roles `operator` / `planner` / `admin` / `viewer` (`:101`). `EXECUTION_POLICY.md:138`: an auth flow change needs Tom's written approval | Customers log in with a one-time WhatsApp link, into a customer realm that is separate from staff. Staff auth is untouched. | §1.2-2; spec §5 item 6 | exception approved 2026-09-25 (spec §4.5) |
| X3 | `LOCKED_DECISIONS.md:129`: "System does not own customer orders" | The rule holds, so this is not an exception. The portal keeps a submission log, and Shopify owns the order. | §1.2-2 | confirmation approved 2026-09-25 (spec §4.5) |
| X4 | none cited in the source | The order engine (`api/src/order-intake/engine/`) is used through a wrapper and never edited. This is a scope rule (masterprompt §5). | §1.2-2 | approved 2026-09-25 (spec §4.5) |
| X5 | `MODULE_TEMPLATE.md:118`: a flag flip needs "Tom approval + dry-run + ≥24h soak + RUNTIME_READY". The same ceremony appears at `EXECUTION_POLICY.md:117` and `:134` | `customer_portal_live` replaces the ≥24h soak. The safety evidence in its place is D3, D4 and D8, plus Tom's own first order. | §1.2-5 | exception approved 2026-09-25 (spec §4.5) |
| X6 | `sales-declaration.md:284`: customer-facing sends sit behind `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` | WhatsApp replies to a customer's own action are transactional, not outreach, so that flag does not govern them | §1.2-1(b) | approved 2026-09-25 (spec §4.5) |
| X7 | `LOCKED_DECISIONS.md:131` and `:265`: Green Invoice is supplier-invoice evidence only | The portal does not introduce this. Every Shopify order already gets a Green Invoice customer invoice through an existing Shopify-side integration (spec §2 W0-3). The portal calls no Green Invoice API, and billing is unchanged in v1. | spec §5 item 7 | named; no change proposed |
| X8 | `sales-declaration.md:286-287`: LionWheel and Green Invoice are read-only for the sales module | The portal writes neither. LionWheel picks the order up through its own Shopify integration (spec §2 W0-2). | spec §5 item 8 | named; no change proposed |
| X9 | `LOCKED_DECISIONS.md:107`: "No full RTL layout in v1" | The customer pages are Hebrew and RTL throughout (spec §6; the design reference) | Named neither in masterprompt §1.2-2 nor in spec §5; found while drafting | `UNRESOLVED — for Tom` (U3) |
| X10 | `LOCKED_DECISIONS.md:80`: operator copy is "per-string Tom-pinned; no surface-wide approval is implied". `EXECUTION_POLICY.md:139`: Hebrew copy needs a Tom register entry | §1.2-9 approves the design reference's strings by reference, not one by one, and no register location is named for pages the API serves | found while drafting | `UNRESOLVED — for Tom` (U4) |

### 0.4 The numbers (counts only, measured 2026-09-24)

- **`order_intake.wa_customer_map`** is the WhatsApp order bot's map from phone to Shopify customer.
  It has 210 rows, one phone each, and every row has a customer (masterprompt §2.2):
  - 194 rows were auto-resolved by the bot because the phone is on exactly one Shopify customer
    record.
  - 15 rows were auto-resolved across several accounts. For these, the bot picked the account with
    the most orders.
  - 1 row was entered by hand. It appears to be GT's internal test mapping. This is not yet
    confirmed, and it must be confirmed privately before any use (r2 W0 step 6).
- **Replay** of the 1,115 non-cancelled orders since 2026-06-26, under the Phase-A rules (spec §2
  W0-4b, §4.2):
  - 742 (66.5%) would go straight in, with no one re-keying them.
  - 349 are under ₪800 and would be redirected to WhatsApp.
  - 36 would go in without a line on an archived or unknown SKU. That line stays greyed out.
- **WhatsApp outbound from the order line has never succeeded in production.** Every send attempt
  from 2026-09-09 to 2026-09-24 failed (masterprompt §2.2). Until Tom's switch M1, no login link can
  reach any phone.

---

## 1. Module name

`customer-portal`, with the private schema `customer_portal` (masterprompt §1.2-1).

## 2. Business purpose

GT's business customers do not order for themselves online today: in the last 90 days the online
store produced 0 orders, and all of the latest 100 orders reached Shopify as draft orders (spec §1).
The portal lets a customer with portal access log in by WhatsApp, see their own prices (the prices
they already pay, by the Phase-A family rule), reorder a past order, and send an order that lands in
Shopify as an ordinary order, which Green Invoice, LionWheel and route-print-pack then handle exactly
as today (masterprompt §1, §1.1). Its primary users are GT's business customers (external) and GT
staff with the `admin` role, who approve registrations and can create a login link by hand (§1.2-6).
It comes now because three things are in place: Phase A settled the pricing, login and registration
rules with Tom on 2026-09-24 (spec §4); the page design is finished, as the v6 reference Tom reviewed
over six rounds (design reference README); and Tom's bar for it, in his words, is
`לא מתפשרים על הuiux!` (spec §4.4).

## 3. Owner lane

Approved 2026-09-25 (§1.2-1, spec §4.5): three owner lanes. The existing executors carry them under this module's scope:
- `backend-db`: the API module and the migration;
- `portal`: the staff screen (portal tranche 179);
- `integration`: the Shopify order write and the WhatsApp replies.

**Primary owner lane** (the lane that decides ambiguous routing, template §3):
`UNRESOLVED — for Tom` (U1). The sources name three lanes and no primary one.

## 4. Source of truth

| Entity | Primary key | Authority (storage) | Tiebreaker when sources disagree |
|---|---|---|---|
| Customer order | Shopify order id and name | Shopify | Shopify wins. `LOCKED_DECISIONS.md:129` holds: `order_submission` is a log of what the portal sent, not the order (§1.2-2). |
| Portal access: which phone may log in, and as which Shopify customer | `customer_portal.access.id` (uuid); `wa_phone` is unique | `customer_portal.access` | Only `access` decides portal login. It is backfilled once from the bot's map (§1.2-4). After that it changes only when staff approve or revoke. The map is never written, and later edits to the map do not flow in (r2 §1.2-1(c)). |
| Customer price | none stored; computed on each request | Shopify. The price comes from the customer's last 40 non-cancelled orders (the paid line price, after discounts). The list price is the SKU's variant price. | One pricing function serves both the catalog view and the order submit. The submit reprices from a fresh snapshot and refuses any line whose price moved (`409 PRICE_CHANGED`). `sales_core.customer_price` is not a source; it held 0 rows on 2026-09-24 (masterprompt §2.4, §3.5). |
| What a customer can see | SKU | brain `docs/warehouses/catalog-truth.md` (40 SKUs), plus items the customer already buys outside it. Minus 0.3 L (decided in Phase A) and minus the four exclusions in §1.2-8. | A line is sellable only if it resolves to an ACTIVE Shopify variant priced above 0 (r2 W3). The exclusions apply even to items in the customer's own history. |
| One-time links, sessions, registrations | uuid | `customer_portal.link`, `.session`, `.registration` | owned by the module |
| Launch gate | `flag_key` | the `private_core.feature_flags` row `customer_portal_live` | The flag row is the only switch (§1.2-5). |
| Staff identity | existing | existing staff auth (the `admin` role) | untouched (§1.2-2) |

**Pricing rules** (Phase A, not reopened): the family rule as `customer-portal-decisions.md` S6
states it (spec §4.1–§4.2), plus:
- **Amounts** (spec §2 W0-VAT; masterprompt §3.4):
  - The number stored in Shopify is ex-VAT. The page shows it labelled ex-VAT, then VAT = subtotal ×
    0.18, then total = subtotal × 1.18.
  - The page never shows Shopify's own tax fields.
  - Each order line is written with the stored number. It is never multiplied or divided by 1.18.
- **Minimum:** ₪800 ex-VAT, on those same numbers (Sales-Machine D-015). The engine's own minimum
  flag is informational only; the portal applies ₪800 itself (spec §2 W0-VAT).

## 5. Data model

All five tables live in the private schema `customer_portal` (§1.2-1; masterprompt r2 W2):
- `revoke all on schema customer_portal from public`.
- RLS is on for every table, with no policies, so only the table owner (the API's Postgres pool) can
  read them.
- No table has a foreign key to any factory-os core table.

| Table | Primary key | Holds | Mutable? | Audit |
|---|---|---|---|---|
| `access` | `id` uuid; `wa_phone` unique | Who may log in, as which Shopify customer: the phone, the Shopify customer id, a display name and a branch | Yes. A staff revoke sets `revoked_at`, and a later approval re-activates the row. | `approved_at`; `approved_by` (`backfill-2026-09-24` or a staff email); `source` (`backfill` or `registration`); `revoked_at` |
| `session` | `id` uuid; `token_hash` unique | A signed-in device, for 180 days | Yes (`last_seen_at`, `revoked_at`) | `created_at`, `expires_at`, `revoked_at`. Only the sha256 of the cookie token is stored, never the token. |
| `link` | `id` uuid; `token_hash` unique | One-time `login` and `register` links sent to a phone | Set once (`used_at`) | `created_by` (`whatsapp`, a staff email, or `e2e`), `created_at`, `expires_at`, `used_at`. Stores the hash only. |
| `registration` | `id` uuid; at most one `pending` row per phone (partial unique index) | Business name, branch or city, contact name, a suggested customer (read from the map when the phone is already there), and the decision | Yes (`pending` → `approved` or `rejected`) | `decided_by`, `decided_at`, `created_at` |
| `order_submission` | `id` uuid; `idem_key` unique | A log of each submit: the lines as the server priced them, the ex-VAT subtotal, the Shopify draft id, order id and order name, and any error | Yes (`submitting` → `created` or `failed`) | `created_at`, `updated_at`, `status`, `error` |

**Backfill** (§1.2-4, approved 2026-09-25 (spec §4.5)). It takes every row of `order_intake.wa_customer_map` that has a
`shopify_customer_id` and whose note does not start with `auto-resolved from Shopify;`:
`shopify_customer_id is not null and coalesce(notes,'') not ilike 'auto-resolved from Shopify;%'`.
- On 2026-09-24 that selects 195 rows (194 single-match plus 1 manual) and leaves out the 15
  multi-match rows (masterprompt §2.2).
- If Tom wants a person to approve every row instead, the backfill is empty. The staff screen then
  needs a bulk "approve" for the single-match rows, which is a new item for his approval (§1.2-3).

**Outside the schema** (§1.2-1):
- The migration inserts one row into `private_core.feature_flags`: `customer_portal_live`,
  `enabled=false`, `value={"allowlist":""}`.
- Later changes to that flag are data entries made through `apply_migration` (masterprompt r2 W2,
  landmine 5).
- Nothing else outside the schema is created or written.

**Migration:** `db/migrations/NNNN_customer_portal.sql`, plus the pgTAP file
`db/tests/NNNN_customer_portal.test.sql`.
- NNNN comes from the FR1→write→FR2 bracket, run against both the migrations folder and the
  production migration list (`EXECUTION_POLICY.md:75-88`; masterprompt landmine 4).
- It is applied between the house entries `check_rebuild_verifier_before_NNNN` and
  `check_rebuild_verifier_after_NNNN` (r2 W2).

## 6. Upstream systems

| System | What is read | Auth | Frequency | Freshness tolerance | Failure mode |
|---|---|---|---|---|---|
| Shopify Admin API | The customer's last 40 non-cancelled orders, for prices and "order again". The ACTIVE variants of catalog and history SKUs. Draft orders by tag, for idempotency. Customer search, on the staff screen. | The backend's existing app token (§1.2-1(a)) | Live on each request. Variants are cached 10 min and a customer's history 5 min. The order submit always reads fresh. | 5 min for display. None for a submit, which reprices fresh and can return `PRICE_CHANGED`. | The submit answers `SHOPIFY_ERROR`, and the page shows the A9 "send failed" line. A create timeout triggers a tag lookup, never a blind second create. |
| WhatsApp order line (inbound) | Only a text that normalises to A1. It is caught by a single front gate `(0b)` in the bot's message handler, placed after the lead-line gate. | Unchanged: the order-intake bot's existing inbound path | Per message | Live | With the flag off, the gate returns nothing and the bot runs unchanged. |
| `order_intake.wa_customer_map` | Phone → Shopify customer. Used for the one-time backfill, and to suggest a customer on a registration. The `portal-verify` script also selects eligible customers from it, read-only (r2 W7). | Database | The backfill runs once; the suggestion is read per registration | n/a | n/a |
| `order_intake.wa_event_log` | The time of the phone's newest inbound message. It decides whether an order confirmation falls inside the 24-hour window. | Database | Per created order | Live | The confirmation is skipped, and the order still returns 201. |
| `private_core.feature_flags` | The `customer_portal_live` row | Database | Every session request and every gate check | Live | n/a |
| brain `docs/warehouses/catalog-truth.md` | The 40 sellable SKUs. They are hard-coded in `api/src/portal/catalog.ts` from the design reference's page-id → SKU table, which is itself read from this file. | Repo | At build | Per release | n/a |

## 7. Downstream consumers

| Consumer | How it gets the data | Stale-read tolerance |
|---|---|---|
| Green Invoice, LionWheel, route-print-pack and planning demand (all via Shopify) | The portal's order is an ordinary Shopify order: a completed draft, tagged `portal`. Each system picks it up through its existing path, as it does today. Billing is unchanged in v1 (spec §4.3 item 1; §2 W0-2, W0-3, W0-5a). | as today |
| The customer | The ordering page (with a session) and the WhatsApp replies (A2–A4, A6) | live |
| GT staff (`admin`) | The staff screen `/admin/portal-registrations`. A Telegram message to the existing staff alert chat on each new registration; its text is staff-facing (masterprompt r2 W3). `complete_failed` alerts through the existing alert path. | live |
| The `portal-verify` workflow | D3 and D4 verification: read-only, counts only (masterprompt r2 W7) | per run |

## 8. Write boundaries

```yaml
may_write:
  - customer_portal.* (the five tables)
      by backend-db-executor (the migration) and by the API at runtime
  - private_core.feature_flags, the customer_portal_live row only
      The migration creates it disabled. Before launch it may be enabled for the
      internal test mapping only. Pilots or "*" only on Tom's word (§1.2-5, M3).
  - Shopify draftOrderCreate + draftOrderComplete(paymentPending:true),
      tagged portal and pk-<idem_key>, through the backend's existing app token
      (§1.2-1(a)). draftOrderCalculate runs first, as a check.
  - WhatsApp text replies through the existing order-line sender:
      A2, A3 or A4 only in reply to a customer's own login message;
      A6 once per order, only inside the 24-hour window (§1.2-1(b)).
      Dormant until M1. A5 is sent by a person, not by the system.
  - A Telegram notification of each new registration, to the existing staff
      alert chat (staff-facing text). A failed send never fails the registration.
  - An UNPUBLISHED Shopify theme copy (the site entry), through the Shopify
      connector (§1.2-10)
  - Code: the allowed paths in §12, per lane.
  - docs/decisions/modules/customer-portal-*.md (this declaration and the decisions log)
may_not_write:
  - factory-os core tables (stock_ledger, balance_anchors, items, components, bom_*, ...)
      and every projection
  - order_intake.wa_customer_map, or any other order-bot table (r2 §1.2-1(c))
  - the order engine (api/src/order-intake/engine/) or shopify/commit.ts
      (§1.2-2; masterprompt §5)
  - Green Invoice, LionWheel, Make, planning, stock (§1.2-1)
  - other modules' private schemas, sales_core included
  - any other feature flag, the frozen flags in gt-factory-os/CLAUDE.md,
      or WHATSAPP_AUTO_COMMIT_ENABLED
  - the MAIN Shopify theme; publishing any theme (Tom's act, M5)
  - DNS, Railway settings, tokens (Tom's switches, §17.2)
  - .env*, credentials, secrets
  - brain authority docs, AI_BRAIN_ROUTER.md and REGISTRY.md included
      (MODULE_TEMPLATE.md §8; CLAUDE.md §Write boundaries; this module's rows: §18)
```

## 9. Read boundaries

```yaml
may_read:
  - order_intake.wa_customer_map (once for the backfill; per registration for the suggestion;
      by the portal-verify script, to select eligible customers)
  - order_intake.wa_event_log (the 24-hour window check)
  - private_core.feature_flags (customer_portal_live)
  - Shopify: customers, orders and their line items, product variants, draft orders by tag
  - the existing staff session (admin role), for the staff routes
  - brain docs/warehouses/catalog-truth.md (at build)
may_not_read:
  - factory-os core tables (stock_ledger, balance_anchors, bom_*, ...)
  - other modules' private tables, sales_core.customer_price included (it is not a price source)
  - secrets and .env*, beyond the API's existing runtime configuration
```

## 10. UX surfaces

### 10.1 Customer pages: Hebrew, RTL, served by the API (not the portal)

The design is the v6 ordering-page reference `gt-factory-os/docs/superpowers/specs/2026-09-24-portal-page/`
(private), which Tom reviewed over six rounds. The build ports it and does not redesign it
(masterprompt §0 standard 5, W4). Its sample data is replaced with live data, and its demo line is
removed.

| Route | Access | What it is |
|---|---|---|
| `GET /portal/login` | public, no data | the login page (A7) |
| `GET /portal/l/:token` | one-time token | A small page with no data. It posts the token to be consumed, so that a link preview cannot spend the link (r2 W3). |
| `POST /portal/api/login/consume` | one-time token | Consumes an unused, unexpired `login` link whose access is not revoked, and creates a 180-day session |
| `GET /portal/register/:token`, `POST /portal/api/register` | one-time token | The registration page (A8) and its submit. Creates a pending registration and notifies staff. |
| `GET /portal/` | session | the ordering page |
| `GET /portal/api/bootstrap` | session | The account, the customer's prices and sellable flags, and their recent orders |
| `POST /portal/api/orders` | session | the order submit (§11) |
| `POST /portal/api/logout` | session | revokes the session |
| `GET /portal/api/health` | public, no data | the deployed commit |
| static images and fonts | public | whitelisted files only |

- **Role gating.** Customers are a separate realm, not a staff role.
  - Every session request re-reads the customer's `access` row, which must not be revoked.
  - It also re-reads the flag. If the flag is off, or the customer is not allowlisted, the answer is
    `PORTAL_CLOSED`.
  - Without a session, data routes answer 401 and `/portal/` redirects (302) to login.
  - Logged out, nothing shows a price, a customer name or a phone number (masterprompt §0 standard 2,
    D5).
- **Checked at:** 390×844 and 1360×860 (D8). Spec §6 records the accessibility as built: text contrast
  of 4.5:1 or better, tap targets of at least 44 px, and all motion switched off under reduced motion.
- **UX handoff packet:** U5 · **RUNTIME_READY:** U6 · **Hebrew register:** U4 (strings in
  Appendix A) · **full-RTL layout:** U3 (X9).

### 10.2 Staff screen: English, in the portal, `admin` only (§1.2-6)

- **Route:** `/admin/portal-registrations` in `gt-factory-os-portal` (tranche 179), gated by the
  `(admin)` layout. Whoever holds `admin` approves; today that is Tom.
- **Pending tab.** Each registration shows its phone, its fields and the suggested customer.
  - A customer search shows whether the registration's phone is on that customer's record
    (`phone_matches`, r2 W3 and W5).
  - Buttons: Approve, Reject.
  - After an approval, a "Send approval on WhatsApp" button opens a chat with A5 ready. A person
    sends it.
- **Login-link tab.** Staff search the customers who have access and use "Create login link". This
  creates a 24-hour one-time link, which a person copies or sends by hand through "Open WhatsApp". It
  lets pilots start before WhatsApp sending is fixed.
- **Approved list:** "Revoke access" (r2 W5). It sets `revoked_at` and ends every session of that
  access row.
- **Staff API routes.** They use the existing staff session and require `admin`; anything else gets
  403:
  - `GET /api/v1/queries/portal/registrations`
  - `GET /api/v1/queries/portal/customer-search`
  - `POST /api/v1/mutations/portal/registrations/:id/decide`
  - `GET /api/v1/queries/portal/approved`
  - `POST /api/v1/mutations/portal/login-link`
  - `POST /api/v1/mutations/portal/access/:id/revoke`
- **UX handoff packet:** U5. **RUNTIME_READY:** U6.
- **Hebrew:** none. The surface is English (§1.2-6), so the portal's list of Hebrew surfaces
  (`gt-factory-os-portal/CLAUDE.md`) is not touched.

### 10.3 Site entry (§1.2-10)

A `כניסת לקוחות` link goes into the brand site's navigation, and into the burger menu too. It is
added through the `gt-site` generator and uploaded only to an unpublished theme copy. The build never
writes to MAIN. Publishing is Tom's act, M5 (masterprompt r2 W8).

## 11. Integration surfaces

| Provider / surface | Gate (default off) | Contract | Idempotency | Reversal |
|---|---|---|---|---|
| **Shopify order write.** `draftOrderCalculate`, then the guard, then `draftOrderCreate`, then `draftOrderComplete(paymentPending:true)` | `customer_portal_live`: `enabled`, plus `value.allowlist` (Shopify customer ids, comma-separated, or `*`). Approved 2026-09-25 (§1.2-5, X5, spec §4.5) to replace the ≥24h soak. | masterprompt r2 W3, "Order submit" (private) | One `idem_key` (uuid) per cart, reused on every retry until a definite answer. It is unique in `order_submission` and becomes the Shopify tag `pk-<idem_key>`. On a timeout or 5xx, the tag is looked up before any retry, so there is never a blind second create. A `submitting` row older than 2 min is resolved by the same lookup. | No automated reversal. If the draft is created but not completed: the row becomes `failed`, the draft id is kept, a `complete_failed` alert goes out, and the answer is 202 (A9). A real order is undone by staff: cancel it in Shopify and in LionWheel, and issue a Green Invoice credit (masterprompt §6 M4). |
| **WhatsApp.** Login replies (A2, A3, A4) and one confirmation (A6) | `customer_portal_live`. With it off, the gate falls through and the bot is unchanged. Outbound stays dormant until M1. | masterprompt r2 W3, "WhatsApp gate" | At most 5 links per phone per hour. Login links are valid for 10 min, register links for 24 h, and each works once. One confirmation per created order, only inside the 24-hour window. | A sent message cannot be recalled. An unused link expires. A failed send never changes the order's 201. |
| **Telegram** staff notification | none (staff-facing) | masterprompt r2 W3 | one per registration | n/a |
| **Shopify theme** (site entry) | Unpublished copy only. Publishing is Tom's (M5). | masterprompt r2 W8 | n/a | Leave the copy unpublished, or re-publish the previous theme. |
| **Green Invoice, LionWheel** | not called by this module | n/a | n/a | n/a |

**Frozen flags:** untouched (masterprompt §5; §8 `may_not_write`; `EXECUTION_POLICY.md` §Frozen flags).

**Money- and customer-facing writes.** `EXECUTION_POLICY.md:137` requires Tom's written approval plus
a dry-run. The dry-run is D4: `draftOrderCalculate` runs and 0 orders are created. Tom's written go
comes at M3 (who goes live) and M4 (the first real order).

## 12. Agent ownership

Approved 2026-09-25 (§1.2-1, spec §4.5): the existing executor agents do the work under this module's scope, and no new
agent files are created for v1. This departs from `MODULE_TEMPLATE.md:125` and `:129`, which call for
module-scoped agents and a `<module>-architect` for the declaration phase. Tom's decision on §1.2-1
covers this.

| Lane | Agent | Allowed paths (masterprompt r2 W2–W5) |
|---|---|---|
| module-arch | none created; this declaration was drafted in the docs lane (masterprompt W1) | `docs/decisions/modules/customer-portal-*` |
| backend-db | `backend-db-executor` | `db/migrations/NNNN_customer_portal.sql`, `db/tests/NNNN_customer_portal.test.sql`, `api/src/portal/**`, `api/src/server.ts` (one registration line), root `vitest.config.ts` (include) and `package.json` (`test:portal`) |
| integration | `integration-boundary-executor` | Owns the Shopify order write and the WhatsApp replies (§1.2-1). That covers their code inside `api/src/portal/**`, plus the one `(0b)` gate in `api/src/order-intake/worker.ts`, with its `buildLiveDeps` wiring, because that gate triggers the replies. W3 is headed "backend-db + integration lanes" and does not split files between the two lanes. |
| portal | `portal-production-executor` | The tranche 179 manifest: `docs/portal-os/tranches/179-portal-registrations.md`, `src/app/(admin)/admin/portal-registrations/**`, its route handlers through `src/lib/api-proxy.ts`, `docs/portal-os/registry.md`, and its tests |
| not assigned in the sources | none named | W7: `api/scripts/portal_verify.ts` and `.github/workflows/portal-verify.yml`. W8: the `gt-site` generator (`tools/patch_rtl_shell.py`), the theme files it rebuilds, and the unpublished theme copy. See U2. |

## 13. Commands needed

None are proposed for v1. The sources define no bespoke slash command.

## 14. Tests required

These come from masterprompt r2 W2, W3 (D9), W5 and W7. Each test must exist and pass, reported N/N.

- **Schema.** The pgTAP file is committed. In production the same assertions run as boolean catalog
  and count reads, reported N/N; pgTAP's `plan()` cannot run inside the read-only production
  transaction. The assertions:
  - the tables and their primary keys exist;
  - RLS is on for every table;
  - no backfilled phone is a multi-match map row;
  - every eligible map row was backfilled;
  - the flag row exists and is disabled;
  - the unique index on pending registrations is partial on `status = 'pending'`.
- **Unit tests: pricing.** Vitest, with dependency injection as in the bot's worker tests:
  - the family rule;
  - two prices in the newest order;
  - the list-price fallback;
  - the exact per-SKU price;
  - the 0.3 L and §1.2-8 exclusions;
  - history items from outside the catalog;
  - a history snapshot is never priced as a sibling.
- **Idempotency and failure modes: orders.**
  - A double submit creates one order.
  - A retry with the same key after a lost response creates one order.
  - A stale `submitting` row triggers a tag lookup, then completes the order or marks it `failed`.
  - A key owned by another customer gets 409, and nothing about that row is revealed.
  - A key outside the customer's priced set gets `BAD_LINE`.
  - A price change on one line gets `PRICE_CHANGED`, even when the subtotal is unchanged.
  - `BELOW_MINIMUM`.
  - A create timeout triggers a tag lookup and no second create.
  - A complete failure returns 202, raises an alert and keeps the draft id.
  - A failed WhatsApp confirmation still returns 201.
  - The confirmation is skipped outside 24 h.
  - With the flag off, the answer is `PORTAL_CLOSED`.
- **WhatsApp gate.**
  - With the flag off, the message falls through.
  - A phone with access that is allowlisted gets a login link.
  - A multi-match phone gets the register flow.
  - An unknown phone falls through when the allowlist is not `*`.
  - The rate limit holds.
  - A message that is not A1 is left untouched.
- **Session.**
  - An expired or used link is rejected.
  - Opening the link page alone (a link preview) does not consume the link.
  - Revoked access rejects every request and issues no new link.
  - The cookie flags are set.
  - Logout revokes the session.
- **Routes.**
  - Every data route answers 401 without a cookie.
  - The Origin check holds.
  - The static whitelist refuses `../`.
- **Cross-module.**
  - `rebuild_verifier() = 0` immediately before and after the migration, through the house entries
    `check_rebuild_verifier_before_NNNN` and `_after_NNNN`.
  - All order-intake tests pass, and after deploy the bot's health output is byte-identical (D7).
  - The `api` typecheck adds no new error to the 14-error baseline (masterprompt §2.2).
- **Live in production, with no writes.**
  - **D3, price truth:** at least 30 customers, compared against an independent oracle over the same
    40-order window, with `price_mismatches=0`.
  - **D4:** for at least 10 customers, `draftOrderCalculate` equals the portal subtotal to the agora,
    with 0 errors and 0 drafts tagged `portal`.
  - **D5, logged out:** every data route answers 401, `/portal/` answers 302, and nothing served
    without a session contains `₪` next to a digit.
  - **D8:** Playwright at 390×844 and 1360×860, through a minted test link (§1.2-7). 0 console
    errors, no horizontal scroll, send is never clicked, and the session is revoked afterwards.
- **Staff screen.** A Playwright `@mocked` test that renders pending registrations and approves one,
  plus vitest where the house does it. `portal-pr-guard` is green (D10).
- **Site entry.** The `gt-site` `build.yml` is green, its price guard included, and the MAIN theme is
  unchanged (D11).
- **Evidence layers** (masterprompt §3.2). There are five, none of them substitutes for another, and
  each is reported separately:
  1. stubs;
  2. `portal-verify` against real Shopify, with no writes;
  3. logged-out checks on production;
  4. a minted test login on production;
  5. Tom's own first order.
- **Caveat** (masterprompt §2.3). `gt-factory-os` CI neither typechecks nor tests `api/src`. Every
  gate above is a command the executing session runs and reports N/N. A CI workflow for API tests is
  out of scope (masterprompt §5).

**Test access for D8:** §1.2-7 (approved 2026-09-25 (spec §4.5)). The internal test mapping must first be confirmed
privately, on the map row and on the Shopify customer it points to. If it turns out to be a real
customer, there is no test account: D8's logged-in half is skipped and "name a test account" goes to
Tom (r2 W0 step 6).

## 15. Gates

| Gate | Exit criteria | Masterprompt D-items |
|---|---|---|
| Module Gate 1: Declaration | This file, with Tom's written decision on each §1.2 item, including any changes he makes. **Open.** | D1 |
| Module Gate 2: Foundation | `NNNN_customer_portal` is applied through the FR1/FR2 bracket, between the two verifier entries, and both entries succeed. The backfill count equals the eligible count at apply time, and 0 multi-match rows are backfilled. The production boolean checks pass N/N. The pgTAP file is committed. No new agent files (§12). | D2 |
| Module Gate 3: Truth | D3 price truth and D4 order dry-run are green. The D9 vitest list is green. D6: the deployed commit equals the merge SHA. | D3, D4, D6, D9 |
| Module Gate 4: UX | The D5 logged-out checks pass. The D8 Playwright run passes in production. D10: the staff screen is merged with `portal-pr-guard` green. A `/ux-release-gate` SHIP verdict for the module's routes is U7. | D5, D8, D10 |
| Module Gate 5: Integration | The flag is created disabled, and before launch it is enabled for the internal test mapping only (§1.2-5). The WhatsApp paths stay dormant until M1. 0 real orders until M4. The frozen flags are untouched. D11: the site entry is on an unpublished copy only. | D11 |
| Module Gate 6: Cross-module | D7: the bot is unchanged apart from the gate. `rebuild_verifier() = 0` before and after. Nothing is written to core, to the bot's map, or to `sales_core`. | D2, D7 |
| Execution | D12: the simplification held and every ban-grep returns 0. D13: verification before completion ran last. D14: the report was delivered. | D12–D14 |

## 16. Rollback / disable strategy

- **Feature flag.** Turning `customer_portal_live` off is the rollback (§1.2-5). The portal then
  behaves as if it did not exist:
  - WhatsApp login messages fall through to the bot unchanged.
  - Every portal API answers `PORTAL_CLOSED`, and the page shows the A9 "closed" line.

  To shut out one customer, remove them from the allowlist, or use the staff "Revoke access" button,
  which ends their sessions.
- **Code:** revert through new PRs and redeploy. Never force-push (masterprompt r2 W6 step 7).
- **Schema:** `customer_portal` stays in place, because there is no `DROP` in production
  (`gt-factory-os/CLAUDE.md:19`). The module stays isolated without a drop: nothing in core
  references these tables, and the bot's map was never written.
- **Jobs:** the module adds no scheduled job. `portal-verify` runs only when dispatched.
- **Orders already created:** these are ordinary Shopify orders. Staff undo them one by one: cancel in
  Shopify and in LionWheel, and issue a Green Invoice credit.
- **Site entry:** leave the copy unpublished, or re-publish the previous theme. The build never writes
  to MAIN.
- **Communication plan** (who is told when the portal is switched off): `UNRESOLVED — for Tom` (U8).
- **Rollback dry-run:** the flag-off paths are tested in §14 (the gate falls through; the portal
  answers `PORTAL_CLOSED`).

## 17. Tom decisions required

Each item is tracked in `docs/decisions/modules/customer-portal-decisions.md`.

### 17.1 D1: the ten proposals

These are masterprompt r2 §1.2 items 1–10 (§0.1 above), each marked
`approved 2026-09-25 (spec §4.5)`. By the categories of template §17:
auth §1.2-2, -3, -4, -6 · cross-module §1.2-1 (X6) · Hebrew register §1.2-9 · launch §1.2-5, -7, -8, -10.
- **External integration credentials:** none new. The module uses the backend's existing Shopify app
  token and the existing order-line sender (§1.2-1). Sending needs Tom's M1.
- **Cost and vendor:**
  - No new vendor.
  - Hosting inside the existing API adds ₪0 (spec §4.2 item 6).
  - The login reply goes out inside the 24-hour window the customer's own message opens, so it
    needs no WhatsApp template and costs nothing per message (spec §2 W0-6, W0-6b).

### 17.2 Tom's switches after D1 (masterprompt §6)

None of these needs a secret value in any file (§8 `may_not_write`).
- **M1: fix WhatsApp sending** (about 5 min). This blocks login and every bot reply.
  - It is a configuration change on the API service that only Tom can make. The steps are in
    masterprompt §6 M1 (private).
  - **Proof:** Tom sends A1 from his own phone to the order line and receives a link.
  - **Side effect:** the bot's existing catalog pointer starts reaching customers for the first time
    (masterprompt §2.4).
- **M2: domain** (about 10 min, plus DNS propagation).
  1. Add the portal's subdomain to the API service.
  2. Add the DNS records it shows.
  3. Once the certificate is active, set the portal's public-URL variable.

  Host names and steps are in masterprompt §6 M2 (private). **Proof:** the portal's health route
  answers on the new host.
- **M3: who goes live.** Tom answers `pilots: <names>` or `everyone`, and the session writes the
  allowlist.
- **M4: the first real order** (about 5 min). It needs Tom's written go (§11).
  - Tom logs in as the internal test account, by WhatsApp after M1 or through a staff "Create login
    link" before it.
  - He sends one small real order, ideally something GT needs.
  - **Checked afterwards:** the order is in Shopify, tagged `portal`; Green Invoice issued a type-305
    invoice; a LionWheel task exists.
  - **To undo it:** staff cancel it in Shopify and in LionWheel, and issue a Green Invoice credit.
- **M5: publish** (about 1 min, after M2 and M4). Tom publishes the theme copy that carries the site
  entry, and the session checks the live link.
- **Not blocking launch:**
  - the WhatsApp confirmation template, needed for confirmations outside 24 h;
  - the 15 multi-match customers, who reach the staff screen as they try to log in;
  - three can SKUs whose Shopify list prices are stored grossed up. A customer who never bought them
    would see them 18% high (spec §2 W0-VAT).

### 17.3 UNRESOLVED — for Tom

Each item below is something the template asks for that the sources do not settle.
1. **U1: the primary owner lane** (§3). Template §3 asks for one owner lane, the one that decides
   ambiguous routing. §1.2-1 names three (`backend-db`, `portal`, `integration`) and no primary.
2. **U2: the lane for W7 and W8** (§12, last row). No lane owns W7 or W8; template §12 needs allowed
   paths for each.
3. **U3: RTL** (X9). Tom reviewed it over six rounds; no written exception is recorded.
4. **U4: the Hebrew register for customer copy** (X10). The customer pages are API-served, outside
   the portal register (`portal_ux_standard.md`). Open: where their entry lives, and whether approval
   by reference is enough.
5. **U5: the UX handoff packet** (§10). `LOCKED_DECISIONS.md:81` requires one before merge for every
   user-visible portal change, and template §10 asks for its path. The sources name none for the
   staff screen. For the customer pages, the only UX artifact is the design reference.
6. **U6: RUNTIME_READY** (§10). Template §10 asks for the signal name of a backend-bound surface,
   and portal authoring enters Mode B only on `RUNTIME_READY(form)` (`EXECUTION_POLICY.md` §W2
   modes). The sources name no signal for the staff screen.
7. **U7: `/ux-release-gate`** (§15 Gate 4). Template §15 and §18 ask for a SHIP verdict on every
   module route, and `LOCKED_DECISIONS.md:79` says an open P0 blocks shipping. The sources' UX
   evidence is D8 (Playwright in production) and D10 (`portal-pr-guard`, `@mocked`). They do not say
   whether `/ux-release-gate` also runs, in particular on the customer pages the API serves.
8. **U8: communication plan on disable** (§16). Template §16 asks who is notified when the module is
   switched off. The sources define what customers then see (the A9 "closed" line), but not who tells
   customers or staff.

## 18. Definition of done (module v1)

- [x] Gate 1: Tom's written D1 is recorded privately with its date (spec §4.5).
      `factory-os-governor` then updates this file's status line to cite it.
- [ ] Gates 2–6 are closed with evidence, and D1–D14 are each green with an evidence pointer.
- [ ] Every §17 item is answered, U1–U8 included.
- [ ] Every §14 test is green, reported N/N for each evidence layer.
- [ ] The rollback (flag off) is exercised in tests, and the revert path is written down.
- [ ] `factory-os-governor` adds the module's lane rows to `AI_BRAIN_ROUTER.md` §3 and notes the
      module in `REGISTRY.md`, after D1 (template process step 6).
- [ ] `CURRENT_STATE.md` records the module's live status.
- [ ] Tom's switches M1–M5 are done, or Tom has explicitly deferred them.

---

## Appendix A — Customer-facing Hebrew, approved 2026-09-25 as part of §1.2-9 (spec §4.5)

This is copied word for word from masterprompt Appendix A, which is identical in r1 and r2. Approved
2026-09-25 as written, as part of §1.2-9 (spec §4.5). Tom changed nothing.

**A1 — ready text in the WhatsApp login link:**
`כניסה לפורטל ההזמנות של GT`

**A2 — WhatsApp reply with a login link, in three lines:**
`הקישור שלך לפורטל ההזמנות של GT:` · `{url}` · `הקישור תקף ל־10 דקות ולכניסה אחת.`

**A3 — WhatsApp reply to an unknown or unapproved phone, in four lines:**
`המספר הזה עוד לא מחובר לחשבון לקוח אצלנו.` · `לבקשת גישה לפורטל ההזמנות (דקה אחת):` ·
`{url}` · `אחרי שנאשר, נעדכן אתכם כאן.`

**A4 — WhatsApp reply while a registration is pending:**
`הבקשה שלכם לגישה לפורטל ההזמנות בבדיקה אצלנו. נעדכן אתכם כאן כשתאושר.`

**A5 — approval message, sent by a person from the staff screen, in two lines:**
`הגישה שלכם לפורטל ההזמנות של GT אושרה.` · `להזמנה: {portal_url}`

**A6 — WhatsApp order confirmation (only inside the 24-hour window), in two lines:**
`תודה! קיבלנו את הזמנה {order_name}.` · `סה״כ ₪{subtotal} לפני מע״מ (₪{total} כולל מע״מ).`

**A7 — login page:**

| Element | Text |
|---|---|
| Title | `כניסה לפורטל ההזמנות` |
| Lead | `נכנסים עם וואטסאפ, בלי סיסמה.` |
| Step 1 | `לוחצים על הכפתור ושולחים את ההודעה שנפתחת.` |
| Step 2 | `מקבלים מאיתנו קישור כניסה.` |
| Button | `כניסה עם וואטסאפ` |
| Note | `יש לשלוח מהמספר שממנו אתם מזמינים מאיתנו.` |
| Expired | `הקישור כבר לא בתוקף. שלחו שוב את ההודעה ונשלח קישור חדש.` |

**A8 — registration page:**

| Element | Text |
|---|---|
| Title | `בקשת גישה לפורטל ההזמנות` |
| Fields | `שם העסק` · `סניף או עיר` · `שם איש הקשר` |
| Button | `שליחת הבקשה` |
| Done | `קיבלנו את הבקשה. אחרי שנאשר, נעדכן אתכם בוואטסאפ.` |
| Expired | the A7 expired line |

**A9 — ordering page additions:**

| Where it appears | Text |
|---|---|
| Price changed | `חלק מהמחירים התעדכנו. העגלה עודכנה — בדקו ושלחו שוב.` |
| Send failed | `ההזמנה לא נשלחה. נסו שוב בעוד רגע, או כתבו לנו בוואטסאפ.` |
| Created, not completed | `ההזמנה הגיעה אלינו, והצוות משלים אותה ידנית. נחזור אליכם אם צריך.` |
| Closed | `ההזמנות באתר סגורות כרגע. אפשר להזמין כרגיל בוואטסאפ.` |
| Unsellable line | `לא זמין להזמנה באתר` |
| Reorder skipped lines | `חלק מהפריטים לא זמינים באתר ולא נוספו.` |
| Logout | `יציאה` |
| Special-request WhatsApp text | `שלום, יש לי בקשה לגבי הזמנה` |

**Also covered by §1.2-9, by reference:**
- Every Hebrew string in the design reference
  `gt-factory-os/docs/superpowers/specs/2026-09-24-portal-page/index.html` (private), except its demo
  line `תצוגת דמו. לא נשלחה הזמנה אמיתית.`, which is removed.
- The site-entry label `כניסת לקוחות`.

Any other customer-facing string the build needs is **not** approved until Tom approves it. Until
then, the nearest Appendix A string is used (masterprompt §1.2-9).

**Staff-facing, and not part of §1.2-9** (listed so that every Hebrew string the module sends is
visible here): the Telegram notification of a new registration,
`בקשת גישה חדשה לפורטל: {business_name} · {branch_city}` (masterprompt r2 W3).

## Appendix B — Out of scope for v1, beyond §8 (masterprompt §5)

- the bot's behaviour beyond the `(0b)` gate, including its known receipt-send bug;
- Green Invoice, LionWheel, Make, the distributor billing switch ("Ice Dream"), Resend, and WhatsApp
  templates;
- `gt-factory-os` PR #283 and its migrations 0353/0354;
- `gt-site` PR #16;
- WhatsApp sends to anyone, other than code paths that stay dormant until M1;
- any real order, `draftOrderCreate` or `draftOrderComplete` in production before Tom's go (M4);
- delivery dates, payment, promotions, and email;
- anything in spec §7 that is not in masterprompt §4.
