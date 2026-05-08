/**
 * Unit tests for Shopify api-schemas and mapper.
 *
 * Invariants tested:
 *   - every fixture parses cleanly against its declared schema
 *   - push path produces a valid InventorySetQuantitiesInput
 *   - compareQuantity is sourced from syncState.last_pushed_available
 *   - absolute quantity equals platformProjectedQty
 *   - ignoreCompareQuantity is always false in v1
 *   - idempotency key is deterministic given same (runId, target)
 *   - negative quantity throws ShopifyMapperError
 *   - first-push (null compareQuantity) throws ShopifyMapperError
 *   - read mapper extracts SKU + available/on_hand correctly
 *   - drift classifier returns the right verdict per case
 */

import { describe, test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  InventoryLevelSchema,
  InventorySetQuantitiesInputSchema,
} from "../api-schemas.js";
import {
  classifyDrift,
  deriveIdempotencyKey,
  mapInventoryLevelToReconciliationRow,
  mapPushRequestToPlan,
  ShopifyMapperError,
} from "../mapper.js";
import { PushQuantityRequestSchema } from "../mirror-shapes.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const FIXTURES = resolve(__dirname, "..", "..", "..", "fixtures", "shopify");

function loadFixture(name: string): unknown {
  return JSON.parse(readFileSync(resolve(FIXTURES, name), "utf-8"));
}

/* ---------------------------------------------------------------------- *
 * Schema parse
 * ---------------------------------------------------------------------- */

describe("Shopify api-schemas parse fixtures", () => {
  test("inventory-set-quantities-input--happy", () => {
    const raw = loadFixture("inventory-set-quantities-input--happy.json");
    const parsed = InventorySetQuantitiesInputSchema.parse(raw);
    assert.equal(parsed.name, "available");
    assert.equal(parsed.ignoreCompareQuantity, false);
    assert.equal(parsed.quantities.length, 1);
    assert.equal(parsed.quantities[0]!.quantity, 42);
    assert.equal(parsed.quantities[0]!.compareQuantity, 40);
  });

  test("inventory-level-read--single-location", () => {
    const raw = loadFixture("inventory-level-read--single-location.json");
    const parsed = InventoryLevelSchema.parse(raw);
    assert.equal(parsed.item.sku, "GT-HIB-LOW-1L");
    assert.ok(parsed.quantities.length > 0);
    assert.equal(parsed.location.isActive, true);
  });
});

/* ---------------------------------------------------------------------- *
 * deriveIdempotencyKey
 * ---------------------------------------------------------------------- */

describe("deriveIdempotencyKey", () => {
  const base = {
    runId: "00000000-0000-0000-0000-000000000001",
    inventoryItemId: "gid://shopify/InventoryItem/111",
    locationId: "gid://shopify/Location/222",
  };

  test("same inputs produce same key", () => {
    assert.equal(deriveIdempotencyKey(base), deriveIdempotencyKey(base));
  });

  test("different runId => different key (retry after compare-mismatch is a new logical push)", () => {
    const other = { ...base, runId: "00000000-0000-0000-0000-000000000002" };
    assert.notEqual(deriveIdempotencyKey(base), deriveIdempotencyKey(other));
  });

  test("different inventoryItemId => different key", () => {
    const other = {
      ...base,
      inventoryItemId: "gid://shopify/InventoryItem/999",
    };
    assert.notEqual(deriveIdempotencyKey(base), deriveIdempotencyKey(other));
  });

  test("different locationId => different key", () => {
    const other = { ...base, locationId: "gid://shopify/Location/999" };
    assert.notEqual(deriveIdempotencyKey(base), deriveIdempotencyKey(other));
  });
});

/* ---------------------------------------------------------------------- *
 * mapPushRequestToPlan — happy path
 * ---------------------------------------------------------------------- */

