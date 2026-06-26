# Master-Prompt for Cloud Claude Code — build the WhatsApp order-intake bot end-to-end

**For:** Tom · **Date:** 2026-06-26 · **Use:** paste into Claude Code (cloud) pointed at the
`gt-factory-os` repo. Self-contained: it has the architecture, the proven Shopify queries, the
component list, the safety rules, and the definition of done. The engine is already built, tested
(31/31), and pushed on branch `feat/order-intake-engine`.

---

```
ROLE & MISSION
You are Claude Code building the GT Everyday WhatsApp B2B order-intake bot to production, end-to-end, in the gt-factory-os repo. A customer texts an order in natural Hebrew to GT's WhatsApp number; the bot identifies the customer, builds a priced cart, the customer approves, and a Shopify order/draft is created — automatically when confident, as a draft for a human when not. Finish ALL remaining components, with tests, to a deployable state. ONE brain only — the tested factory-os engine. Do NOT build a second/parallel system (no Make, no reimplemented parsing).

START HERE — WHAT ALREADY EXISTS (do not rewrite it; build on it)
- Branch: `feat/order-intake-engine` (checked out / base your work on it).
- The ENGINE is done and proven — `api/src/order-intake/engine/`:
  - `types.ts` (Zod: RawLine, ResolvedLine, PricedLine, Flag, Cart, GuardResult, ResolveStatus)
  - `bottles.ts` (bottlesOf)
  - `ports.ts` — the seam to Shopify: `ShopifyCatalogPort { variantsByQuery(q): Promise<VariantRecord[]>; lastPaid(customerId, variantId): Promise<LastPaid|null> }`
  - `resolve.ts` (barcode→sku resolution, ACTIVE-only, AMBIGUOUS/UNMATCHED/NO_ACTIVE, HALT on discontinued GT-MAR-*/GT-KOG-*/*-XP- matcha)
  - `pricing.ts` (last-paid → catalog fallback → manual override; flags PRICE_GAP/NO_HISTORY_CATALOG/NO_PRICE/ZERO_PRICE)
  - `guard.ts` (expectedTotal = Σ(unit×bottles); evaluateGuard detects double-VAT)
  - `build-cart.ts` — `buildCart(spec: OrderSpec, port): Promise<Cart>` ; `OrderSpec = {customer_id, pack_default?, lines: RawLine[]}` ; Cart.ready = zero flags AND every line OK+priced
  - `__tests__/` + `__fixtures__/2026-06-23/` — 31 vitest tests incl. a golden replay of 9 real orders. Run: `npx vitest run api/src/order-intake/engine` → MUST stay green.
- Config in repo: `api/src/order-intake/config/lexicon.json` (Hebrew phrasing → variant + conventions) and `customers.seed.json` (customer name → Shopify id/branch, for seeding).
- Tech: TypeScript ESM/NodeNext (import siblings with `.js`), Zod, vitest. The repo also has a Supabase project (`supabase/`) and existing integration clients under `api/src/integrations/` (greeninvoice client is a good style reference; check for an existing Shopify client to reuse).

ARCHITECTURE (target)
One deployable unit: a Supabase Edge Function `wa-order-bot` that runs the pipeline, using the tested engine as the brain and Supabase Postgres (`order_intake` schema) for state. If importing the Node engine into the Deno edge runtime causes friction, you MAY instead run the worker as a Node service in the factory-os api and keep the edge function a thin verify+forward receiver — but the engine LOGIC must be the exact tested modules (reuse them; re-run the engine tests). Pick the simpler path that keeps the 31 tests green.

PIPELINE (message → order)
1) Edge receiver: handle WhatsApp Cloud API webhook (Dualhook delivers Cloud-API-format webhooks). GET verify handshake (`hub.verify_token` == WA_VERIFY_TOKEN). POST: verify signature, write raw event to `order_intake.wa_event_log` (idempotent on `wa_message_id`), ACK fast.
2) FRONT GATE:
   a. Known customer? sender phone (E.164) → `order_intake.wa_customer_map` → Shopify customer + branch + bot_enabled. Unknown/disabled → do nothing except (optional) flag for Doreen; never auto-order.
   b. COEXISTENCE — defer to humans: Dualhook/Cloud API mirrors staff replies from the WhatsApp Business app as `smb_message_echoes` events. If a human already replied to this chat (echo seen in the session window), mark the session human-handled and STAY SILENT. The bot is the fallback, never competes with a person.
   c. Order intent? classify the message (Claude) ORDER / NOT_ORDER / AMBIGUOUS. Only ORDER proceeds; NOT_ORDER → silent; AMBIGUOUS → one short clarifier.
3) PARSE (Claude): Hebrew free-text → RawLine[] using lexicon.json conventions (sizes: ליטר/גדול=1L, חצי/קטן/500מל=0.5L, matcha חצי קילו=500g; carton ארגז=6 bottles; ללא סוכר → *-FRE-*; matcha = Shizuoka only; default size 1L when unstated). Output each line with barcode and/or sku + qty_bottles or qty_cartons+pack.
4) Build cart with the engine: `buildCart({customer_id, pack_default:6, lines}, liveShopifyPort)`.
5) CART REPLY: interactive WhatsApp message, Hebrew product names (from lexicon `he`/aliases), itemized `qty × name @ price = subtotal`, total "כולל מע"מ", buttons [אישור ✅][עריכה ✏️][ביטול ❌]. Long carts → text list + button message. Store the session (`order_intake.wa_session`). Edit = free-text delta → re-parse → re-show.
6) On אישור — CONFIDENCE GATE: cart.ready (zero flags) → create a committed Shopify order. Any flag → create a Shopify DRAFT tagged `needs-review` with the flags in the note; tell the customer "מאשרים אצלנו, נחזור אליך". 
7) Loop close: Shopify webhook (draft completed / order created) → send the customer their confirmation.
8) Bot stays OFF until go-live: gate everything behind env flags WHATSAPP_ORDER_INTAKE_ENABLED (default false) and WHATSAPP_AUTO_COMMIT_ENABLED (default false → drafts-only). With auto-commit off, EVERY order becomes a draft for Tom — that's the supervised Phase-1 mode.

COMPONENTS TO BUILD (all under api/src/order-intake/ unless noted)
A) `db/migrations/<next-number>_order_intake.sql` (+ a `db/tests` pgTAP test, matching the repo's migration/test conventions). Private schema `order_intake`, NO FK to core tables:
   - wa_customer_map(id uuid pk, wa_phone text unique, shopify_customer_id text, display_name text, branch text, payment_mode text check in ('terms','pay_now') default 'terms', bot_enabled boolean default false, default_pack int default 6, notes text, created_at timestamptz default now(), updated_at timestamptz default now())
   - wa_session(id uuid pk, customer_map_id uuid references order_intake.wa_customer_map(id), state text, cart_json jsonb, collecting_until timestamptz, shopify_draft_id text, shopify_order_id text, flags_json jsonb, expires_at timestamptz, created_at, updated_at)
   - wa_event_log(id uuid pk, wa_message_id text unique, direction text, wa_phone text, session_id uuid, type text, raw_payload jsonb, processed_at timestamptz, status text, created_at default now())
B) `shopify/port.ts` — implement ShopifyCatalogPort against Shopify Admin GraphQL (see QUERIES). Reuse an existing repo Shopify client if present.
C) `shopify/commit.ts` — draftOrderCalculate (guard) + draftOrderCreate (draft) + order creation; priceOverride per line (DIRECT, tax-inclusive, NEVER ×1.18); attach customer, tags, note, poNumber; guard must read PASS (total == Σ(unit×bottles)) before create.
D) `parse/parse.ts` — `LlmPort` interface + `parse(message, customerContext, lexicon): Promise<{intent, lines: RawLine[]}>` using the Anthropic API (claude model id from env, structured/JSON output). Unit-test with a MOCK LlmPort (no network in tests).
E) `whatsapp/send.ts` — send text + interactive button messages via Dualhook's Cloud-API endpoint (POST https://{DUALHOOK_OR_GRAPH_BASE}/{WA_PHONE_NUMBER_ID}/messages, Authorization: Bearer {WA_SEND_TOKEN}). Build the cart message + confirmations.
F) `worker.ts` — the pipeline (front gate → parse → buildCart → reply → confidence gate → commit), with session + idempotency + the OFF/auto-commit flags + defer-to-humans.
G) `supabase/functions/wa-order-bot/index.ts` — the Edge Function (receiver + worker glue), Deno-compatible (zod via esm.sh if needed).
H) `.env.example` listing every secret (below). `README.md` for the module: setup, deploy, the supervised-test runbook.

SHOPIFY QUERIES (proven on 2026-06-23 — reuse these exact shapes; Admin GraphQL 2025-07, endpoint https://{SHOPIFY_STORE_DOMAIN}/admin/api/2025-07/graphql.json, header X-Shopify-Access-Token: {SHOPIFY_ADMIN_API_TOKEN})
- Resolve variant: `query($q:String!){ productVariants(first:10, query:$q){ nodes { id sku barcode displayName price inventoryQuantity product { id title status } } } }` with q = `barcode:<bc>` (also try barcode with leading zeros stripped) then `sku:<sku>`. Use only product.status == ACTIVE.
- Last-paid: `query($id:ID!){ customer(id:$id){ orders(first:40, sortKey:CREATED_AT, reverse:true){ nodes { name createdAt cancelledAt lineItems(first:100){ nodes { originalUnitPriceSet{shopMoney{amount}} variant { id } } } } } } }` → most-recent non-cancelled originalUnitPrice for that variantId.
- Customer search (seeding): `query($q:String!){ customers(first:10, query:$q){ nodes { id displayName email phone numberOfOrders state defaultAddress { company city address1 } } } }`
- Guard (no save): `mutation($input:DraftOrderInput!){ draftOrderCalculate(input:$input){ calculatedDraftOrder { taxesIncluded subtotalPriceSet{shopMoney{amount}} totalTaxSet{shopMoney{amount}} totalPriceSet{shopMoney{amount}} lineItems{ title quantity } } userErrors{ field message } } }`
- Create draft: `mutation($input:DraftOrderInput!){ draftOrderCreate(input:$input){ draftOrder { id name invoiceUrl status poNumber totalPriceSet{shopMoney{amount currencyCode}} } userErrors{ field message } } }`
- DraftOrderInput line item: `{ variantId, quantity: <bottles>, priceOverride: { amount: <unit_price.toFixed(2)>, currencyCode: 'ILS' } }`; attach `purchasingEntity: { customerId }`, `useCustomerDefaultAddress: true`, `tags`, `note`, `poNumber`, `visibleToCustomer: false`.

SECRETS (.env.example — never hardcode, never commit real values; on Supabase use `supabase secrets set`)
SHOPIFY_STORE_DOMAIN, SHOPIFY_ADMIN_API_TOKEN (scopes: write_draft_orders, read_draft_orders, read_customers, read_products), SHOPIFY_ADMIN_API_VERSION=2025-07, ANTHROPIC_API_KEY, ANTHROPIC_MODEL, WA_PHONE_NUMBER_ID, WA_SEND_TOKEN (Dualhook), WA_VERIFY_TOKEN, WA_APP_SECRET (signature verify), SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, WHATSAPP_ORDER_INTAKE_ENABLED=false, WHATSAPP_AUTO_COMMIT_ENABLED=false.

HARD RULES (do not violate)
- The bot stays OFF: keep WHATSAPP_ORDER_INTAKE_ENABLED and WHATSAPP_AUTO_COMMIT_ENABLED false. Deploy in drafts-only/supervised mode. Do NOT flip them to true — that's Tom's go-live decision.
- Do NOT touch WhatsApp/Meta/Dualhook account setup — that is the Cowork agent's lane (transport). You only consume the IDs/tokens from env. Never disconnect anything.
- Secrets: only from env / Supabase secrets. Never print, log, or commit them.
- Do NOT write to factory-os core tables (stock_ledger, balance_anchors, bom_*, items, components, ...). Everything in the `order_intake` schema.
- TDD: write tests first where practical, mock all external I/O (Shopify, Anthropic, WhatsApp) in unit tests, keep `npx vitest run` green (the 31 engine tests included). Commit frequently with clear messages. Work on `feat/order-intake-engine` (or a child branch); push your branch.
- Reuse the engine and the proven query shapes; do not reimplement parsing/pricing/guard logic that already exists.

DIVISION OF LABOR (you ↔ the Cowork agent, via Tom)
- Cowork owns transport: WhatsApp Coexistence onboarding via Dualhook, business verification, the IDs/tokens. You own the brain/code/deploy.
- The handshake: after you deploy the edge function, output the WEBHOOK URL (+ WA_VERIFY_TOKEN) — Tom gives it to Cowork to set as Dualhook's Webhook Override. You receive (via Tom, in env) the WA_PHONE_NUMBER_ID + WA_SEND_TOKEN.

DEFINITION OF DONE
- All components A–H built; `npx vitest run` fully green (incl. the 31 engine tests + new unit/integration tests with mocks).
- The edge function deploys; a recorded/sample WhatsApp webhook payload drives the full pipeline in a local/integration test and produces a correct Shopify DRAFT (against a dev store or with the Shopify client mocked).
- `.env.example` + module README complete, incl. the supervised-test runbook and the go-live (flag-flip) steps.
- Output for Tom: the webhook URL to hand Cowork, the list of secrets to set, and the exact command to deploy. State clearly that the bot is OFF (drafts-only) until Tom flips the flags.

SEQUENCE
1) Read the spec context above + the engine. Run the engine tests, confirm 31 green.
2) Build A (schema) → B (port) → C (commit) → D (parse) → E (send) → F (worker) → G (edge function) → H (env/README), each with tests, committing as you go.
3) Wire an integration test that feeds a sample webhook and asserts a correct draft.
4) Deploy the edge function (drafts-only, flags false). Output the handshake info for Tom.
Do not stop until the pipeline works end-to-end in supervised (drafts-only) mode and all tests are green. If you hit a genuine blocker that needs Tom (a secret, a dev store, a decision), state it precisely and keep building everything else.
```
