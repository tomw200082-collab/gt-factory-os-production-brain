#!/usr/bin/env bash
# Stop hook — GT Factory OS harness
#
# Runs when Claude is about to end a response. Enforces the no-dead-air rule:
# the final assistant message must name at least one concrete next action for
# Tom. If the message ends on "waiting" / "idle" / "all lanes parked" without
# a next move, we emit an additional context line so Claude sees it and adds
# one before finalizing.
#
# We do not hard-block Stop. Hard-blocking Stop can loop. Instead, we inject
# feedback that Claude processes on its next turn if the user continues.

set -eu

PAYLOAD="$(cat || true)"

annotate() {
  printf '%s\n' "Stop hook: $1" >&2
}

# Try to pull out the last assistant message text. Schema varies; best-effort.
LAST_MSG="$(printf '%s' "$PAYLOAD" | tr -d '\r')"

# Red flags: phrases that indicate dead air.
DEAD_AIR_PATTERNS='all lanes parked|all lanes idle|waiting for upstream|nothing to do|no next action|standing by'

# Green flag: a line that starts with a next-action prompt.
NEXT_ACTION_PATTERNS='next action|next move|strongest next|one immediate|action for Tom|Strongest next move'

if printf '%s' "$LAST_MSG" | grep -Eqi "$DEAD_AIR_PATTERNS"; then
  if ! printf '%s' "$LAST_MSG" | grep -Eqi "$NEXT_ACTION_PATTERNS"; then
    annotate "final message hits dead-air patterns without a next action. Per EXECUTION_POLICY.md no-dead-air rule, name the single smallest concrete operator unlock action before ending."
    exit 0
  fi
fi

# If the message has a PASS/FAIL/BLOCKED status block, ensure it is followed
# by a next-action line. Governor output must close with one.
if printf '%s' "$LAST_MSG" | grep -Eq 'STATUS:[[:space:]]*(PASS|FAIL|BLOCKED)'; then
  if ! printf '%s' "$LAST_MSG" | grep -Eqi "$NEXT_ACTION_PATTERNS"; then
    annotate "response carries STATUS line but no next-action line. Add one per the no-dead-air rule."
    exit 0
  fi
fi

exit 0