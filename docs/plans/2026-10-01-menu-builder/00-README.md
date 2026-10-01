# GT Menu Builder / Guided Sales Configurator — discovery folder (Session 1)

**Status: PRODUCT DESIGN APPROVED — WAITING FOR SALES FOUNDATION (Tom, 2026-10-01). No Menu Builder production implementation has begun.** Next: Session 2 (independent review, see `07-product-review-handoff.md`).
**Sales Foundation Gate: HOLD** (GT Pulse Unit A on draft PRs gt-factory-os #329 and gt-factory-os-portal #239; release deferred by Tom 2026-09-30; the next Sales session may expand the design). Implementation stays hard-blocked until that gate passes **and** Tom unlocks it, whatever the state of the product spec.

> Design-phase artifacts. **Not authority docs.** Tom's decisions live in his words and, where they touch sales doctrine, in `Sales-Machine/doctrine/decisions.md`. Governing instruction: the Menu Builder masterprompt Tom pasted on 2026-10-01 (three sessions: discovery → independent review → implementation).

## Files

| File | What it is |
|---|---|
| `ground-truth.md` | The reconstructed reality: the lead → first-order journey as it runs, the approved and built GT Pulse state, the customer ordering portal, the staff sales corridor, the data map, the decisions that already bind the Builder, conflicts, re-run recipes |
| `dependency-ledger.md` | **Builder ↔ Sales Dependency Ledger** (mandatory): 19 dependencies (DL-01…DL-19) and four proposed contracts (IC-1…IC-4), each with source, status, provisional assumption and recheck item |
| `decision-ledger.md` | Decision Ledger (MB-D01…) and the conflicts/drift found (C-01…C-12) |
| `01-placement-recommendation.md` | MB-D01: placement — Session 1 analysis; **deferred by Tom** |
| `02-finish-and-quantity-recommendation.md` | MB-D08 + MB-D03: the two-layer finish and the zero-question starter kit with the ₪800 round-up — **approved** |
| `03-economics-recommendation.md` | MB-D04: which numbers the Builder shows — **approved** |
| `04-discovery-model-recommendation.md` | MB-D06: groups, curated start, consequence chip, my-menu bar — **approved** |
| `05-integration-and-architecture-decisions.md` | MB-D02/D07/D09/D10/D11/D12 and the Sales System Integration Contract proposal; the 24 h task — **approved** |
| `06-decision-ready-product-spec.md` | **The Decision-Ready Product Spec** (36 sections, copy batch, acceptance criteria, unresolved assumptions) — **approved by Tom 2026-10-01** |
| `07-product-review-handoff.md` | **Product Review Handoff** for Session 2: everything a fresh session needs to audit the product without this conversation |
| `evidence/` | Verbatim read-only reconstructions dated 2026-10-01: gt-site lead funnel · customer ordering portal · sales/lead backend · staff sales corridor · drinks/products data map |

## Rules this folder follows

- Design may run in parallel with the Sales workstream; shared implementation may not. Nothing here changes the lead journey, CRM schema, GT Pulse behaviour, pricing, order handoff, WhatsApp automation, portal routes or production.
- Every dependency on unfinished Sales work is in `dependency-ledger.md`; every consequential decision in `decision-ledger.md` with a status (`FINAL` · `PROVISIONAL — SALES DEPENDENCY` · `NEEDS DATA` · `DEFERRED` · `OPEN`).
- Before implementation: FINAL SALES RECONCILIATION PASS against the accepted Sales code, spec updated first, then `SALES FOUNDATION GATE: PASS | HOLD`.
