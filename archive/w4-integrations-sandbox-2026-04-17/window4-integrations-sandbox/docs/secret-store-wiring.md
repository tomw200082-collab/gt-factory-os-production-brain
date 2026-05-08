# Secret-store wiring — LIONWHEEL_API_TOKEN

**Owner:** Window 4
**Status:** design note — no runtime code reads secrets from any store yet
**Referenced from:** runtime handoff §E.3, blocker register E.3

## 1. Threat model

The LionWheel shipping-company token grants:

- read access to every task in GT's LionWheel tenant
- read access to every visit, route, driver, and company record in GT's tenant
- write access (POST/PUT/PATCH) — tasks can be created, updated, cancelled

That last point is the reason this token cannot live anywhere an attacker can reach:

- no runtime code should log it
- no error message should contain it
- no `error_detail` jsonb column on `integration_run` should ever store it
- no conversation history, no committed source, no config file in the repo
- no operator terminal scrollback on a shared machine

The token in conversation history (from the prior Window 4 session) is **burned** for production purposes. It must be rotated before Slice 1 runtime lights up.

## 2. Where the token lives

### Production

Canonical storage: **Supabase secrets** (or the ops team's existing secret-store equivalent — Vault, Doppler, AWS SSM Parameter Store, or Supabase Vault within the DB).

Criteria the chosen store must meet:

- at-rest encryption by the platform
- access control keyed to the runtime service account, not operator identity
- audit trail on read
- rotation is a single-API-call affair, not a manual re-deploy
- separate staging and production namespaces (no shared secrets)

### Local development

- `.env.local` file, **never committed**, `.gitignore` already covers `.env*`
- value supplied by the operator running the CLI skeleton

### CI / test environments

- never use the production token
- use the LionWheel sandbox credential documented in contract pack (`c_key_7afa4a75-...`) once it is confirmed safe per blocker G.10

## 3. Env-var naming contract

Locked names (see `src/lionwheel/env.ts`):

| Variable | Purpose | Default | Allowed values |
|---|---|---|---|
| `LIONWHEEL_API_TOKEN` | the shipping-company key | **(none — required)** | non-empty string |
| `LIONWHEEL_BASE_URL` | API base URL | `https://members.lionwheel.com/api/v1` | valid URL |
| `LIONWHEEL_SYNC_ENABLED` | kill-switch | `true` | `true/false/1/0/on/off/yes/no` |
| `LIONWHEEL_REQUEST_TIMEOUT_MS` | per-request timeout | `15000` | positive integer |

The runtime reads these names and only these names. Any rename requires a coordinated change across the Window 4 runtime, the ops runbook, and this document.

## 4. Read path at runtime

```
ops tooling (Vault / Supabase Secrets / etc.)
         │
         │  exposed as env at process start
         ▼
    process.env.LIONWHEEL_API_TOKEN
         │
         │  passed into parseRuntimeEnv()
         ▼
    RuntimeEnv.apiToken
         │
         │  constructor-injected into LionWheelFetcherConfig.apiToken
         ▼
    Fetcher implementation (future)
         │
         │  appended as ?key=<token> query param per contract pack §B.2
         ▼
        HTTPS request to members.lionwheel.com
```

Rules enforced by this path:

1. The token enters the process exactly once, via env.
2. It is held in exactly one place — the fetcher config — after validation.
3. It never appears in logs, error objects, or trace output. The `redactToken()` helper exists in `env.ts` for any string that might incidentally contain it.
4. It is never serialized into `integration_run.error_detail`. Before any response body is written into that jsonb column, the runtime wrapper must apply `redactToken()`.
5. It is never forwarded to a sub-process, a subagent, or an LLM prompt.

## 5. Rotation posture

- Expected rotation cadence: **every 90 days** (proposal; operator sets).
- Rotation on suspicion: **immediate**, with a forced `LIONWHEEL_SYNC_ENABLED=false` during the gap. Ops runbook must document the turnaround.
- Overlap: LionWheel supports one active token per shipping company. There is no dual-active rotation; a short service-side gap (seconds to a few minutes) is unavoidable during rotation. The kill-switch flag must be engaged for that window so no `integration_run` is recorded as `failed` simply because the token was in transit.

## 6. Kill-switch coupling

When `LIONWHEEL_SYNC_ENABLED=false`:

- the fetcher's `isEnabled()` callback returns false
- every fetch method short-circuits to `{ kind: "disabled_by_kill_switch" }`
- the runtime wrapper records `integration_run` rows with `status='superseded'` and `trigger_source='kill_switch'`
- no HTTP is performed; no token is transmitted
- the freshness view transitions to `broken` for LionWheel entities within ~1 minute (per runtime handoff §C.6)

The kill-switch is the ops-team escape hatch during token rotation, rate-limit incidents, or upstream outages.

## 7. What this document does NOT do

- does not choose the secret store vendor (Supabase secrets is the recommendation; ops decides)
- does not write any secret-store client code
- does not provision the env in any actual environment
- does not rotate the current live token (operator action, see blocker register E.3)

## 8. Open items this document depends on

See [blocker-register.md](./blocker-register.md) — specifically E.3 "Operator blockers" (token rotation) and G.11 from the contract pack.
