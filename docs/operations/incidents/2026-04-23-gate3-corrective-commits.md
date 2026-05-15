# Incident reference — Three corrective commits during Gate 3 DB run (2026-04-18 → 2026-04-23)

> **Origin:** migrated verbatim from `CURRENT_STATE.md` §"Three corrective commits during Gate 3 DB run (reference)" during Phase 8 Run F Wave 4 Hole 2 cleanup (2026-05-09). The original section in CURRENT_STATE.md was removed.
>
> **Type:** historical reference / corrective-commit log. Not an active incident — Gate 3 is currently PARTIAL for an unrelated reason (LionWheel pick-reconciliation chain repair corridor in flight).
>
> **Cross-reference:** `gate3_closure_decision_pack.md`; `CURRENT_STATE.md` §Gate 3 — Stock Truth.

---

## Three corrective commits during Gate 3 DB run

These three commits were the in-flight corrections that landed during the Gate 3 DB tranche to close test-shape and import-order defects. Each was a small bounded fix; together they unblocked the parity gate proof.

- `c03990c` — 0001 pgTAP plan count 23 → 26 (3 `col_is_pk` miscounted)
- `797e7cf` — `import_masters.ts` BOM import (bom_head / bom_version / bom_lines + FK ordering)
- `88af93e` — 0009 pgTAP P6b expect 2 not 1 (EXCEPT symmetric diff counts both sides)

## Why this is preserved as a reference

The three commits are not a current open issue, but they are useful as:
- audit trail showing how the Gate 3 DB tranche actually closed (the closure pack cited the live pgTAP counts; these commits made those counts true);
- pattern reference for future plan-count vs assertion-count mismatches and FK-ordered import bugs.

No further action is required. Future Gate 3 follow-ups (e.g. LionWheel pick-reconciliation chain repair) are tracked separately under the active corridor in `ACTIVE_NOW.md` and the gate status in `CURRENT_STATE.md`.
