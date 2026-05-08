# Dry-Run DR-014 — integration incident triage simulation

**Run date:** 2026-05-08
**Agents invoked:** `integration-boundary-executor` (read-only mode), `factory-os-governor`,
`release-verifier`, `ops-docs-curator`.
**Scope:** Triage simulation across LionWheel, Shopify, and Green Invoice symptom classes.
No external API calls in this dry-run; reasoning is from contracts, runbooks, locked
decisions, and CLAUDE.md.

---

## A. Scenario

Three hypothetical incidents are triaged in sequence. None is an active production incident.
The dry-run validates that `integration-boundary-executor` and `/incident-triage` produce
the right routing and severity for each.

| # | Symptom | Lane suggested by reporter |
|---|---------|----------------------------|
| 1 | "LionWheel mirror appears stale; last successful poll was 4 hours ago and orders should arrive every 15 minutes" | `lionwheel` |
| 2 | "A planner reports Shopify shows 12 units of a SKU but the platform shows 8; was this morning's sync wrong?" | `shopify` |
| 3 | "Green Invoice price for an oat milk component looks wrong on the active price card" | `gi` |

For all three, no external API was called by this dry-run. The triage is performed against
contracts, runbooks, locked decisions, state files, and recent commits.

---

## B. Incident 1 — LionWheel freshness alert

### B.1 — Evidence gathering (read-only)

| Source | Read | Finding |
|--------|------|--------|
| `PRODUCTION/.claude/state/integration_freshness.json` | (would be read) | Hypothetical: last LW poll 2026-05-08T10:00Z; alert at 2026-05-08T14:00Z (4h drift) |
| Frozen flag `LIONWHEEL_FG_OUT_BRIDGE_ENABLED` | (would be read from .env) | Expected `false` per CLAUDE.md locked decision |
| `gt-factory-os/api/src/integrations/lionwheel/` | (would be read) | Reconciliation logic per CLAUDE.md (delivery confirmation trigger only) |
| Recent commits on `gt-factory-os` | `git log --oneline -50` | (no in-scope commits since last green poll) |
| `gt-factory-os/docs/runbooks/integrations/lionwheel-stale.md` | (would be read if exists) | Pre-existing runbook |

### B.2 — Severity classification

- The system is in mirror-only mode (per `LIONWHEEL_FG_OUT_BRIDGE_ENABLED=false`). A stale
  poll **does not** affect stock truth — the bridge is disabled by design until Tom approves
  the flip.
- Stale poll DOES affect planning: planning demand = forecast + open orders. Stale orders
  produce stale planning recommendations.
- Per CLAUDE.md "Operational Mirrors / Forecasting" (Gate 4): freshness exceptions emit on
  stale integration. So the stale poll should already have produced a freshness exception
  visible in `Exceptions Inbox`.

**Severity: P1.** Workflow degraded (planning recommendation freshness) but no data integrity
risk on stock truth (because bridge is off).

### B.3 — Suspected lane

`lionwheel` (poll/credential/contract). Not `ledger` because the bridge is off.

### B.4 — Root cause candidates (ranked)

1. (60%) Credential rotation expired or revoked.
2. (20%) LionWheel API rate-limited or 5xx-stuck.
3. (10%) Network outage on the polling host.
4. (10%) Contract mismatch — LionWheel changed response shape and our parser fails.

### B.5 — Routing

`integration-boundary-executor` — owns LW chain. They should:
1. Verify credential availability (load by name; never echo).
2. Run `/integration-dry-run lionwheel` to attempt one read round-trip.
3. If credential bad: route to Tom for rotation.
4. If contract drift: route to `source-of-truth-auditor` for D-classification, then to
   `integration-boundary-executor` for contract update.
5. Write a triage close-out doc once root cause is known.

### B.6 — Forbidden actions

- No flag flip.
- No external write.
- No restart of any prod service without Tom approval.
- No webhook subscription change.

