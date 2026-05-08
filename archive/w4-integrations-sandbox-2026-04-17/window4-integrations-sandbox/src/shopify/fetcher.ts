/**
 * Shopify fetcher interface.
 *
 * Contract between the future runtime wrapper (CLI, scheduler) and the
 * fetcher implementation. NO IMPLEMENTATION IN THIS FILE.
 *
 * Design notes:
 *   - Errors surface as typed FetchResult variants, not thrown exceptions
 *   - isEnabled() kill switch is checked at every entry; false short-
 *     circuits to `disabled_by_kill_switch` without HTTP
 *   - Runtime implementation is BLOCKED on:
 *       - Gate 3 closure
 *       - Window 1 Shopify migrations (queued only after Gate 3)
 *       - Shopify Admin API token provisioning (outside current cycle scope)
 */

import { z } from "zod";
import type { InventoryLevel, ShopifyUserError } from "./api-schemas.js";
import type { ShopifyErrorClass, ShopifyPushPlan } from "./mirror-shapes.js";

/* ---------------------------------------------------------------------- *
 * FetchResult discriminated union.
 * ---------------------------------------------------------------------- */

export type FetchResult<T> =
  | { kind: "ok"; value: T }
  | { kind: "auth_error"; endpoint: string; traceId: string; body: unknown }
  | {
      kind: "user_errors";
      endpoint: string;
      traceId: string;
      userErrors: ShopifyUserError[];
    }
  | {
      kind: "compare_mismatch";
      endpoint: string;
      traceId: string;
      userErrors: ShopifyUserError[];
    }
  | {
      kind: "rate_limit";
      endpoint: string;
      traceId: string;
      retryAfterSeconds: number | null;
    }
  | {
      kind: "network_timeout";
      endpoint: string;
      traceId: string;
      timeoutMs: number;
    }
  | {
      kind: "schema_drift";
      endpoint: string;
      traceId: string;
      zodIssues: z.ZodIssue[];
    }
  | { kind: "disabled_by_kill_switch"; endpoint: string; traceId: string }
  | { kind: "unknown_error"; endpoint: string; traceId: string; cause: unknown };

/** Map a non-ok FetchResult to the ShopifyErrorClass vocabulary. */
export function errorClassOf<T>(
  result: Exclude<FetchResult<T>, { kind: "ok" }>
): ShopifyErrorClass {
  switch (result.kind) {
    case "auth_error":
      return "auth";
    case "compare_mismatch":
      return "shopify_compare_mismatch";
    case "user_errors":
      return "unknown";
    case "rate_limit":
      return "rate_limit";
    case "network_timeout":
      return "network_timeout";
    case "schema_drift":
      return "schema_drift";
    case "disabled_by_kill_switch":
      // runtime wrapper records status='superseded' rather than error for
      // this case; ShopifyErrorClass still needs a stable bucket for the
      // error_class column when it IS written.
      return "unknown";
    case "unknown_error":
      return "unknown";
  }
}

/* ---------------------------------------------------------------------- *
 * Push success shape returned on `ok` for pushInventorySet.
 * ---------------------------------------------------------------------- */

export interface ShopifyPushSuccess {
  /** Shopify inventoryAdjustmentGroup id if returned; UNRESOLVED exact field path. */
  adjustmentGroupId?: string;
  /** Shopify's post-set quantity value. */
  resultingQuantity: number;
  /** What the runtime wrapper will persist as the new last_pushed_* value. */
  lastPushedValue: number;
}

/* ---------------------------------------------------------------------- *
 * Fetcher configuration.
 * ---------------------------------------------------------------------- */

export interface ShopifyFetcherConfig {
  /** Shop domain, e.g. "gteveryday.myshopify.com" */
  readonly shopDomain: string;
  /**
   * API version. 2026-04 is the minimum for required @idempotent
   * directive usage; older versions would let the runtime skip
   * idempotency silently.
   */
  readonly apiVersion: string;
  /**
   * Admin API access token. Injected via runtime env; never appears in
   * logs or error bodies.
   */
  readonly apiToken: string;
  readonly requestTimeoutMs: number;
  /** Kill switch. false => short-circuit with disabled_by_kill_switch. */
  readonly isEnabled: () => boolean;
}

/* ---------------------------------------------------------------------- *
 * Fetcher interface.
 * ---------------------------------------------------------------------- */

export interface ShopifyFetcher {
  /**
   * Execute a ShopifyPushPlan via the inventorySetQuantities mutation,
   * applying @idempotent with plan.idempotencyKey.
   */
  pushInventorySet(
    plan: ShopifyPushPlan,
    options: FetchOptions
  ): Promise<FetchResult<ShopifyPushSuccess>>;

  /**
   * Paginated read of InventoryLevels at a location. Consumed by the
   * reconciliation pass (Slice S2, not Slice S1).
   */
  readInventoryLevelsForLocation(
    locationId: string,
    options: FetchOptions
  ): Promise<FetchResult<InventoryLevel[]>>;

  /**
   * Resolve a Shopify InventoryItem GID by SKU. Used by the mapping-
   * population flow (Slice S3, not Slice S1).
   */
  resolveInventoryItemIdBySku(
    sku: string,
    options: FetchOptions
  ): Promise<FetchResult<{ inventoryItemId: string }>>;
}

export interface FetchOptions {
  readonly traceId: string;
}
