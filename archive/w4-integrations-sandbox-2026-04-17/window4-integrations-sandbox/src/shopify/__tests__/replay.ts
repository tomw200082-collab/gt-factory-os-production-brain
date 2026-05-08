/**
 * Shopify fixture replay harness.
 *
 * Loads every JSON file in fixtures/shopify/, classifies by filename
 * prefix, parses through the appropriate Zod schema, and runs the
 * mapper (push / reconciliation) for compatible fixtures. Prints one
 * line per fixture + a summary; exits 0 if every fixture parsed
 * cleanly, 1 otherwise. Performs no HTTP.
 */

import { readdirSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  InventoryLevelSchema,
  InventorySetQuantitiesInputSchema,
} from "../api-schemas.js";
import {
  classifyDrift,
  mapInventoryLevelToReconciliationRow,
} from "../mapper.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = resolve(__dirname, "..", "..", "..", "fixtures", "shopify");

type FixtureKind =
  | "inventory_set_input"
  | "inventory_level_read"
  | "unknown";

interface ReplayResult {
  fixture: string;
  kind: FixtureKind;
  outcome: "PASS" | "FAIL";
  error?: string;
  notes: string[];
}

function classify(filename: string): FixtureKind {
  if (filename.startsWith("inventory-set-quantities-input--")) return "inventory_set_input";
  if (filename.startsWith("inventory-level-read--")) return "inventory_level_read";
  return "unknown";
}

function replay(filename: string): ReplayResult {
  const path = resolve(FIXTURES_DIR, filename);
  const kind = classify(filename);
  const notes: string[] = [];
  try {
    const raw: unknown = JSON.parse(readFileSync(path, "utf-8"));
    switch (kind) {
      case "inventory_set_input": {
        const parsed = InventorySetQuantitiesInputSchema.parse(raw);
        notes.push(`name=${parsed.name}`);
        notes.push(`reason="${parsed.reason}"`);
        notes.push(`ignoreCompareQuantity=${parsed.ignoreCompareQuantity ?? false}`);
        notes.push(`quantities=${parsed.quantities.length}`);
        if (parsed.quantities[0]) {
          notes.push(
            `  qty[0] inventoryItemId=${parsed.quantities[0].inventoryItemId} quantity=${parsed.quantities[0].quantity} compareQuantity=${parsed.quantities[0].compareQuantity ?? "null"}`
          );
        }
        break;
      }
      case "inventory_level_read": {
        const parsed = InventoryLevelSchema.parse(raw);
        const row = mapInventoryLevelToReconciliationRow(parsed, "2026-04-17T00:00:00Z");
        notes.push(`sku=${row.sku ?? "null"}`);
        notes.push(`available=${row.availableQty ?? "null"}`);
        notes.push(`on_hand=${row.onHandQty ?? "null"}`);
        notes.push(`locationIsActive=${row.locationIsActive ?? "undefined"}`);
        const verdict = classifyDrift({ platformProjectedQty: row.availableQty, row });
        notes.push(`  classifyDrift(platformQty=availableQty) => ${verdict.kind}`);
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
    process.stdout.write(`${r.outcome} [${r.kind}] ${r.fixture}\n`);
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
