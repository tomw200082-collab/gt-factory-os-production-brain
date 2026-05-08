/**
 * LionWheel fetcher interface.
 *
 * This file declares the contract between the future runtime caller
 * (CLI, scheduler, webhook handler) and the fetcher implementation.
 *
 * There is intentionally NO implementation in this file. The interface
 * is the contract; the implementation is runtime work that happens only
 * after Window 1 has authored the mirror migrations (handoff §D.1) and
 * the operator has rotated the LionWheel token (handoff §E.3).
 *
 * Design notes (from runtime handoff §B.8):
 *   - The fetcher parses and shapes. It does NOT upsert. Upserting is the
 *     job of the runtime wrapper that owns the DB connection.
 *   - The fetcher returns a typed TaskFetchResult that contains every
 *     mirror-ready upsert shape plus the raw_payload for resilience.
 *   - Errors are surfaced as typed Result variants — never thrown as raw
 *     exceptions — so the runtime wrapper can classify them into
 *     IntegrationRunErrorClass (§C.4 of the contract pack).
 *   - The fetcher accepts a "kill switch" signal; when set, every call
 *     short-circuits without making an HTTP request (runtime handoff §C.6).
 */

import { z } from "zod";
import type { Task, Route } from "./api-schemas.js";
import type {
  TaskFetchResult,
  IntegrationRunErrorClass,
} from "./mirror-shapes.js";

/* ---------------------------------------------------------------------- *
 * Fetch result — discriminated union so the runtime wrapper can classify
 * into IntegrationRunErrorClass without pattern-matching strings.
 * ---------------------------------------------------------------------- */

export type FetchResult<T> =
  | { kind: "ok"; value: T }
  | { kind: "not_found"; endpoint: string; trace_id: string }
  | { kind: "auth_error"; endpoint: string; trace_id: string; body: unknown }
  | {
      kind: "schema_drift";
      endpoint: string;
      trace_id: string;
      zodIssues: z.ZodIssue[];
    }
  | {
      kind: "rate_limit";
      endpoint: string;
      trace_id: string;
      retry_after_seconds: number | null;
    }
  | {
      kind: "network_timeout";
      endpoint: string;
      trace_id: string;
      timeout_ms: number;
    }
  | {
      kind: "partial_payload";
      endpoint: string;
      trace_id: string;
      reason: string;
    }
  | { kind: "disabled_by_kill_switch"; endpoint: string; trace_id: string }
  | { kind: "unknown_error"; endpoint: string; trace_id: string; cause: unknown };

/** Map a non-ok FetchResult into the IntegrationRunErrorClass vocabulary. */
export function errorClassOf<T>(
  result: Exclude<FetchResult<T>, { kind: "ok" }>
): IntegrationRunErrorClass {
  switch (result.kind) {
    case "not_found":
      return "not_found";
    case "auth_error":
      return "auth";
    case "schema_drift":
      return "schema_drift";
    case "rate_limit":
      return "rate_limit";
    case "network_timeout":
      return "network_timeout";
    case "partial_payload":
      return "partial_payload";
    case "disabled_by_kill_switch":
      // Runtime wrapper should treat kill-switch as a distinct run status
      // ("superseded") rather than an error; we still return a bucket so
      // the error_class column has a stable value when it is stored.
      return "unknown";
    case "unknown_error":
      return "unknown";
  }
}

/* ---------------------------------------------------------------------- *
 * Fetcher configuration — no implementation, only the shape of inputs the
 * runtime will supply.
 * ---------------------------------------------------------------------- */

export interface LionWheelFetcherConfig {
  /** Base URL. Contract pack §B.2: "https://members.lionwheel.com/api/v1" */
  readonly baseUrl: string;

  /**
   * Shipping-company API token. The fetcher receives this via config;
   * it never reads process.env directly. Secret-store wiring document
   * (docs/secret-store-wiring.md) describes how the runtime loads it.
   *
   * MUST NOT be logged. MUST NOT appear in error_detail. MUST be appended
   * as a `?key=<token>` query parameter, not as a header (contract pack
   * §B.2 — LionWheel auth is query-param-based).
   */
  readonly apiToken: string;

