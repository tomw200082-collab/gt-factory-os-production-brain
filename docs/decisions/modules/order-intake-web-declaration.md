# Module declaration — `order-intake-web`

> **Status:** submitted for Tom's written approval. Design approved in chat
> 2026-08-10; this declaration closes Module Gate 1.
> **Design:** `docs/superpowers/specs/2026-08-10-order-intake-web-design.md`
> **Template:** `MODULE_TEMPLATE.md`

## 0. Why this is a channel, not a new module

`order-intake` already exists inside factory-os (`gt-factory-os/api/src/order-intake`)
and already takes customer-facing orders — over WhatsApp. This adds a **web channel**
to that module: same engine, same pricing, same guards, same Shopify commit path.

It gets a declaration anyway, because one thing genuinely is new: a **public,
unauthenticated surface on a GT domain**. That is blast radius the existing module has
never had, and it is exactly what this template exists to make explicit.

**It owns no new core entities and adds no new writer to the money path.**

## 1. Module name

`order-intake-web` — web channel of `order-intake`.

## 2. Business purpose

Today a new HoReCa buyer has no self-serve way to place a first order: it goes through
Doreen, by phone or WhatsApp. Existing buyers reorder passively. This gives both a
catalog page that produces a real Shopify draft, so an order can start at 23:00 without
anyone at GT awake. Primary user: **external customer** (café / restaurant buyer),
with a GT human as approver. Why now: the money rail (PayPlus via Shopify draft
`invoiceUrl`, Green Invoice ↔ Shopify) is already live and proven, so the page is the
only missing piece.

## 3. Owner lane

`integration` (existing) for the intake endpoint and Shopify commit; `portal` for the
approval screen. The public page is a standalone static/SSR surface owned by the
integration lane. No new lane.

## 4. Source of truth

| Entity | PK | Storage | Tiebreaker |
|---|---|---|---|
| Order / draft order | Shopify draft order id | **Shopify** | Shopify wins; it is the order system of record |
| Customer | Shopify customer id | **Shopify** | Shopify wins |
| Customer agreed price | — | derived at approval from Shopify order history (`order-intake/engine/pricing.ts`) | last real paid price beats catalog |
| Sellable stock | `item_id` | **factory-os** (`current_balances`), mirrored to Shopify `available` by the reconciler | factory-os is authoritative; Shopify is the sync target |
| Tax document | GI document id | **Green Invoice** | GI wins |
| Web submission audit | `submission_id` | factory-os, module-scoped table | — |

## 5. Data model

The module owns **one** table: `order_intake_web.submissions` — the raw submitted
cart plus business details, the resulting draft id, and status. Append-only; a status
change is a new row keyed by `submission_id`.

FKs into factory-os stop at `items.item_id` (read-only). No factory-os core table
gains a column. No `stock_ledger`, `balance_anchors`, `bom_*` access of any kind.

## 6. Upstream systems

| System | Auth | Frequency | Freshness tolerance | Failure mode |
|---|---|---|---|---|
| Shopify Admin API | existing app token | live on submit | n/a | submit fails closed with a "we got your details, we'll call" page; the submission row is still written |
| factory-os catalog + availability | internal | live read, cached ≤60s | 5 min (reconciler cycle) | fall back to hiding availability rather than showing a wrong number |

## 7. Downstream consumers

| Consumer | Pattern | Stale tolerance |
|---|---|---|
| GT approval screen | direct query on `submissions` + Shopify draft | live |
| Existing Shopify order pipeline | unchanged — a draft is a draft | n/a |
| Green Invoice ↔ Shopify app | unchanged — fires on paid order | n/a |

## 8. Write boundaries

```yaml
may_write:
  - order_intake_web.submissions            by order-intake-web endpoint
  - Shopify draft orders (via existing commitCart)   by order-intake-web endpoint
  - Shopify customers (create only, new buyers)      by order-intake-web endpoint
may_not_write:
  - factory-os core (stock_ledger, balance_anchors, items, components, bom_*)
  - Shopify inventory levels / available          (the reconciler owns those)
  - Shopify orders — no completion, no capture, no cancel
  - Green Invoice — nothing, ever; the Shopify app issues documents
  - .env*, credentials, secrets
  - PRODUCTION authority docs
```

