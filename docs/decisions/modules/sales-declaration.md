# Module Declaration — `sales`

> **Status: DRAFT — awaiting Tom's written approval.** This is a proposal, not
> authority. Per `CLAUDE.md` → Future module rule and `MODULE_TEMPLATE.md`, no
> `sales` code, schema, agents, or UX surfaces may be built until Tom approves
> this declaration in writing and `factory-os-governor` adds the module's lane
> row(s) to `AI_BRAIN_ROUTER.md` §3. Until then the router returns
> `verdict: NEW_MODULE_REQUIRED` for sales work.
>
> **Authored:** 2026-07-18 (branch `claude/gt-sales-system-jnzf6k`).
> **Owner of the declaration process:** `factory-os-governor`. **Approver:** Tom.
> **Do not promote this file to authority. Do not update the router from it until approved.**

---

## 0. Blueprint — why this module, and the evidence base

### 0.1 The strategic thesis (grounded in professional sources)

A deep-research pass (5 search angles, 22 sources fetched, 25 claims adversarially
verified, 3 refuted) converged on one calibrated conclusion for GT:

- **Every canonical framework sequences ICP/segmentation FIRST** — before outreach,
  tooling, or hiring. (Predictable Revenue / Aaron Ross — primary source; Dream 100 /
  Chet Holmes; Sales Acceleration Formula / Mark Roberge. 3-0 verified vs. a primary
  source.)
- **GT is post-product-market-fit** (87–98% monthly returning-customer rate) with a
  **new-account bottleneck** (~3–29 new customers/month). Highest leverage is therefore
  **retention/expansion first, acquisition second** — a priority weighting, not a
  settled truth (the "retention over acquisition" claim carried a split 2-1 vote; Byron
  Sharp / Ehrenberg-Bass credibly argue acquisition drives most growth, and GT's own
  stated bottleneck *is* acquisition).
- **The single highest-ROI system to build first is silent-churn detection.** Wholesale
  churn is silent: accounts do not cancel, they quietly reorder less, then less often,
  then go dark. The #1 early-warning signal is a gap/decline in the reorder pattern
  (classic RFM recency/frequency). (RepSpark, WholesaleHelper, ProspectSoft — 3-0
  verified across four underlying claims.)
- **Treat each multi-branch chain as ONE key account** via an account "hierarchy"
  (parent→branch family tree), then run a deliberate **land-and-expand** motion with
  **white-space mapping** (which products each branch has not yet bought). (gtmnow +
  Salesforce docs; Davies & Ryals KAM maturity model — Springer, primary; Kapta,
  DemandFarm. Mostly 3-0.) **Calibration:** the OWNER is the single account owner —
  tiered KAM teams are enterprise-scale over-engineering for ~7-branch chains.
- **Acquisition = a lean, targeted Dream 100** (hand-picked most-wanted accounts,
  samples + education-based marketing) — NOT high-volume cold outreach.
- **Founder runs the motion before any hire; ops starts fractional, not a full-time
  RevOps hire; when a rep is paid, comp ties to retention/NRR, not gross bookings.**
  (Roberge; Closing Foundry; Stage 2 Capital.)
- **Track 5–9 KPIs, not everything**, chosen by "where would poor performance most
  jeopardize the business." Lean on existing tools (Shopify + Make + spreadsheet /
  lightweight layer), not a new platform. (NetSuite; Miller 7±2.)

