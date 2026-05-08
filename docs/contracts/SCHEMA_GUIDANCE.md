<!--
PROVENANCE: Extracted verbatim from PRODUCTION/CLAUDE.md on 2026-05-08 (HEAD: 5833fe6)
at the start of Phase 8 Run F kernel rewrite.

Source line ranges in pre-rewrite CLAUDE.md:
- Core architectural model: lines 157-168
- Input-source map: lines 195-202
- Schema guidance (primary keys, precision, BOM modeling, purchased finished goods,
  audit semantics): lines 256-280
- Integration guidance (LionWheel, Shopify, Green Invoice): lines 282-300
- Security and access rules: lines 302-308
- Observability and operations: lines 310-315

This file is a continuation of CLAUDE.md authority -- it codifies the schema/integration/
operations guidance that should not live in the boot kernel. The post-rewrite CLAUDE.md
kernel points here for full text. If this file conflicts with CLAUDE.md or with
EXECUTION_POLICY.md or with locked decisions in LOCKED_DECISIONS.md, those win.

Pre-rewrite full archive: PRODUCTION/docs/archive/CLAUDE.md.pre-kernel-rewrite-2026-05-08.md
-->

# GT Factory OS — Schema, Integration, and Operations Guidance

> **Authority layer:** technical guidance for schema, BOM modeling, audit semantics, integrations, security, and observability. Extracted from `CLAUDE.md` to keep the kernel thin.
>
> **Authority rules (inherited):**
> 1. `CLAUDE.md` (boot kernel) and `LOCKED_DECISIONS.md` (full locked text) win on any conflict with this file.
> 2. `EXECUTION_POLICY.md` wins on operational policy.
> 3. This file is technical / contract-level guidance — not policy.

---

## Core architectural model

The system is designed as these layers:

1. **Canonical master data** — items, components, BOM (head/version/lines), suppliers, supplier_items, planning policy, UOM tables
2. **Operational event intake** — forms, planning screens, integrations, admin imports
3. **Validation and policy gate** — required fields, idempotency, duplicate detection, approval thresholds, UOM validation, permission checks
4. **Canonical ledger** — append-only stock ledger; one source of stock history; reversal rows only
5. **Projection layer** — current stock projection, open orders mirror views, open supply views, readiness and exception projections
6. **Planning engine** — SQL-first; writes to `planning_runs` and `planning_run_lines`; never mutates masters or ledger
7. **Portal** — operator/planner/admin workflows; role-gated routes
8. **Dashboard** — read-only control tower; no editing
9. **Jobs and integrations** — LionWheel pull, planning recompute, nightly exports, integrity checks, digest emails

---

## Input-source map

- **Forms (human-reported facts):** Goods Receipt; Waste / Adjustment; Physical Count; Production Actual (Phase 3); PO creation workflow
- **Planning screens (structured judgment):** Forecast planning workspace; Purchase recommendation review; Production recommendation review
- **Integrations:** LionWheel orders and shipments; Shopify FG stock sync; Green Invoice invoice/price evidence
- **Admin / bulk import:** item master; component master; BOM maintenance; supplier maintenance; planning policy
- **CLI / scripts:** initial imports; backfills; repair scripts; migration scripts; one-off reconciliation
- **Explicitly forbidden as runtime dependency:** MCP is not a runtime input channel. Claude Code tooling must not become part of the live operational path.

---

## Schema guidance

### Primary keys
- Legacy text IDs as PKs for business masters where stable and meaningful
- UUIDs for system-generated records, forms, runs, approvals, history

### Precision
- Exact numeric types, never float
- High-precision numeric standard for quantities, ratios, UOM conversions
- Separate lower-scale money standard for money
- Prefer domains to keep quantity/money semantics consistent

### BOM modeling
- Versioned structure: `bom_head` / `bom_version` / `bom_lines`
- `items` points to a BOM head / active version model, never to ad hoc version fields

### Purchased finished goods
- Do not duplicate `BOUGHT_FINISHED` items into components
- `items.supply_method` enum (exact legacy values, not normalized): `('MANUFACTURED','BOUGHT_FINISHED','REPACK')`
  - `MANUFACTURED` — produced from a BOM
  - `BOUGHT_FINISHED` — resold as-is; direct supplier mapping via `supplier_items.item_id`
  - `REPACK` — produced by repackaging an input component; supplier mapping lives on the input component, not on the repack output

### Audit semantics
For important human actions, preserve both a user foreign key and a display-name snapshot.

---

## Integration guidance

### LionWheel
- Mirror internally
- Never compute planning directly from live API calls
- Use polling plus webhooks where available
- Track snapshot runs and retirement semantics
- Treat split/merge and cancellation handling as first-class reconciliation concerns

### Shopify
- Sync FG stock from the rebuilt system to Shopify
- Reconcile periodically
- Exception-based review for unexplained drift

### Green Invoice
- Feed `price_history`
- Do not auto-create new components from invoice lines
- Do not auto-update active prices unless mapping quality and threshold rules pass
- Net-of-VAT cost semantics

---

## Security and access rules
- Core tables live in a private schema
- Browser does not talk directly to core operational tables
- API is the permission boundary
- Selective RLS only where it actually helps
- Protect audit tables and ledger from update/delete
- Prefer soft-delete / archive for masters

---

## Observability and operations
- Keep a jobs run log
- Track latest successful run for every scheduled job
- Emit exceptions for stale integrations and failed jobs
- Global break-glass mode that makes the system read-only and pauses jobs
- Prefer clear failure over silent drift
