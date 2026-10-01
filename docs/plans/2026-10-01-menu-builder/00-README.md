# GT Menu Builder / Guided Sales Configurator — discovery folder (Session 1)

**Status: DISCOVERY + PRECISION PRODUCT DESIGN. No Menu Builder production implementation has begun.**
**Sales Foundation Gate: HOLD** (GT Pulse Unit A on draft PRs gt-factory-os #329 and gt-factory-os-portal #239; release deferred by Tom 2026-09-30; the next Sales session may expand the design). Implementation stays hard-blocked until that gate passes **and** Tom unlocks it, whatever the state of the product spec.

> Design-phase artifacts. **Not authority docs.** Tom's decisions live in his words and, where they touch sales doctrine, in `Sales-Machine/doctrine/decisions.md`. Governing instruction: the Menu Builder masterprompt Tom pasted on 2026-10-01 (three sessions: discovery → independent review → implementation).

## Files

| File | What it is |
|---|---|
| `ground-truth.md` | The reconstructed reality: the lead → first-order journey as it runs, the approved and built GT Pulse state, the customer ordering portal, the staff sales corridor, the data map, the decisions that already bind the Builder, conflicts, re-run recipes |
| `dependency-ledger.md` | **Builder ↔ Sales Dependency Ledger** (mandatory): 18 dependencies, each with source, status, provisional assumption and recheck item |
| `decision-ledger.md` | Decision Ledger (MB-D01…) and the conflicts/drift found (C-01…C-12) |
| `01-placement-recommendation.md` | MB-D01: where the Builder sits in the journey — owner-minded recommendation put to Tom |
| `evidence/` | Verbatim read-only reconstructions dated 2026-10-01: gt-site lead funnel · customer ordering portal · sales/lead backend · staff sales corridor · drinks/products data map |

Later files on this branch: the Decision-Ready Product Spec (incl. the Sales System Integration Contract), the Product Review Handoff for Session 2.

## Rules this folder follows

- Design may run in parallel with the Sales workstream; shared implementation may not. Nothing here changes the lead journey, CRM schema, GT Pulse behaviour, pricing, order handoff, WhatsApp automation, portal routes or production.
- Every dependency on unfinished Sales work is in `dependency-ledger.md`; every consequential decision in `decision-ledger.md` with a status (`FINAL` · `PROVISIONAL — SALES DEPENDENCY` · `NEEDS DATA` · `DEFERRED` · `OPEN`).
- Before implementation: FINAL SALES RECONCILIATION PASS against the accepted Sales code, spec updated first, then `SALES FOUNDATION GATE: PASS | HOLD`.
