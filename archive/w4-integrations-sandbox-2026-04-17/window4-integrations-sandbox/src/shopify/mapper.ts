/**
 * Pure mappers for the Shopify FG-sync boundary.
 *
 * Three concerns, all pure:
 *   1. push path: PushQuantityRequest -> ShopifyPushPlan
 *      (produces the InventorySetQuantitiesInput the fetcher will call
 *       with, plus a deterministic idempotency key)
 *   2. read path: InventoryLevel -> ShopifyReconciliationRow
 *      (extracts SKU + available/on_hand quantities for drift detection)
 *   3. drift path: (platformQty, row) -> ShopifyDriftVerdict
 *      (classifies a pair into match / drift / location_inactive /
 *       shopify_unmapped_on_platform with the right exception code)
 *
 * Invariants enforced at the mapper layer (not configurable):
 *   - platformProjectedQty >= 0 (throws on negative)
 *   - first-push compareQuantity is unresolved (throws, forcing the
 *     runtime wrapper to perform an InventoryLevel read first)
 *   - ignoreCompareQuantity is always false in v1
 *   - Shopify quantities are integer — no string-decimal coercion
 *
 * No I/O. No HTTP. Callable today from tests and the CLI skeleton.
 */

import type { InventoryLevel, InventorySetQuantitiesInput } from "./api-schemas.js";
import type {
  PushQuantityRequest,
  ShopifyDriftVerdict,
  ShopifyPushPlan,
  ShopifyReconciliationRow,
} from "./mirror-shapes.js";

/* ---------------------------------------------------------------------- *
 * Push: PushQuantityRequest -> ShopifyPushPlan
 * ---------------------------------------------------------------------- */

export function mapPushRequestToPlan(req: PushQuantityRequest): ShopifyPushPlan {
  if (req.platformProjectedQty < 0) {
    throw new ShopifyMapperError(
      `platformProjectedQty must be >= 0 for sku=${req.sku} (got ${req.platformProjectedQty})`
    );
  }

  const compareQuantity =
    req.quantityName === "on_hand"
      ? (req.syncState.last_pushed_on_hand ?? null)
      : req.syncState.last_pushed_available;

  if (compareQuantity === null || compareQuantity === undefined) {
    throw new ShopifyMapperError(
      `first-push compareQuantity unresolved for sku=${req.sku} at location=${req.locationId}; ` +
        `runtime wrapper must perform an InventoryLevel read before mapping`
    );
  }

  const input: InventorySetQuantitiesInput = {
    name: req.quantityName,
    reason: req.reason,
    referenceDocumentUri: req.referenceDocumentUri,
    ignoreCompareQuantity: false,
    quantities: [
      {
        inventoryItemId: req.mapping.shopify_inventory_item_id,
        locationId: req.locationId,
        quantity: req.platformProjectedQty,
        compareQuantity,
      },
    ],
  };

  return {
    input,
    idempotencyKey: deriveIdempotencyKey({
      runId: req.runId,
      inventoryItemId: req.mapping.shopify_inventory_item_id,
      locationId: req.locationId,
    }),
    auditReference: req.referenceDocumentUri,
  };
}

/**
 * Deterministic idempotency key for the @idempotent directive.
 *
 * Same logical push = same key (safe to retry at the transport layer).
 * A retry after compare-mismatch is a NEW logical push (new runId) and
 * therefore gets a NEW key — which is the intended behavior.
 */
export function deriveIdempotencyKey(params: {
  runId: string;
  inventoryItemId: string;
  locationId: string;
}): string {
  return `gt:${params.runId}:${params.inventoryItemId}:${params.locationId}`;
}

/* ---------------------------------------------------------------------- *
 * Read: InventoryLevel -> ShopifyReconciliationRow
 * ---------------------------------------------------------------------- */

export function mapInventoryLevelToReconciliationRow(
  level: InventoryLevel,
  observedAt: string
): ShopifyReconciliationRow {
  return {
    shopifyInventoryItemId: level.item.id,
    sku: level.item.sku ?? null,
    locationId: level.location.id,
    locationIsActive: level.location.isActive,
    availableQty: findQuantity(level, "available"),
    onHandQty: findQuantity(level, "on_hand"),
    observedAt,
  };
}

function findQuantity(level: InventoryLevel, name: string): number | null {
  for (const q of level.quantities) {
    if (q.name === name) return q.quantity;
  }
  return null;
}

/* ---------------------------------------------------------------------- *
 * Drift: (platformQty, row) -> ShopifyDriftVerdict
 *
 * Order of checks matters — inactive location dominates (sync is halted
 * regardless of values), then the unmapped-on-platform case, then the
 * match/drift comparison.
 * ---------------------------------------------------------------------- */

export function classifyDrift(params: {
  platformProjectedQty: number | null;
  row: ShopifyReconciliationRow;
}): ShopifyDriftVerdict {
  const { platformProjectedQty, row } = params;

  if (row.locationIsActive === false) {
    return { kind: "location_inactive", exceptionCode: "shopify_location_inactive" };
  }

  if (platformProjectedQty === null || platformProjectedQty === undefined) {
    return {
      kind: "shopify_unmapped_on_platform",
      exceptionCode: "shopify_sku_unmapped",
    };
  }

  const shopifyQty = row.availableQty ?? 0;
  if (platformProjectedQty === shopifyQty) return { kind: "match" };

  return {
    kind: "drift",
    delta: platformProjectedQty - shopifyQty,
    platformQty: platformProjectedQty,
    shopifyQty,
    exceptionCode: "shopify_inventory_drift",
  };
}

/* ---------------------------------------------------------------------- *
 * Mapper-internal error (distinct from fetcher-level FetchResult errors).
 * ---------------------------------------------------------------------- */

export class ShopifyMapperError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ShopifyMapperError";
  }
}
