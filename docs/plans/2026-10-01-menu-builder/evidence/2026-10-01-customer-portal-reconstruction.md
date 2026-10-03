> Evidence — read-only reconstruction by a Session 1 exploration agent, verbatim (2026-10-01). Authority: `system_verified` where a file:line is cited; re-read the file before relying on a value.

# Customer ordering portal: technical and visual reconstruction
Repo `/home/user/gt-factory-os` on main, read 2026-10-01, read-only.

**Path shorthand.** `P/` means `/home/user/gt-factory-os/api/src/portal/`. "spec" means `docs/superpowers/specs/2026-09-24-customer-portal-design.md`. "UX gate" means `docs/superpowers/plans/2026-09-25-customer-portal-ux-gate.md`.

## Five facts that shape a sibling product

1. **No framework, no build, no JS files.** `P/public/app/` holds only `manifest.webmanifest`.
   - The whole ordering UI is one file, `P/public/index.html` (1584 lines). Its CSS and JS are inline; the JS is a single ES5 IIFE using `innerHTML` templates and event delegation.
   - The entry pages (login, link, register) share `P/public/css/panel.css`.
2. **It runs inside the existing Fastify API on Railway.** It is mounted by `registerPortalRoutes(app,{extractSession})` at `api/src/server.ts:118`.
   - The public host is `https://gt-factory-os-api-production.up.railway.app`.
   - `order.gteveryday.com` is wired as `PORTAL_HOST` (`P/login.ts:36`), but DNS has not moved yet.
3. **The session cookie only reaches `/portal`.** `gtp_sid` is set with `Path=/portal` (`P/session.ts:17`), and the CSP is `connect-src 'self'` and `img-src 'self' data:`. A Menu Builder that wants the same identity has to live under `/portal/…` on the same host and self-host its images.
4. **The catalog is code, not a table.** The 40 SKUs are in `P/catalog.ts`, and the presentation data is the `P` list in `index.html:652-683`.
   - Prices are computed live from Shopify order history (`P/pricing.ts`).
   - The only DB inputs to what customers see are planner availability (`customer_portal.item_availability_current`) and the launch flag.
5. **The order handoff is a real Shopify order.** The flow is `draftOrderCreate` → `draftOrderComplete(paymentPending:true)`, tagged `portal` (customers). Lead orders stop at a draft, tagged `lead`.

---

## 1. Routes

### Customer routes (`P/routes.ts:195-339`)
**Common rules for the whole scope:**
- **POST checks** (`:196-203`):
  - Must be `content-type: application/json`, else `415 UNSUPPORTED_MEDIA_TYPE`.
  - When an `Origin` header is present, it must be one of `https://order.gteveryday.com`, the Railway URL, or `PORTAL_PUBLIC_URL`. Otherwise `403 BAD_ORIGIN`.
- **Every response** gets `SECURITY_HEADERS` (`:92-98`) and, by default, `cache-control: no-store` (`:204-208`).
  - The headers are `nosniff` and `referrer-policy: same-origin`.
  - The CSP is `default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'`.
- **HTML pages** are sent `private, no-cache`, with an ETag and 304 support, gzipped when accepted (`:165-172`).

| Method | Path | Auth | Returns | Ref |
|---|---|---|---|---|
| GET | `/` (host = `order.gteveryday.com` only) | public | 302 → `/portal/` | `:193` |
| GET | `/portal` | public | 302 → `/portal/` | `:210` |
| GET (and auto HEAD) | `/portal/` | session | No session: **302 `/portal/login`**, decided on the server. With a session: `index.html`, and it starts the customer's price fetch without awaiting it (`prefetch`, `:186-190`). | `:215-220` |
| GET | `/portal/login` | public | `login.html` | `:221` |
| GET | `/portal/l/:token` | public | `link.html`; never spends the token (WhatsApp previews GET links) | `:225` |
| POST | `/portal/api/login/consume` `{token}` | token | `410 LINK_EXPIRED`, or `{ok:true}` plus `Set-Cookie gtp_sid`. Creates the session and prefetches prices. | `:226-235` |
| GET | `/portal/register/:token` | token | `register.html` if the register link is valid (peek only), else 302 `/portal/login?e=expired` | `:237-238` |
| POST | `/portal/api/register` `{token,business_name,branch_city,contact_name}` (each trimmed, 1–120) | token | `422 INVALID` · `401 LINK_EXPIRED` · `201 {ok:true}`. Inserts a pending registration (idempotent per phone) and sends a Telegram notice to staff. | `:240-252` |
| GET | `/portal/api/bootstrap` | session + flag/allowlist | 401 `UNAUTHORIZED` · 503 `PORTAL_CLOSED` · 502 `SHOPIFY_ERROR` · 200 `{account:{name,branch}, items, extra, recent, min_ex_vat:800, vat_rate:0.18, order_line:'972543982444'}` | `:254-274` |
| POST | `/portal/api/orders` `{idem_key:uuid, lines:[{key, qty:int 1–999, price≥0}] 1–80}` | session + flag | 201 `{order_name}` · 202 `CREATED_NOT_COMPLETED` · 409 `IN_PROGRESS`/`CONFLICT`/`PRICE_CHANGED{items,extra}` · 422 `INVALID`/`BAD_LINE`/`NOT_IN_PAIRS`/`BELOW_MINIMUM` · 502 `SHOPIFY_ERROR` | `:276-283`, `P/orders.ts:37-44` |
| POST | `/portal/api/restock-request` `{key}` | session + flag | 422 `INVALID` · 409 `NOT_UNAVAILABLE` · 200 `{waiting:true}` (a list a person works from; nothing messages the customer) | `:286-295` |
| POST | `/portal/api/logout` | cookie | Always sends the cleared cookie. 401 with no cookie, else revokes the session and returns 204. | `:297-303` |
| GET | `/portal/lead/:token` | token in path | `index.html` in "lead mode": the boot line is string-replaced. It throws at boot if `index.html:12` changes. | `:152-160`, `:306` |
| GET | `/portal/api/lead/:token` | lead token; **flag `enabled` only, no allowlist** | 503 · 410 `LINK_EXPIRED` · 502 · 200 `{account:{name:'',branch:''}, lead:true, items, extra:[], recent:[], min_ex_vat, vat_rate, order_line:'972547588132'}` | `:307-317`, `P/lead.ts:109-116` |
| POST | `/portal/api/lead/:token/orders` `{idem_key, lines:[{key,qty,price,label≤120}], business_name, branch_city, contact_name}` | lead token + flag | 201 `{draft:'#D…'}`, same error codes as orders, 410 on a dead link | `:318-326`, `P/lead.ts:82-94` |
| GET | `/portal/api/health` | public | `{ok:true, commit}` | `:328` |
| GET | `/portal/{img,fonts,css,app}/:name` | public whitelist | Read once at boot into memory (`:84-91`, `:142`). 404 `NOT_FOUND` for anything else. With `?v=`: `public, max-age=31536000, immutable`; without: `max-age=604800`. ETag = first 12 characters of the base64url SHA-1. | `:331-338` |

Pages are templated at boot (`:146-149`):
- `{{V}}` is the asset version, a hash of all asset ETags.
- `{{ORDER_LINE}}` is `972543982444`.
- `{{WA_LOGIN}}` is `https://wa.me/972543982444?text=<A1>`.

### Staff routes
These use the staff Supabase session (`extractOrFail`). The `planner` gate allows planner or admin; the `reader` gate allows operator, planner, admin or viewer (`:344-350`, `auth/session.ts:38-44`).

