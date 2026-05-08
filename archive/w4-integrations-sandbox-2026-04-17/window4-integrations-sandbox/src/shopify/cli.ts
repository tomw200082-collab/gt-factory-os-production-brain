/**
 * Shopify CLI skeleton — Slice S1 dry-run entry point.
 *
 * PERFORMS NO HTTP. Parses args, validates env, prints what a real run
 * WOULD do, exits. The fetcher module is not imported here — excludes
 * any possibility of an accidental HTTP side effect from this file.
 */

import { ENV_VAR_NAMES, EnvValidationError, parseRuntimeEnv } from "./env.js";
import type { RuntimeEnv } from "./env.js";

const USAGE = `\
Usage:
  cli.ts --push --sku <string> --quantity <int> --location <id> [--name available|on_hand] [--reason <string>]
  cli.ts --reconcile --location <id>
  cli.ts --help

Required environment:
  ${ENV_VAR_NAMES.apiToken}               Shopify Admin API access token
  ${ENV_VAR_NAMES.shopDomain}              Shop domain (e.g. gteveryday.myshopify.com)
Optional environment:
  ${ENV_VAR_NAMES.apiVersion}       default "2026-04" (minimum for @idempotent)
  ${ENV_VAR_NAMES.killSwitch}           default true
  ${ENV_VAR_NAMES.requestTimeoutMs}     default 30000

Exit codes:
  0  dry-run completed; no HTTP was performed
  1  invalid arguments
  2  invalid environment
  3  kill switch is off
`;

type CliCommand =
  | { kind: "help" }
  | {
      kind: "push";
      sku: string;
      quantity: number;
      locationId: string;
      name: "available" | "on_hand";
      reason: string;
    }
  | { kind: "reconcile"; locationId: string };

function parseArgs(argv: readonly string[]): CliCommand | { kind: "error"; message: string } {
  if (argv.length === 0 || argv.includes("--help") || argv.includes("-h")) {
    return { kind: "help" };
  }

  const flags = new Set<string>();
  const values: Record<string, string> = {};
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (!token.startsWith("--")) {
      return { kind: "error", message: `unexpected positional argument "${token}"` };
    }
    const next = argv[i + 1];
    if (next === undefined || next.startsWith("--")) {
      flags.add(token);
    } else {
      values[token] = next;
      i += 1;
    }
  }

  const hasPush = flags.has("--push") || values["--push"] !== undefined;
  const hasReconcile = flags.has("--reconcile") || values["--reconcile"] !== undefined;

  if (hasPush && hasReconcile) {
    return { kind: "error", message: "--push and --reconcile are mutually exclusive" };
  }

  if (hasPush) {
    const sku = values["--sku"];
    const quantityStr = values["--quantity"];
    const locationId = values["--location"];
    const nameRaw = values["--name"] ?? "available";
    const reason = values["--reason"] ?? "correction";

    if (!sku) return { kind: "error", message: "--push requires --sku" };
    if (!quantityStr) return { kind: "error", message: "--push requires --quantity" };
    if (!locationId) return { kind: "error", message: "--push requires --location" };
    const quantity = Number.parseInt(quantityStr, 10);
    if (!Number.isFinite(quantity) || quantity < 0) {
      return {
        kind: "error",
        message: `--quantity must be a non-negative integer (got "${quantityStr}")`,
      };
    }
    if (nameRaw !== "available" && nameRaw !== "on_hand") {
      return {
        kind: "error",
        message: `--name must be "available" or "on_hand" (got "${nameRaw}")`,
      };
    }
    return { kind: "push", sku, quantity, locationId, name: nameRaw, reason };
  }

  if (hasReconcile) {
    const locationId = values["--location"];
    if (!locationId) return { kind: "error", message: "--reconcile requires --location" };
    return { kind: "reconcile", locationId };
  }

  return { kind: "error", message: "expected --push or --reconcile" };
}

function describePlannedRun(command: CliCommand, env: RuntimeEnv): string {
  switch (command.kind) {
    case "help":
      return USAGE;
    case "push":
      return [
        `Would execute Shopify mutation: inventorySetQuantities`,
        `target: https://${env.shopDomain}/admin/api/${env.apiVersion}/graphql.json`,
        `sku: ${command.sku}`,
        `location: ${command.locationId}`,
        `name: ${command.name}`,
        `quantity: ${command.quantity} (absolute set)`,
        `reason: "${command.reason}"`,
        `compareQuantity: <resolved-from-shopify_sku_sync_state-at-run-time>`,
        `idempotency key: gt:<run_id>:<inventory_item_id>:${command.locationId}`,
        `@idempotent directive: REQUIRED (API ${env.apiVersion} >= 2026-04)`,
        `ignoreCompareQuantity: false (v1 always compare-and-set)`,
        `kill_switch_enabled: ${env.isEnabled}`,
        `(no HTTP performed in this skeleton)`,
      ].join("\n");
    case "reconcile":
      return [
        `Would reconcile: paginated InventoryLevel read for location ${command.locationId}`,
        `target: https://${env.shopDomain}/admin/api/${env.apiVersion}/graphql.json`,
        `expected response: InventoryLevel[] with embedded item + quantities`,
        `downstream: classifyDrift against platform projection per row`,
        `kill_switch_enabled: ${env.isEnabled}`,
        `(no HTTP performed in this skeleton)`,
      ].join("\n");
  }
}

export function main(
  argv: readonly string[],
  env: Record<string, string | undefined>
): { exitCode: number; stdout: string; stderr: string } {
  const command = parseArgs(argv);

  if (command.kind === "error") {
    return { exitCode: 1, stdout: "", stderr: `${command.message}\n\n${USAGE}` };
  }
  if (command.kind === "help") {
    return { exitCode: 0, stdout: USAGE, stderr: "" };
  }

  let runtimeEnv: RuntimeEnv;
  try {
    runtimeEnv = parseRuntimeEnv(env);
  } catch (e) {
    if (e instanceof EnvValidationError) {
      return { exitCode: 2, stdout: "", stderr: e.message };
    }
    return { exitCode: 2, stdout: "", stderr: `unexpected env error: ${String(e)}` };
  }

  if (!runtimeEnv.isEnabled) {
    return {
      exitCode: 3,
      stdout: "",
      stderr: `${ENV_VAR_NAMES.killSwitch} is false; Shopify sync disabled by configuration.`,
    };
  }

  return { exitCode: 0, stdout: describePlannedRun(command, runtimeEnv), stderr: "" };
}

const isEntryPoint =
  import.meta.url === `file://${process.argv[1]?.replace(/\\/g, "/")}`;
if (isEntryPoint) {
  const result = main(
    process.argv.slice(2),
    process.env as Record<string, string | undefined>
  );
  if (result.stdout) process.stdout.write(result.stdout + "\n");
  if (result.stderr) process.stderr.write(result.stderr + "\n");
  process.exit(result.exitCode);
}