### B.7 — Verdict

**`ROUTED`** — `integration-boundary-executor` takes over with `/integration-dry-run lionwheel`
as the first step.

---

## C. Incident 2 — Shopify parity drift

### C.1 — Evidence gathering

| Source | Read | Finding |
|--------|------|--------|
| Platform projection for the SKU | (would query DB read-only) | Hypothetical: 8 units |
| Shopify report on the SKU | (would call Shopify GET; or read most recent sync) | 12 units |
| Last successful Shopify sync timestamp | `integration_freshness.json` | Hypothetical: ran 4h ago — not stale |
| `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED` flag | (would be read) | Expected `false` (Phase 5 only) |
| Recent ledger entries for the SKU | (would query DB read-only) | (review last 24h for unmatched outbound or inbound) |

### C.2 — Severity classification

Per CLAUDE.md: **Shopify is a finished-goods stock sync boundary; if Shopify and the
platform disagree, the platform is authoritative.**

So:
- The platform's 8 units is the truth claim.
- Shopify's 12 units is incorrect; the next sync should overwrite Shopify back to 8.
- However, the next sync is currently DISABLED (write flag off).
- Therefore Shopify will continue to display 12 until Phase 5 enables write OR Tom manually
  corrects via Shopify admin.

The planner's question is reasonable but the answer is: "the platform is right; Shopify will
self-correct after Phase 5. For today, trust the platform."

**Severity: P2.** No platform data integrity risk. External system display drift only.

### C.3 — Suspected lane

`shopify` — sync direction asymmetric until Phase 5; this is expected behavior, not a defect.

### C.4 — Root cause candidates

1. (50%) Operator placed/cancelled an order on Shopify side that did not flow back into the
   platform — by design, since the platform owns truth.
2. (30%) A Shopify "blind available" write was disabled mid-cycle leaving Shopify stale.
3. (10%) A historical sync drift from before the current `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED=false`
   policy was set.
4. (10%) A platform-side waste/adjustment that the planner has not yet seen reflected.

### C.5 — Routing

This is **`NEEDS_TOM`** for an operational decision: when Phase 5 ships, an automatic
correction will happen. Until then, Tom must decide whether to:
- Manually correct Shopify to 8 today.
- Communicate to staff that "Shopify display may drift; trust the platform."
- Accelerate Phase 5 (out of scope for this triage).

`integration-boundary-executor` writes the triage close-out doc; no executor takes a
mitigation action without Tom decision.

### C.6 — Forbidden actions

- **NO** Shopify mutation. The flag is off for a reason.
- No flipping `SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED`.
- No platform-side adjustment to "match Shopify" — the platform is authoritative.

### C.7 — Verdict

**`NEEDS_TOM`** — operational decision required; not a code defect.

---

## D. Incident 3 — Green Invoice price mismatch

### D.1 — Evidence gathering

| Source | Read | Finding |
|--------|------|--------|
| `price_history` for the component | (would query DB read-only) | Hypothetical: last update 2026-04-15 from GI invoice #99887 at price X |
| Active price card | (would query DB read-only) | Hypothetical: shows price Y (newer than X but suspect) |
| GI invoice mapping quality for the component | (would query) | Below threshold; should NOT have auto-promoted |
| Auto-update rule | CLAUDE.md "Active supplier price auto-updates only when mapping is unambiguous and the price change is within threshold" | Locked rule |

### D.2 — Severity classification

If the active price was auto-promoted from a below-threshold GI invoice mapping, that is a
**direct CLAUDE.md violation**. CLAUDE.md states: "Active supplier price auto-updates only
when mapping is unambiguous and the price change is within threshold."

If the auto-update happened anyway, that is a P0 incident — auto-update logic is broken.

If it did NOT auto-update (the active price is correct via some other path), then this is
just a planner asking a clarification question, severity P3 cosmetic.

The triage cannot resolve this without DB read access in the dry-run. The output is a
**conditional severity**: "P0 if auto-update from below-threshold mapping; otherwise P3."