| Method | Path | Gate | Purpose |
|---|---|---|---|
| GET | `/api/v1/queries/portal/registrations?status=pending\|approved\|rejected` | planner | Access requests (`:352-357`) |
| GET | `/api/v1/queries/portal/customer-search?q=&registration_id=` | planner | Shopify customer search, with `phone_matches` (`:362-379`) |
| POST | `/api/v1/mutations/portal/registrations/:id/decide` `{decision, shopify_customer_id gid}` | planner | Approve or reject. Approval returns a `wa_link` with message A5 for a person to send (`:381-391`). |
| GET | `/api/v1/queries/portal/approved?q=` | planner | Approved customers (`:393-396`) |
| POST | `/api/v1/mutations/portal/login-link` `{access_id}` | planner | 24 h one-time link, `{url, wa_link}`; 409 if the portal is closed to that customer (`:398-413`) |
| POST | `/api/v1/mutations/portal/access/:id/revoke` | planner | Revokes the access row and its sessions (`:415-421`) |
| GET | `/api/v1/queries/portal/catalog` | reader | One row per CATALOG SKU: state, history, waiting count, on_hand, Shopify title (`:424-454`) |
| POST | `/api/v1/mutations/portal/catalog/:sku` | planner | Availability change, one append-only row (`:456-473`) |
| GET | `/api/v1/queries/portal/catalog/:sku/requests` | planner | Open "tell me" requests (`:475-480`) |
| POST | `/api/v1/mutations/portal/catalog/:sku/requests/:id/notified` | planner | Marks a request notified (`:482-489`) |

**Non-HTTP entry point.** The WhatsApp bot's front gate (`api/src/order-intake/worker.ts:215-219`) and the staff invite (`:151`, `:173-186`) run `createPortalGate` and `createPortalInvite` from `P/login.ts`.

---

## 2. Identity and session

### Who a customer is
A customer is one row in `customer_portal.access`:
- `wa_phone` (unique, digits only) ↔ `shopify_customer_id` (gid), plus `display_name` and `branch`.
- `source` is `backfill` or `registration`; `revoked_at` marks revocation (`db/migrations/0355_customer_portal.sql:24-34`).

At launch the table was backfilled from the bot's `order_intake.wa_customer_map`, read-only. The backfill skipped rows whose notes start `auto-resolved from Shopify;` (multi-match phones) (`0355:98-102`). The portal never writes the bot's map.

The launch gate is the flag `private_core.feature_flags.customer_portal_live`: `enabled` plus `value.allowlist`, a comma list of numeric ids or gids, where `*` means everyone (`0355:104-107`, `P/store.ts:149-153`, `P/login.ts:52-60`).

### How login works
Login is a customer-initiated WhatsApp message followed by a one-time link sent to that phone. There is no OTP and no password (`P/login.ts:1-8`).
1. The login page button is `wa.me/972543982444?text=` followed by `A1 = 'כניסה לפורטל ההזמנות של GT'` (`:15-16`).
2. The bot's gate matches A1 after `normalizeText`, which drops punctuation and emoji and lowercases (`:47-50`, `:99-113`).
3. The reply decides by the phone's state (`sendLink`, `:144-165`):
   - **Revoked access:** nothing is sent.
   - **Approved and allowlisted:** a login link `…/portal/l/<token>`, valid 10 minutes, with text A2 (`:18`, `:28`, `:153-155`).
   - **Pending registration:** text A4, no link.
   - **Unknown phone, and the allowlist contains `*`:** a registration link `…/portal/register/<token>`, valid 24 hours, with text A3.
   - **Otherwise:** the gate falls through to the bot.
4. **Rate limit:** 5 replies per phone per hour (`:33`). The count is links in `customer_portal.link` plus A4 replies logged in `order_intake.wa_event_log` (`P/store.ts:163-170`).
5. **Why the link goes to the phone:** inbound WhatsApp is authenticated by WABA id only, with no HMAC. A forged inbound message must never log anyone in, so the link always goes to the phone and never back to the requester (spec §W0-6b `:106-113`).
6. **Staff paths:**
   - Doreen's quick reply ending in `INVITE_MARK = 'הקישור האישי שלכם מגיע בהודעה הבאה'` is echoed to the bot, which mints a 24 h link (`:25`, `:122-136`).
   - The staff "Create login link" route also gives 24 h (`STAFF_LINK_MS`).

### `portal_login_link_sent` and `portal_register_link_sent`
These are `GateAction` values (`P/login.ts:77-79`) that the worker stores as the event's processed status in `order_intake.wa_event_log` (`worker.ts:378-383`, `:404`).
- `portal_login_link_sent`: an approved, allowlisted phone sent A1 and got a 10-minute link.
- `portal_register_link_sent`: an unknown phone, with the open (`*`) allowlist, got A3 and a 24 h registration link.
- The siblings are `portal_registration_pending` and `portal_rate_limited`.
- The invite variants are `portal_invite_link_sent`, `portal_invite_register_link_sent`, `portal_invite_pending`, and `portal_invite_no_link` with a reason: `portal_closed`, `rate_limited`, `access_revoked`, `not_allowlisted` or `registration_closed` (`:83`).

### Tokens, links and sessions
- **Tokens:** `randomBytes(32).toString('base64url')`, which is 43 characters. Only the SHA-256 hex is stored (`P/session.ts:11-12`).
- **Links** live in `customer_portal.link`: `purpose` login or register, `wa_phone`, `access_id`, `created_by`, `expires_at`, `used_at` (`0355:47-58`).
  - A valid link is unused, unexpired, and its access row is not revoked (`P/store.ts:136-138`).
  - Consuming one is an atomic `UPDATE … RETURNING`.
- **Session** lives in `customer_portal.session` with `token_hash`, `access_id`, `expires_at`, `last_seen_at` (touched on every request), and `revoked_at` (`0355:36-44`).
- **Cookie:** `gtp_sid=<token>; HttpOnly; Secure; SameSite=Lax; Path=/portal; Max-Age=15552000`, which is **180 days** (`P/session.ts:7-19`). It is asserted verbatim in `routes.test.ts:113`.
- **Revoking access** revokes every session on it (`P/store.ts:330-336`).

### The entry pages
- **`link.html`** (`P/public/link.html:31-54`):
  - It shows a spinner reading «נכנסים לפורטל ההזמנות…» and POSTs the token to `/portal/api/login/consume`.
  - On success it goes to `location.replace('/portal/')`.
  - On a 4xx it sends `HEAD /portal/` first: an already-signed-in browser goes straight in, otherwise it goes to `/portal/login?e=expired`.
  - After 6 s it adds «זה לוקח יותר מהרגיל…».
  - On a network failure it shows an offline note and a «לנסות שוב» button, and retries automatically on the `online` event.
- **`register.html`** (`P/public/register.html:33-79`):
  - Three fields: «שם העסק», «סניף או עיר», «השם שלכם». Validation is client-side, using `aria-invalid` and inline errors.
  - It POSTs `/portal/api/register`. 201 shows the "received" note and a WhatsApp button; 401 shows the expired note.
  - Staff then approve by picking the Shopify customer. `decide` inserts or reactivates the access row in one transaction with the decision (`P/store.ts:275-312`).
  - Staff are notified by Telegram (`P/deps.ts:31-37`) and by email through the Edge Function `portal-registration-notify` every 5 minutes (`db/migrations/0356…sql`).
- **`login.html`**:
  - It shows `?e=expired|session|out` messages; `session` adds «העגלה שלכם שמורה.» when `gtp_cart_v1` exists.
  - A `HEAD /portal/` probe shows «אתם כבר מחוברים».
  - After the customer comes back from WhatsApp it shows a note, and after 60 s a help link (`P/public/login.html:51-67`).

### Anonymous visitors
An anonymous visitor sees **no catalog and no prices**.
- `/portal/` redirects to login on the server (`routes.ts:215-217`).
- Every data route returns 401.
- `routes.test.ts:68-79` asserts the login page contains no `₪` amount.

