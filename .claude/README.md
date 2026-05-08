# GT Factory OS — Claude Code Autonomy Harness

Project-local harness so Claude Code can work on GT Factory OS with more safe autonomy and less operator babysitting. **Not a runtime dependency of Factory OS** — this is build tooling.

## What this harness does
- **Scopes work to a single owning lane** via five subagents (W1, W2, W4 executors; verifier; governor).
- **Blocks cross-lane and destructive writes** via project permissions and a `PreToolUse` hook.
- **Keeps the opening context thin** — `SessionStart` hook loads only `claude.md`, `CURRENT_STATE.md`, `EXECUTION_POLICY.md`, `ACTIVE_NOW.md` (authority-layer files) and prints a compact state summary. No long memory dumps.
- **Prevents "PASS without evidence"** via `SubagentStop` hook.
- **Forbids dead-air endings** via `Stop` hook — every session must end with one immediate next move for Tom.

## What this harness does **not** do
- It does **not** implement Factory OS features. Agents write prompts and code for the build; they are not live operational components.
- It does **not** override locked project decisions. Any attempt to do so produces `contract_failure` and halts.
- It does **not** connect to live integrations. MCP config contains placeholders only; real credentials must be supplied out-of-band.
- It does **not** bypass safety via `--dangerously-skip-permissions`. Destructive commands require explicit escalation.

## How to run work through W1 / W2 / W4

1. **Start the session.** `SessionStart` prints the compact state summary. If `ACTIVE_NOW.md` is stale (older than a few days), refresh it before dispatching work.
2. **Dispatch to the right lane.** Use the `Agent` tool and set `subagent_type` to the matching executor:
   - `executor-w1` — DB / schema / migrations / tests / imports / verification
   - `executor-w2` — canonical portal (Mode A by default; Mode B only after `RUNTIME_READY(form)`)
   - `executor-w4` — requirements specs, dashboard contracts, integration prep artifacts
3. **Verify before accepting.** Route claimed-complete work through `verifier` before treating it as PASS.
4. **Route collisions or ambiguity to `governor`.** The governor picks the next move, detects ownership conflicts, and chooses retry / replan / escalate.
5. **At most three active lanes at once** — W1 + W2 + W4. W5 (governance) is on-demand only.

## When W5 is invoked
Only for:
- approve / reject review of a landed artifact
- real ownership collision
- `contract_failure` or `assumption_failure` arbitration
- explicit execution-map revision

The governor agent fulfills the W5 role on-demand. It is not a standing lane.

## How `RUNTIME_READY` works
- `FILE_READY(form)` = files exist in a usable handoff shape. **Does not authorize W2 canonical authoring.**
- `RUNTIME_READY(form)` = W1's execution-authorization signal. Backend contract for that named form is sufficiently closed and evidenced.
- **W2 switches from Mode A to Mode B only on `RUNTIME_READY(form)`**, scoped to that one form.
- W1 emits the signal by writing `.claude/state/runtime_ready.json` with the form name and evidence path. `executor-w2` checks this file before entering Mode B. `pre_tool_use.sh` also checks it before allowing portal canonical writes.

## Reading the three status words
- **PASS** — verifier saw concrete evidence (path, test output, parity gate). Work is accepted.
- **FAIL** — verifier saw a contract, assumption, data, tool, or ownership failure. Specific clause cited. Do not rerun blindly — follow the retry policy in `EXECUTION_POLICY.md`.
- **BLOCKED** — a human checkpoint is required or an UNRESOLVED item is in the path. Tom must act before the loop can continue.

## Avoiding deadlocks
- Every reply ends with **one immediate next operator action** (the `no-dead-air` rule). If every lane is parked, the action might be "confirm the Waste/Adj contract draft is ready to circulate" or "supply LionWheel sandbox credentials" — but never "all lanes idle".
- If a subagent returns BLOCKED with unclear dependency, route it to `governor`, not to another executor. Silent skipping is forbidden.
- `TOOL_FAILURE_UNCLEARED` parks the affected W4 artifact but does not force a project reassessment.

## Files in this harness
```
.claude/
├── README.md              this file
├── SIGNALS.md             FILE_READY / RUNTIME_READY / TOOL_FAILURE_UNCLEARED rules
├── settings.json          hooks + permissions
├── mcp.json               MCP starter config (placeholders)
├── agents/
│   ├── executor-w1.md
│   ├── executor-w2.md
│   ├── executor-w4.md
│   ├── verifier.md
│   └── governor.md
├── hooks/
│   ├── session_start.sh
│   ├── pre_tool_use.sh
│   ├── subagent_stop.sh
│   └── stop.sh
└── state/
    ├── runtime_ready.json    (created when W1 emits signals; empty until then)
    └── active_mode.json      (W2 current mode; Mode A by default)
```

## Authority references
This harness references but does not restate:
- **Durable contract** — `claude.md` (wins on locked decisions)
- **Current state** — `CURRENT_STATE.md` (sole authority on gate status)
- **Execution policy** — `EXECUTION_POLICY.md` (mirrors `factory-os-autonomous-builder` skill; skill wins on divergence)
- **Active context** — `ACTIVE_NOW.md` (ephemeral; defers to `CURRENT_STATE.md` when stale)

If this harness conflicts with any of those, **those files win**.