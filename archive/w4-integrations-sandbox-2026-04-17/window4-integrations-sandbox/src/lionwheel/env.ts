/**
 * Typed env-var parsing for the LionWheel runtime.
 *
 * This module declares the set of env vars the runtime will need. It is
 * pure validation — reading and validating a record passed in — with no
 * side effects. The CLI and future runtime call `parseRuntimeEnv` with
 * `process.env` at startup.
 *
 * Deliberate design choices:
 *   - The module does NOT read process.env itself. The caller passes
 *     the record, so tests and the CLI skeleton can pass synthetic
 *     records without touching the ambient environment.
 *   - The module does NOT log the token at any verbosity level.
 *   - The module validates the shape of LIONWHEEL_API_TOKEN only loosely
 *     (non-empty string); the secret-store wiring doc describes the
 *     rotation posture separately.
 */

import { z } from "zod";

/** Canonical env var names this integration consumes. */
export const ENV_VAR_NAMES = {
  apiToken: "LIONWHEEL_API_TOKEN",
  baseUrl: "LIONWHEEL_BASE_URL",
  killSwitch: "LIONWHEEL_SYNC_ENABLED",
  requestTimeoutMs: "LIONWHEEL_REQUEST_TIMEOUT_MS",
} as const;

/**
 * RuntimeEnv — the validated, typed view of env the runtime actually uses.
 *
 * This is a separate shape from RawEnv (the unvalidated record) so the
 * caller is forced through the parse step.
 */
export const RuntimeEnvSchema = z.object({
  apiToken: z.string().min(1, "LIONWHEEL_API_TOKEN must not be empty"),
  baseUrl: z.string().url("LIONWHEEL_BASE_URL must be a valid URL"),
  isEnabled: z.boolean(),
  requestTimeoutMs: z.number().int().positive(),
});
export type RuntimeEnv = z.infer<typeof RuntimeEnvSchema>;

/** Default base URL per contract pack §B.2. */
export const DEFAULT_BASE_URL = "https://members.lionwheel.com/api/v1";
export const DEFAULT_REQUEST_TIMEOUT_MS = 15_000;

/**
 * parseRuntimeEnv — validate a raw env record into a RuntimeEnv.
 *
 * Throws `EnvValidationError` with a redacted-message list of problems.
 * The token is never included in the error; only its presence/absence is.
 */
export function parseRuntimeEnv(raw: Record<string, string | undefined>): RuntimeEnv {
  const rawToken = raw[ENV_VAR_NAMES.apiToken];
  const rawBaseUrl = raw[ENV_VAR_NAMES.baseUrl] ?? DEFAULT_BASE_URL;
  const rawEnabled = raw[ENV_VAR_NAMES.killSwitch];
  const rawTimeout = raw[ENV_VAR_NAMES.requestTimeoutMs];

  const problems: string[] = [];

  if (!rawToken || rawToken.length === 0) {
    problems.push(
      `${ENV_VAR_NAMES.apiToken} is required (see docs/secret-store-wiring.md)`
    );
  }

  let isEnabled = true;
  if (rawEnabled !== undefined) {
    const lc = rawEnabled.trim().toLowerCase();
    if (lc === "false" || lc === "0" || lc === "off" || lc === "no") {
      isEnabled = false;
    } else if (lc === "true" || lc === "1" || lc === "on" || lc === "yes") {
      isEnabled = true;
    } else {
      problems.push(
        `${ENV_VAR_NAMES.killSwitch} must be true|false|1|0|on|off|yes|no (got "${rawEnabled}")`
      );
    }
  }

  let requestTimeoutMs = DEFAULT_REQUEST_TIMEOUT_MS;
  if (rawTimeout !== undefined) {
    const parsed = Number.parseInt(rawTimeout, 10);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      problems.push(
        `${ENV_VAR_NAMES.requestTimeoutMs} must be a positive integer (got "${rawTimeout}")`
      );
    } else {
      requestTimeoutMs = parsed;
    }
  }

  if (problems.length > 0) {
    throw new EnvValidationError(problems);
  }

  const parseResult = RuntimeEnvSchema.safeParse({
    apiToken: rawToken,
    baseUrl: rawBaseUrl,
    isEnabled,
    requestTimeoutMs,
  });

  if (!parseResult.success) {
    throw new EnvValidationError(
      parseResult.error.issues.map(
        (issue) => `${issue.path.join(".") || "(root)"}: ${issue.message}`
      )
    );
  }

  return parseResult.data;
}

export class EnvValidationError extends Error {
  public readonly problems: readonly string[];
  constructor(problems: readonly string[]) {
    super(`Runtime env validation failed:\n  - ${problems.join("\n  - ")}`);
    this.name = "EnvValidationError";
    this.problems = problems;
  }
}

/**
 * Redact the token from any string for logging.
 * The fetcher and CLI both call this before anything is written to
 * logs, error_detail jsonb, or stdout.
 */
export function redactToken(s: string, token: string): string {
  if (token.length === 0) return s;
  return s.split(token).join("<REDACTED_TOKEN>");
}
