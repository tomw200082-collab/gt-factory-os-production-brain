/**
 * Mirror upsert shapes — the shape the fetcher produces for Window 1's
 * eventual mirror tables.
 *
 * These are Zod schemas representing the PROPOSED mirror column shapes
 * from window4-lionwheel-runtime-handoff.md §B. They are not DDL.
 * Window 1 is the sole authority on the final table shapes and will
 * finalize types, constraints, and indexes when authoring migrations.
 *
 * The fetcher interface (fetcher.ts) returns values of these types.
 * Window 1 migrations, when authored, must be satisfiable by instances
 * of these shapes — that's the contract this file enforces.
 *
 * Invariants:
 *   - `order_total`, `quantity`, `price`, `weight` remain strings
 *     (string-decimal preservation; parse at read time, never at write).
 *   - `raw_payload` carries the full upstream object unmodified, for
 *     schema-drift resilience and late-promotion of fields without re-pull.
 *   - `mirror_source_watermark` is the upstream `updated_at` snapshot at
 *     ingest; Window 1's upsert WHERE clause uses this to guarantee
 *     order-independent convergence (runtime handoff §B.8).
 */

import { z } from "zod";

/** Terminal task statuses (contract pack §B.8 + §B.10 retirement rule). */
export const TERMINAL_TASK_STATUSES = [
  "COMPLETED",
  "CANCELED",
  "FINAL_FAILED",
  "ROUNDTRIP_DELIVERED",
] as const;

export function isTerminalStatus(status: string): boolean {
  return (TERMINAL_TASK_STATUSES as readonly string[]).includes(status);
}

/* ---------------------------------------------------------------------- *
 * lw_task upsert shape — runtime handoff §B.2
 * ---------------------------------------------------------------------- */

export const LwTaskUpsertSchema = z.object({
  id: z.number().int(),
  public_id: z.string(),
  organization_id: z.number().int(),
  company_id: z.number().int(),

  status: z.string(),
  pick_status: z.string(),
  roundtrip_status: z.string(),
  urgency: z.string(),

  is_roundtrip: z.boolean(),
  same_day: z.boolean(),
  is_terminal: z.boolean(),

  /** NON-UNIQUE in the mirror index. Split orders share wp_order_id. */
  wp_order_id: z.string(),
  wp_order_key: z.string().nullable(),
  creation_origin: z.string(),
  creation_trigger: z.string(),
  driver_id: z.number().int().nullable(),
  packages_quantity: z.number().int(),

  pickup_at: z.string(),
  completed_at: z.string().nullable(),
  wp_order_at: z.string().nullable(),
  created_at_upstream: z.string(),
  updated_at_upstream: z.string(),

  /** string-decimal; parse at read time, not here */
  order_total: z.string().nullable(),

  notes: z.string().nullable(),
  org_note: z.string().nullable(),
  driver_note: z.string().nullable(),

  /** full /tasks/show response body for this task; schema-drift resilience */
  raw_payload: z.unknown(),

  /** mirror_source_watermark = updated_at_upstream snapshot at ingest */
  mirror_source_watermark: z.string(),
});
export type LwTaskUpsert = z.infer<typeof LwTaskUpsertSchema>;

/* ---------------------------------------------------------------------- *
 * lw_visit upsert shape — runtime handoff §B.3
 * ---------------------------------------------------------------------- */

export const LwVisitUpsertSchema = z.object({
  id: z.number().int(),
  task_id: z.number().int(),
  route_id: z.number().int().nullable(),
  organization_id: z.number().int().optional(),
  company_id: z.number().int().optional(),
  driver_id: z.number().int().nullable(),

  kind: z.string(),
  is_done: z.boolean(),

  visit_at: z.string(),
  delivered_at: z.string().nullable(),
  failed_at: z.string().nullable(),
  failure_reason: z.string().nullable(),

  recipient_name: z.string().nullable(),
  phone: z.string(),
  phone2: z.string().optional(),
  email: z.string().optional(),

  city: z.string(),
  street: z.string().optional(),
  number: z.string().optional(),
  apartment: z.string().optional(),
  floor: z.string().optional(),
  zip_code: z.string().nullable().optional(),

  latitude: z.number(),
  longitude: z.number(),
  delivery_latitude: z.number().nullable(),
  delivery_longitude: z.number().nullable(),

  packages_quantity: z.number().int(),
  notes: z.string().nullable(),

  created_at_upstream: z.string().optional(),
  updated_at_upstream: z.string().optional(),

  raw_payload: z.unknown(),
  mirror_source_watermark: z.string().optional(),
});
export type LwVisitUpsert = z.infer<typeof LwVisitUpsertSchema>;

