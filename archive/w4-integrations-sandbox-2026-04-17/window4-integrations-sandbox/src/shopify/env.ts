/**
 * Typed env parsing for the Shopify FG-sync runtime.
 *
 * Same pattern as LionWheel's env.ts: pure validation, caller passes the
 * record, typed errors, token never logged. Kill switch evaluated here
 * and surfaced as a boolean on RuntimeEnv.
 */

import { z } from "zod";

export const ENV_VAR_NAMES = {
  apiToken: "SHOPIFY_ADMIN_API_TOKEN",
  shopDomain: "SHOPIFY_SHOP_DOMAIN",
  apiVersion: "SHOPIFY_ADMIN_API_VERSION",
  killSwitch: "SHOPIFY_SYNC_ENABLED",
  requestTimeoutMs: "SHOPIFY_REQUEST_TIMEOUT_MS",
} as const;

/**
 * Default API version: 2026-04 — the minimum that requires @idempotent.
 * Using an older version would let the runtime skip idempotency silently,
 * which is a safety regression.
 */
export const DEFAULT_API_VERSION = "2026-04";
export const DEFAULT_REQUEST_TIMEOUT_MS = 30_000;

export const RuntimeEnvSchema = z.object({
  apiToken: z.string().min(1, "SHOPIFY_ADMIN_API_TOKEN must not be empty"),
  shopDomain: z
    .string()
    .regex(/^[a-z0-9-]+\.myshopify\.com$/i, "SHOPIFY_SHOP_DOMAIN must be *.myshopify.com"),
  apiVersion: z.string().regex(/^\d{4}-\d{2}$/, "SHOPIFY_ADMIN_API_VERSION must be YYYY-MM"),
  isEnabled: z.boolean(),
  requestTimeoutMs: z.number().int().positive(),
});
export type RuntimeEnv = z.infer<typeof RuntimeEnvSchema>;

export class EnvValidationError extends Error {
  public readonly problems: readonly string[];
  constructor(problems: readonly string[]) {
    super(`Shopify runtime env validation failed:\n  - ${problems.join("\n  - ")}`);
    this.name = "EnvValidationError";
    this.problems = problems;
  }
}

export function parseRuntimeEnv(raw: Record<string, string | undefined>): RuntimeEnv {
  const rawToken = raw[ENV_VAR_NAMES.apiToken];
  const rawDomain = raw[ENV_VAR_NAMES.shopDomain];
  const rawVersion = raw[ENV_VAR_NAMES.apiVersion] ?? DEFAULT_API_VERSION;
  const rawEnabled = raw[ENV_VAR_NAMES.killSwitch];
  const rawTimeout = raw[ENV_VAR_NAMES.requestTimeoutMs];

  const problems: string[] = [];

  if (!rawToken || rawToken.length === 0) {
    problems.push(`${ENV_VAR_NAMES.apiToken} is required`);
  }
  if (!rawDomain || rawDomain.length === 0) {
    problems.push(`${ENV_VAR_NAMES.shopDomain} is required`);
  }

  let isEnabled = true;
  if (rawEnabled !== undefined) {
    const lc = rawEnabled.trim().toLowerCase();
    if (["false", "0", "off", "no"].includes(lc)) isEnabled = false;
    else if (["true", "1", "on", "yes"].includes(lc)) isEnabled = true;
    else
      problems.push(
        `${ENV_VAR_NAMES.killSwitch} must be true|false|1|0|on|off|yes|no (got "${rawEnabled}")`
      );
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

  if (problems.length > 0) throw new EnvValidationError(problems);

  const parsed = RuntimeEnvSchema.safeParse({
    apiToken: rawToken,
    shopDomain: rawDomain,
    apiVersion: rawVersion,
    isEnabled,
    requestTimeoutMs,
  });
  if (!parsed.success) {
    throw new EnvValidationError(
      parsed.error.issues.map((i) => `${i.path.join(".") || "(root)"}: ${i.message}`)
    );
  }
  return parsed.data;
}

export function redactToken(s: string, token: string): string {
  if (token.length === 0) return s;
  return s.split(token).join("<REDACTED_TOKEN>");
}
