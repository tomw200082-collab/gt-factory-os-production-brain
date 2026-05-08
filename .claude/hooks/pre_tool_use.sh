#!/usr/bin/env bash
# PreToolUse hook — GT Factory OS harness
#
# Receives the pending tool call on stdin as JSON. Exits non-zero to block.
# Prints the block reason to stderr so Claude sees it and can adjust.
#
# This hook enforces structural bans:
#   - Sandbox-to-canonical writes (W3 touching canonical repo)
#   - Direct writes to secrets / env files
#   - Destructive bash commands not explicitly escalated
#   - Canonical portal writes when no RUNTIME_READY(form) signal exists
#
# Semantic enforcement (e.g., "is this agent authorized for this lane?") lives
# primarily in the agent system prompts. This hook is the structural backstop.

set -eu

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

block() {
  # Exit 2 signals a PreToolUse block to Claude Code; stderr becomes feedback.
  printf '%s\n' "PreToolUse block: $1" >&2
  exit 2
}

# Read the JSON payload from stdin. We do not require jq — fall back to grep.
PAYLOAD="$(cat || true)"

get_field() {
  # Extract a top-level string field. Tolerates missing field.
  local key="$1"
  printf '%s' "$PAYLOAD" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" \
    | head -n1 | sed -E "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"([^\"]*)\".*/\1/"
}

TOOL_NAME="$(get_field tool_name)"
# Common path-carrying fields across Write/Edit/Read tools.
TARGET_PATH=""
for key in file_path path filename target; do
  candidate="$(get_field "$key")"
  if [ -n "$candidate" ]; then
    TARGET_PATH="$candidate"
    break
  fi
done

# Best-effort extraction of Bash command.
TOOL_CMD="$(printf '%s' "$PAYLOAD" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' \
  | head -n1 | sed -E 's/.*"command"[[:space:]]*:[[:space:]]*"([^"]*)".*/\1/')"

# --- Rule 1: deny writes to secrets / env files --------------------------
case "$TARGET_PATH" in
  *.env|*.env.*|*/.env|*/.env.*|*/secrets/*|*/credentials/*|*/.ssh/*|*/.aws/*)
    block "write to secret/env path denied: $TARGET_PATH"
    ;;
esac

# --- Rule 2: deny W3 sandbox writing into canonical repo -----------------
# Canonical paths live under Projects/gt-factory-os/. Sandbox paths contain
# window2-portal-sandbox. A Bash command that cp's sandbox → canonical is
# an ownership violation.
case "$TOOL_CMD" in
  *window2-portal-sandbox*gt-factory-os*|*gt-factory-os*window2-portal-sandbox*)
    case "$TOOL_CMD" in
      *cp*|*mv*|*rsync*|*install*)
        block "sandbox->canonical file promotion forbidden (W3 never owns canonical). Re-type concepts into canonical primitives instead."
        ;;
    esac
    ;;
esac

# --- Rule 3: deny destructive bash commands ------------------------------
case "$TOOL_CMD" in
  *"rm -rf /"*|*"rm -rf ~"*|*"rm -rf ."*|*"rm -fr /"*|*"rm -fr ~"*)
    block "destructive rm -rf pattern denied"
    ;;
  *"git push --force"*|*"git push -f"*)
    case "$TOOL_CMD" in
      *" main"*|*" master"*)
        block "force-push to main/master denied"
        ;;
    esac
    ;;
  *"git reset --hard"*)
    block "git reset --hard requires explicit operator escalation (not auto-allowed)"
    ;;
  *"drop database"*|*"DROP DATABASE"*|*"truncate table"*|*"TRUNCATE TABLE"*)
    block "destructive SQL denied"
    ;;
esac

# --- Rule 4: canonical portal writes need RUNTIME_READY ------------------
# If the target path is under Projects/gt-factory-os/portal/ and the tool is
# Write/Edit, require a non-empty runtime_ready.json. This is a coarse gate:
# the executor-w2 agent prompt enforces the form-scoping; the hook only
# ensures at least one RUNTIME_READY signal exists before any portal canonical
# write is attempted.
case "$TARGET_PATH" in
  *Projects/gt-factory-os/portal/*|*Projects\\gt-factory-os\\portal\\*)
    case "$TOOL_NAME" in
      Write|Edit|NotebookEdit)
        RR="$PROJECT_ROOT/.claude/state/runtime_ready.json"
        # Look for a real signal entry (must carry an emitted_at timestamp).
        # Schema-description occurrences of "form" do NOT count.
        if [ ! -s "$RR" ] || ! grep -q '"emitted_at"' "$RR"; then
          block "canonical portal write requires RUNTIME_READY(form). .claude/state/runtime_ready.json contains no emitted signals. W2 stays in Mode A."
        fi
        ;;
    esac
    ;;
esac

# --- Rule 5: W4 requirements-only (coarse) -------------------------------
# If the target is a .sql / .ts / .js file under docs/integrations, that is
# out of W4's requirements-only scope. Block so the executor routes to W1
# instead.
case "$TARGET_PATH" in
  */docs/integrations/*.sql|*/docs/integrations/*.ts|*/docs/integrations/*.js)
    block "W4 is requirements-only. Schema/runtime code belongs to W1. Route to executor-w1."
    ;;
esac

exit 0