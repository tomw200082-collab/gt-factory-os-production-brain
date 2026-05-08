# Signals — GT Factory OS harness

Shared signal definitions used by subagents and by hooks. Authoritative source is `EXECUTION_POLICY.md` (which itself mirrors the `factory-os-autonomous-builder` skill). This file exists to keep signal semantics close to the code that enforces them.

## `FILE_READY(form)`
- **Meaning:** files, paths, or implementation surfaces for the named form exist in a usable handoff shape.
- **Does NOT authorize:** W2 canonical authoring. `FILE_READY` is necessary, not sufficient.
- **Recorded where:** informal. Mentioned in handoff docs. No state file.

## `RUNTIME_READY(form)`
- **Meaning:** W1's execution-authorization signal. The backend / runtime contract for the named form is sufficiently closed and evidenced. W2 may enter Mode B for that one form only.
- **Does authorize:** W2 canonical authoring for the named form only. A separate `RUNTIME_READY(other_form)` is required for each additional form. Exiting Mode B (after local portal E2E green) returns W2 to Mode A.
- **Recorded where:** `.claude/state/runtime_ready.json`. The file starts as `{ "signals": [] }`. W1 appends entries with fields: `form` (e.g., "GoodsReceipt"), `emitted_at` (ISO-8601 UTC), `evidence_path` (relative path to backend contract doc or test output proving closure), `emitted_by` (always `"executor-w1"`). Example entry:
  ```json
  { "form": "GoodsReceipt", "emitted_at": "2026-04-17T14:30:00Z", "evidence_path": "Projects/gt-factory-os/docs/goods_receipt_runtime_contract.md", "emitted_by": "executor-w1" }
  ```
- **Who writes:** `executor-w1` only. Any other agent writing here is an ownership conflict.
- **Who reads:** `executor-w2` before entering Mode B; `pre_tool_use.sh` before allowing portal canonical writes.

## `TOOL_FAILURE_UNCLEARED`
- **Meaning:** a W4 rolling-requirements artifact whose same tool failure has repeated after one retry. The artifact is parked.
- **Does NOT authorize:** silent continuation to the next backlog item. W4 may continue only if no open `contract_failure`, no open `assumption_failure`, and no dependency collision exist. Unclear dependency → governor escalation.
- **Does NOT trigger:** project-wide reassessment.
- **Status, not class:** lives inside the `tool_failure` class. There are exactly five failure classes.

## Five failure classes (locked)
1. `contract_failure` — violates locked contract. No retry. Human checkpoint mandatory.
2. `data_failure` — real input is missing / malformed / stale. Retry after upstream repair.
3. `tool_failure` — environmental failure. Retry once, then escalate per §8. W4 variant: retry once, then `TOOL_FAILURE_UNCLEARED`.
4. `assumption_failure` — guessing a value not in the contract pack. No retry. Human checkpoint mandatory.
5. `ownership_conflict` — two windows touching the same surface, or a move outside the active lane. Governor arbitration required.

## Window-label sanity
If a pasted message's window label does not match the surface touched, correct the classification **before** routing. Record the relabel explicitly: `"message labeled WX → reclassified as WY because <reason>"`. Never pass a mislabeled window through to later steps.

## Artifact visibility (W5 / governor review)
A governor review is valid only when the artifact is:
1. pasted inline in full, **or**
2. at a verified readable path on disk (path exists, file readable, content inspected).

**Summary-only review is forbidden.** If only a summary is available, emit `assumption_failure` and request the full artifact.

## No-dead-air
Every reply ends with one concrete next operator action for Tom. "Waiting", "all lanes idle", silence are not valid output states.