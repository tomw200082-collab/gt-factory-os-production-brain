/**
 * Shopify Admin GraphQL schemas relevant to FG sync.
 *
 * Every field traces to one of:
 *   - shopify.dev/docs/api/admin-graphql/latest/mutations/inventorySetQuantities
 *   - shopify.dev/docs/api/admin-graphql/latest/input-objects/InventoryQuantityInput
 *   - shopify.dev/docs/api/admin-graphql/latest/objects/InventoryLevel
 *   - well-documented Shopify public patterns for InventoryItem, Location,
 *     InventoryQuantity, and UserError (not re-verified verbatim this pass;
 *     schemas are permissive via .passthrough() so real responses parse
 *     cleanly even with additional fields)
 *
 * No field name is invented. UNRESOLVED items are explicitly labelled.
 *
 * Boundary rule distinct from LionWheel/Green Invoice: Shopify quantities
 * are Int (native numeric), NOT string-decimal. Quantities type as
 * `z.number().int()`. The platform FG projection is integer-valued.
 */

import { z } from "zod";

/* ---------------------------------------------------------------------- *
 * Quantity name enum.
 *
 * Shopify docs explicitly list "available" and "on_hand" as names
 * SETTABLE via inventorySetQuantities. Additional names (incoming,
 * committed, reserved, damaged, safety_stock, quality_control) appear
 * in Shopify inventory-state docs but are typically READ-ONLY / derived;
 * the v1 GT FG sync sets only "available" (and optionally "on_hand").
 * ---------------------------------------------------------------------- */

export const InventorySetQuantityNameSchema = z.enum(["available", "on_hand"]);
export type InventorySetQuantityName = z.infer<typeof InventorySetQuantityNameSchema>;

/**
 * Open enum for READ paths (reconciliation) — accepts any name Shopify
 * returns. Runtime wrapper logs novel values for later lock.
 */
export const InventoryStateNameSchema = z.string();

/* ---------------------------------------------------------------------- *
 * InventoryQuantityInput — input object for inventorySetQuantities.
 *
 * Verbatim fields: inventoryItemId, locationId, quantity, compareQuantity,
 * changeFromQuantity (2026-01+).
 * ---------------------------------------------------------------------- */

export const InventoryQuantityInputSchema = z.object({
  /** Shopify InventoryItem GID, e.g. "gid://shopify/InventoryItem/12345" */
  inventoryItemId: z.string().min(1),
  /** Shopify Location GID */
  locationId: z.string().min(1),
  /** Absolute integer quantity. v1 rejects negative at the mapper layer. */
  quantity: z.number().int(),
  /**
   * Required when ignoreCompareQuantity=false (v1 default).
   * Shopify refuses the mutation unless persisted quantity == compareQuantity.
   */
  compareQuantity: z.number().int().nullable().optional(),
  /**
   * Alternative to compareQuantity, added in API version 2026-01+.
   * Not used in v1 (platform prefers absolute-set with compareQuantity).
   */
  changeFromQuantity: z.number().int().optional(),
});
export type InventoryQuantityInput = z.infer<typeof InventoryQuantityInputSchema>;

/* ---------------------------------------------------------------------- *
 * InventorySetQuantitiesInput — outer input object.
 *
 * Verbatim fields: name, reason, referenceDocumentUri, ignoreCompareQuantity,
 * quantities.
 * ---------------------------------------------------------------------- */

export const InventorySetQuantitiesInputSchema = z.object({
  name: InventorySetQuantityNameSchema,
  /**
   * Required string. Docs show "correction" as an example value; the
   * full reason enum is UNRESOLVED this pass. Runtime should log any
   * novel value so the enum can be locked without re-authoring.
   */
  reason: z.string().min(1),
  /** URI back to the platform `integration_run.id` for audit. */
  referenceDocumentUri: z.string().optional(),
  /** v1 default: false. Setting true bypasses compare-and-set safety. */
  ignoreCompareQuantity: z.boolean().optional(),
  quantities: z.array(InventoryQuantityInputSchema).min(1),
});
export type InventorySetQuantitiesInput = z.infer<typeof InventorySetQuantitiesInputSchema>;

/* ---------------------------------------------------------------------- *
 * InventoryQuantity (read-side element of InventoryLevel.quantities).
 *
 * The typical public shape is { name, quantity, updatedAt }. Not
 * re-verified verbatim this pass; schema is permissive.
 * ---------------------------------------------------------------------- */

export const InventoryQuantitySchema = z.object({
  name: InventoryStateNameSchema,
  quantity: z.number().int(),
  updatedAt: z.string().optional(),
}).passthrough();
export type InventoryQuantity = z.infer<typeof InventoryQuantitySchema>;

/* ---------------------------------------------------------------------- *
 * InventoryItem (minimal shape for SKU mapping).
 *
 * Confidently-public fields: id, sku. Additional fields (tracked,
 * countryCodeOfOrigin, variant, harmonizedSystemCode) preserved via
 * .passthrough() rather than asserted verbatim this pass.
 * ---------------------------------------------------------------------- */

export const InventoryItemSchema = z.object({
  id: z.string().min(1),
  /** Nullable — Shopify permits items without SKU in some configurations. */
  sku: z.string().nullable().optional(),
}).passthrough();
export type InventoryItem = z.infer<typeof InventoryItemSchema>;

/* ---------------------------------------------------------------------- *
 * Location (minimal).
 *
 * Confidently-public fields: id, name, isActive. GT FG sync requires at
 * minimum id + isActive (§B.6 conflict rule: shopify_location_inactive
 * halts sync).
 * ---------------------------------------------------------------------- */

export const LocationSchema = z.object({
  id: z.string().min(1),
  name: z.string().optional(),
  isActive: z.boolean().optional(),
}).passthrough();
export type Location = z.infer<typeof LocationSchema>;

/* ---------------------------------------------------------------------- *
 * InventoryLevel — primary read object for reconciliation.
 *
 * Verbatim fields: id, canDeactivate, createdAt, deactivationAlert,
 * isActive, item, location, quantities, updatedAt, scheduledChanges.
 * ---------------------------------------------------------------------- */

export const InventoryLevelSchema = z.object({
  id: z.string().min(1),
  canDeactivate: z.boolean(),
  createdAt: z.string(),
  deactivationAlert: z.string().nullable().optional(),
  isActive: z.boolean(),
  item: InventoryItemSchema,
  location: LocationSchema,
  quantities: z.array(InventoryQuantitySchema),
  updatedAt: z.string(),
  /**
   * scheduledChanges connection exists per docs; inner fields UNRESOLVED
   * this pass. Preserved as unknown so parse does not fail when present.
   */
  scheduledChanges: z.unknown().optional(),
}).passthrough();
export type InventoryLevel = z.infer<typeof InventoryLevelSchema>;

/* ---------------------------------------------------------------------- *
 * UserError (post-mutation error envelope).
 *
 * Shopify's standard UserError shape across GraphQL mutations is
 * { field, message, code }. Exact shape for inventorySetQuantities not
 * re-verified verbatim this pass. Schema requires `message` (always
 * present on any UserError) and optional field/code; additional fields
 * survive via passthrough.
 * ---------------------------------------------------------------------- */

export const ShopifyUserErrorSchema = z.object({
  message: z.string(),
  field: z.array(z.string()).nullable().optional(),
  code: z.string().nullable().optional(),
}).passthrough();
export type ShopifyUserError = z.infer<typeof ShopifyUserErrorSchema>;