Framing doctrine layered on top (owner's stated references): **The Ultimate Sales
Machine** (Chet Holmes) — 12 things done 4,000 times, "pigheaded discipline," Dream 100,
education-based marketing — provides the skeleton; **small-wins** (Weick 1984 / Amabile's
progress principle) provides the cadence: every build step must deliver standalone value.

### 0.2 The evidence base — two live numbers (Shopify, read-only, 2026-07-18)

Pulled from the live store (`greenteaeveryday.myshopify.com`) across the first 100
established-repeat accounts (>8 orders). B2B base was mass-created ~2023-05, so
tenure ≈ 3.2 years and **annual ≈ lifetime ÷ 3.2**.

**Number 1 — annual value per account (the pivotal number):**

| Tier | Lifetime / account | Annual / account | vs. single order (₪1,346) |
|---|---|---|---|
| Whale (יונימרקט) | ₪887,553 | ~₪279K/yr | ×207 |
| Large chain (Isrotel, Mina Tomei, Wix) | ₪200K–940K | ₪40K–296K/yr | ×30–220 |
| Typical established branch | ₪15K–95K | ~₪6K–30K/yr | ×5–22 |

→ Per-account annual value is **5×–200×** the single order. KAM and targeted outbound
are decisively justified.

**Number 2 — silent-churn (sleeping accounts), by chain — value at risk:**

| Sleeping chain | Branches | Lifetime | Annual at risk | Silent since |
|---|---|---|---|---|
| **Mina Tomei / מינה טומיי** | 5 | ₪388,612 | ~₪122K/yr | ~2026-02 (~5.5mo — recent, recoverable) |
| **Isrotel (hotels)** | ~13 | ₪940,436 | ~₪296K/yr | ~2024-09/10 (~21mo) |
| **King Kong** | 4 | ₪78,826 | ~₪25K/yr | 6–7 months |
| **Landwer** | 7 | ₪68,040 | ~₪21K/yr | ~2023–24 (dead) |

Plus large singles: מתוק וטעים ₪161,689 (dead since 2023-10), קפה עם גבעת חן ₪46,108,
אולין סושי רמת השרון ₪32,829. **In just the first 100 accounts, >₪1.7M in lifetime
revenue sits in accounts that have gone silent.**

**Data caveats (must be preserved in the system's behavior):** `amountSpent` is
lifetime and includes at least one anomaly (58 orders, ₪0). "Silent in Shopify" ≠
"churned" — some accounts may buy via another channel (Green Invoice direct, a
distributor). The system's job is to **surface for human review**, never to declare
churn. Annualization assumes a steady rate; real ordering is lumpy/seasonal.

---

## 1. Module name

`sales`

## 2. Business purpose

The `sales` module turns GT's passive, reorder-driven revenue into a repeatable,
system-backed sales operation without adding a new operational platform. It solves three
problems the current setup cannot see: (a) **silent churn** — loyal accounts (and whole
chains) that quietly stop ordering with no alert; (b) **un-captured expansion** — chains
ordering branch-by-branch with no HQ-level relationship and no view of which branches/
products are un-penetrated (white-space); (c) **stalled acquisition** — ~3–29 new
accounts/month with no deliberate motion. Primary user: **Tom** (the single account
owner), with future operator/portal surfaces. Why now: the base is large and loyal
(₪1.9M/quarter, 87–98% retention) but revenue leakage and growth are both invisible to
today's tools; the factory-os brain, Shopify, LionWheel, Make and Green Invoice already
hold the data needed to make them visible.

## 3. Owner lane

`sales-arch` (module-architect, read-only) for the declaration + design phase. Post-
approval, the primary owner lane is a single **cross-module owner**: **Tom is the sole
account owner**; module agents are scoped builders, not account managers. No tiered KAM
headcount (explicitly out of scope — enterprise over-engineering for ~7-branch chains).

**Amendment 2026-07-18 (Tom decision, in writing this session):** the module's
knowledge / doctrine / agent-declaration layer lives in the dedicated **`Sales-Machine`**
repo (`tomw200082-collab/Sales-Machine`) — the sales brain, parallel to PRODUCTION for
factory-os. Its boot kernel (truth constitution) and decisions log govern that layer;
agent declarations are authored in `Sales-Machine/agents/`. Lane isolation unchanged:
nothing in Sales-Machine touches factory-os core, and this declaration remains the
module's governance gate.

## 4. Source of truth

| Entity | PK | Storage (authority) | Tiebreaker when sources disagree |
|---|---|---|---|
| Customer / account (commercial) | Shopify customer id | **Shopify** (commercial system of record) | Shopify wins on commercial customer data |
| B2B company ↔ branch hierarchy | `sales_core` account_id | **`sales_core`** (module-owned) | Module owns the chain grouping; Shopify tags are a mirror |
| Order / reorder history | Shopify order id | **Shopify** (+ Green Invoice for off-Shopify B2B invoices) | Shopify for Shopify orders; Green Invoice is evidence for direct invoices |
| Delivery / shipment state | LionWheel id | **LionWheel mirror** (per CLAUDE.md) | LionWheel wins |
| Sleeping-signal / touch-log / white-space / Dream-100 | `sales_core` PKs | **`sales_core`** (module-owned) | Module owns its own intelligence |

**Hard rule:** the `sales` module never becomes an authority for stock truth. It reads
factory-os product/BOM catalog **via curated views only**, and writes **nothing** to
factory-os core. Master data after seed remains Postgres core per CLAUDE.md; the sales
module's private schema is additive and droppable.

## 5. Data model

All module tables live in a private schema **`sales_core`** (scoped; the sales backend
agent cannot touch factory-os core tables). Proposed entities:

| Table | PK | Mutable? | Audit | FKs to factory-os |
|---|---|---|---|---|
| `sales_core.account` | UUID | mutable | updated_at + change log | maps to Shopify customer id (external ref, not FK to core) |
| `sales_core.account_hierarchy` | (parent_account_id, child_account_id) | mutable | change log | none |
| `sales_core.contact` | UUID | mutable | change log | none |
| `sales_core.touch_log` | UUID | append-only | immutable | none |
| `sales_core.sleeping_signal` | UUID | append-only (recomputed snapshots) | immutable | reads order history (Shopify), not core |
| `sales_core.whitespace_map` | (account_id, product_ref) | mutable (rebuilt) | rebuild timestamp | **reads** factory-os sellable-catalog **view** only |
| `sales_core.dream100_target` | UUID | mutable | change log | none |

Primary-key strategy: UUID for module-owned rows; external string refs for Shopify/
LionWheel/Green Invoice ids. `touch_log` and `sleeping_signal` are append-only (mirrors
the ledger doctrine — history is immutable, corrections are new rows). Cross-module reads
(the sellable catalog for white-space) are **views only**; cross-module writes are
forbidden.

## 6. Upstream systems

| System | Auth | Read frequency | Freshness tolerance | Failure mode |
|---|---|---|---|---|
| Shopify (customers, orders, tags, metafields) | existing app/API | polled (daily) + on-demand | 24h for briefs; live for a manual run | brief runs on last snapshot; flag staleness |
| LionWheel mirror | existing (Postgres mirror) | as mirrored | per mirror | degrade to Shopify-only signal |
| Green Invoice (off-Shopify B2B invoices) | existing (no-guess rule stands) | polled | 24–48h | treat as "unknown", never assume churn |

## 7. Downstream consumers

| Consumer | Read pattern | Stale-read tolerance |
|---|---|---|
| Weekly sales brief (skill) | on run (scheduled + on-demand) | 24h |
| Sleeping-account alert (skill/Make) | on run | 24h |
| Tom (chat / email / push) | delivered | 24h |
| Future portal `/sales` screen | polled view | 24h |
| Marketing (education-based collateral, Dream 100) | manual, curated | n/a |

## 8. Write boundaries

```yaml
may_write:
  - sales_core.*                          by sales-backend-builder
  - Shopify customer tags/metafields (sales-scoped only: customer-type,
      chain-parent, sleeping-flag, dream100)   by sales-integration-builder
  - Shopify Email / Flow drafts (customer-facing sends)  by sales-integration-builder
      — GATED by frozen flag SALES_CUSTOMER_OUTREACH_WRITE_ENABLED (see §11)
  - docs/decisions/modules/sales-*.md (this declaration + decisions log)  by sales-arch
may_not_write:
  - factory-os core tables (stock_ledger, balance_anchors, items, components, bom_*, ...)
  - balance_anchors / any stock projection
  - other modules' private schemas
  - .env*, credentials, secrets
  - PRODUCTION authority docs (CLAUDE.md, EXECUTION_POLICY.md, CURRENT_STATE.md,
      WORKSPACE_MAP.md, ACTIVE_NOW.md, AI_BRAIN_ROUTER.md)
  - AI_BRAIN_ROUTER.md / AGENT_REGISTRY.md / COMMAND_REGISTRY.md
      (only factory-os-governor updates these, AFTER Tom approval)
```

## 9. Read boundaries

```yaml
may_read:
  - Shopify customers/orders/tags/metafields
  - LionWheel mirror (delivery/shipment state)
  - Green Invoice invoice evidence (read-only)
  - factory-os SELLABLE CATALOG via a curated view only (for white-space mapping)
may_not_read:
  - factory-os core tables directly (stock_ledger, bom_*, balance_anchors — use views)
  - other modules' private tables (curated views only)
  - secrets / .env*
```

## 10. UX surfaces  [conditional — deferred to a later gate]

No portal route ships in v1. A future `/sales` route (accounts board, sleeping list,
chain white-space, Dream 100 pipeline) is **deferred** and, if built, obeys portal
locked decisions: role-gated, Hebrew/RTL with a Tom-approved register entry, UX release
gate SHIP verdict, RUNTIME_READY for any backend-bound data. v1 delivers value through
the **weekly brief skill + email/push**, not a new screen.

## 11. Integration surfaces  [conditional]

| Provider | Frozen flag (default `false`) | Contract doc | Idempotency | Reversal |
|---|---|---|---|---|
| Shopify — customer-facing sends (Email/Flow/WhatsApp) | **`SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`** (NEW; `false` until Tom written approval + dry-run + ≥24h soak + RUNTIME_READY) | `docs/integrations/sales-outreach.md` (to author) | one send per (account, campaign, period) key | send is logged in `touch_log`; suppression list honored |
| Shopify — customer tags/metafields (sales-scoped) | reversible, single-scope; allowed when confident per External-action authorization | same | tag writes idempotent by design | tag removable |
| LionWheel | read-only in v1 | n/a | n/a | n/a |
| Green Invoice | read-only in v1 | n/a | n/a | n/a |

**Note:** the existing frozen flags `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` and
`SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` concern FG **inventory** writes and are
untouched by this module. Customer-facing outreach is a *different* surface and gets its
own flag above — no automated customer send happens until that flag is flipped under the
full ceremony. Confirm-before-acting on any mass/customer-facing send stands regardless.

## 12. Agent ownership

| Lane | Agent name | Status | Allowed-paths scope |
|---|---|---|---|
| module-arch | `sales-architect` | required (declaration phase) | read-only; `docs/decisions/modules/sales-*` |
| backend-db | `sales-backend-builder` | required if backend built | `sales_core.*`, `db/sales/**` — NOT factory-os core |
| portal | `sales-portal-builder` | required only if UI built (deferred) | portal `sales/**` routes only |
| integration | `sales-integration-builder` | required for Shopify/LW/GI boundary | `docs/integrations/sales-*`, sales-scoped Shopify writes |

Each agent needs an `AGENT_TEMPLATE.md` file before creation (post-approval). Module
agents cannot touch factory-os core schema — enforced by allowed-paths.

## 13. Commands needed  [conditional]

| Command | Purpose | Primary agent | Verdict tokens |
|---|---|---|---|
| `/sales-weekly-brief` | The Holmes "six things" list + 5–9 KPIs, delivered | sales skill | PASS / HOLD_FOR_TOM (per `VERDICT_GLOSSARY.md`) |
| `/sleeping-accounts` | Off-pace / missing-order list with value-at-risk, for human review | sales skill | PASS |
| `/account-whitespace` | Per-chain: branches × products not yet bought | sales skill | PASS |
| `/dream100-review` | Review/advance the Dream 100 acquisition list | sales skill | PASS |

New commands require `factory-os-governor` PROCEED + Tom approval before creation.

## 14. Tests required

- **Unit:** sleeping-signal math (days-since-last vs. per-account cadence baseline);
  annualization; white-space set difference.
- **Integration (within module):** hierarchy roll-up (branch orders sum to chain);
  Shopify tag write/read round-trip; touch-log append-only enforcement.
- **Cross-module reconciliation:** white-space reads from the sellable-catalog view
  **never mutate** core; a rebuild proves `sales_core` holds no core-truth copy that can
  drift.
- **Idempotency:** outreach dedupe by (account, campaign, period) — no double-send.
- **Failure-mode:** Shopify/LionWheel/Green Invoice unavailable → brief degrades and
  flags staleness, never invents churn; "silent in Shopify" is labeled "needs check,"
  not "churned."
- **Golden-path E2E:** a known sleeping chain (e.g. Mina Tomei) surfaces in the brief
  with correct value-at-risk and per-branch last-order dates.

## 15. Gates

| Gate | Exit criteria |
|---|---|
| M-Gate 1 — Declaration | This file approved by Tom in writing |
| M-Gate 2 — Foundation | `sales_core` schema in place; sales-architect exists; tests scaffolded; account hierarchy modeled from existing chain tags |
| M-Gate 3 — Truth (first win) | Sleeping-account detection round-trips on live Shopify data; the two numbers reproduce; tests green |
| M-Gate 4 — UX (if/when built) | UX release gate SHIP for any `/sales` route (deferred) |
| M-Gate 5 — Integration | Outreach dry-run clean; `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` still `false` until soak |
| M-Gate 6 — Cross-module | Reconciliation tests pass; zero contamination of factory-os core / stock truth |

## 16. Rollback / disable strategy

- **Schema isolation:** `sales_core` is a private schema; dropping it removes the module
  with zero effect on factory-os core.
- **Feature flag:** the weekly-brief skill and any outreach are behind flags; disabling
  reverts GT to today's passive state.
- **Tag cleanup:** sales-scoped Shopify tags/metafields are namespaced and removable.
- **Job disable:** scheduled brief/alert jobs can be paused independently.
- **UX hide:** no v1 route; future route is hideable by role/flag.
- **Comms:** Tom notified on any disable.

## 17. Tom decisions required

1. **Platform path** (money/vendor): stay on Shopify-plan workaround (tags/metafields)
   vs. a B2B/wholesale app vs. upgrade to **Shopify Plus** (native Companies, per-company
   price lists, B2B login). Current plan = "Shopify", `companiesCount = 0`. Pivotal for
   how the chain hierarchy is stored long-term. *(Partially resolved 2026-07-18: Tom
   opened the dedicated `Sales-Machine` brain repo for the knowledge/agents layer. The
   Shopify-plan question itself remains open.)*
2. **Customer-outreach automation**: approve/deny flipping
   `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` (with dry-run + soak). Until then: brief-only,
   Tom sends manually.
3. **Contact-data remediation policy**: the B2B records use placeholder login emails
   (`@guerrillamail.biz`, `@israelmail.com`) — decide whether/how the module writes real
   ordering-contact email/phone/WhatsApp for the top accounts.
4. **Retention-vs-acquisition weighting**: confirm "retention/expansion first" (the data
   supports it, but acquisition is the stated bottleneck — this is a strategy call).
5. **Comp model** if/when a salesperson is paid (tie to retention/NRR — Roberge).
6. **Hebrew register entries** for any customer-facing copy / future portal surface.

Tracked in `docs/decisions/modules/sales-decisions.md` (to open on approval).

## 18. Definition of done (module v1)

- [ ] §15 gates 1–3 + 5–6 closed with evidence (Gate 4 deferred).
- [ ] All §17 Tom decisions answered.
- [ ] Sleeping-account detection live on all accounts (not just the first 100 sampled),
      value-at-risk correct, "needs-check ≠ churned" labeling enforced.
- [ ] Account hierarchy covers all known chains; per-chain white-space map builds.
- [ ] Weekly brief delivers the "six things" + 5–9 KPIs (Hebrew, branded), like
      `daily-ops-guardian`.
- [ ] All §14 tests green with N/N counts; cross-module reconciliation proves zero core
      contamination.
- [ ] Rollback (drop `sales_core`) dry-run-tested.
- [ ] `AI_BRAIN_ROUTER.md` §3 + `AGENT_REGISTRY.md` + `COMMAND_REGISTRY.md` updated
      **by factory-os-governor** post-approval; `CURRENT_STATE.md` records module status.

---

## Appendix A — How it manifests in practice (the phased build / small-wins ladder)

Each rung delivers standalone value (Weick small-wins); nothing here builds a new
**runtime** platform. *(Amended 2026-07-18: the knowledge/agents brain lives in the
dedicated `Sales-Machine` repo per Tom's decision — see §3. Runtime code placement, if
ever needed, is decided at its own gate.)*

1. **Win 1 — Sleeping radar (weeks).** A skill in the `daily-ops-guardian` mold reads
   Shopify order history, computes each account's own cadence, and lists off-pace/missing
   accounts with value-at-risk — for Tom's review (not auto-action). *Manifestation:* the
   Mina Tomei chain (~₪122K/yr, silent 5.5mo) surfaces this week. Runs on existing data;
   zero new infra. **This is the highest-ROI first system per the research.**
2. **Win 2 — Chain hierarchy (weeks).** Standardize the existing brand tags
   (`landwer`, `r2m`, `minatomei`, `isrotel`…) into a parent→branch map so a chain reads
   as one account. *Manifestation:* "Isrotel = 13 branches, 12 dark since Sept 2024" is
   one line, not 13 unreadable rows.
3. **Win 3 — White-space map (month).** Per chain, branches × products-not-yet-bought.
   *Manifestation:* "R2M buys product A at 6/7 branches — branch 7 and product B are open."
4. **Win 4 — Weekly brief (month).** The Holmes "six things" + 5–9 KPIs, delivered
   Hebrew/branded. *Manifestation:* Monday list: "call these 3 sleeping accounts, 2 Dream
   100 touches, 1 branch-rollout." The machine writes the list; Tom executes.
5. **Win 5 — Dream 100 acquisition (months).** ~50–100 hand-picked HoReCa targets
   (chains weighted — one win = many branches) + samples + education-based marketing —
   the marketing linkage. *Manifestation:* one Core Story feeds every channel; Dream 100
   gets it first.
6. **Win 6 — People & comp (later).** Only once the motion is proven: Tom first, then
   fractional ops, comp tied to retention/NRR.

## Appendix B — Sources (from the verified research pass)

Predictable Revenue (predictablerevenue.com — primary) · Sales Acceleration Formula /
Roberge (nateliason.com summary of the Wiley book) · Dream 100 / Chet Holmes
(predictableprofits.com, chetholmes.com) · Davies & Ryals KAM maturity (Springer —
primary) · account hierarchy / land-and-expand (gtmnow.com + Salesforce docs, kapta.com,
demandfarm.com) · silent churn & win-back (repspark.com, wholesalehelper.io,
prospectsoft.com) · KPIs (netsuite.com). Full verification log, confidence levels, and
the 3 refuted claims: research pass 2026-07-18 (retained in session evidence).
