#!/usr/bin/env bash
# SubagentStop hook — GT Factory OS harness
#
# Receives the subagent's completion payload on stdin. Its job is to protect
# against "PASS without evidence" creeping into parent context.
#
# If the subagent output declares STATUS: PASS but contains none of the evidence
# markers a real PASS should have (file path, pgTAP line, parity gate, test
# output, runtime_ready.json update, verifier verdict), downgrade by emitting
# an additional context line that flags the PASS as unverified. We do not
# block here — we annotate, and leave the decision to the governor / parent.

set -eu

PAYLOAD="$(cat || true)"

annotate() {
  printf '%s\n' "SubagentStop check: $1" >&2
}

# Pull out the subagent's textual result (best-effort — the exact schema varies).
RESULT="$(printf '%s' "$PAYLOAD" | tr -d '\r')"

# Does the result claim PASS?
if printf '%s' "$RESULT" | grep -Eq 'STATUS:[[:space:]]*PASS|^PASS$|^\*\*PASS\*\*'; then
  # Look for evidence markers. Any one of these is acceptable.
  if printf '%s' "$RESULT" | grep -Eq \
    'path:[[:space:]]*[A-Za-z0-9_./\\-]+\.(sql|md|ts|tsx|js|json|py)' \
    || printf '%s' "$RESULT" | grep -Eq '[0-9]+[[:space:]]*/[[:space:]]*[0-9]+[[:space:]]*(pgTAP|tests|green|assertions)' \
    || printf '%s' "$RESULT" | grep -Eq 'parity[[:space:]]+gate|rebuild_verifier|drift_count' \
    || printf '%s' "$RESULT" | grep -Eq 'runtime_ready\.json' \
    || printf '%s' "$RESULT" | grep -Eq 'verifier[[:space:]]+verdict:[[:space:]]*PASS' \
  ; then
    annotate "subagent PASS with evidence markers — accepted."
    exit 0
  else
    annotate "subagent declared PASS but no evidence marker found (no file path, no N/M test count, no parity gate, no runtime_ready.json update, no verifier verdict). Treat as BLOCKED until verifier confirms."
    exit 0
  fi
fi

exit 0