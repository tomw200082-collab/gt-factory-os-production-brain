/**
 * Unit tests for api-schemas, isTerminalStatus, and mapper.
 *
 * Runs via: `npm test` (tsx --test ...). Pure; no HTTP, no DB, no
 * filesystem writes. Reads fixture JSON files only.
 *
 * Invariants tested:
 *   - every fixture parses cleanly against its declared schema
 *   - terminal-status classification matches the contract pack §B.8 table
 *   - mapper propagates parent task_id to embedded visits and order_items
 *   - mapper captures raw_payload unchanged
 *   - mapper preserves string-decimal semantics for order_total,
 *     order_items.price, order_items.quantity
 *   - numeric quantity from upstream becomes string in the mirror
 *   - split orders share wp_order_id and survive as distinct rows
 */

import { describe, test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  LionWheelErrorBodySchema,
  RoutesListResponseSchema,
  TaskShowResponseSchema,
  TasksByOrderIdResponseSchema,
} from "../api-schemas.js";
import { isTerminalStatus, TERMINAL_TASK_STATUSES } from "../mirror-shapes.js";
import {
  mapOrderItemToUpsert,
  mapTaskToFetchResult,
  normalizeQuantity,
} from "../mapper.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = resolve(__dirname, "..", "..", "..", "fixtures", "lionwheel");

function loadFixture(name: string): unknown {
  return JSON.parse(readFileSync(resolve(FIXTURES_DIR, name), "utf-8"));
}

/* ---------------------------------------------------------------------- *
 * Schema parsing — every fixture must round-trip through its schema.
 * ---------------------------------------------------------------------- */

describe("api-schemas parse fixtures", () => {
  test("task-show--completed-single-visit", () => {
    const raw = loadFixture("task-show--completed-single-visit.json");
    const parsed = TaskShowResponseSchema.parse(raw);
    assert.equal(parsed.task.status, "COMPLETED");
    assert.equal(parsed.task.visits.length, 1);
    assert.equal(parsed.task.order_items.length, 2);
  });

  test("task-show--canceled", () => {
    const raw = loadFixture("task-show--canceled.json");
    const parsed = TaskShowResponseSchema.parse(raw);
    assert.equal(parsed.task.status, "CANCELED");
    assert.equal(parsed.task.completed_at, null);
    assert.equal(parsed.task.driver_id, null);
  });

  test("tasks-by-order-id--split returns an array of tasks", () => {
    const raw = loadFixture("tasks-by-order-id--split.json");
    const parsed = TasksByOrderIdResponseSchema.parse(raw);
    assert.equal(parsed.tasks.length, 2);
  });

  test("routes--populated has embedded visits", () => {
    const raw = loadFixture("routes--populated.json");
    const parsed = RoutesListResponseSchema.parse(raw);
    assert.equal(parsed.length, 1);
    assert.equal(parsed[0]!.visits.length, 1);
  });

  test("routes--empty is a valid empty list", () => {
    const raw = loadFixture("routes--empty.json");
    const parsed = RoutesListResponseSchema.parse(raw);
    assert.equal(parsed.length, 0);
  });

  test("error--401 matches verbatim 401 shape", () => {
    const raw = loadFixture("error--401.json");
    const parsed = LionWheelErrorBodySchema.parse(raw);
    assert.equal(parsed.error, "API Key is wrong");
  });

  test("error--404 matches verbatim 404 shape", () => {
    const raw = loadFixture("error--404.json");
    const parsed = LionWheelErrorBodySchema.parse(raw);
    assert.equal(parsed.error, "Not found");
  });
});

/* ---------------------------------------------------------------------- *
 * isTerminalStatus — classify every enum value from §B.8.
 * ---------------------------------------------------------------------- */

describe("isTerminalStatus", () => {
  const TERMINAL = new Set<string>(TERMINAL_TASK_STATUSES);
  const ALL_STATUSES = [
    "UNASSIGNED",
    "ASSIGNED",
    "ACTIVE",
    "COMPLETED",
    "CANCELED",
    "ROUNDTRIP_DELIVERED",
    "IN_INVENTORY",
    "OUT_INVENTORY",
    "FAILED",
    "FINAL_FAILED",
    "IN_TRANSFER",
  ];

  for (const status of ALL_STATUSES) {
    const expected = TERMINAL.has(status);
    test(`${status} -> ${expected ? "terminal" : "not terminal"}`, () => {
      assert.equal(isTerminalStatus(status), expected);
    });
  }

  test("unknown status is classified as non-terminal (fail-safe)", () => {
    // An unknown status should NOT be retired. Runtime handoff §C.5:
    // schema-drift cases halt ingest; they must never auto-retire.
    assert.equal(isTerminalStatus("SOMETHING_NEW"), false);
  });
});

/* ---------------------------------------------------------------------- *
 * normalizeQuantity — boundary coercion.
 * ---------------------------------------------------------------------- */

describe("normalizeQuantity", () => {
  test("undefined -> null", () => assert.equal(normalizeQuantity(undefined), null));
  test("string passes through", () => assert.equal(normalizeQuantity("7"), "7"));
  test("number becomes string", () => assert.equal(normalizeQuantity(42), "42"));
  test("zero number becomes '0'", () => assert.equal(normalizeQuantity(0), "0"));
  test("negative number preserved", () => assert.equal(normalizeQuantity(-3), "-3"));
  test("decimal number preserved in string form", () => assert.equal(normalizeQuantity(1.5), "1.5"));
  test("empty string is preserved (not coerced to null)", () => assert.equal(normalizeQuantity(""), ""));
});

