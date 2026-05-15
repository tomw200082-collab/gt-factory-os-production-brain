# Historical State Snapshots — Index

> **Purpose:** preserve point-in-time state material that has been moved out of the live `CURRENT_STATE.md` to keep that file scoped to the allowed sections (gate status, completion %, critical path, UNRESOLVED, failure modes, UX gate, active corridor pointer).
>
> **Read order:** newest first. Each snapshot states its origin section and its date of capture.
>
> **Authority status:** historical / read-only. Not authoritative on current state. For current state, read `CURRENT_STATE.md` and `ACTIVE_NOW.md`.
>
> **Maintained by:** `ops-docs-curator` (writes; under `factory-os-governor` approval).

---

## Snapshots

| Date captured | Snapshot file | Origin section in CURRENT_STATE.md (pre-cleanup) | Notes |
|---|---|---|---|
| 2026-05-08 | [2026-05-08-planning-corridor-detailed-state.md](2026-05-08-planning-corridor-detailed-state.md) | §"Active corridor — Planning Corridor v1 (baseline 2026-04-30)" + main-tip progression + RUNTIME_READY signal listing + Gate 3 prior closure evidence + Canonical paths | Preserves the full evidence chain across Shopify v2 corridor, Professional Stock-Truth Monitoring corridor, Daily Production Plan, Two-Head BOM Repair, planning corridor cycles 1–8, and the Gate 5 14-commit tranche listing. |
| 2026-05-08 | [2026-05-08-phase8-ai-brain-rewrite-snapshot.md](2026-05-08-phase8-ai-brain-rewrite-snapshot.md) | §"Phase 8 Run B + Run C status" + §"Phase 8 Run F status" + §"Phase 8 Run F.2 / F.2b status" | AI Brain rewrite milestones — Run B (production execution agents + commands), Run C (FLOW-003 closure), Run F (kernel rewrite), Run F.2 / F.2b (private remote push), Run G (in-progress closure). |
| 2026-04-25 | [2026-04-25-ralph-loop-snapshot.md](2026-04-25-ralph-loop-snapshot.md) | §"Last calibration" header (2026-04-27 line) + §"Ralph Loop corridor status (2026-04-25 — RE-AUDIT COMPLETE)" | Re-audit findings — exception deep links, admin-screen API wiring, Tom Tax check, completed corridors table at the time. |
| 2026-04-23 | [2026-04-23-layer-0-snapshot.md](2026-04-23-layer-0-snapshot.md) | §"Last calibration" header (2026-04-23 line) + §"Layer 0 validation — SUBSTANTIALLY COMPLETE (2026-04-23)" | Infrastructure validation, first live production event, closed-loop verification, Layer 0 verdict CLOSED. |

## Move history

- **2026-05-09 — Phase 8 Run F Wave 4 Hole 2:** all four snapshots above were created in this cleanup pass. Origin file: `CURRENT_STATE.md` (pre-cleanup line counts: 554). The four snapshots together preserve every line of removed historical content. The `CURRENT_STATE.md` rewrite kept only the Tom-approved allowed sections (gate status, completion %, critical path, UX gate, active corridor pointer, UNRESOLVED items, likely failure modes).
