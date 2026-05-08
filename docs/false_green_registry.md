# GT Factory OS — False-Green Registry

> **Purpose:** Prevents false-readiness claims from being re-introduced in future planning cycles. Every entry records a claim that overstated the system's real operational state, what the actual state was, and how it was detected.
>
> **Schema per entry:** Claim | Source | Actual state | How detected | Corrective note

---

## Entries

| Claim | Source | Actual state | How detected | Corrective note |
|-------|--------|-------------|--------------|----------------|
| "All v1 gates CLOSED — system is done" | Gate closure packs, CURRENT_STATE.md | Code layer complete; zero real operators have ever used the system; zero real stock events in production DB | Direct audit 2026-04-23: confirmed no production stock events, Tom has never logged in via magic-link | Gate closure = code + tests pass. Operational readiness = real operators using real forms with real data. These are different axes. |
| "RUNTIME_READY signals prove forms work" | `.claude/state/runtime_ready.json` | Signals mean handlers were tested with HTTP fixtures. No real operator has ever submitted any form to the production database. | Direct audit 2026-04-23 | RUNTIME_READY = handler was written and tested. Not: a real operator used this in production. Operational use has never happened. |
| "Gate 3 CLOSED / Stock Truth established" | `gate3_closure_decision_pack.md` | Ledger/anchors/projection are genuinely correct — against 209 imported seed anchors. Zero real daily events have ever been posted. The first real GR post is the first real parity test under live conditions. | Direct audit 2026-04-23 | "Stock truth" at DB/contract layer is correct. "Stock truth" as an operational fact (trustworthy running balances from real operator events) does not yet exist. |
| "Portal makes zero real API calls" | Exploration agent (analyzed wrong directory) | The exploration analyzed `PRODUCTION/portal/` (a separate mock-only workstream). The canonical portal `window2-portal-sandbox/` has full Supabase auth, real API proxy, and scores 86/100 on the internal readiness scorecard. | Direct investigation of `C:/Users/tomw2/Projects/window2-portal-sandbox/` 2026-04-23 | Always verify which portal directory is being analyzed. The canonical portal is `window2-portal-sandbox/`, not `PRODUCTION/portal/`. |
| "Auth is not implemented — 2-4 weeks to wire" | Initial planning session exploration | Auth is fully implemented: Supabase magic-link, `/auth/callback`, middleware session refresh, JWT forwarding in API proxy, self-link mechanism. Portal deployed on Vercel with auth working. | Direct code inspection of `window2-portal-sandbox/src/app/(auth)/`, `src/middleware.ts`, `src/lib/api-proxy.ts` | The gap was a false-green in reverse: work claimed as "not done" was actually complete. Layer 0 is a validation sprint, not an implementation sprint. |
| "rebuild_verifier() = 0 means stock truth is verified" | Gate 3 closure evidence | True against 209 seed anchors in a clean import. Not yet verified after a stream of real events with real corrections, reversals, and concurrent submissions. | Direct audit 2026-04-23 | rebuild_verifier() = 0 after seeds is necessary but not sufficient. The first real operational cycle (2+ weeks of live events + one physical count) is the real parity test. |

---

*Registry initiated: 2026-04-23.*
*Next update: after any audit that finds a claim overstating operational readiness.*