## 9. Read boundaries

```yaml
may_read:
  - private_core.items (ACTIVE sellable), case_pack, product_group
  - curated availability view / Shopify variant available
  - Shopify customer + order history (for the approval step's price lookup)
may_not_read:
  - stock_ledger and projections directly (curated views only)
  - other modules' private tables
  - secrets/.env*
```

## 10. UX surfaces

| Route | Gating | Notes |
|---|---|---|
| `pricelist.gteveryday.com` (public) | none | Hebrew + RTL by nature — customer-facing marketing surface, outside the portal's English-first rule. Needs its own copy register entry. |
| portal approval screen (path TBD, §17) | admin / planner | English per portal standard |

Hebrew copy for the public page needs a Tom-approved register entry before build.

## 11. Integration surfaces

| Provider | Frozen flag | Contract | Idempotency | Reversal |
|---|---|---|---|---|
| Shopify (draft create) | `ORDER_INTAKE_WEB_ENABLED` — default `false` | reuses `order-intake/shopify/commit.ts` | one open draft per submission, `claimSession` CAS | a draft is deletable; nothing is charged before human approval |
| PayPlus | none new — already the Shopify gateway | n/a | n/a | Shopify refund, by a human |
| Green Invoice | none new — the Shopify app issues | n/a | n/a | credit note, by a human |

`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is untouched: this module never initiates
contact. It responds to a buyer who came to the page.

## 12. Agent ownership

No new agents. `integration-boundary-executor` owns the endpoint;
`portal-production-executor` owns the approval screen. Both already have declarations
and allowed-paths.

## 13. Commands needed

None.

## 14. Tests required

Listed in the design doc §Tests. Categories: unit (carton rule, floor, ח.פ check
digit), integration (submission → draft, every line placed), idempotency
(double-submit → one draft), failure-mode (Shopify down, stale availability), E2E
golden path (build cart → draft appears with the right totals and tags).

Cross-module reconciliation: none required — the module writes no core truth.

## 15. Gates

| Gate | Exit criteria |
|---|---|
| 1 — Declaration | This file approved by Tom in writing |
| 2 — Foundation | `submissions` table + endpoint skeleton + tests scaffolded; flag `false` |
| 3 — Truth | A submission round-trips to a Shopify draft with correct totals and tags; all §14 tests green |
| 4 — UX | Public page passes `/ux-release-gate`; Hebrew register entry approved |
| 5 — Integration | Dry-run: 10 submissions produce 10 correct drafts, none completed, none charged |
| 6 — Cross-module | Proof no core table was written; `rebuild_verifier() = 0` unchanged |

## 16. Rollback / disable strategy

`ORDER_INTAKE_WEB_ENABLED=false` closes the endpoint; the page then shows a
"contact us" form only. `order_intake_web` is a separate schema and can be dropped
whole without touching core. The public hostname can be repointed to the static
pricelist in one DNS change. No cron, no job. Drafts created before rollback are
ordinary Shopify drafts and stay valid.

## 17. Tom decisions required

| # | Decision | Blocking |
|---|---|---|
| 1 | Where DNS for `gteveryday.com` is managed, so `pricelist` can get a CNAME | yes — and the printed link is dead until it is done |
| 2 | Who approves web orders (Doreen / Tom / both), and whether the approval screen is a portal route or Shopify admin + the `needs-review` tag | yes |
| 3 | May a brand-new customer submit an order before a human has spoken to them, or does the page open an account request first? | yes |
| 4 | Hebrew copy register entry for the public page | before Gate 4 |
| 5 | Hosting: same Vercel account as the portal, or separate | before Gate 2 |
| 6 | `items.case_pack` for the 17 items missing it | no — not on the rule's path |

## 18. Definition of done

- [ ] Gates §15 all closed with evidence.
- [ ] Tom decisions §17 answered.
- [ ] `/ux-release-gate` SHIP on the public page.
- [ ] §14 tests green, N/N reported.
- [ ] Rollback dry-run: flag off → page degrades correctly.
- [ ] `AI_BRAIN_ROUTER.md` §3 records the channel under the existing lane rows.
- [ ] `CURRENT_STATE.md` records live status.

---

**Submitted:** 2026-08-10 · **Approver:** Tom.
