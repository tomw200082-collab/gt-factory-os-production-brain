/**
 * Fixture replay harness.
 *
 * Loads every JSON file in fixtures/lionwheel/, classifies it by filename
 * prefix, parses it through the appropriate Zod schema, and (for task
 * fixtures) runs the mapper. Prints a one-line result per fixture plus a
 * summary; exits 0 if every fixture parsed cleanly, 1 otherwise.
 *
 * Run via: `npm run replay` (tsx src/lionwheel/__tests__/replay.ts).
 *
 * Purpose: a lightweight smoke check operators can run after adding a
 * fixture, before spending time on pgTAP in Window 1 or unit tests here.
 * Complements `npm test`; does not replace it.
 *
 * Performs no HTTP. Writes nothing. Pure stdout.
 */

import { readdirSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  LionWheelErrorBodySchema,
  RoutesListResponseSchema,
  TaskShowResponseSchema,
  TasksByOrderIdResponseSchema,
} from "../api-schemas.js";
import { mapTaskToFetchResult } from "../mapper.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = resolve(__dirname, "..", "..", "..", "fixtures", "lionwheel");

type FixtureKind = "task_show" | "tasks_by_order_id" | "routes" | "error" | "unknown";

interface ReplayResult {
  fixture: string;
  kind: FixtureKind;
  outcome: "PASS" | "FAIL";
  error?: string;
  notes: string[];
}

function classify(filename: string): FixtureKind {
  if (filename.startsWith("task-show--")) return "task_show";
  if (filename.startsWith("tasks-by-order-id--")) return "tasks_by_order_id";
  if (filename.startsWith("routes--")) return "routes";
  if (filename.startsWith("error--")) return "error";
  return "unknown";
}

function replay(filename: string): ReplayResult {
  const path = resolve(FIXTURES_DIR, filename);
  const kind = classify(filename);
  const notes: string[] = [];
  try {
    const raw: unknown = JSON.parse(readFileSync(path, "utf-8"));
    switch (kind) {
      case "task_show": {
        const parsed = TaskShowResponseSchema.parse(raw);
        const mapped = mapTaskToFetchResult(parsed.task);
        notes.push(`status=${parsed.task.status}`);
        notes.push(`is_terminal=${mapped.task.is_terminal}`);
        notes.push(`visits=${mapped.visits.length}`);
        notes.push(`order_items=${mapped.order_items.length}`);
        break;
      }
      case "tasks_by_order_id": {
        const parsed = TasksByOrderIdResponseSchema.parse(raw);
        const wpIds = new Set(parsed.tasks.map((t) => t.wp_order_id));
        notes.push(`tasks=${parsed.tasks.length}`);
        notes.push(`distinct_wp_order_ids=${wpIds.size}`);
        for (const task of parsed.tasks) {
          const r = mapTaskToFetchResult(task);
          notes.push(`  task_id=${r.task.id} is_terminal=${r.task.is_terminal}`);
        }
        break;
      }
      case "routes": {
        const parsed = RoutesListResponseSchema.parse(raw);
        const totalVisits = parsed.reduce((n, route) => n + route.visits.length, 0);
        notes.push(`routes=${parsed.length}`);
        notes.push(`embedded_visits=${totalVisits}`);
        break;
      }
      case "error": {
        const parsed = LionWheelErrorBodySchema.parse(raw);
        notes.push(`error="${parsed.error}"`);
        break;
      }
      case "unknown":
        throw new Error(`unrecognized fixture prefix: ${filename}`);
    }
    return { fixture: filename, kind, outcome: "PASS", notes };
  } catch (e) {
    return {
      fixture: filename,
      kind,
      outcome: "FAIL",
      error: e instanceof Error ? e.message : String(e),
      notes,
    };
  }
}

export function main(): number {
  const files = readdirSync(FIXTURES_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort();

  if (files.length === 0) {
    process.stdout.write(`no fixtures found in ${FIXTURES_DIR}\n`);
    return 1;
  }

  const results = files.map(replay);
  const failures = results.filter((r) => r.outcome === "FAIL");

  for (const r of results) {
    const header = `${r.outcome} [${r.kind}] ${r.fixture}`;
    process.stdout.write(`${header}\n`);
    for (const n of r.notes) process.stdout.write(`    ${n}\n`);
    if (r.error) process.stdout.write(`    error: ${r.error}\n`);
  }

  process.stdout.write(`\n${results.length} fixtures, ${failures.length} failures\n`);
  return failures.length > 0 ? 1 : 0;
}

const isEntry = import.meta.url === `file://${process.argv[1]?.replace(/\\/g, "/")}`;
if (isEntry) {
  process.exit(main());
}
