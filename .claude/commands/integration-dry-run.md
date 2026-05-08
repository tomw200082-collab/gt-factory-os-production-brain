# /integration-dry-run

Run an integration dry-run for LionWheel, Shopify, Green Invoice, or a Supabase Edge Function in
**read-only / dry-post-only mode**. Produces evidence sufficient to request a Tom-approved flag
flip or external-write authorization. No external writes occur during the dry-run itself.

## Purpose

Establish that an integration handler is correct, freshness is healthy, and frozen flags are in
expected state — *before* requesting any production write authorization or flag flip. Produces
a dry-run evidence document that becomes the input to a `factory-os-governor` decision.

## Usage

```
/integration-dry-run <provider>
/integration-dry-run lionwheel
/integration-dry-run shopify
/integration-dry-run green-invoice
/integration-dry-run lionwheel --task <task-id>
/integration-dry-run shopify --skus <comma-list>
/integration-dry-run green-invoice --document <doc-id>
```

## Arguments

| Arg | Required | Description |
|-----|---------|-------------|
| provider | yes | One of `lionwheel`, `shopify`, `green-invoice`, `edge-function:<name>`, `job:<name>` |
| --task | no | LionWheel task id to focus the dry-run on |
| --skus | no | Shopify SKU list to focus the dry-run on |
| --document | no | Green Invoice document id to focus the dry-run on |
| --since | no | ISO timestamp for "since" parameter where the integration supports it |
| --save | no | If `true`, save dry-run evidence to `PRODUCTION/docs/phase8/dry-runs/`; default `true` |

## Agents involved

| Agent | Role |
|-------|------|
| `integration-boundary-executor` | Runs the dry-run; produces evidence doc |
| `factory-os-governor` | Reviews evidence; issues PROCEED / HOLD on subsequent flag flip or external write |
| `release-verifier` | (Optional) verifies dry-run readiness before production cutover |

## Required inputs

1. The named provider and any focus argument.
2. Current state of frozen flags (`LIONWHEEL_FG_OUT_BRIDGE_ENABLED`, `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`).
3. Latest successful poll timestamp for the integration (freshness gate).
4. Integration credential availability (verified by name; never echo value — print
   `SET len=N` only per `feedback_env_display_allowlist.md`).
5. The relevant integration contract doc in `gt-factory-os/docs/integrations/<provider>.md`.

## Required outputs

A dry-run evidence document at `PRODUCTION/docs/phase8/dry-runs/DR-<NNN>-<provider>-<surface>.md`,
containing:

1. **Run metadata** — provider, environment, timestamp, agent, focus argument.
2. **Frozen flags state** — current value of every relevant flag with timestamp.
3. **Freshness check** — last successful poll, last success delta, expected vs actual.
4. **Sample payload (read)** — one full read response from the integration, with secrets
   masked (`SET len=N`).
5. **Transform validation** — the read response transformed by the handler, validated
   against the contract; any drift reported.
6. **Dry-post simulation** — the write payload that *would* be sent if the flag were on,
   shown but **not sent**. Idempotency key shown.
7. **Bridge readiness** — RUNTIME_READY signal status; whether the chain is wired to a
   route that does not exist or has not shipped.
8. **Soak status** — for flag-flip readiness: hours since last flag transition; whether
   soak ≥ 24h has elapsed.
9. **Stop conditions tripped** — any of the integration-boundary-executor stop conditions.
10. **Verdict** — one of:
    - `READY_FOR_FLIP_REQUEST` — clean; Tom may now authorize a flag flip.
    - `READY_FOR_EXTERNAL_WRITE_REQUEST` — clean; Tom may now authorize a one-off external write.
    - `NOT_READY` — named blockers; does not yet justify a Tom request.

## Allowed scope (dry-run only)

- Read external API endpoints (GET only) for the named provider.
- Read local DB (read-only) for handler state.
- Read contract docs and runbooks.
- Write the dry-run evidence document under `PRODUCTION/docs/phase8/dry-runs/`.
- Append freshness state to `PRODUCTION/.claude/state/integration_freshness.json` (append-only).

## Forbidden scope

- **No external POST/PUT/PATCH/DELETE** to any provider during the dry-run.
- **No flag flip** — the dry-run produces evidence to request a flip; flipping is a
  separate, Tom-approved action.
- **No DB writes** to production.
- **No `supabase functions deploy`** during the dry-run.
- **No webhook subscription changes.**
- **No ledger writes** — direct or indirect.
- **No credential changes.**

## Side-effect policy

**Read-only on external systems.** Local-only writes are limited to:
- The dry-run evidence document.
- The integration freshness append-only log.

No external state changes during the dry-run. Period.

## Validation requirements

The command must verify, before producing the evidence doc:

1. Frozen flags are in expected state (`false` for both unless Tom has authorized otherwise).
2. The integration credential is loadable (verified by name only; never echo).
3. At least one read round-trip succeeds and parses cleanly against the contract.
4. The dry-post payload would be valid against the contract.
5. The handler's idempotency key is deterministic and collision-free.
6. The pre-anchor guard (per CLAUDE.md) is respected for LionWheel chain dry-runs.

## Tom approval triggers

The dry-run itself is a `no-approval-required` action. The follow-up actions it enables
require explicit Tom written approval:

- Flipping `LIONWHEEL_FG_OUT_BRIDGE_ENABLED`.
- Flipping `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`.
- Any external write (POST/PUT/PATCH/DELETE) to a production integration.
- `supabase functions deploy <name>`.
- Any new webhook subscription.

The dry-run evidence doc is the *input* to those Tom-approval conversations, not a substitute
for them.

## Stop conditions

| Condition | Action |
|-----------|--------|
| Frozen flag found unexpectedly `true` | `NOT_READY` + `frozen_flag_unexpected_state` signal |
| Credential not loadable | `NOT_READY` + `data_failure` signal; never silently fall back to PROD |
| Contract drift detected (response shape != contract) | `NOT_READY` + `stale_contract_reference` |
| LionWheel non-terminal status trigger attempted | `NOT_READY` + `lw_non_terminal_trigger_rejected` |
| Forbidden movement_type emission attempted | `NOT_READY` + `forbidden_movement_type_attempted` |
| Pre-anchor pick attempt | `NOT_READY` + `lw_pick_pre_anchor_skipped` |
| GI auto-price-update with quality below threshold | `NOT_READY` + `gi_price_mapping_quality_below_threshold` |
| Shopify on-hand parity drift > threshold | `NOT_READY` + `shopify_parity_drift` |

## GitHub / mobile usability

- This command does not interact with GitHub.
- The dry-run evidence doc is plain markdown; suitable for pasting into a Tom-approval
  conversation or attaching to a PR.

## Local-only limitations

- The dry-run requires the local environment to have the integration credential loaded.
  If running on a fresh machine, the credential must be available before the dry-run
  produces meaningful evidence.

## Example

```
/integration-dry-run lionwheel --task 12345
/integration-dry-run shopify --skus GT-001,GT-002,GT-003
/integration-dry-run green-invoice --document 99887
```

## Not usable for

- Performing production external writes.
- Flipping frozen flags.
- Deploying Supabase Edge Functions.
- Subscribing webhooks.
- Mutating credentials.