The only priced page reachable without a session is a **lead link** (`/portal/lead/<token>`). It shows list prices only.

### Leads (non-customers), in `P/lead.ts`
- **How a lead gets a link.** In the lead journey (`api/src/order-intake/sales/journey.ts:164-170`), the button «אני רוצה להזמין» (`lj.order`) decides:
  - If the phone is in `wa_customer_map` with a Shopify id, the lead gets the normal `${base}/portal/`.
  - Otherwise `createLeadLinkMinter` (`P/lead.ts:38-47`) inserts `customer_portal.lead_link` (`token_hash`, `lead_id` FK to `sales_core.lead`, `wa_phone`, `expires_at = now()+14 days`, `used_at`) (`0360_lead_journey.sql:117-126`).
- **What a lead order writes:**
  - `customer_portal.lead_submission` (`0360:128-145`): `idem_key`, `link_id`, `lead_id`, `wa_phone`, the three fields, `lines`, `subtotal_ex_vat`, `status` (submitting, drafted or failed), and the draft id and name.
  - Two `sales_core.lead_event` rows (`P/lead.ts:298-308`):
    - `draft_order`, with payload `{draft_id, draft_name, total_ex_vat, idem_key}` and actor `system:lead-journey`.
    - `auto_message` for the confirmation.
  - Once an order is submitted, **all** of the lead's links are closed (`:295-297`).
- **What it never writes:** `order_intake` or `customer_portal.access`.

---

## 3. Catalog

**Source: code, not a DB table.**
- `CATALOG` (`P/catalog.ts:28-51`) holds 40 SKUs, keyed `<page id>:<variant key>`:
  - 11 teas × 2 sizes. The `TEAS` stems are at `:22-26`; FRESH is `HIB`, DETOX is `LUI`, `LOW` means regular and `FRE` means sugar-free.
  - 7 matcha and powder products, 3 ODK purées, 8 accessories.
- Families and helpers (`:62-65`):
  - The price families are `TEA_1L`, `TEA_05` and `ODK_1L`, held in `FAMILY_OF`.
  - `category` is `tea`, `matcha`, `odk` or `acc`.
  - `KEY_OF_SKU` maps SKU to key.
- `EXCLUDED_SKUS` (`:57-60`) are never shown, even from history: the four 0.3 L teas plus `GT-SHI-CER-30/50`, `GTCFR-GTCOC-FRO` and `AP-JUG-NEA`.
- History items outside the catalog get the key `x-<encodeURIComponent(sku)>:1` (`:69-71`). They appear in an extra category, «מוצרים נוספים».
- The SKU ↔ key ↔ image map is `docs/superpowers/specs/2026-09-24-portal-page/README.md:23-62`. That folder (`index.html` v6) is "the visual and interaction source of truth… Port it; do not redesign it."

**Presentation data lives only in the page.** The `P` list is at `index.html:645-683`.
- Each product carries `id`, `cat`, `name` (English brand name, set in GT Latin, or Hebrew for accessories), `origin`, `bg` (flavour tint), `c` (flavour accent), `tag` («ללא סוכר»), `six` (bottle product), and `v` variants `{k, label}`.
- Size labels are «1 ליטר», «500 מ״ל», «500 גרם», «1 ק״ג», «22 שקיקים × 18 גרם», «ערכה» and «יחידה».
- `INGR` (`:685`) holds ingredients in customers' words.
- `ALIAS` (`:688-698`) holds search keys from the bot's lexicon.

**Categories and sections.**
- Section order: `tea` «תמציות תה», `matcha` «מאצ׳ה ואבקות», `odk` «מחיות פרי», `acc` «אביזרים», `extra` «מוצרים נוספים» (`:703-706`).
- Chips (`:475-483`): «הכול», «תמציות תה», «תה 1 ליטר», «תה 500 מ״ל», «מאצ׳ה ואבקות», «מחיות פרי», «אביזרים». Each chip shows a count.

**Fields exposed to the customer.** Bootstrap `items[key]` is `{price|null, sellable, unavailable?, upcoming?, headline?, back_on?, return_note?, alternative?, waiting?}` (`P/pricing.ts:66-69`).
- **Sellable** means the engine resolved exactly one ACTIVE variant with a price above 0 (`pricing.ts:124`; `engine/resolve.ts:27-36`).
- A non-sellable item shows «לא זמין להזמנה כאן · להזמנה בוואטסאפ», with a `wa.me` link carrying the item name (`index.html:824-825`).

**Images.**
- They are self-hosted WebP files exported from Canva "Raw", **not Shopify images**, in `P/public/img/`.
- Prefixes:
  - `l-<id>`: 1 L amber bottle.
  - `h-<id>`: 0.5 L illustrated bottle.
  - `p-`: powder bag.
  - `o-`: ODK pouch.
  - `a-`: accessory photo on a sage podium, cropped with `object-fit: cover`.
- Each image comes in two sizes, full and `-320`, served through `srcset`. Intrinsic sizes come from `DIM` (`index.html:709`):

  | Prefix | Full | `-320` |
  |---|---|---|
  | `l` | 298×640 | 149×320 |
  | `h` | 284×640 | 142×320 |
  | `o` | 430×640 | 215×320 |
  | `p` | 342×640 | 171×320 |
  | `a` | 540×540 | 320×320 |

- `sizes` is `(min-width:1100px) 100px, 18vw` for bottles and `(min-width:1100px) 240px, 50vw` for photos.
- The first 4 cards load eagerly with `fetchpriority="high"`; the first-row detox images are also preloaded (`:15-18`).
- The Matcha Kit uses a typographic tile ("Matcha<br>Kit"). Extras use a Hebrew word tile.

### Bottles in pairs (PR #324, commit `32b0623`, Tom 2026-09-28)
- **Server.** `inPairs(sku) = FAMILY_OF.has(sku)` (`P/catalog.ts:63-64`), which covers tea 1 L, tea 500 ml and ODK. Matcha is not in pairs.
  - `orders.ts:181` and `lead.ts:189` return `422 NOT_IN_PAIRS` on any odd qty.
  - This is checked after `PRICE_CHANGED` and before `BELOW_MINIMUM`.
- **Stepper math on the page** (`index.html:926-933`):
  - `stepOf = p.six ? 2 : 1`.
  - `up(q) = min(q + s - q%s, 999 - 999%s)`, so an odd number lands on the next pair, with a maximum of 998.
  - `down(q) = max(0, q - (q%s || s))`.
- **Typed odd quantities** are rounded up, with the note «נמכר בזוגות, אז עיגלנו ל־{n}.» (`:995`).
- **Odd lines from a reorder or a saved cart:**
  - The line is kept and marked `.odd`, with the badge «נמכר בזוגות».
  - Send is disabled with the label «עגלו לזוגות כדי לשלוח».
  - The `#pairBox` notice offers a one-tap «לעגל לזוגות» (`:550-553`, `:1187-1194`).
- **Cards** show the line «נמכר בזוגות» (`.pair`). Cart lines also get a «+6 · ארגז» carton chip (`:1110`).

### How the planner controls what customers can order (tranche 182 and follow-ups)
- **The staff screen** is `/planning/portal-catalog` in the separate repo `/home/user/gt-factory-os-portal` (`docs/portal-os/tranches/182-portal-catalog-availability.md`; also 183 "coming soon" and 184 restock text). It proxies the four staff routes above.
- **The data** is the append-only `customer_portal.item_availability` table (`0357:23-49`). A trigger refuses any UPDATE or DELETE. The current state per SKU is the view `item_availability_current`, the latest row per SKU (`0357:51-54`, `0358`).
  - Columns: `available`, `headline` (≤20 characters, replaces «אזל מהמלאי»), `upcoming` (0358; the "coming soon" look), `back_on` date, `return_note` (≤25), `alternative_sku`, internal `note` (≤200), `changed_by`.
  - Marking a SKU available again clears every outage field (`routes.ts:462-471`).
