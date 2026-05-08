/**
 * Platform-side shapes for Shopify FG sync.
 *
 * These are proposals for Window 1 to consume when/if it takes up the
 * Shopify migrations AFTER Gate 3 closes. Window 1 is NOT queued for
 * this work in the current cycle — Window 1 stays focused on Gate 3.
 * The shapes below exist so the mapper, fetcher, and eventual runtime
 * wrapper have typed targets.
 *
 * See window4-shopify-greeninvoice-contract-pack.md §B.9 for rationale.
 */

import { z } from "zod";
import { InventorySetQuantitiesInputSchema } from "./api-schemas.js";

/* ---------------------------------------------------------------------- *
 * integration_run extension enums (reused table; Window 1's eventual
 * CHECK-constraint migration applies these values — no new table here).
 * ---------------------------------------------------------------------- */

export const ShopifyRunKindSchema = z.enum([
  "shopify_sku_push",
  "shopify_sku_reconciliation",
]);
export type ShopifyRunKind = z.infer<typeof ShopifyRunKindSchema>;

export const ShopifyErrorClassSchema = z.enum([
  "auth",
  "shopify_compare_mismatch",
  "shopify_location_inactive",
  "shopify_sku_unmapped",
  "shopify_inventory_drift",
  "rate_limit",
  "network_timeout",
  "schema_drift",
  "partial_payload",
  "unknown",
]);
export type ShopifyErrorClass = z.infer<typeof ShopifyErrorClassSchema>;

/* ---------------------------------------------------------------------- *
 * Push request — what the runtime wrapper hands the mapper per SKU.
 * ---------------------------------------------------------------------- */

export const PushQuantityRequestSchema = z.object({
  /** Platform items.sku. Non-empty. */
  sku: z.string().min(1),
  /**
   * Authoritative FG quantity from the platform projection.
   * Integer; FG stock is whole units. Must be >= 0; mapper enforces.
   */
  platformProjectedQty: z.number().int().nonnegative(),
  /** Shopify mapping row, pre-resolved by the runtime wrapper. */
  mapping: z.object({
    shopify_inventory_item_id: z.string().min(1),
    shopify_variant_id: z.string().nullable().optional(),
  }),
  /**
   * Last values the platform successfully pushed for this SKU at this
   * location. `last_pushed_available === null` iff this is the first-ever
   * push; mapper refuses to emit a plan in that case and forces the
   * runtime wrapper to do a read first.
   */
  syncState: z.object({
    last_pushed_available: z.number().int().nullable(),
    last_pushed_on_hand: z.number().int().nullable().optional(),
  }),
  /** Authoritative FG location GID. */
  locationId: z.string().min(1),
  /** integration_run.id this push is part of. */
  runId: z.string().uuid(),
  /** Correlation id for logs. */
  traceId: z.string().min(1),
  /** v1 default "available". "on_hand" opt-in by operator. */
  quantityName: z.enum(["available", "on_hand"]),
  /** Required on the Shopify mutation; default "correction". */
  reason: z.string().min(1).default("correction"),
  /** Optional URI back to the platform's integration_run for audit. */
  referenceDocumentUri: z.string().optional(),
});
export type PushQuantityRequest = z.infer<typeof PushQuantityRequestSchema>;

/* ---------------------------------------------------------------------- *
 * Push plan — the mapper's output; the fetcher's input.
 *
 * Bundles the mutation input with the idempotency key derivation so the
 * fetcher has one object that fully describes the call it should make.
 * ---------------------------------------------------------------------- */

export const ShopifyPushPlanSchema = z.object({
  input: InventorySetQuantitiesInputSchema,
  /**
   * Deterministic key applied via the @idempotent directive (required at
   * API version 2026-04+). Derived from (runId, inventoryItemId,
   * locationId) so retries of the same logical push carry the same key.
   */
  idempotencyKey: z.string().min(1),
  auditReference: z.string().optional(),
});
export type ShopifyPushPlan = z.infer<typeof ShopifyPushPlanSchema>;

/* ---------------------------------------------------------------------- *
 * Reconciliation row — per-SKU-per-location result of the read path.
 * ---------------------------------------------------------------------- */

export const ShopifyReconciliationRowSchema = z.object({
  shopifyInventoryItemId: z.string().min(1),
  /** Join key to platform items.sku. Null allowed per Shopify semantics. */
  sku: z.string().nullable(),
  locationId: z.string().min(1),
  locationIsActive: z.boolean().optional(),
  availableQty: z.number().int().nullable(),
  onHandQty: z.number().int().nullable(),
  observedAt: z.string(),
});
export type ShopifyReconciliationRow = z.infer<typeof ShopifyReconciliationRowSchema>;

/* ---------------------------------------------------------------------- *
 * Drift verdict — produced by classifyDrift(platformQty, row).
 *
 * Discriminated by `kind`. `match` is the clean case; the three failure
 * kinds each carry the exception code that routes them to the Exceptions
 * Inbox (contract pack §E).
 * ---------------------------------------------------------------------- */

export const ShopifyDriftVerdictSchema = z.discriminatedUnion("kind", [
  z.object({ kind: z.literal("match") }),
  z.object({
    kind: z.literal("drift"),
    delta: z.number().int(),
    platformQty: z.number().int(),
    shopifyQty: z.number().int(),
    exceptionCode: z.literal("shopify_inventory_drift"),
  }),
  z.object({
    kind: z.literal("shopify_unmapped_on_platform"),
    exceptionCode: z.literal("shopify_sku_unmapped"),
  }),
  z.object({
    kind: z.literal("location_inactive"),
    exceptionCode: z.literal("shopify_location_inactive"),
  }),
]);
export type ShopifyDriftVerdict = z.infer<typeof ShopifyDriftVerdictSchema>;
