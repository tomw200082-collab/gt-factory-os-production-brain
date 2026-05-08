/**
 * LionWheel API response schemas.
 *
 * Every field in this file traces to one of:
 *   - live inspection evidence captured in window4-lionwheel-contract-pack.md
 *     Appendix A (inspected)
 *   - official LionWheel docs referenced in the same pack (docs)
 *
 * No field name is invented. UNRESOLVED items are modelled as permissive
 * types with a contract-pack reference in the comment.
 *
 * Invariants preserved here (see contract pack §§B.6–B.7):
 *   - `order_total`, `order_items.price`, `order_items.quantity`,
 *     `order_items.weight` are string-decimal at the wire — accept them
 *     as strings (or numeric for `quantity` until G.1 resolves).
 *   - Open enums (`status`, `pick_status`, `urgency`, `route.status`,
 *     `visit.kind`, etc.) are `z.string()` with log-on-parse expected at
 *     the fetcher layer. See contract pack §G.2.
 *   - `.passthrough()` on task / visit / route preserves fields that are
 *     not promoted to structured mirror columns; the fetcher captures the
 *     full object as `raw_payload` at upsert time.
 */

import { z } from "zod";

/* ---------------------------------------------------------------------- *
 * Error envelope (observed verbatim on HTTP 401 and 404).
 * ---------------------------------------------------------------------- */

export const LionWheelErrorBodySchema = z.object({
  error: z.string(),
});
export type LionWheelErrorBody = z.infer<typeof LionWheelErrorBodySchema>;

/* ---------------------------------------------------------------------- *
 * order_item — embedded in task.order_items[]
 * Contract pack §B.7.
 * ---------------------------------------------------------------------- */

export const OrderItemSchema = z.object({
  id: z.number().int(),
  sku: z.string(),
  name: z.string(),
  variant: z.string().nullable().optional(),
  /**
   * UNRESOLVED (contract pack §G.1): live inspection was truncated before
   * `quantity` type was confirmed. Docs declare the field but not whether
   * it arrives as a string-decimal (matching `order_total`) or numeric.
   * Accept both; runtime must log when a novel shape appears so the lock
   * can be made later without re-pulling.
   */
  quantity: z.union([z.string(), z.number()]).optional(),
  /** string-decimal per docs; store verbatim */
  price: z.string().optional(),
  /** string-decimal per docs; store verbatim */
  weight: z.string().optional(),
  notes: z.string().nullable().optional(),
}).passthrough();
export type OrderItem = z.infer<typeof OrderItemSchema>;

/* ---------------------------------------------------------------------- *
 * visit — embedded in task.visits[] and in routes[].visits[]
 * Contract pack §B.5 (union of /routes and /tasks/show observations).
 * ---------------------------------------------------------------------- */

export const VisitSchema = z.object({
  id: z.number().int(),
  task_id: z.number().int(),
  route_id: z.number().int().nullable(),
  organization_id: z.number().int().optional(),
  company_id: z.number().int().optional(),
  driver_id: z.number().int().nullable(),

  /** UNRESOLVED enum (§G.2): observed "DELIVERY" only; "PICKUP" expected */
  kind: z.string(),
  is_done: z.boolean(),

  /** ISO-8601 with Israel timezone offset observed */
  visit_at: z.string(),
  delivered_at: z.string().nullable(),
  failed_at: z.string().nullable(),
  failure_reason: z.string().nullable(),

  created_at: z.string().optional(),
  updated_at: z.string().optional(),

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
}).passthrough();
/*
 * Fields intentionally not promoted here (preserved via .passthrough()):
 *   eta_at, eta_at_formatted, eta_window, early_eta_at, late_eta_at,
 *   earliest, latest, earliest_at, latest_at, earliest_latest_time,
 *   loaded_at, geo_provider, geo_type, geo_fence_id, matches_count,
 *   partial_match, location_id, location_cache_id, state, entrance,
 *   entrance_code, region_str, salary, salary_origin, priority, group,
 *   daily_order, color, route_locked, route_name, task_status,
 *   wp_order_id (as a convenience duplicate on the route-embedded form),
 *   any org-configured custom Hebrew-keyed fields (§G.8).
 */
export type Visit = z.infer<typeof VisitSchema>;

/* ---------------------------------------------------------------------- *
 * task — returned by /tasks/show (wrapped in { task: ... })
 *            and /tasks/by_order_id (wrapped in { tasks: [...] })
 * Contract pack §B.6.
 * ---------------------------------------------------------------------- */