describe("mapPushRequestToPlan — happy path", () => {
  const req = PushQuantityRequestSchema.parse({
    sku: "GT-HIB-LOW-1L",
    platformProjectedQty: 42,
    mapping: { shopify_inventory_item_id: "gid://shopify/InventoryItem/111" },
    syncState: { last_pushed_available: 40 },
    locationId: "gid://shopify/Location/222",
    runId: "00000000-0000-0000-0000-000000000001",
    traceId: "trace-abc",
    quantityName: "available",
    reason: "correction",
  });

  test("produces a valid InventorySetQuantitiesInput", () => {
    const plan = mapPushRequestToPlan(req);
    const parsed = InventorySetQuantitiesInputSchema.safeParse(plan.input);
    assert.ok(parsed.success, `invalid input shape: ${JSON.stringify(parsed.error ?? {})}`);
  });

  test("compareQuantity equals syncState.last_pushed_available", () => {
    const plan = mapPushRequestToPlan(req);
    assert.equal(plan.input.quantities[0]!.compareQuantity, 40);
  });

  test("absolute quantity equals platformProjectedQty", () => {
    const plan = mapPushRequestToPlan(req);
    assert.equal(plan.input.quantities[0]!.quantity, 42);
  });

  test("ignoreCompareQuantity is false (v1 compare-and-set safety)", () => {
    const plan = mapPushRequestToPlan(req);
    assert.equal(plan.input.ignoreCompareQuantity, false);
  });

  test("name passes through", () => {
    const plan = mapPushRequestToPlan(req);
    assert.equal(plan.input.name, "available");
  });

  test("reason passes through (required Shopify field)", () => {
    const plan = mapPushRequestToPlan(req);
    assert.equal(plan.input.reason, "correction");
  });

  test("idempotencyKey is deterministic", () => {
    const a = mapPushRequestToPlan(req).idempotencyKey;
    const b = mapPushRequestToPlan(req).idempotencyKey;
    assert.equal(a, b);
  });

  test("on_hand quantityName sources compareQuantity from last_pushed_on_hand", () => {
    const onHandReq = PushQuantityRequestSchema.parse({
      ...req,
      quantityName: "on_hand",
      syncState: { last_pushed_available: 40, last_pushed_on_hand: 38 },
    });
    const plan = mapPushRequestToPlan(onHandReq);
    assert.equal(plan.input.name, "on_hand");
    assert.equal(plan.input.quantities[0]!.compareQuantity, 38);
  });
});

/* ---------------------------------------------------------------------- *
 * mapPushRequestToPlan — rejects invalid input
 * ---------------------------------------------------------------------- */

describe("mapPushRequestToPlan — rejects invalid input", () => {
  test("negative quantity throws ShopifyMapperError", () => {
    assert.throws(
      () =>
        mapPushRequestToPlan({
          sku: "X",
          platformProjectedQty: -1,
          mapping: { shopify_inventory_item_id: "gid://shopify/InventoryItem/1" },
          syncState: { last_pushed_available: 0 },
          locationId: "gid://shopify/Location/1",
          runId: "00000000-0000-0000-0000-000000000001",
          traceId: "t",
          quantityName: "available",
          reason: "correction",
        }),
      ShopifyMapperError
    );
  });

  test("first-push (last_pushed_available=null) throws ShopifyMapperError", () => {
    assert.throws(
      () =>
        mapPushRequestToPlan({
          sku: "X",
          platformProjectedQty: 5,
          mapping: { shopify_inventory_item_id: "gid://shopify/InventoryItem/1" },
          syncState: { last_pushed_available: null },
          locationId: "gid://shopify/Location/1",
          runId: "00000000-0000-0000-0000-000000000001",
          traceId: "t",
          quantityName: "available",
          reason: "correction",
        }),
      ShopifyMapperError
    );
  });

  test("first-push on_hand (last_pushed_on_hand undefined) throws", () => {
    assert.throws(
      () =>
        mapPushRequestToPlan({
          sku: "X",
          platformProjectedQty: 5,
          mapping: { shopify_inventory_item_id: "gid://shopify/InventoryItem/1" },
          syncState: { last_pushed_available: 10 },
          locationId: "gid://shopify/Location/1",
          runId: "00000000-0000-0000-0000-000000000001",
          traceId: "t",
          quantityName: "on_hand",
          reason: "correction",
        }),
      ShopifyMapperError
    );
  });
});

