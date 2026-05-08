# window4-integrations-sandbox

**Owner:** Window 4 (Integrations / Jobs / Exports / Dashboard Contracts)
**Status:** parallel-safe scaffolding — NOT runtime, NOT canonical
**Upstream docs:**
- [window4-lionwheel-contract-pack.md](../window4-lionwheel-contract-pack.md) — accepted contract pack
- [window4-lionwheel-runtime-handoff.md](../window4-lionwheel-runtime-handoff.md) — accepted runtime handoff spec

## What this directory is

Window-4-owned TypeScript scaffolding that reduces Gate 4 implementation risk without crossing into live sync, DDL, scheduler wiring, webhook endpoints, portal, or planning-engine work.

The files here are **reference and contract scaffolding**, not canonical runtime. When Slice 1 runtime begins, the contents of `src/lionwheel/` will be promoted into the backend monorepo **by re-typing**, not by file copy. File-copy from sandbox to canonical is explicitly forbidden (CLAUDE.md §4.1 / §6.4 anti-pattern).

## What it is NOT

- NOT the runtime fetcher (no HTTP is performed anywhere here)
- NOT the CLI that will run against production LionWheel (the CLI here exits before any HTTP)
- NOT the migration layer (no DDL here)
- NOT the webhook endpoint (no server code here)
- NOT the scheduler (no cron / trigger code here)
- NOT a portal integration (no React / Next.js here)
- NOT ready to count as runtime completion. Gate 4 is still at 0% runtime per user rule.

## Phase A — First runtime slice (frozen from runtime handoff)

**Slice 1: single-task pull via `GET /tasks/show/:task_id`, CLI-driven, writes to mirror tables, one `integration_run` row per invocation.**

### Invariants that cannot be violated

1. `wp_order_id` is NON-UNIQUE. Split orders share it. Mirror schema must not add a unique index on it.
2. String-decimal semantics preserved at ingest. `task.order_total`, `order_items.price`, `order_items.quantity`, `order_items.weight` are stored as `text` and parsed only at read time.
3. No generic `/tasks` list endpoint exists. The fetcher works per `task_id` or per `/routes?date=` only.
4. No invented field names. Every field in the Zod schemas traces to the inspected response evidence in the contract pack.
5. `raw_payload` preservation on every mirror entity (jsonb) — protects against schema drift.
6. Kill-switch halts LionWheel sync only; never touches `stock_ledger`, `balance_anchors`, or masters.
7. `order_items.sku` matches `items.sku` by lookup; NEVER auto-create an `items` row from an integration payload.
8. Idempotent upsert: `ON CONFLICT DO UPDATE WHERE EXCLUDED.updated_at > mirror_source_watermark`. Order-independent convergence.

### Window ownership for Slice 1 outputs

| Output | Owner |
|---|---|
| Zod API schemas | **Window 4** (this directory) |
| Mirror upsert shapes (as types) | **Window 4** (this directory) |
| Fetcher interface | **Window 4** (this directory) |
| CLI entry-point | **Window 4** (this directory when complete) |
| Secret-store wiring design | **Window 4** |
| Actual migrations / DDL | **Window 1** |
| `freshness_status_view` SQL | **Window 1** |
| pgTAP tests V.1–V.12 | **Window 1** |
| Portal consumer (Slice 6, later) | **Window 2** |

## Directory map

```
window4-integrations-sandbox/
├── README.md                              # this file
├── package.json                           # minimal node package, zod-only dep
├── tsconfig.json                          # strict TypeScript
├── src/lionwheel/
│   ├── api-schemas.ts                     # Zod schemas for LionWheel API responses
│   ├── mirror-shapes.ts                   # Zod schemas for mirror upsert shapes
│   ├── mapper.ts                          # pure API -> mirror mapper, no I/O
│   ├── fetcher.ts                         # typed fetcher interface, no implementation
│   ├── env.ts                             # typed env-var parsing, no side effects
│   ├── cli.ts                             # CLI skeleton — validates args + env, exits before HTTP
│   └── __tests__/
│       ├── mapper.spec.ts                 # unit tests (node:test)
│       └── replay.ts                      # fixture replay harness
├── src/shopify/
│   ├── api-schemas.ts                     # Zod schemas for Shopify Admin GraphQL shapes
│   ├── mirror-shapes.ts                   # Zod for push request / push plan / drift verdict
│   ├── mapper.ts                          # pure mappers: push, read->reconciliation, drift
│   ├── fetcher.ts                         # typed fetcher interface, no implementation
│   ├── env.ts                             # typed env-var parsing, no side effects
│   ├── cli.ts                             # CLI skeleton — validates args + env, exits before HTTP
│   └── __tests__/
│       ├── mapper.spec.ts                 # unit tests (node:test)
│       └── replay.ts                      # fixture replay harness
├── fixtures/lionwheel/
│   ├── README.md                          # fixture catalogue + redaction rules
│   ├── task-show--completed-single-visit.json
│   ├── task-show--canceled.json
│   ├── tasks-by-order-id--split.json
│   ├── routes--populated.json
│   ├── routes--empty.json
│   ├── error--401.json
│   └── error--404.json
├── fixtures/shopify/
│   ├── README.md                          # fixture catalogue + redaction rules
│   ├── inventory-set-quantities-input--happy.json
│   └── inventory-level-read--single-location.json
└── docs/
    ├── secret-store-wiring.md             # how LIONWHEEL_API_TOKEN gets to runtime
    └── blocker-register.md                # canonical Window 4 blocker register
```

## How to exercise (optional, not required for this pass)

```sh
# from this directory
npm install
npm run typecheck             # strict tsc, no emit (covers both integrations)
npm test                      # unit tests via node:test (both integrations)
npm run test:lionwheel        # LionWheel unit tests only
npm run test:shopify          # Shopify unit tests only
npm run replay                # fixture smoke-check across both integrations
npm run replay:lionwheel      # LionWheel fixture smoke-check only
npm run replay:shopify        # Shopify fixture smoke-check only
```

None of these commands performs HTTP, touches a DB, or mutates any state. They are pure static analysis and in-memory parsing. They are **not required** for this pass to count as parallel-safe; their value is as a **typed reference** that future runtime authors can trust.

## What produced this scaffolding

Governance: [factory-os-autonomous-builder skill](../../..) — Window 4 third pass, 2026-04-17. See the governance output in conversation for the §9 structured summary.