- **Overlay on prices.** `withAvailability` is applied fresh on every bootstrap and order (`pricing.ts:166-182`). It never touches the 5-minute price cache. For an unavailable SKU it:
  - drops the offer;
  - shows `back_on` only while the date has not passed in Asia/Jerusalem;
  - shows the alternative only while that alternative is itself on offer.
- **What the customer sees.** The card stays in its place, greyed, with the state word, the return line («צפי d.M») and «עדכנו אותי כשחוזר». The restock request goes to `customer_portal.restock_request` (`0357:56-65`).
- **Permanent retirement** of a product is a code change to `CATALOG` and to `P`.

---

## 4. Pricing (`P/pricing.ts`)

**Sources:** Shopify Admin GraphQL only. There are no portal price tables; `sales_core.customer_price` and its siblings hold 0 rows and are unused (spec `:71-76`).
- **List price** is `productVariant.price` from the `VARIANTS` query: about 380 variants, fetched in two pages of 250 and cached for 10 minutes (`:19-26`, `:52`, `:227-233`).
- **Customer price** comes from the customer's last 40 non-cancelled orders, fetched 5 orders × 50 lines per page, newest first (`:31-49`, `:51`, `:236-251`).
  - The unit price is `discountedUnitPriceAfterAllDiscountsSet` (paid, after discounts).
  - Lines priced 0 or below (gifts) are ignored (`:85`).
  - The history snapshot is cached per customer for 5 minutes (`:53`). Concurrent callers share one fetch. `forget()` runs after an order (`:255-299`).
- **Rule** (spec §4.1 `:312-343`; `lastPaidBySku`, `:80-96`):
  - A family SKU (`TEA_1L`, `TEA_05`, `ODK_1L`) takes the price of the newest order's first family line, for **every** flavour in the family.
  - Any other SKU takes its own exact last paid price.
  - If neither applies, the engine's list price is used (`buildCart` with `pricing_mode:'full'`; `engine/` is used, never edited).
  - History SKUs outside the catalog are offered only to that customer, at the exact last paid price, under `extra`.
- **Leads:** `listPrices()` prices every catalog SKU at list price (`:289-291`).
- **VAT:** prices are **ex-VAT**.
  - The stored Shopify number is ex-VAT, and Green Invoice bills it × 1.18. This was verified on 5 invoices (spec §W0-VAT `:26-69`).
  - `VAT_RATE = 0.18` and `MIN_ORDER_PRE_VAT = 800` come from `api/src/order-intake/engine/build-cart.ts:21-22`.
  - The engine's `MIN_ORDER_INCL_VAT = 944` is **not** used by the portal.
  - The portal never multiplies or divides by 1.18. The Shopify `priceOverride` is `unit_price.toFixed(2)` in `ILS` (`orders.ts:106`).
- **Rounding** (client `index.html:1075`, `:1101`; server `orders.ts:30-35`):
  - `sub = round2(Σ qty×price)`
  - `vat = round2(sub×0.18)`
  - `tot = round2(sub+vat)`
- **Currency format:**
  - `money(n) = '₪' + n.toLocaleString('en-US',{min/maxFractionDigits:2})`, for example `₪1,234.50`.
  - `whole(n)` drops decimals, for `₪800` (`index.html:722-723`).
  - Every amount sits in `.num` (LTR-isolated, tabular figures).
  - Labels are always «לפני מע״מ» or «כולל מע״מ». The VAT line reads «מע״מ 18%».
- **Minimum ₪800 ex-VAT:**
  - The server returns `422 BELOW_MINIMUM` (`orders.ts:182`).
  - The page disables send and shows «מינימום הזמנה: ₪800 לפני מע״מ», a right-to-left progress meter, «חסרים עוד ₪X כדי לשלוח», «בקשה מיוחדת? כתבו לנו בוואטסאפ», and up to 3 "להשלמה" (top-up) items from history (`index.html:1121-1152`).
- **Discounts and promotions:** none. Promotions are deferred (spec §4.2 item 7). Engine price flags never block.
- **Price drift:** checked line by line, with |server − shown| > 0.005 giving `409 PRICE_CHANGED` and fresh `items` and `extra` (`orders.ts:177-180`).

---

## 5. Orders (`P/orders.ts`)

**Customer path: `submitOrder`, `:123-219`.**
1. `beginSubmission` inserts `customer_portal.order_submission` (`idem_key` unique; status submitting, created or failed; lines as priced by the server; `subtotal_ex_vat`; draft, order id and name; error) (`0355:76-90`).
2. Replays:
   - Another customer's key returns `409 CONFLICT`.
   - An order already created returns 201 with the same `order_name`.
   - A known draft returns 202.
   - A `submitting` row younger than 2 minutes returns `409 IN_PROGRESS`. An older one is claimed as stale, its draft is found by tag, and it is settled; it is never re-created.
   - A `failed` row with no draft is retried under the same key.
3. Fresh prices are taken with `pricedFor(…, fresh=true)`. The checks then run in order: `BAD_LINE` (no offer; covers planner-unavailable items), `PRICE_CHANGED`, `NOT_IN_PAIRS`, `BELOW_MINIMUM`.
4. The draft input (`draftInput`, `:101-107`) is:
   - `purchasingEntity:{customerId}`, `useCustomerDefaultAddress:true`, `visibleToCustomer:false`;
   - `tags:['portal','pk-<idem_key>']`;
   - `lineItems:[{variantId, quantity, priceOverride:{amount, currencyCode:'ILS'}}]`.
5. `draftOrderCalculate` runs as the double-VAT guard. Shopify's total must be within ±0.05 of Σ and must not equal Σ×1.18 (±0.5) (`:113-121`, `engine/guard.ts:12-20`). Nothing is created unless it passes.
6. `draftOrderCreate` runs. If the create times out or fails in transport, the code looks the draft up by its exact tag (`FIND`, `:65-69`; Shopify tag search matches tokens, so the tag is re-checked exactly).
   - If nothing definite comes back, the row stays `submitting`, an alert `commit_failed` goes to staff, and the call returns 502.
7. `settle`, `:227-249`: `draftOrderComplete(id, paymentPending:true)`, then status `created`, then `pricer.forget`.
   - The page gets 201 `{order_name:'#GT…'}`.
   - If completion fails, the draft is kept, an alert `complete_failed` goes to staff, and the call returns `202 CREATED_NOT_COMPLETED`. Staff complete it by hand.
8. **Confirmation A6.** It is a WhatsApp text from the order line, sent only if the customer wrote within 23.5 h (`:28`, `:252-261`). Its text is «תודה! קיבלנו את ההזמנה. מספר הזמנה: …» with the line count and totals (`:34-35`). A failed send never changes the 201.

**What triggers downstream systems.** The portal calls neither Green Invoice nor LionWheel. Completing the draft creates a normal Shopify order with source `shopify_draft_order`, PENDING (spec §3 `:293-300`). Then:
- Green Invoice issues a type 305 tax invoice 5–11 s after the order is created (spec §W0-3 `:184-199`).
- LionWheel's own Shopify integration opens a task 4–10 s after creation (§W0-2 `:173-182`).
- route-print-pack and planning demand read LionWheel as they do today (§W0-5a).
- The API app has `write_draft_orders` but **not** `write_orders`, so draft then complete is the only path (§W0-1 `:158-171`).