/* ---------------------------------------------------------------------- *
 * mapInventoryLevelToReconciliationRow
 * ---------------------------------------------------------------------- */

describe("mapInventoryLevelToReconciliationRow", () => {
  const raw = loadFixture("inventory-level-read--single-location.json");
  const level = InventoryLevelSchema.parse(raw);

  test("extracts SKU from embedded item", () => {
    const row = mapInventoryLevelToReconciliationRow(level, "2026-04-17T00:00:00Z");
    assert.equal(row.sku, "GT-HIB-LOW-1L");
  });

  test("extracts inventoryItemId from embedded item", () => {
    const row = mapInventoryLevelToReconciliationRow(level, "2026-04-17T00:00:00Z");
    assert.equal(row.shopifyInventoryItemId, level.item.id);
  });

  test("extracts available quantity", () => {
    const row = mapInventoryLevelToReconciliationRow(level, "2026-04-17T00:00:00Z");
    assert.equal(row.availableQty, 50);
  });

  test("extracts on_hand quantity", () => {
    const row = mapInventoryLevelToReconciliationRow(level, "2026-04-17T00:00:00Z");
    assert.equal(row.onHandQty, 50);
  });

  test("propagates observedAt verbatim", () => {
    const ts = "2026-04-17T00:00:00Z";
    const row = mapInventoryLevelToReconciliationRow(level, ts);
    assert.equal(row.observedAt, ts);
  });
});

/* ---------------------------------------------------------------------- *
 * classifyDrift
 * ---------------------------------------------------------------------- */

describe("classifyDrift", () => {
  const baseRow = {
    shopifyInventoryItemId: "gid://shopify/InventoryItem/1",
    sku: "GT-HIB-LOW-1L",
    locationId: "gid://shopify/Location/1",
    locationIsActive: true,
    availableQty: 50,
    onHandQty: 50,
    observedAt: "2026-04-17T00:00:00Z",
  };

  test("matching values -> match", () => {
    const v = classifyDrift({ platformProjectedQty: 50, row: baseRow });
    assert.equal(v.kind, "match");
  });

  test("platform higher than Shopify -> drift with positive delta", () => {
    const v = classifyDrift({ platformProjectedQty: 55, row: baseRow });
    assert.equal(v.kind, "drift");
    if (v.kind === "drift") {
      assert.equal(v.delta, 5);
      assert.equal(v.platformQty, 55);
      assert.equal(v.shopifyQty, 50);
      assert.equal(v.exceptionCode, "shopify_inventory_drift");
    }
  });

  test("platform lower than Shopify -> drift with negative delta", () => {
    const v = classifyDrift({ platformProjectedQty: 48, row: baseRow });
    assert.equal(v.kind, "drift");
    if (v.kind === "drift") {
      assert.equal(v.delta, -2);
    }
  });

  test("inactive location dominates -> location_inactive", () => {
    const v = classifyDrift({
      platformProjectedQty: 50,
      row: { ...baseRow, locationIsActive: false },
    });
    assert.equal(v.kind, "location_inactive");
    if (v.kind === "location_inactive") {
      assert.equal(v.exceptionCode, "shopify_location_inactive");
    }
  });

  test("null platformProjectedQty -> shopify_unmapped_on_platform", () => {
    const v = classifyDrift({ platformProjectedQty: null, row: baseRow });
    assert.equal(v.kind, "shopify_unmapped_on_platform");
    if (v.kind === "shopify_unmapped_on_platform") {
      assert.equal(v.exceptionCode, "shopify_sku_unmapped");
    }
  });

  test("availableQty null treated as 0 for diff baseline", () => {
    const v = classifyDrift({
      platformProjectedQty: 10,
      row: { ...baseRow, availableQty: null },
    });
    assert.equal(v.kind, "drift");
    if (v.kind === "drift") {
      assert.equal(v.shopifyQty, 0);
      assert.equal(v.delta, 10);
    }
  });
});