/* ---------------------------------------------------------------------- *
 * lw_order_item upsert shape — runtime handoff §B.4
 * ---------------------------------------------------------------------- */

export const LwOrderItemUpsertSchema = z.object({
  id: z.number().int(),
  task_id: z.number().int(),
  sku: z.string(),
  name: z.string(),

  /**
   * Stored as text pending G.1 resolution; preserves string-decimal.
   * Nullable because upstream `order_item.quantity` is declared optional
   * in OrderItemSchema (G.1 unresolved) — the mapper emits null when the
   * field is absent rather than guessing a default.
   */
  quantity: z.string().nullable(),
  price: z.string().nullable(),
  variant: z.string().nullable(),
  weight: z.string().nullable(),
  notes: z.string().nullable(),

  raw_payload: z.unknown(),
});
export type LwOrderItemUpsert = z.infer<typeof LwOrderItemUpsertSchema>;

/* ---------------------------------------------------------------------- *
 * Composite result of a /tasks/show fetch, ready to upsert atomically.
 * The fetcher returns this shape; Window 1's upsert layer consumes it.
 * ---------------------------------------------------------------------- */

export const TaskFetchResultSchema = z.object({
  task: LwTaskUpsertSchema,
  visits: z.array(LwVisitUpsertSchema),
  order_items: z.array(LwOrderItemUpsertSchema),
});
export type TaskFetchResult = z.infer<typeof TaskFetchResultSchema>;

/* ---------------------------------------------------------------------- *
 * integration_run record shape — runtime handoff §B.5
 *
 * The fetcher does not insert integration_run rows directly; that's the
 * job of the runtime host (Window 1 migration + Window 4 runtime wrapper).
 * This shape is exported so the future wrapper has a typed target.
 * ---------------------------------------------------------------------- */

export const IntegrationRunStatusSchema = z.enum([
  "pending",
  "running",
  "succeeded",
  "partial",
  "failed",
  "superseded",
]);
export type IntegrationRunStatus = z.infer<typeof IntegrationRunStatusSchema>;

export const IntegrationRunKindSchema = z.enum([
  "task_refresh",
  "routes_sweep",
  "webhook_ingest",
  "reconciliation_pass",
]);
export type IntegrationRunKind = z.infer<typeof IntegrationRunKindSchema>;

export const IntegrationRunTriggerSchema = z.enum([
  "manual",
  "scheduler",
  "webhook",
  "reconciliation_job",
  "kill_switch",
]);
export type IntegrationRunTrigger = z.infer<typeof IntegrationRunTriggerSchema>;

export const IntegrationRunErrorClassSchema = z.enum([
  "auth",
  "not_found",
  "rate_limit",
  "network_timeout",
  "schema_drift",
  "partial_payload",
  "unknown",
]);
export type IntegrationRunErrorClass = z.infer<typeof IntegrationRunErrorClassSchema>;

export const IntegrationRunRecordSchema = z.object({
  id: z.string().uuid(),
  integration: z.literal("lionwheel"),
  run_kind: IntegrationRunKindSchema,
  status: IntegrationRunStatusSchema,
  started_at: z.string(),
  finished_at: z.string().nullable(),
  duration_ms: z.number().int().nullable(),
  records_attempted: z.number().int(),
  records_upserted: z.number().int(),
  records_skipped_stale: z.number().int(),
  records_retired: z.number().int(),
  records_failed: z.number().int(),
  error_class: IntegrationRunErrorClassSchema.nullable(),
  /** MUST NOT contain the LionWheel token; redact before write */
  error_detail: z.unknown().nullable(),
  request_watermark_from: z.string().nullable(),
  request_watermark_to: z.string().nullable(),
  sweep_date: z.string().nullable(),
  trigger_source: IntegrationRunTriggerSchema,
  trace_id: z.string(),
  evidence_sample: z.unknown().nullable(),
  endpoint: z.string(),
  upstream_task_ids: z.array(z.number().int()).nullable(),
});
export type IntegrationRunRecord = z.infer<typeof IntegrationRunRecordSchema>;