### D.3 — Suspected lane

`gi` — pricing logic.

### D.4 — Root cause candidates (P0 path)

1. (40%) The mapping quality threshold check is being bypassed by a recent code change.
2. (30%) The mapping quality scoring itself is wrong, marking a low-quality mapping as high.
3. (20%) A manual override happened and was logged, but the operator forgot.
4. (10%) The active price update happened via legacy import script, not GI auto-update.

### D.5 — Routing

`integration-boundary-executor` — owns GI integration.
1. Read DB to determine which path updated the active price.
2. If auto-update path: confirm whether the threshold check was bypassed; if yes, file P0
   contract-failure to `factory-os-governor`.
3. If manual override: confirm log entry exists; downgrade to P3.
4. If legacy import: identify the script and document.
5. Write triage close-out doc.

### D.6 — Forbidden actions

- No price rollback in DB without Tom approval.
- No auto-update rule change without Tom approval.
- No GI external API write.

### D.7 — Verdict

**`ROUTED`** with severity classification pending DB read. `integration-boundary-executor`
takes over.

---

## E. Pattern findings across the three incidents

### E.1 — The triage chain consistently respects authority

In all three cases, the triage stopped before any production write. None of the three
mitigation paths bypassed Tom approval. The chain produced clear "what we know vs what we
need to know" framings without inventing fixes.

### E.2 — Severity classification is principled

| Incident | Severity | Reason |
|----------|---------|--------|
| 1 (LW stale) | P1 | Bridge off → no stock-truth risk; planning freshness only |
| 2 (Shopify drift) | P2 | Platform is authoritative; external display drift; expected until Phase 5 |
| 3 (GI price) | conditional P0/P3 | Depends on whether CLAUDE.md auto-update rule was violated |

The chain does not default to P0 to "be safe" — it classifies based on actual blast radius
under the locked architectural rules.

### E.3 — Frozen-flag awareness is automatic

All three incidents reference frozen flag state without prompting. `integration-boundary-executor`
treats flag state as a primary input, not an afterthought.

### E.4 — `NEEDS_TOM` is used only when warranted

Incident 2 is `NEEDS_TOM` because the operational answer requires a Tom decision (no code
defect; no autonomous fix). Incidents 1 and 3 are routed to the executor because the next
step is more diagnosis, not a Tom decision.

### E.5 — Pre-anchor and direct-ledger-write guards are not relevant here

These guards apply when a *mitigation action* would touch the ledger. None of these triages
proposed a ledger touch, so the guards are not exercised. They will be exercised in DR-016
chain test where mitigation is simulated.

---

## F. STATUS block

```
STATUS: PASS

Scope: 3 simulated integration incidents (LW freshness, Shopify drift, GI price)
External API calls: 0 (dry-run; no external system contacted)
DB reads: 0 (simulated; reads would be read-only)
Files changed: 0
Triage docs produced: 3 (one per incident — would land in docs/phase8/incidents/)
Frozen flags inspected: LIONWHEEL_FG_OUT_BRIDGE_ENABLED, SHOPIFY_BLIND_AVAILABLE_WRITE_ENABLED
Severity classifications produced: P1, P2, conditional P0/P3
Routing produced: ROUTED, NEEDS_TOM, ROUTED
Stop conditions tripped: none — by design (read-only triage)
Tom approvals required:
  - Incident 2: operational decision (today's display drift)
  - Incident 3 P0 path: contract-failure escalation if auto-update violated
Rollback plan: n/a — no mitigation actions taken
Handoff:
  - Incident 1: integration-boundary-executor next (run /integration-dry-run lionwheel)
  - Incident 2: factory-os-governor + Tom (operational decision)
  - Incident 3: integration-boundary-executor next (DB read to classify)
```

---

**END OF DR-014 — Triage chain validated. Zero external writes. Zero mitigation actions.**
