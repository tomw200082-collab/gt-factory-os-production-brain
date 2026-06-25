# GT Factory OS — Module Declaration: `order-intake`

> **STATUS: APPROVED by Tom — 2026-06-25 (in chat: "אני מאשר, תתחיל לבנות").** G1 closed. The
> `order-intake` module may now be built (engine first, per the plan; bot stays OFF until staged
> go-live). Brain lives in gt-factory-os; transport via Coexistence + Dualhook (see runbooks). Router
> §3 / agent-registry updates by `factory-os-governor` to follow.
>
> **Design spec:** `docs/superpowers/specs/2026-06-24-whatsapp-order-intake-design.md`
> **First plan:** `docs/superpowers/plans/2026-06-24-order-intake-engine.md`

---

## 1. Module name
`order-intake`

## 2. Business purpose
A WhatsApp agent that lets GT's B2B customers (cafes/bakeries) place orders by texting in natural
Hebrew, the way Doreen relays them today. The agent identifies the customer from the chat, classifies
the message as an order, builds a priced cart, lets the customer approve it, and turns it into a
Shopify order — automatically when confident, with a human checkpoint (a Shopify draft) when not.
**Primary users:** external B2B customers (order senders); Doreen (maps unrecognised numbers); Tom
(reviews flagged drafts). **Why now:** the 2026-06-23 session proved the reasoning manually — 9 real
orders entered correctly via the `shopify-draft-order-from-po` skill. Automating it removes the manual
relay bottleneck and typo risk, and the engine already exists to be ported.

## 3. Owner lane
`order-intake-integration` (primary — the module is an integration boundary over WhatsApp / Shopify /
Green Invoice / Anthropic). `module-arch` (`order-intake-architect`, read-only) governs the declaration
phase and ambiguous routing until the build lanes are active.

## 4. Source of truth
| Entity | Primary key | Storage | Tiebreaker |
|---|---|---|---|
| Committed order | Shopify order id | **Shopify** | Shopify wins (it is the order system of record) |
| WA number → customer identity | `wa_phone` (E.164) | `order_intake.wa_customer_map` | The map wins; seeded from GT's saved WhatsApp contacts × Shopify customers |
| Live cart (transient) | `wa_session.id` | `order_intake.wa_session` | Transient; never authoritative after COMMITTED |
| Invoice / payment evidence | GI document id | **Green Invoice** | GI wins for invoice/payment facts |
| Inbound/outbound message log | `wa_message_id` | `order_intake.wa_event_log` (append-only) | Audit only |

WhatsApp (Cloud API) is **transport only** — never a source of truth. Catalog + last-paid prices are
read **live from Shopify** (not copied into the module).

## 5. Data model
Private schema `order_intake` (drop-safe; no FK into factory-os core).
| Table | PK | FKs to core | Mutability | Audit |
|---|---|---|---|---|
| `wa_customer_map` | uuid | none — `shopify_customer_id` is an **external** Shopify gid string, not an FK | mutable | `updated_at` |
| `wa_session` | uuid | none — references `wa_customer_map.id` (intra-module) | mutable (state machine) | `updated_at`, terminal states retained |
| `wa_event_log` | uuid (+ `wa_message_id` UNIQUE) | none | **append-only** | the audit trail itself |

**Hard rule honoured:** all tables in the `order_intake` schema. The module's backend agent cannot
touch `stock_ledger`, `balance_anchors`, `bom_*`, `items`, `components`, etc. Cross-module reads only
via curated views. No core-table columns added.

## 6. Upstream systems
| System | Auth | Frequency | Freshness tolerance | Failure mode |
|---|---|---|---|---|
| WhatsApp Cloud API (Meta) | app secret + permanent token | webhook (inbound) | real-time | receiver retries/queues; Meta re-sends; idempotent on `wa_message_id` |
| Shopify Admin GraphQL | existing admin token | live read (variants, last-paid, customers) | seconds | on error → no auto-commit; flag → draft; retry |
| Anthropic API (Claude) | API key | per inbound message (intent + parse) | real-time | on error/low-confidence → route to draft; never auto-commit |
| Green Invoice (Morning) | existing key id + secret | on commit (invoice / pay link) | seconds | order stands; invoice retried + alerted |