**Draft-only lead orders (PR #321, commit `a68ba16`; `P/lead.ts:137-225`).**
- The flow mirrors the customer path: same idempotency, stale lookup, guard and checks, at list prices.
- The draft has **no customer**. It carries:
  - `tags:['lead','pk-<idem>']`;
  - note `הזמנה מקישור ליד (קו הלידים) · business · city · contact · +phone`;
  - `customAttributes` `lead_id`, `business_name`, `city`, `contact_name`, `wa_phone` (`:120-135`).
- It is **never completed**, on any path. A completed order would be invoiced and dispatched.
- Afterwards (`drafted`, `:218-225`):
  - status `drafted`, and every link of the lead closes;
  - the `lead_event` `draft_order` row is written;
  - the confirmation goes out on the lead line `972547588132`: free-form `TEXT.confirm` inside 23.5 h, else the template `gt_lead_order_confirmation` with params `[lines, total]` (`:230-247`);
  - the owner gets a Telegram «טיוטת הזמנה חדשה מליד: …».
- Staff then create the customer (skill `customer-setup-shopify-gi`) and complete the draft by hand.
- `lead.test.ts:124-128` fails if `lead.ts` contains `draftOrderComplete`, `COMPLETE`, `settle` or `submitOrder`.

---

## 6. Store and state

**Server.** The server keeps no cart. `customer_portal.order_submission` and `lead_submission` are submission logs keyed by `idem_key`. "Shopify owns the order" (`0355:75`). `P/store.ts` is raw SQL over `pg`, behind the `PortalStore` interface (`:86-134`), with an in-memory fake for tests.

**Client** (`localStorage`, `index.html:736-740`, `:1293-1313`):
- `gtp_cart_v1 = {v:1, a:acct, o:order[], c:{key:qty}, k:idem, p:pendingSince, t}`.
  - `acct` is `display_name·branch`, or `lead·<token>` in lead mode (`:1489`).
  - Writes are debounced by 250 ms.
  - On load the cart is restored only if the account matches and it is under **14 days** old.
  - Lines without a price are dropped with a message; planner-unavailable lines get «הוסר: {p}, אזל מהמלאי».
  - A restored cart shows the sticky note «העגלה מהביקור הקודם חזרה. המחירים עודכנו להיום.» with «ניקוי העגלה».
  - A cart saved while *pending* resumes the pending state with the **same idem key** and replays it.
- `gtp_last_v1 = {a, n:orderNo, t, c:lines, v:totalIncVat}` drives two things for 24 h: the strip «נשלחה היום ב־{t} · הזמנה {n} · {v} כולל מע״מ» and the duplicate-order confirmation (`:1328-1331`, `:1452-1458`).
- `gtp_again_v1 = {w, h}` remembers the reorder slot's height so the first paint does not shift (G-31, `:12`, `:1218`).
- **Logout** clears `gtp_cart_v1` and `gtp_last_v1` (`:1559`). A 401 saves the cart, then redirects to `/portal/login?e=session` (`:1529`).
- A tab left hidden for more than 30 minutes re-prices when it is shown again (`:1568-1572`).

---

## 7. Frontend (`P/public/index.html`)

**Stack and boot:**
- Vanilla ES5 in one IIFE (`:589-1581`), no modules.
- Rendering is HTML strings through `innerHTML` with `esc()` for data, plus delegated listeners on `#grid`, `#lines` and `#orders`.
- **State:** `P`; `byKey[key]={p,v}`; `cart{key:qty}`; `order[]` in insertion order; `HIST` (3 recent orders); `extras`; `state{cat,q}`; `changed{key:oldPrice}`.
- **Send state machine** `S = 'idle'|'sending'|'pending'|'done'`, with `idem`, `pendingSince`, `sent` and `checks` (`:711-715`, `:1316`).
- **Boot:**
  1. An inline `<head>` script starts `fetch('/portal/api/bootstrap')` before any CSS (`:12`). The server has already begun pricing when it served the page.
  2. The catalogue renders first, from the static `P`, with price placeholders.
  3. "One reveal" (`:1574-1580`; cards-loading gate `:52-56`): a bootstrap that lands within 700 ms paints at once. A slower one gets a skeleton after 700 ms. Past 2.5 s the catalogue paints without prices.
  4. Fonts gate the reveal, up to 2.5 s (`fontsP`, `:596-597`). Chips and the placeholder stay hidden until `html.fonts` is set.
- **Performance budget held:** LCP ≤ 1300 ms, CLS ≤ 0.01, ≤ 350 KB. Measured: median LCP 1156 ms, CLS 0, 151 KB (cards-loading gate `:145`).

**Layout:**
- The sticky header `.top` sits at `top: calc(var(--top) - var(--brand))`. The brand row (logo, account name and branch, «יציאה») scrolls away and the tools row (search plus chips) pins (`:76-87`).
- `.layout` is at most 1320 px wide. Main runs as a container (`container: main/inline-size`).
- **Grid:** 2 columns (gap 14 px), or 4 columns (gap 18 px) from a 640 px container. It is "two columns or four, never three", so a tea's 1 L and 500 ml cards always share a row (`:166-168`; cards-loading gate `:58`).
- Section headers `.sec` are 800 26 px, with a count.

**Product card anatomy** (`card()`, `:812-827`; CSS `:171-235`). From top to bottom:
1. `.ph` picture area, aspect `1/.92`, background the flavour tint `--bg`:
   - `.circle`, a flavour disc 72% wide at 44% from the top, coloured `--c`;
   - `.duo`, the bottle or bag at 82% height (500 ml at 74%), with a soft radial "floor" shadow under it;
   - `.got`, an in-cart badge at inline-start: an ink pill with ✓ and the quantity;
   - `.tag` «ללא סוכר» at inline-end, a white pill;
   - `.un-tag`, the state sticker.
2. An SVG `.wave`, 22 px.
3. `.body`, in this order:
   - `.origin`, 12 px 700, for example «תמצית ישראלית», shown first via `order:-1`;
   - `.name` in GT Latin, 30 px, auto-fitted with `min(30px, (100cqi-28px)/(len×.4))`, followed by `.vsz` for the size (800 16 px);
   - `.flag`, a flavour-dot line for sugar-free;
   - `.ingr`, ingredients at 13 px;
   - `.pair`;
   - `.var`, a **fixed 76 px** area holding `.price` (16 px 700; a 52×14 pill placeholder while loading) and `.ctl`.
- **In the cart:** `.card.in` gets a 2.5 px ink ring, the disc scales ×4 to fill the card, and the bottle hops (translateY −10 px, rotate −3°).
- **Hover (fine pointers only):** the card lifts 3 px, the disc scales 1.25, and the bottle tilts −2.5° at scale 1.05.
- **Sold out:** greyscale at opacity .5 and a quiet white stamp.
- **Coming soon (`.soon`):** full colour, a halo, an ink sticker rotated −4° with ✦, a sheen passing every 6 s, and a solid "tell me" button.

**Quantity stepper:**
- «הוספה» (an outline pill, 44 px) turns into a stepper laid out `44px | qty | 44px`, with a `grow` clip-path animation of .32 s.
- **First add:** a thumbnail flies to the bag (phone) or the cart count (desktop) over 450 ms, then `bump`. On Android, `navigator.vibrate(8)`.
- A second tap within 450 ms counts as `+`; the qty input is read-only briefly (`:975-977`).
- At the last step the minus becomes a trash icon.
- **Keyboard:** digits 1–9 on «הוספה» set the quantity, Enter commits, `/` focuses search. The maximum is 999 (998 in pairs).
- **Cart lines** use the same stepper (48 px qty), plus «+6 · ארגז» for bottles. A removed line offers «ביטול» (undo) for 6 s.

**Cart surfaces** (UX gate §8; `:367-406`):
- **Below 560 px:** a bottom sheet at `88dvh` with radius 26/26/0/0, a 44×5 swipe handle (dismiss past 90 px or above .5 px/ms), a scrim, `role=dialog` plus `aria-modal`, `inert` on the background, and `pushState` so the back gesture closes it.
- **560–1099 px:** a drawer from the inline-end edge, `min(440px, 100%−48px)`, with the pill bar on the same edge.
- **1100 px and up:** a sticky side cart, 340 px wide (360 px from 1280 px).
- **The bar (phone and tablet)** is fixed, ink, radius 22 px, min-height 64 px. It holds the bag and count, the ex-VAT subtotal, a 4 px minimum track, and «לעגלה».

**Reorder («להזמין שוב», `:1201-1245`):**
- A snap scroller of the last 3 orders, switching to a grid from a 700 px container.
- The first card expands in place with editable steppers; it is open by default from 560 px.
- Tapping merges into the cart **by max**, with undo.
- Badges read «נשלחה היום» or «האחרונה».
- Unsellable lines appear in terracotta with a WhatsApp link.
- A first-time customer sees the card «ההזמנה הראשונה שלכם».

**Summary:** a `<dl>` with «סה״כ לפני מע״מ», «מע״מ 18%» and «סה״כ כולל מע״מ». The total is 26 px and counts up over 250 ms.

**Confirmation («done», `:1408-1437`):**
- It appears inside the cart panel; on a phone the sheet opens.
- An 84 px green check pops and its stroke draws itself. The title is «קיבלנו את ההזמנה» (32 px), followed by «מספר הזמנה N · היום, HH:MM», the counts, «פירוט ההזמנה» in a `<details>`, and «ההזמנה אצלנו ותצא לפי סבב החלוקה הרגיל שלכם.».
- Actions are «שיתוף» (Web Share, with a `wa.me` fallback) and «סיום».
- A 202 adds «הצוות שלנו משלים אותה…». A lead order shows «נחזור אליכם בקרוב לתיאום המשלוח.».

**Send outcomes** (`settle`, `:1348-1375`):

| Response | What the page does |
|---|---|
| 201 or 202 | Done screen |
| 401 | Login redirect (cart saved) |
| 503 | Closed screen; the cart is offered as text to send on WhatsApp |
| `PRICE_CHANGED` / `BAD_LINE` | Re-price: the old price shown struck through, with the badge «המחיר עודכן» |
| `NOT_IN_PAIRS` | Focus moves to «לעגל לזוגות» |
| Other 4xx | «ההזמנה לא נשלחה…» |
| Network failure, 5xx or `IN_PROGRESS` | **Pending**: the cart locks and keeps its key; automatic replays at 5, 15, 45, 120 and 150 s (`:1364`); «לשלוח שוב בלי שינוי» or «לשנות בכל זאת» (which drops the key); after 3 misses, a WhatsApp link carrying the request id |

**Other states:**
- **Loading:** a skeleton and `aria-busy`.
- **Load error:** `#loadErr` «לא הצלחנו לטעון…» with «לנסות שוב».
- **Offline:** send is refused with «אין חיבור לאינטרנט. העגלה שמורה…». The `online` event retries.
- **Slow send:** after 8 s, «החיבור איטי…».
- **Duplicate:** «כבר שלחתם היום הזמנה זהה…».
- **Empty search:** a message, «חיפוש בכל הקטגוריות», and a WhatsApp link.
- **Empty cart:** its own copy.
- **Lead link gone:** `gone()`.

**Motion:**
- Search and filter changes use a FLIP reflow: 440 ms `cubic-bezier(.22,1,.36,1)`, with newcomers fading in from scale .94 over 340 ms. It is skipped when more than 12 cards move (`:860-895`).
- Keyframes: `lin`, `grow`, `pop`, `hop`, `shine`, `ring` (the desktop cart flashes on reorder), `barin`, `draw`, `spin`, `skin`/`skp`.

**Language and direction:**
- Hebrew only: `<html lang="he" dir="rtl">` on all four pages, and the manifest declares `dir:"rtl"`, `lang:"he"`.
- English product names are wrapped in `<span lang="en" translate="no">`.
- Layout uses logical properties throughout.
- Dates use `he-IL` `{day:'numeric', month:'long'}`; times use `he-IL` 2-digit hour and minute.

**Accessibility:**
- **Navigation:** skip links «דילוג לקטלוג» and «דילוג לעגלה»; an `h1.sr` heading; `role=search`; chips are `aria-pressed` buttons inside `role=group`.
- **Labels:** add buttons carry screen-reader text with name, size and price. Steppers have `aria-label`s such as «הוספת זוג: …» and «הסרה מהעגלה: …». The qty input uses `inputmode=numeric` and `enterkeyhint=done`.
- **Announcements:** one live region (`#live`, polite) plus `#cartNote` (`role=status`) and `#cartAlert` (`role=alert`, which takes focus). Toasts are `aria-hidden` and never shown while the cart is visible.
- **Meter:** `role=progressbar` with `aria-valuenow`, `aria-valuemax` and `aria-valuetext`.
- **Focus:** an obscured-focus fix scrolls focused controls out from under the sticky header and the bar (`:913-922`). Focus is restored when the sheet closes. Escape closes the sheet.
- **Touch targets:** at least 44 px (`--h-control`). The `.nfy` (32 px drawn) and `.un-alt` (24 px) controls extend their hit areas with `::after`.
- Hover styles apply only under `(hover:hover) and (pointer:fine)`. `forced-colors` rules exist.
- Measured contrast (spec `:571-580`): ink 14.6:1, muted 5.8:1, green 5.6:1.
- Harness: `api/scripts/portal_ux_shots.mts` runs axe on every state, a 44×44 tap-target check and focus checks.

---

## 8. Visual tokens
The same `:root` block appears in `P/public/css/panel.css:3-24` and `index.html:29-50`. A test enforces that the two are identical (`tokens.test.ts`).

**Colours:**

| Role | Tokens |
|---|---|
| Ink and text | `--ink #20241F`, `--ink-soft #4B5148`, `--muted #5E6359`, `--placeholder #6B7065`, `--ink-hover #343A32` |
| Paper and surfaces | `--paper #FBF8F2` (page, `theme-color`), `--paper-2 #FCFAF6` (cart foot), `--card #F3EFE6`, `--white #FFFFFF` |
| Brand | `--gt #3E6E34` (progress, success, focus ring), `--gt-d #2B4F24` (links, success text), `--terra #9A5433` (small warm text and badges; the site's `#C4744B` darkened to 5.3:1) |
| Lines | `--line #E7E1D3`, `--line-soft #EFEADF`, `--line-strong #948B78` (input borders) |
| Controls | `--track #D3CAB6`, `--disabled #D8D1C1`, `--handle #DCD5C6` |
| On ink | `--on-ink-muted #C9CCC3`, `--on-ink-accent #9CC58B` |
| States | `--ok-bg #E7EFE2`, `--alert-bg #F8ECE4`, `--alert-ink #8A2E16` |
| Overlays | `--scrim rgba(32,36,31,.42)`, `--select rgba(62,110,52,.22)`; focus ring halo `0 0 0 4px rgba(62,110,52,.14)` |

**Flavour tints (`bg`) and accents (`c`)**, from `index.html:653-682`:

| Product | `bg` | `c` |
|---|---|---|
| detox | #F6D9CF | #D8492B |
| detoxsf | #DDEBD6 | #4E8C4A |
| revive | #D5EDEA | #0FA3A3 |
| energy | #E2DEF2 | #4B3B8F |
| consc | #F6D9E6 | #C2185B |
| american | #F6DCD3 | #C62828 |
| fresh | #F3D9DD | #A31F34 |
| freshsf | #F7E3E0 | #E63950 |
| desertea | #F3E7C9 | #D9A413 |
| calm | #E6E1F2 | #8E7CC3 |
| namastea | #F0E2CC | #C98A2D |
| matcha, kit | #DDEBD6 | #5F8F4E |
| hojicha | #EFE3CC | #A9752E |
| ube | #E8DFF2 | #7C5CBF |
| mango | #FBE8CC | #EE9B2F |
| strawberry | #F8DADD | #D6364B |
| peach | #FBE3D6 | #EE8A5E |
| accessories, extras | #E4E9DC | — |

**Typography:**
- `--f: 'Heebo','Arial Hebrew',sans-serif` and `--f-display: 'GT Latin','Heebo','Arial Hebrew',sans-serif`.
- Heebo is self-hosted and variable (100–900), in 3 `unicode-range` subsets: Hebrew including ₪, digits and punctuation, and Latin letters (`fonts/heebo.css`; `index.html:22-24`).
- "GT Latin" is Bebas Neue (OFL). It covers A–Z and a–z only and is used for **product names only** (`:25`; UX gate decision 12).
- Body text is 16 px/1.5. The scale tokens are `--t-xs 12`, `--t-s 13`, `--t-m 14`, `--t-body 16`, `--t-l 20`, `--t-xl 26`, `--t-2xl 32`, `--t-name 30`, `--t-word 44`.
- Literal sizes also in use: 11, 15, 17, 18, 19, 21, 24, and 28/34 (the panel `h1`).
- Weights in use: 400, 600, 700, 800. Headings take `letter-spacing:-.01em`; GT Latin names take `.01em`.
- Headings use `text-wrap: balance`; `p` and `li` use `pretty`. `.num` sets `tabular-nums; direction:ltr; unicode-bidi:isolate`.

**Shape, elevation and motion:**
- Radii: `--r-s 12`, `--r-m 16`, `--r-l 24` (cards, panels), `--r-pill 999`. The sheet uses 26, the bar 22 and the bag 14.
- Shadows:
  - `--sh-1 0 6px 24px rgba(32,36,31,.07)`
  - `--sh-2 0 24px 48px -24px rgba(32,36,31,.28)` (hover)
  - `--sh-3 0 18px 40px -16px rgba(32,36,31,.55)` (bar, toast)
  - Cards `0 6px 30px rgba(32,36,31,.08)`; cart and panel `0 18px 50px -30px rgba(32,36,31,.35)`
  - `--sh-floor`, a radial floor under bottles, instead of a drop-shadow filter that iOS clips.
- Motion: easings `--ease cubic-bezier(.22,.61,.36,1)`, `--out cubic-bezier(.22,1,.36,1)`, `--spring cubic-bezier(.34,1.4,.5,1)`; durations `--d-press .15s`, `--d-ui .25s`, `--d-move .45s`. Pressed controls scale to .96–.98.
- Layout tokens: `--h-control 44px`, `--brand 60px`, `--pin 68px` (70 from 1100 px), `--max 1320px`, `--cartw 340px`.

**Buttons, chips and notes:**
- **Primary `.send`:** 54 px pill, ink background, paper text, 800 17 px. Hover `#343A32`. Disabled (`aria-disabled`) is `#D8D1C1` with ink-soft text. While busy it shows an 18 px spinner.
- **Secondary:** `.ghost` (panel) or `.add` is a pill with a 1.5 px ink outline on white. `.add` fills with ink on hover. The `.obtn` reorder button is a 46 px pill.
- **Text actions:** `.wa`, 44 px, `--gt-d`, 800 14 px, underlined with a 3 px offset.
- **Chip:** 44 px pill, 1.5 px `--line` border, white, 800 14 px, with a 12 px muted count. Pressed is ink with paper text. Overflowing edges fade with a 48 px mask.
- **Search:** 44 px pill with a 1.5 px `--line-strong` border. Focus switches to an ink border plus the green halo.
- **Badges:** `.badge` is a terracotta pill, 11 px 800. `.o-new` is an ink pill. `.biz` is a `--card` pill, 13 px 800, reading «ללקוחות עסקיים בלבד».
- **Notes:** `.msg` and `.note` use a `--card` background with radius 12–16, 700 14–15 px. Error notes use `--alert-bg`/`--alert-ink`, success notes `--ok-bg`/`--gt-d`. `.pend` is a warning group with 40 px pill buttons.

**Breakpoints:**

| Breakpoint | Effect |
|---|---|
| 360 px | Short send label |
| 440 px container | Cart line on one row |
| 150 px card container | Hides the alternative link |
| 560 px / 1100 px | Phone, tablet and desktop cart tiers |
| 640 px container | 4-column grid |
| 700 px container | Reorder cards switch to a grid |
| 700 px (entry pages) | Brand band of bottles on discs (`panel.css:58-70`) |
| 900 px | Search and chips on one row |
| 1280 px | Wider cart, chip counts shown again |
| `max-height` 700 / 520 px | Compaction for short screens |

**z-index:** top 30, bar 40, scrim 55, cart 60, toast 80, fly 90, skip link 100.

**Light only, no dark mode:** `color-scheme: only light` plus the meta tag; UX gate decision 8 says "hardened, not themed".

**Safe areas:** `--top` and `--bot` read `env(safe-area-inset-*)` with `viewport-fit=cover`. The bar sits at `bottom: calc(12px + var(--bot))`. When the keyboard opens (`visualViewport`, more than 150 px), the bar is hidden.

**Reduced motion:** all durations become .01 ms, the sheen is off, the check is drawn statically, and the spinner slows to 1.4 s. In JS, the `reduce` flag skips the fly, FLIP, count-up, hop, vibration and smooth scrolling (`index.html:448-453`, `:716-717`; `panel.css:72`).

**PWA:** `manifest.webmanifest` has `name` «הזמנות GT», `short_name` «GT», `start_url` and `scope` `/portal/`, `display: standalone`, and `#FBF8F2` for background and theme. The favicon is an SVG: a green `#3E6E34` disc carrying «GT» on paper.

---

## 9. Tests (`P/__tests__/`, vitest, in-memory `fakes.ts`)
- **`tokens.test.ts`:** `index.html` and `panel.css` declare the same `:root` tokens, more than 40 of them.
- **`routes.test.ts`:**
  - Logged out: every data route returns 401, `/portal/` returns 302 to login, the login page has no `₪` amount, and the security headers are present.
  - The host redirect works and health is public.
  - A link GET spends nothing; consuming a link sets the exact cookie string.
  - Used, expired and wrong-purpose links return 410. Revoking access kills sessions and links.
  - The bootstrap shape is checked.
  - Prices are prefetched once by the link login or the page. A closed portal fetches no prices.
  - The flag off returns `PORTAL_CLOSED`. Logout revokes the session.
  - A registration link is single-use, and staff are notified.
  - Foreign `Origin` returns 403 and non-JSON returns 415. Assets are whitelisted, with ETag/304 and `?v=` immutable.
  - Staff roles (planner and admin only). Approval writes the access row with no write to the bot map. Local phone search. 24 h login link. Customer search `phone_matches`.
  - Catalogue routes: role gates, one row per change, validation (20/25/200 character limits, real dates, a valid alternative).
  - Marking available clears the outage. D3: a flip reaches the next bootstrap despite the cache. The restock loop.
- **`orders.test.ts`:**
  - `pricer.forget` runs after an order.
  - Calculate → create → complete, tagged `portal`, at stored prices.
  - Same-key retry and double submit each produce one order. Stale `submitting` rows settle by tag or fail. `IN_PROGRESS` under 2 minutes. Another customer's key returns 409.
  - `BAD_LINE`, including planner-unavailable items. Per-line `PRICE_CHANGED`. `BELOW_MINIMUM`. `NOT_IN_PAIRS`, with matcha exempt.
  - The double-VAT guard never creates. A timed-out create is found by tag and never sent twice. A failed lookup is never read as "no draft".
  - A completion failure returns 202, raises an alert and keeps the draft.
  - WhatsApp confirmation only inside 24 h; a failed send still returns 201.
- **`pricing.test.ts`:**
  - The family rule covers flavours never bought, the newest line wins, the first line wins inside the newest order, and ODK counts as a family.
  - No history means list prices. Other SKUs use their exact last price. Gifts and cancelled orders are ignored. No sibling inference.
  - Excluded SKUs never show. Extras are offered at the last paid price. Archived items appear greyed in recent orders. Keys are safe in selectors.
  - Caches: 5 minutes, shared fetches, `forget()` generations.
  - Availability: returns a new object, a past `back_on` is hidden, an alternative shows only while on offer, `waiting` is scoped to the customer, unavailable lines stay in reorder.
- **`gate.test.ts`:**
  - Flag off falls through. A1 normalisation. 10-minute link sent to the phone. Not allowlisted falls through. Multi-match goes to registration. Unknown falls through unless `*`. Revoked gets nothing. Pending gets A4. The 5-per-hour cap counts every creator and the A4 replies. Allowlist parsing.
  - Invite: 24 h links, the register link, pending A4, `no_link` reasons, the mark recognised through emoji and a signature, and the shared cap.
- **`lead.test.ts`:**
  - Draft only: tags `['lead','pk-…']`, no `purchasingEntity`, never completed on the first try, a replay, the stale path or a timeout.
  - A closed link answers only a replay of its own order.
  - Minimum, price change and pairs apply.
  - The source contains no completion code.
  - Confirmation: free-form vs template, and the forced-template switch.
- **`lead_routes.test.ts`:**
  - The lead page boots from the lead bootstrap.
  - Bootstrap returns 410 for an unknown, used or expired link, and 503 when the portal is closed.
  - Orders return 422 or 410 before anything reaches Shopify.
  - The lead-wake job route auth.
- **Gates outside unit tests:**
  - `api/scripts/portal_copy_check.mjs` fails on any customer-visible Hebrew string not in the approved register (UX gate §5).
  - `api/scripts/portal_ux_shots.mts` is the Playwright harness: shots, axe, CLS, tap targets.
  - `api/scripts/portal_verify.ts` runs live price and guard checks against production Shopify, printing counts only.

---

## 10. Decisions already locked that a sibling product must respect

- **VAT and the minimum (spec §W0-VAT `:54-69`; §4.2):**
  - The Shopify number is ex-VAT, and Green Invoice bills it × 1.18.
  - Show it labelled ex-VAT, then the VAT line, then the total including VAT.
  - Never multiply or divide by 1.18.
  - The minimum is ₪800 on those numbers. Below it, send is disabled and a WhatsApp button is offered, with no draft.
- **Pricing (§4.1 `:312-343`):**
  - Three families (TEA_1L, TEA_05, ODK_1L), each with one price per customer taken from the newest family line.
  - Every other SKU uses its own last paid price, else the list price.
  - 0.3 L is out, and the excluded SKUs never show.
  - History items outside the catalog are visible to that customer only.
  - Engine flags never block. Prices are "simply shown".
- **v1 package (§4.2–4.3 `:345-418`):**
  - Every accepted order is a real Shopify order (draft then complete, tagged `portal`). There is no draft or exception path for customers.
  - Billing is unchanged: Green Invoice issues the 305 on creation, then LionWheel, then route-print-pack.
  - No credit check.
  - One-tap WhatsApp login, with the link sent to the phone.
  - Registration requires staff approval.
  - It is hosted in the existing API.
  - Personal signed links and promotions come later.
- **Tom's quality bar (§4.4 `:420-426`):** «לא מתפשרים על הuiux» ("no compromise on the UI/UX"), with the brand DNA.
- **Module boundaries (§4.5, D1 §1.2-1/2/5/8/9 `:442-452`):**
  - Writes stay inside the `customer_portal` schema. The only exceptions are its flag row, Shopify drafts tagged `portal`, WhatsApp replies to a customer's own login message, and one confirmation inside 24 h.
  - Never write `order_intake.wa_customer_map`.
  - `engine/` is used only through a wrapper.
  - Launch is gated by `customer_portal_live` and its allowlist.
  - Customer-facing Hebrew must be approved copy.
- **Systems facts (§W0-1, W0-2, W0-3, W0-6b):**
  - There is no `orderCreate` scope.
  - A completed order is invoiced within seconds and dispatched to LionWheel. This is why lead orders stay drafts (also lead-journey spec §3.7, `docs/superpowers/specs/2026-09-28-lead-journey-design.md:239-263`).
  - Inbound WhatsApp is not HMAC-verified, so never authenticate from an inbound message alone.
- **UX gate §4, decisions 1–15 (`:172-190`):**
  - The cart is client-side `localStorage`, per account, for 14 days.
  - After an unknown send outcome the cart locks and the same key is reused.
  - Logout clears the cart.
  - Reorder merges by max, with undo.
  - No toasts while the cart is visible.
  - Loading is catalogue-first.
  - Light scheme only.
  - The cart stays an `<aside>` with `inert`, not a native `<dialog>`.
  - The phone keeps the card system.
  - GT Latin is for product names only.
  - Tiers are 560 and 1100 px.
  - WhatsApp links that carry order text go to `ORDER_LINE`.
  - Every amount states its VAT basis.
- **Other gate rules:**
  - Grid "2 or 4, never 3" and a first paint that is layout-final (CLS 0), from the cards-loading gate.
  - Token parity between `index.html` and `panel.css` (G-56).
  - The copy gate.
- **Availability (`docs/superpowers/plans/2026-09-26-customer-portal-availability-masterprompt.md:108-159`):**
  - Planner or admin only. Manual only: stock on hand is a hint and never flips anything.
  - Cards stay in place.
  - One append-only table. No Shopify change.
  - No dates taken from the production plan.
  - A person sends every customer message.
  - The planner chooses the alternative.
  - Words: «אזל מהמלאי» or «בקרוב», «צפי d.M», `return_note` ≤ 25 characters.
- **Pairs (Tom 2026-09-28; `docs/superpowers/plans/2026-09-28-customer-portal-pairs-gate.md`):** bottles (both tea sizes and ODK) sell in pairs, and the server enforces it.
- **Repo lanes (`gt-factory-os/CLAUDE.md`):** this repo must not edit the staff portal's source (`gt-factory-os-portal/`). Staff screens ship through that repo's own tranche process.

---

## Integration seams for the Menu Builder (observations, not decisions)

- **Identity reuse needs the `/portal` path.** Serve the new page under `/portal/…` inside the same Fastify scope. It then gets the security headers, the Origin/JSON POST guard, `gtp_sid`, and can call `customerOr401` and `pricedFor`.
- **Price data already exists.** `GET /portal/api/bootstrap` gives the customer's own price per catalog key, plus availability (`unavailable`, `upcoming`, `alternative`). Lead mode gives list prices.
- **Two handoff options:**
  - **Server:** POST `/portal/api/orders` with `lines:[{key, qty, price}]`. The prices must equal what the bootstrap showed, bottles must be in pairs, the subtotal must be at least ₪800 ex-VAT, and a fresh `idem_key` is needed per cart.
  - **Client:** write `gtp_cart_v1` (`{v:1, a:'<display_name>·<branch>', o, c, k:null, p:null, t:Date.now()}`). The portal restores it on the next load with «העגלה מהביקור הקודם חזרה…».
- **Catalog keys** are the shared vocabulary: `<page id>:<variant>`, for example `detox:1l`, `matcha:500`, `mango:1l`. They are fixed in `P/catalog.ts` and mirrored in the page's `P`.
- **Coupling to watch:** lead mode depends on the exact boot line at `index.html:12` (`routes.ts:154-157`).