/* ---------------------------------------------------------------------- *
 * Mapper — completed task.
 * ---------------------------------------------------------------------- */

describe("mapTaskToFetchResult — completed single-visit", () => {
  const raw = loadFixture("task-show--completed-single-visit.json");
  const parsed = TaskShowResponseSchema.parse(raw);
  const result = mapTaskToFetchResult(parsed.task);

  test("is_terminal derived from COMPLETED", () => {
    assert.equal(result.task.is_terminal, true);
  });

  test("mirror_source_watermark equals upstream updated_at", () => {
    assert.equal(result.task.mirror_source_watermark, parsed.task.updated_at);
  });

  test("created_at/updated_at renamed to *_upstream", () => {
    assert.equal(result.task.created_at_upstream, parsed.task.created_at);
    assert.equal(result.task.updated_at_upstream, parsed.task.updated_at);
  });

  test("raw_payload captures the full upstream task", () => {
    assert.deepEqual(result.task.raw_payload, parsed.task);
  });

  test("order_total preserved as string", () => {
    assert.equal(typeof result.task.order_total, "string");
    assert.equal(result.task.order_total, "370.50");
  });

  test("visits count matches upstream", () => {
    assert.equal(result.visits.length, parsed.task.visits.length);
  });

  test("every visit task_id equals parent task.id", () => {
    for (const v of result.visits) {
      assert.equal(v.task_id, parsed.task.id);
    }
  });

  test("order_items count matches upstream", () => {
    assert.equal(result.order_items.length, parsed.task.order_items.length);
  });

  test("every order_item task_id equals parent task.id", () => {
    for (const oi of result.order_items) {
      assert.equal(oi.task_id, parsed.task.id);
    }
  });

  test("order_items quantity and price remain strings", () => {
    for (const oi of result.order_items) {
      if (oi.quantity !== null) {
        assert.equal(typeof oi.quantity, "string", `quantity for id=${oi.id}`);
      }
      if (oi.price !== null) {
        assert.equal(typeof oi.price, "string", `price for id=${oi.id}`);
      }
    }
  });
});

/* ---------------------------------------------------------------------- *
 * Mapper — canceled task.
 * ---------------------------------------------------------------------- */

describe("mapTaskToFetchResult — canceled", () => {
  const raw = loadFixture("task-show--canceled.json");
  const parsed = TaskShowResponseSchema.parse(raw);
  const result = mapTaskToFetchResult(parsed.task);

  test("is_terminal true for CANCELED", () => {
    assert.equal(result.task.is_terminal, true);
  });

  test("status preserved verbatim", () => {
    assert.equal(result.task.status, "CANCELED");
  });

  test("driver_id null survives into mirror", () => {
    assert.equal(result.task.driver_id, null);
  });

  test("completed_at null survives into mirror", () => {
    assert.equal(result.task.completed_at, null);
  });
});

/* ---------------------------------------------------------------------- *
 * Mapper — order_item normalization edge cases.
 * ---------------------------------------------------------------------- */

describe("mapOrderItemToUpsert — edge cases", () => {
  test("numeric upstream quantity becomes mirror string", () => {
    const mapped = mapOrderItemToUpsert(
      {
        id: 999_001,
        sku: "GT-EDGE-NUM",
        name: "numeric-quantity edge",
        variant: null,
        quantity: 42,
      },
      7777
    );
    assert.equal(mapped.task_id, 7777);
    assert.equal(typeof mapped.quantity, "string");
    assert.equal(mapped.quantity, "42");
    assert.equal(mapped.price, null);
    assert.equal(mapped.weight, null);
    assert.equal(mapped.variant, null);
    assert.equal(mapped.notes, null);
  });

  test("missing upstream quantity becomes mirror null", () => {
    const mapped = mapOrderItemToUpsert(
      {
        id: 999_002,
        sku: "GT-EDGE-MISS",
        name: "missing-quantity edge",
        variant: null,
      },
      7777
    );
    assert.equal(mapped.quantity, null);
  });

  test("raw_payload captures the full upstream order_item", () => {
    const upstream = {
      id: 999_003,
      sku: "GT-EDGE-RAW",
      name: "raw-payload edge",
      variant: "large",
      quantity: "3",
      price: "99.00",
      weight: "1.25",
      notes: "fragile",
    } as const;
    const mapped = mapOrderItemToUpsert(upstream, 7777);
    assert.deepEqual(mapped.raw_payload, upstream);
  });
});

/* ---------------------------------------------------------------------- *
 * Split order — two tasks share wp_order_id, survive as distinct rows.
 * ---------------------------------------------------------------------- */

describe("split order (non-unique wp_order_id)", () => {
  const raw = loadFixture("tasks-by-order-id--split.json");
  const parsed = TasksByOrderIdResponseSchema.parse(raw);
  const results = parsed.tasks.map(mapTaskToFetchResult);

  test("two distinct task ids", () => {
    assert.notEqual(results[0]!.task.id, results[1]!.task.id);
  });

  test("both tasks share one wp_order_id", () => {
    const wpSet = new Set(results.map((r) => r.task.wp_order_id));
    assert.equal(wpSet.size, 1);
  });

  test("at least one task is non-terminal (open work)", () => {
    const anyOpen = results.some((r) => !r.task.is_terminal);
    assert.equal(anyOpen, true);
  });
});