## 7. Downstream consumers
| Consumer | Read pattern | Stale tolerance |
|---|---|---|
| Shopify (orders/fulfilment) | order created by the module → existing LionWheel/fulfilment flow | n/a (event) |
| Green Invoice | invoice/payment issued by the module | n/a |
| Tom (review) | Shopify admin saved filter "drafts tagged `needs-review`" | minutes |
| (future) dashboard | curated `order_intake` metrics view | hours |

No factory-os core consumer reads `order_intake` private tables directly.

## 8. Write boundaries
```yaml
may_write:
  - order_intake.wa_customer_map  by order-intake-backend-builder
  - order_intake.wa_session       by order-intake-backend-builder / order-intake-integration-builder
  - order_intake.wa_event_log     by order-intake-integration-builder (append-only)
  - Shopify draft/committed orders by order-intake-integration-builder (via existing Shopify client)
  - Green Invoice documents/pay-links by order-intake-integration-builder (via existing GI client)
  - outbound WhatsApp messages     by order-intake-integration-builder (Cloud API)
may_not_write:
  - factory-os core tables (stock_ledger, balance_anchors, items, components, bom_*, ...)
  - other modules' private schemas
  - .env*, credentials, secrets
  - PRODUCTION authority docs (only ops-docs-curator under governor approval)
```

## 9. Read boundaries
```yaml
may_read:
  - Shopify (product variants, customers, orders, draft calculate)
  - Green Invoice (documents, payment status)
  - order_intake.*  (own schema)
  - curated factory-os views ONLY if later needed (e.g. on-hand for an optional stock note)
may_not_read:
  - factory-os core private tables (use curated views only)
  - other modules' private tables
  - secrets / .env*
```

## 10. UX surfaces  [conditional]
**v1: none in the portal.** The customer surface is WhatsApp; the review surface is the existing
Shopify admin (drafts tagged `needs-review`). Therefore no new portal routes, no RUNTIME_READY portal
signal. **However** the bot's WhatsApp messages are user-visible **Hebrew** (cart, prompts,
confirmations) → these require Tom-approved **Hebrew copy register entries** before they ship (locked
decision). Register path proposed: `gt-factory-os-portal/docs/ux/order-intake-wa-copy.md` (copy only,
no portal route).

## 11. Integration surfaces  [conditional]
| Provider | Frozen flag (default `false`) | Contract doc | Idempotency | Reversal |
|---|---|---|---|---|
| WhatsApp Cloud API | `WHATSAPP_ORDER_INTAKE_ENABLED` | `docs/integrations/whatsapp_cloud_api_contract.md` (to write) | `wa_message_id` | n/a (messages) |
| WhatsApp auto-commit | `WHATSAPP_AUTO_COMMIT_ENABLED` | same | per-session order key | flagged orders stay drafts |
| Shopify (orders) | (existing boundary) | existing shopify contracts | per-session idempotency key | draft delete (self-created) / order cancel = human |
| Green Invoice (pay link) | reuse existing GI boundary | `green_invoice_*` + new pay-link addendum | GI doc id | GI credit/void = human |

Both new frozen flags stay `false` until Tom written approval + dry-run + ≥24h soak + RUNTIME_READY,
exactly like the existing frozen flags. Auto-commit is a **separate** flag from message-enable, so the
bot can run in "drafts-only" (Phase-1 trust) with auto-commit off.

## 12. Agent ownership
| Lane | Agent name | Status |
|---|---|---|
| module-arch | `order-intake-architect` | required for declaration phase (read-only) |
| backend-db | `order-intake-backend-builder` | required — `order_intake` schema + migrations |
| integration | `order-intake-integration-builder` | required — receiver, worker, WhatsApp/Shopify/GI/Anthropic |
| portal | — | not needed in v1 (no portal UI) |

Each agent needs an `AGENT_TEMPLATE.md`-based definition with allowed-paths scoped to `order-intake`
directories before it is created. None touch factory-os core schema.

## 13. Commands needed  [conditional]
**v1: none.** The module is event-driven (webhook), not slash-command driven. A future
`/order-intake-status` (operational health) may be proposed later via factory-os-governor PROCEED +
Tom approval.

