# /incident-triage

Read-only diagnosis of an integration freshness issue, sync drift, exception spike, or other
production-affecting incident. Coordinates `integration-boundary-executor`, `factory-os-governor`,
and `release-verifier` to classify severity and lane. Does not mutate production data. Does not
flip flags. Does not deploy.

## Purpose

When the system shows symptoms — stale poll, parity drift, exception spike, freshness alert,
or a user-reported anomaly — `/incident-triage` produces a structured triage report that names
the suspected root cause, classifies severity, and routes to the correct executor for follow-up.
The triage itself never writes; it gathers evidence and routes.

## Usage

```
/incident-triage <description-or-symptom>
/incident-triage lionwheel-stale
/incident-triage shopify-parity-drift
/incident-triage gi-price-mismatch
/incident-triage exception-spike <category>
/incident-triage user-report <one-line-paraphrase>
/incident-triage stock-discrepancy <item-name-or-id>
```

## Arguments

| Arg | Required | Description |
|-----|---------|-------------|
| description | yes | Free-text or one of the canonical incident slugs above |
| --since | no | ISO timestamp limiting the lookback window |
| --severity-suggest | no | Initial severity guess (`P0`/`P1`/`P2`/`P3`); the triage may override |
| --route | no | If known, the lane to investigate first (`lionwheel`, `shopify`, `gi`, `ledger`, `portal`, `planning`, `infra`) |

## Agents involved

| Agent | Role |
|-------|------|
| `integration-boundary-executor` | Reads integration freshness, contract drift, frozen flag state |
| `factory-os-governor` | Issues severity classification and lane routing |
| `release-verifier` | (Optional) verifies whether a recent merge or deploy is implicated |
| `source-of-truth-auditor` | (Optional) checks for contract drift if the symptom suggests it |
| `ops-docs-curator` | (Optional) checks runbooks for known-issue references |

## Required inputs

1. The reported symptom or description.
2. `PRODUCTION/.claude/state/integration_freshness.json` — last successful poll log.
3. `PRODUCTION/.claude/state/runtime_ready.json` — current signal state.
4. The most recent parity / rebuild verification result for the affected surface.
5. Recent commits (`git log --oneline -50`) on relevant repos.
6. Recent deploys (`vercel deployments list` or equivalent — read-only, optional).
7. The relevant integration runbook (if `lionwheel`, `shopify`, `gi`).
8. The relevant contract doc (if a contract failure is suspected).

## Required outputs

A triage report at `PRODUCTION/docs/phase8/incidents/INC-<NNN>-<date>-<slug>.md` containing:

1. **Incident metadata** — date, time, reporter, suspected lane.
2. **Symptom** — concrete one-paragraph description; what the user / system observed.
3. **Severity classification** — one of:
   - `P0` — production data integrity at risk (stock truth wrong, ledger writable directly,
     external system out of sync with platform on critical path).
   - `P1` — operator workflow blocked but no data integrity risk (form fails, dashboard stale,
     planner cannot complete a task).
   - `P2` — degraded but workable (slow, ugly, log spam, minor freshness drift).
   - `P3` — cosmetic.
4. **Suspected lane** — one of `backend`, `portal`, `lionwheel`, `shopify`, `gi`, `ledger`,
   `planning`, `jobs`, `docs`, `infra`.
5. **Evidence gathered** — paths, commits, signal IDs, freshness deltas, exception counts.
6. **Root-cause candidates** — ordered list with confidence scores.
7. **Frozen flag state** — both flags' value with timestamp.
8. **Recent deploys / merges** — list of deploys / merges in the last 7 days that could be
   implicated.
9. **Routing** — which executor takes the next step (with explicit handoff packet contents).
10. **Mitigation suggestions** — read-only suggestions; never executed by this command.
11. **Verdict** — one of:
    - `ROUTED` — triage complete; named executor takes over.
    - `NEEDS_TOM` — incident requires Tom decision before any executor acts (e.g. flag flip).
    - `NO_INCIDENT` — symptom did not correspond to a real defect (e.g. expected behavior).

## Allowed scope (read-only diagnosis)

- Read all relevant state files, logs, runbooks, contracts.
- Read recent git log and (optionally) deploy history.
- Read external API health endpoints (GET only).
- Write the triage report doc under `PRODUCTION/docs/phase8/incidents/`.
- Append a triage entry to `PRODUCTION/docs/phase8/incidents/INDEX.md`.

## Forbidden scope

- **No code changes.**
- **No DB writes.**
- **No external POST/PUT/PATCH/DELETE.**
- **No flag flips.**
- **No deploys.**
- **No mutations to production data.**
- **No Slack / email notifications.** (The triage report can be pasted into a notification by a
  human; the command does not send.)
- **No autonomous remediation.** Triage is diagnosis, not fix.

## Side-effect policy

Writes the triage doc and the optional INDEX entry. No other state changes. Specifically:
- Does not roll back any deploy.
- Does not pause any job.
- Does not flip any flag.
- Does not write to any external system.

## Validation requirements

The command must verify, before producing the report:

1. The symptom maps to a concrete observable (file, log, signal, exception, or user-reported route).
2. The frozen flag state has been read (not assumed).
3. Recent merges and deploys have been considered.
4. At least one canonical evidence path is named.
5. The severity classification follows the documented thresholds (no "P1 because it feels like P1").

## Tom approval triggers

The triage report alone authorizes nothing. Tom must explicitly authorize:

- Any flag flip suggested by the triage.
- Any external write suggested by the triage.
- Any rollback of a recent deploy.
- Any production DB write.
- Any change in lane priority that delays a planned phase / wave transition.

## Stop conditions

| Condition | Action |
|-----------|--------|
| Triage suggests a flag flip is needed | `NEEDS_TOM` — produce the dry-run-required note |
| Triage suggests a rollback of a recent deploy | `NEEDS_TOM` |
| Symptom is a user-reported issue with no observable evidence | `NO_INCIDENT_VERIFIED` — request more info from reporter |
| Triage uncovers a CLAUDE.md violation in production code | `P0` + route to factory-os-governor immediately |
| Triage uncovers a frozen flag in unexpected state | `P0` + `frozen_flag_unexpected_state` |
| Triage uncovers direct ledger write attempt in production | `P0` + `direct_ledger_write_attempted` + Tom |

## GitHub / mobile usability

- The triage report is plain markdown; suitable for paste into any incident comms channel.
- The command does not interact with GitHub except read-only `gh` for PR / commit history.

## Local-only limitations

- Triage requires local access to the state files. Triages run on a fresh machine without
  state access produce a `NO_LOCAL_STATE` verdict instead of a real triage.

## Example

```
/incident-triage lionwheel-stale --since 2026-05-08T10:00:00Z
/incident-triage shopify-parity-drift
/incident-triage user-report "planner sees stale forecast on Tuesday morning"
/incident-triage stock-discrepancy "Margarita Strawberry 250ml"
```

## Not usable for

- Mitigating the incident (mitigation is the routed executor's job).
- Flipping flags.
- Rolling back deploys.
- Writing to production data.
- Sending notifications.