  /** Milliseconds before a single request is considered a timeout. */
  readonly requestTimeoutMs: number;

  /**
   * Kill-switch signal. Evaluated on every call. When true, the fetcher
   * returns { kind: "disabled_by_kill_switch" } without any HTTP work.
   *
   * Runtime handoff §C.6: kill-switch scope is LionWheel only; does not
   * affect ledger, anchors, masters, or other integrations.
   */
  readonly isEnabled: () => boolean;

  /**
   * Callback hook to emit a novel-enum-value observation without blocking
   * the fetch. Runtime wrapper forwards these to an observability sink so
   * the enum-completeness blocker (§G.2 of the contract pack) can close.
   */
  readonly onNovelEnumObserved?: (observation: NovelEnumObservation) => void;
}

export interface NovelEnumObservation {
  readonly endpoint: string;
  readonly fieldPath: string; // e.g. "task.pick_status"
  readonly value: string;
  readonly task_id?: number;
  readonly trace_id: string;
}

/* ---------------------------------------------------------------------- *
 * Fetcher interface — method signatures only.
 * ---------------------------------------------------------------------- */

export interface LionWheelFetcher {
  /**
   * Fetch a single task by id, parse + validate, and return the full
   * TaskFetchResult ready for mirror upsert.
   *
   * Slice 1 entry point (runtime handoff §A.1).
   *
   * Responsibilities:
   *   - HTTP GET /tasks/show/:task_id?key=<token>
   *   - parse with TaskShowResponseSchema
   *   - map Task + embedded visits + embedded order_items into the
   *     TaskFetchResult mirror-ready shape (runtime handoff §B.8 upsert
   *     expectation)
   *   - preserve raw_payload on every returned entity
   *   - compute is_terminal on the task
   *   - call onNovelEnumObserved for any observed open-enum value
   *   - do NOT upsert; the caller owns the DB transaction
   */
  fetchTaskById(
    task_id: number,
    options: FetchOptions
  ): Promise<FetchResult<TaskFetchResult>>;

  /**
   * Fetch all tasks associated with an external wp_order_id. May return
   * multiple tasks — split orders share wp_order_id (contract pack §B.10).
   *
   * Slice 2+ entry point; included in the interface so the shape is
   * stable before implementation begins.
   */
  fetchTasksByWpOrderId(
    wp_order_id: string,
    options: FetchOptions
  ): Promise<FetchResult<TaskFetchResult[]>>;

  /**
   * Fetch a date's routes. Contract pack §B.1: this is the ONLY listing
   * endpoint LionWheel exposes.
   *
   * Slice 2 entry point.
   *
   * Returns parsed routes with embedded visits. Reconciliation into
   * mirror tables is the caller's job (runtime handoff §C.5).
   */
  fetchRoutesByDate(
    date: RouteDate,
    options: FetchOptions
  ): Promise<FetchResult<Route[]>>;

  /**
   * Not-yet-implemented in Slice 1. Listed for interface completeness
   * so future slices do not reshape the interface:
   *   - fetchVisitById
   *   - fetchDriverDailyRoute
   *   - fetchCompany
   */
}

/** "YYYY-MM-DD" — the form accepted by /routes?date=... */
export type RouteDate = `${number}-${number}-${number}`;

export interface FetchOptions {
  /** Correlation id for the calling integration_run; logged, not sent. */
  readonly trace_id: string;
}

/* ---------------------------------------------------------------------- *
 * Intentionally no implementation. Runtime authorship is gated on:
 *   - Window 1 D.1 migrations
 *   - Operator E.3 token rotation
 *   - Operator freshness threshold lock (E.3)
 * See docs/blocker-register.md.
 * ---------------------------------------------------------------------- */