## 14. Tests required
- **Unit:** the engine (resolve/price/guard) — see the engine plan; incl. discontinued guard, price
  flags, VAT/double-VAT.
- **Golden replay:** reproduce the 2026-06-23 nine orders exactly (carts, totals, flags).
- **Integration (within module):** receiver → worker over recorded Meta webhook payloads, against
  Shopify dev store + GI sandbox.
- **Contract:** Meta signature verify; Shopify VAT guard; `wa_message_id` idempotency; per-session
  order idempotency.
- **E2E golden-path:** real test WhatsApp number → clean order auto-commits; flagged order → draft →
  human complete → customer confirmation.
- **Idempotency:** Meta re-send + double-✅ produce no duplicate line / duplicate order.
- **Failure-mode:** Claude error, Shopify error, GI error, unknown number → never auto-commit, never
  duplicate, never false "confirmed".
- **Cross-module:** confirm no write to factory-os core; `order_intake` schema drops cleanly.

## 15. Gates
| Gate | Exit criteria |
|---|---|
| MG1 — Declaration | **This file approved by Tom** (closes G1 for build) |
| MG2 — Foundation | `order_intake` schema + migrations live; module agents exist; engine plan executed to green replay |
| MG3 — Truth | A WhatsApp message round-trips to a correct Shopify order in sandbox; integration tests green |
| MG4 — UX | n/a portal; **Hebrew WA copy register approved by Tom** (the v1 "UX" gate) |
| MG5 — Integration | WhatsApp/Shopify/GI dry-run clean on a test number; both new frozen flags still `false` |
| MG6 — Cross-module | Reconciliation: no factory-os core contamination; schema drop-safe verified |
| Go-live (staged) | Phase-1 drafts-only soak on one pilot cafe → Tom authorizes auto-commit (flag flip) |

## 16. Rollback / disable strategy
- **Kill switch:** `WHATSAPP_ORDER_INTAKE_ENABLED=false` stops all inbound processing + outbound sends
  instantly; `WHATSAPP_AUTO_COMMIT_ENABLED=false` forces drafts-only.
- **Per-customer:** `bot_enabled=false` disables the bot for one customer without affecting others.
- **Schema isolation:** `order_intake` schema has no FK into core → can be dropped without touching
  factory-os truth.
- **Webhook:** unsubscribe the Meta webhook to fully detach transport.
- **Comms:** Tom + Doreen notified on disable; in-flight sessions closed with a polite message.

## 17. Tom decisions required
Tracked in `docs/decisions/modules/order-intake-decisions.md`:
- **Meta:** start + complete the Cloud-API migration; create the Meta app; provide app secret +
  permanent token (G2 — long pole, Tom-only).
- **Anthropic API key** + budget for the parse/intent calls.
- **Green Invoice clearing:** confirm a clearing provider (סליקה) is connected for `pay_now` links
  (else Shopify `invoiceUrl` fallback).
- **Per-customer config:** `payment_mode` (terms/pay-now) and `bot_enabled` per customer; the pilot cafe.
- **Hebrew copy register** for every customer-facing WhatsApp string (cart, prompts, confirmations).
- **Go-live authorization** at each trust step (drafts-only → auto-commit flag flip).

## 18. Definition of done
- [ ] All gates in §15 closed with evidence.
- [ ] All Tom decisions in §17 answered.
- [ ] Hebrew WA copy register approved (the v1 "UX surface" equivalent).
- [ ] All tests in §14 green; golden replay parity proven; coverage report attached.
- [ ] Rollback (§16) dry-run-tested (flag flip + schema drop on a scratch DB).
- [ ] Module added to `AI_BRAIN_ROUTER.md` §3 lane table.
- [ ] Module agents added to `AGENT_REGISTRY.md`; `AGENT_TEMPLATE.md` files exist.
- [ ] `CURRENT_STATE.md` updated with module live status.

---

**Owner:** `factory-os-governor` (governs declarations). **Approver:** Tom.
**Drafted:** 2026-06-24 (by Claude, from the approved design spec). **Approved:** Tom, 2026-06-25.
