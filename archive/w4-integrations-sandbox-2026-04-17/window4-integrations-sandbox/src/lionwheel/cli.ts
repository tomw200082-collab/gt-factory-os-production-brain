/**
 * LionWheel CLI skeleton — Slice 1 entry point.
 *
 * THIS CLI DOES NOT PERFORM HTTP. It:
 *   1. Parses its own arguments.
 *   2. Validates environment variables into a RuntimeEnv.
 *   3. Reports exactly what a real run WOULD do.
 *   4. Exits.
 *
 * Real HTTP is implemented in a future pass, gated on:
 *   - Window 1 completing D.1 migrations (see docs/blocker-register.md)
 *   - Operator completing E.3 token rotation
 *
 * Why a skeleton now, before HTTP:
 *   - Locks the CLI contract (arg shape, exit codes, stdout format) so
 *     operators and CI can wire around it without waiting for runtime.
 *   - Validates that env parsing, kill-switch semantics, and argument
 *     handling are correct before any network call can mask bugs.
 *   - Parallel-safe: no external side effects at any path.
 */

import { parseRuntimeEnv, ENV_VAR_NAMES, EnvValidationError } from "./env.js";
import type { RuntimeEnv } from "./env.js";

const USAGE = `\
Usage:
  cli.ts --task-id <integer>          Dry-run a /tasks/show fetch
  cli.ts --by-order-id <string>       Dry-run a /tasks/by_order_id fetch
  cli.ts --routes-date <YYYY-MM-DD>   Dry-run a /routes?date= fetch
  cli.ts --help                       Print this message

Required environment:
  ${ENV_VAR_NAMES.apiToken}                  LionWheel shipping-company key
Optional environment:
  ${ENV_VAR_NAMES.baseUrl}                   default https://members.lionwheel.com/api/v1
  ${ENV_VAR_NAMES.killSwitch}                default true; when false, fetcher short-circuits
  ${ENV_VAR_NAMES.requestTimeoutMs}          default 15000

Exit codes:
  0  dry-run completed; no HTTP was performed
  1  invalid arguments
  2  invalid environment
  3  kill switch is off (sync disabled by config)
`;

/** Result of parsing CLI args; never performs work itself. */
type CliCommand =
  | { kind: "help" }
  | { kind: "fetch_task"; task_id: number }
  | { kind: "fetch_by_order_id"; wp_order_id: string }
  | { kind: "fetch_routes"; date: string };

function parseArgs(argv: readonly string[]): CliCommand | { kind: "error"; message: string } {
  if (argv.length === 0 || argv.includes("--help") || argv.includes("-h")) {
    return { kind: "help" };
  }

  const pairs = readPairs(argv);
  if ("error" in pairs) return { kind: "error", message: pairs.error };

  const keys = Object.keys(pairs);
  if (keys.length !== 1) {
    return {
      kind: "error",
      message: `expected exactly one of --task-id | --by-order-id | --routes-date (got: ${keys.join(", ") || "none"})`,
    };
  }

  if (pairs["--task-id"] !== undefined) {
    const parsed = Number.parseInt(pairs["--task-id"], 10);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      return { kind: "error", message: `--task-id must be a positive integer (got "${pairs["--task-id"]}")` };
    }
    return { kind: "fetch_task", task_id: parsed };
  }

  if (pairs["--by-order-id"] !== undefined) {
    const value = pairs["--by-order-id"];
    if (value.length === 0) {
      return { kind: "error", message: `--by-order-id must be a non-empty string` };
    }
    return { kind: "fetch_by_order_id", wp_order_id: value };
  }

  if (pairs["--routes-date"] !== undefined) {
    const value = pairs["--routes-date"];
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
      return { kind: "error", message: `--routes-date must be YYYY-MM-DD (got "${value}")` };
    }
    return { kind: "fetch_routes", date: value };
  }

  return { kind: "error", message: `unrecognized argument: ${keys.join(", ")}` };
}

function readPairs(argv: readonly string[]): Record<string, string> | { error: string } {
  const out: Record<string, string> = {};
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (!token.startsWith("--")) {
      return { error: `unexpected positional argument "${token}"` };
    }
    const next = argv[i + 1];
    if (next === undefined || next.startsWith("--")) {
      return { error: `flag "${token}" expects a value` };
    }
    out[token] = next;
    i += 1;
  }
  return out;
}

function describePlannedRun(command: CliCommand, env: RuntimeEnv): string {
  switch (command.kind) {
    case "help":
      return USAGE;
    case "fetch_task":
      return [
        `Would fetch: GET ${env.baseUrl}/tasks/show/${command.task_id}?key=<REDACTED_TOKEN>`,
        `trace_id: <generated-at-run-time>`,
        `kill_switch_enabled: ${env.isEnabled}`,
        `request_timeout_ms: ${env.requestTimeoutMs}`,
        `Downstream target: TaskFetchResult (runtime handoff §B.8)`,
        `(no HTTP performed in this skeleton)`,
      ].join("\n");
    case "fetch_by_order_id":
      return [
        `Would fetch: GET ${env.baseUrl}/tasks/by_order_id/${encodeURIComponent(command.wp_order_id)}?key=<REDACTED_TOKEN>`,
        `trace_id: <generated-at-run-time>`,
        `kill_switch_enabled: ${env.isEnabled}`,
        `expected response shape: { tasks: Task[] } — array, supports split orders`,
        `(no HTTP performed in this skeleton)`,
      ].join("\n");
    case "fetch_routes":
      return [
        `Would fetch: GET ${env.baseUrl}/routes?key=<REDACTED_TOKEN>&date=${command.date}&format=json`,
        `trace_id: <generated-at-run-time>`,
        `kill_switch_enabled: ${env.isEnabled}`,
        `expected response shape: Route[] — top-level array`,
        `(no HTTP performed in this skeleton)`,
      ].join("\n");
  }
}

/** Main — pure; returns the exit code instead of calling process.exit directly. */
export function main(argv: readonly string[], env: Record<string, string | undefined>): { exitCode: number; stdout: string; stderr: string } {
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
      stderr: `${ENV_VAR_NAMES.killSwitch} is false; LionWheel sync disabled by configuration.`,
    };
  }

  return { exitCode: 0, stdout: describePlannedRun(command, runtimeEnv), stderr: "" };
}

/* ---------------------------------------------------------------------- *
 * Wire to process only at the bottom — keeps main() pure for tests.
 *
 * Safety: even if process.env happens to contain a valid LIONWHEEL_API_TOKEN,
 * this invocation still does not perform HTTP. The fetcher is not imported.
 * ---------------------------------------------------------------------- */

const isEntryPoint = import.meta.url === `file://${process.argv[1]?.replace(/\\/g, "/")}`;
if (isEntryPoint) {
  const result = main(process.argv.slice(2), process.env as Record<string, string | undefined>);
  if (result.stdout) process.stdout.write(result.stdout + "\n");
  if (result.stderr) process.stderr.write(result.stderr + "\n");
  process.exit(result.exitCode);
}
