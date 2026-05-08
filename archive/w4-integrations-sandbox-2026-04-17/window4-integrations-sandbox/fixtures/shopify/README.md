# Shopify fixtures

**Owner:** Window 4
**Consumers:** `src/shopify/__tests__/mapper.spec.ts`, `src/shopify/__tests__/replay.ts`

## Purpose

Deterministic, redacted JSON samples of Shopify Admin GraphQL shapes relevant to GT FG sync, used to:

1. exercise the Zod schemas in `src/shopify/api-schemas.ts`
2. exercise the pure mappers in `src/shopify/mapper.ts`
3. provide a replay corpus for regression testing before and after runtime wiring

These fixtures are **not real Shopify responses** captured verbatim. They are hand-authored to match the shape documented at `shopify.dev/docs/api/admin-graphql/latest/` while using fixture-labelled GIDs and non-PII values.

## Redaction rules

| Field | Redaction |
|---|---|
| `inventoryItemId` | `"gid://shopify/InventoryItem/FIXTURE_N"` |
| `locationId` | `"gid://shopify/Location/FIXTURE_N"` |
| Shopify GID `id` fields | `"gid://shopify/<Type>/FIXTURE_N"` |
| `Location.name` | `"FIXTURE_LOCATION"` |
| SKU | real GT SKU convention (`GT-HIB-LOW-1L`, etc.) — not PII, join key to platform `items.sku` |
| Quantity values | small realistic integers |

## Fixture catalogue

| File | Purpose | Shape |
|---|---|---|
| `inventory-set-quantities-input--happy.json` | valid push input with compareQuantity set | `InventorySetQuantitiesInput` |
| `inventory-level-read--single-location.json` | populated InventoryLevel with embedded item and quantities | `InventoryLevel` |

## What these fixtures intentionally do NOT do

- do not contain a real Shopify access token
- do not contain a real Shopify shop domain
- do not drive any live HTTP call
- do not serve as a source of truth for Shopify field completeness — the Zod schemas are the source of truth; fixtures exercise observed happy paths and enumerated edge cases

## Not included this pass (and why)

- **User-error response fixture** — the exact UserError field set for `inventorySetQuantities` was not re-verified verbatim this pass. Authoring a fixture with guessed `code` values would violate the no-invented-fields rule. When a future pass has verbatim confirmation or observed real errors, a `user-error--compare-mismatch.json` can be added.
- **Paginated-read fixture** — the exact PageInfo cursor shape on the `InventoryLevel` connection was not re-verified this pass. A pagination fixture should be added when Slice S2 (reconciliation sweep) begins authoring.
- **Multi-location fixture** — GT's v1 authoritative location model is single-location; multi-location sync is out of scope for Slice S1.
