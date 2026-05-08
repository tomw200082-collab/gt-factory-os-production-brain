#!/usr/bin/env bash
# SessionStart hook — GT Factory OS harness
#
# Prints a compact project state summary to stderr so it lands in the session
# context. Keeps loading thin: references the four authority docs rather than
# dumping their contents.

set -eu

# Resolve project root (the directory containing .claude/)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

print_block() {
  # Print to stderr so Claude Code captures it as SessionStart additionalContext.
  printf '%s\n' "$@" >&2
}

print_block ""
print_block "=== GT Factory OS — SessionStart ==="
print_block ""
print_block "Authority layers (read when relevant; do not restate):"
print_block "  - claude.md           — durable contract (locked decisions)"
print_block "  - CURRENT_STATE.md    — sole authority on live gate status / critical path / UNRESOLVED"
print_block "  - EXECUTION_POLICY.md — standing-order policy (mirrors factory-os-autonomous-builder skill)"
print_block "  - ACTIVE_NOW.md       — ephemeral operator context (if stale, defer to CURRENT_STATE.md)"
print_block ""

ACTIVE_NOW="$PROJECT_ROOT/ACTIVE_NOW.md"
if [ -f "$ACTIVE_NOW" ]; then
  ACTIVE_NOW_AGE=$(( ( $(date +%s) - $(date -r "$ACTIVE_NOW" +%s) ) / 86400 ))
  if [ "$ACTIVE_NOW_AGE" -gt 5 ]; then
    print_block "[warn] ACTIVE_NOW.md is ${ACTIVE_NOW_AGE} days old — content skipped to prevent loading stale context."
    print_block "       Refresh ACTIVE_NOW.md before dispatching. Defer to CURRENT_STATE.md."
    print_block ""
  else
    print_block "--- ACTIVE_NOW summary (${ACTIVE_NOW_AGE}d old) ---"
    sed -n '1,60p' "$ACTIVE_NOW" | grep -v '^> ' >&2 || true
    print_block ""
  fi
else
  print_block "[warn] ACTIVE_NOW.md not found at $ACTIVE_NOW — operator context missing."
  print_block ""
fi

RUNTIME_READY="$PROJECT_ROOT/.claude/state/runtime_ready.json"
if [ -f "$RUNTIME_READY" ]; then
  print_block "--- RUNTIME_READY signals on record ---"
  cat "$RUNTIME_READY" >&2
  print_block ""
else
  print_block "RUNTIME_READY signals: none emitted yet (no .claude/state/runtime_ready.json)."
  print_block ""
fi

print_block "Subagents available: executor-w1, executor-w2, executor-w4, verifier, governor."
print_block "W5 is on-demand via governor; not a standing lane."
print_block "Max 3 active lanes at once (W1 + W2 + W4)."
print_block ""
print_block "Harness docs: .claude/README.md, .claude/SIGNALS.md."
print_block ""

exit 0