export const TaskSchema = z.object({
  id: z.number().int(),
  public_id: z.string(),
  organization_id: z.number().int(),
  company_id: z.number().int(),

  /** UNRESOLVED enum completeness (§G.2); full list in §B.8. Store as string. */
  status: z.string(),
  /** UNRESOLVED enum (§G.2) */
  pick_status: z.string(),
  /** UNRESOLVED enum (§G.2) */
  roundtrip_status: z.string(),
  /** UNRESOLVED enum (§G.2) */
  urgency: z.string(),

  is_roundtrip: z.boolean(),
  same_day: z.boolean(),
  packages_quantity: z.number().int(),
  driver_id: z.number().int().nullable(),

  pickup_at: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  completed_at: z.string().nullable(),

  /** commerce-channel external id, primary GT-side business key; NON-UNIQUE */
  wp_order_id: z.string(),
  wp_order_key: z.string().nullable(),
  wp_order_at: z.string().nullable(),

  creation_origin: z.string(),
  creation_trigger: z.string(),

  /** string-decimal preserved verbatim */
  order_total: z.string().nullable(),

  notes: z.string().nullable(),
  org_note: z.string().nullable(),

  /**
   * May contain a credentialed Green Invoice signed-download URL (§G.12).
   * Mirror as-is. Do NOT dereference from the mirror layer — that belongs
   * to the future Green Invoice integration pack.
   */
  driver_note: z.string().nullable(),

  visits: z.array(VisitSchema),
  order_items: z.array(OrderItemSchema),
  photos: z.array(z.unknown()).optional(),
}).passthrough();
/*
 * Fields preserved via .passthrough(), NOT promoted to structured mirror
 * columns in Slice 1 (list per contract pack §B.6):
 *   signature_url, signature, signee_name, signed_document,
 *   price, fee_cost,
 *   all target_partner_*, origin_partner_*, transferred_at,
 *   transfer_errors, external_line_branch, external_distribution_line,
 *   money_collect, payment_method, money_transferred, money_transferred_at,
 *   age_verification, age_start_date, leave_next_to_door, is_self_pickup,
 *   is_free,
 *   validation_*, delivery_confirmation_*, confirmation_*,
 *   skills, failed_count, stop_time, wait_time, scheduled_template_id,
 *   sms_from_name, otp_code, extra_barcode, task_type, customer_user_agent,
 *   route_code, greeting, gifter_name, gifter_phone, source_order_id,
 *   due_date, earliest, latest, returned_pallets,
 *   batch_id, branch_id, warehouse_id, client_id, user_id, other_user,
 *   payer, printed_at, ready_to_print,
 *   document_number, document_type, invoice_id, distribution_id,
 *   weight, volume, cartons_quantity, surfaces_quantity.
 */
export type Task = z.infer<typeof TaskSchema>;

/* ---------------------------------------------------------------------- *
 * Response envelopes.
 * ---------------------------------------------------------------------- */

/** GET /tasks/show/:task_id */
export const TaskShowResponseSchema = z.object({
  task: TaskSchema,
});
export type TaskShowResponse = z.infer<typeof TaskShowResponseSchema>;

/**
 * GET /tasks/by_order_id/:order_id
 *
 * Returns an array even for a single match; supports multi-task-per-order
 * which is how split orders are represented (contract pack §B.10 split
 * semantics).
 */
export const TasksByOrderIdResponseSchema = z.object({
  tasks: z.array(TaskSchema),
});
export type TasksByOrderIdResponse = z.infer<typeof TasksByOrderIdResponseSchema>;

/* ---------------------------------------------------------------------- *
 * route — returned by /routes?date=YYYY-MM-DD&format=json
 * Contract pack §B.4.
 * ---------------------------------------------------------------------- */

export const RouteSchema = z.object({
  id: z.number().int(),
  /** note Hebrew date format "DD/MM/YYYY"; parse explicitly, not as ISO */
  date: z.string(),
  name: z.string(),

  driver_id: z.number().int().nullable(),
  driver_str: z.string().nullable(),

  /** UNRESOLVED enum (§G.2) — observed "planned" only */
  status: z.string(),

  is_locked: z.boolean(),
  start_time: z.string().nullable(),
  end_eta_at: z.string().nullable(),

  /** "225.74 KMs" form observed; use int_distance for meters */
  distance: z.string().optional(),
  int_distance: z.number().int().nullable(),

  polyline: z.string().nullable(),
  color: z.string().optional(),

  vehicle_id: z.number().int().nullable(),
  vehicle_str: z.string().nullable(),

  external_driver_id: z.string().optional(),
  notes: z.string().nullable(),
  assistant_driver_str: z.string().nullable(),

  /** visits embedded inline per observed /routes response shape */
  visits: z.array(VisitSchema),
}).passthrough();
export type Route = z.infer<typeof RouteSchema>;

/** GET /routes?date=... — top level is a JSON array */
export const RoutesListResponseSchema = z.array(RouteSchema);
export type RoutesListResponse = z.infer<typeof RoutesListResponseSchema>;
