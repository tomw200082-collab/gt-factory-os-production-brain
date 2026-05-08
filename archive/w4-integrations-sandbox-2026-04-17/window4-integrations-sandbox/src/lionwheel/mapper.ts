/**
 * Pure API -> mirror mapper.
 *
 * This module is the single place where an inspected LionWheel API shape
 * is normalized into the mirror-ready upsert shape. It performs:
 *   - is_terminal computation (contract pack §B.8 + §B.10 retirement rule)
 *   - string-decimal preservation for monetary / quantity fields
 *     (runtime handoff §B.2 / §B.4 — no numeric coercion at write time)
 *   - raw_payload capture for schema-drift resilience
 *     (runtime handoff §B.2 — every mirror entity carries its source)
 *   - mirror_source_watermark population from upstream updated_at
 *     (runtime handoff §B.8 — drives idempotent upsert)
 *   - task_id propagation from the parent task down to embedded visits
 *     and order_items (single source of truth for the parent FK)
 *
 * The mapper is pure: no I/O, no HTTP, no DB, no side effects. It is
 * exhaustively testable against fixtures and does not depend on any
 * Window 1 surface. It runs long before Window 1 migrations exist.
 *
 * Invariants enforced (any violation is a bug, not a configurable option):
 *   - order_total, order_items.price, order_items.weight stay as strings
 *   - order_items.quantity is string | null (never number in the mirror)
 *   - raw_payload on each mirror entity is the unmodified upstream object
 *   - visits[].task_id always equals the parent task.id (parent wins if
 *     the embedded value disagrees; the embedded value survives in
 *     raw_payload for audit)
 */

import type { Task, Visit, OrderItem } from "./api-schemas.js";
import {
  isTerminalStatus,
  type LwOrderItemUpsert,
  type LwTaskUpsert,
  type LwVisitUpsert,
  type TaskFetchResult,
} from "./mirror-shapes.js";

/**
 * Map a parsed LionWheel task into a mirror-ready TaskFetchResult.
 *
 * Call site: the future fetcher implementation (W4.6). Until that
 * exists, this mapper is exercised by fixtures in the replay harness
 * and by unit tests.
 */
export function mapTaskToFetchResult(task: Task): TaskFetchResult {
  return {
    task: mapTaskToUpsert(task),
    visits: task.visits.map((v) => mapVisitToUpsert(v, task.id)),
    order_items: task.order_items.map((oi) => mapOrderItemToUpsert(oi, task.id)),
  };
}

export function mapTaskToUpsert(task: Task): LwTaskUpsert {
  return {
    id: task.id,
    public_id: task.public_id,
    organization_id: task.organization_id,
    company_id: task.company_id,

    status: task.status,
    pick_status: task.pick_status,
    roundtrip_status: task.roundtrip_status,
    urgency: task.urgency,

    is_roundtrip: task.is_roundtrip,
    same_day: task.same_day,
    is_terminal: isTerminalStatus(task.status),

    wp_order_id: task.wp_order_id,
    wp_order_key: task.wp_order_key,
    creation_origin: task.creation_origin,
    creation_trigger: task.creation_trigger,
    driver_id: task.driver_id,
    packages_quantity: task.packages_quantity,

    pickup_at: task.pickup_at,
    completed_at: task.completed_at,
    wp_order_at: task.wp_order_at,
    created_at_upstream: task.created_at,
    updated_at_upstream: task.updated_at,

    order_total: task.order_total,

    notes: task.notes,
    org_note: task.org_note,
    driver_note: task.driver_note,

    raw_payload: task,
    mirror_source_watermark: task.updated_at,
  };
}

export function mapVisitToUpsert(visit: Visit, parentTaskId: number): LwVisitUpsert {
  return {
    id: visit.id,
    task_id: parentTaskId,
    route_id: visit.route_id,
    organization_id: visit.organization_id,
    company_id: visit.company_id,
    driver_id: visit.driver_id,

    kind: visit.kind,
    is_done: visit.is_done,

    visit_at: visit.visit_at,
    delivered_at: visit.delivered_at,
    failed_at: visit.failed_at,
    failure_reason: visit.failure_reason,

    recipient_name: visit.recipient_name,
    phone: visit.phone,
    phone2: visit.phone2,
    email: visit.email,

    city: visit.city,
    street: visit.street,
    number: visit.number,
    apartment: visit.apartment,
    floor: visit.floor,
    zip_code: visit.zip_code,

    latitude: visit.latitude,
    longitude: visit.longitude,
    delivery_latitude: visit.delivery_latitude,
    delivery_longitude: visit.delivery_longitude,

    packages_quantity: visit.packages_quantity,
    notes: visit.notes,

    created_at_upstream: visit.created_at,
    updated_at_upstream: visit.updated_at,

    raw_payload: visit,
    mirror_source_watermark: visit.updated_at,
  };
}

export function mapOrderItemToUpsert(oi: OrderItem, parentTaskId: number): LwOrderItemUpsert {
  return {
    id: oi.id,
    task_id: parentTaskId,
    sku: oi.sku,
    name: oi.name,
    quantity: normalizeQuantity(oi.quantity),
    price: oi.price ?? null,
    variant: oi.variant ?? null,
    weight: oi.weight ?? null,
    notes: oi.notes ?? null,
    raw_payload: oi,
  };
}

/**
 * Normalize order_item.quantity into the mirror-side string-or-null form.
 *
 * Upstream shape (OrderItemSchema): z.union([z.string(), z.number()]).optional()
 * Mirror shape  (LwOrderItemUpsertSchema): z.string().nullable()
 *
 * - undefined -> null (honest absence; not "0")
 * - number    -> String(n) (string-decimal preservation at the boundary)
 * - string    -> pass through verbatim
 *
 * Never coerces into a zero; never drops precision.
 */
export function normalizeQuantity(q: string | number | undefined): string | null {
  if (q === undefined) return null;
  if (typeof q === "number") return String(q);
  return q;
}
