#!/usr/bin/env bash
# PreToolUse hook — no session watches anything unless Tom asked for it.
#
# Tom, 2026-09-01: "רק אם אני מבקש שיעקוב אז יעקוב ואם לא אז ששום סשן לא יעקוב
# אף פעם" — only if he asks. Otherwise no session ever watches.
#
# WHY THIS EXISTS AS A HOOK AND NOT ONLY AS A RULE
#
# The harness default is the opposite: after opening a PR a session is told to
# subscribe to its activity without asking, and to schedule its own hourly
# check-ins. That default is not in any file in this repo, so a rule in
# CLAUDE.md is the session choosing to obey. This hook does not depend on the
# session's cooperation — a blocked call is blocked.
#
# One session on 2026-08-31 ran eleven overnight check-ins on three PRs that
# had not changed since the evening. Nothing was wrong with any of them; the
# cost was simply that nobody asked for it.
#
# WHAT IT BLOCKS — the four ways a session starts watching on its own:
#   subscribe_pr_activity   PR webhooks delivered into the session
#   send_later              a self-scheduled wake-up
#   create_trigger          a Routine, one-shot or cron
#   ScheduleWakeup          /loop dynamic pacing
#   CronCreate              a cron Routine
#
# WHAT IT DELIBERATELY DOES NOT BLOCK — the way out always stays open:
#   unsubscribe_pr_activity · delete_trigger · list_triggers · update_trigger
#
# THE OPT-IN
#
# Tom asks for watching -> the session creates .claude/state/watch_enabled and
# the hook stands down for the rest of that session. The file is gitignored and
# the container is ephemeral, so consent does not leak into the next session:
# each one starts closed again. Deleting the file re-arms the block immediately.
#
#
# ONE GAP, MEASURED — the hook cannot close it, the rule below does
#
# Creating a pull request subscribes the session to it SERVER-SIDE. No
# subscribe_pr_activity call is made, so there is nothing for a PreToolUse hook
# to intercept. Observed 2026-09-01 on gt-site#4: the hook was already live and
# the subscription still arrived.
#
# ∴ after opening a PR, a session MUST call unsubscribe_pr_activity unless Tom
# asked for that PR to be watched. This hook never blocks that call — that is
# why the exit path is kept open by design, not merely as a courtesy.
#
# Actions minutes are not the reason. Check-ins run in Claude's container and
# cost zero Actions minutes; only a push to an open PR starts a workflow. The
# reason is that unrequested background work is unrequested.

set -eu

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OPT_IN="$PROJECT_ROOT/.claude/state/watch_enabled"

PAYLOAD="$(cat || true)"

TOOL_NAME="$(printf '%s' "$PAYLOAD" \
  | grep -o '"tool_name"[[:space:]]*:[[:space:]]*"[^"]*"' \
  | head -n1 \
  | sed -E 's/.*"tool_name"[[:space:]]*:[[:space:]]*"([^"]*)".*/\1/')"

# Nothing to judge — let the call through rather than guess.
[ -n "$TOOL_NAME" ] || exit 0

case "$TOOL_NAME" in
  *subscribe_pr_activity*)
    # unsubscribe_pr_activity contains the same substring. Never block the exit.
    case "$TOOL_NAME" in *unsubscribe_pr_activity*) exit 0 ;; esac
    WHAT="watch a pull request" ;;
  *send_later*)       WHAT="schedule a wake-up for itself" ;;
  *create_trigger*)   WHAT="create a Routine" ;;
  ScheduleWakeup)     WHAT="schedule a /loop wake-up" ;;
  CronCreate)         WHAT="create a cron Routine" ;;
  *) exit 0 ;;
esac

[ -f "$OPT_IN" ] && exit 0

printf '%s\n' \
"PreToolUse block: this session may not $WHAT." \
"" \
"Tom's standing rule (2026-09-01): no session watches a PR or schedules its own" \
"check-ins unless he asks for it in that conversation. The harness default is the" \
"opposite, so this hook overrides it." \
"" \
"If Tom HAS asked for it, record his request and retry:" \
"  mkdir -p .claude/state && printf '%s\\n' '<what he asked, and when>' > .claude/state/watch_enabled" \
"" \
"If he has not asked, do not create that file. Finish the work, tell him what is" \
"open, and end the turn. Cleanup is never blocked: unsubscribe_pr_activity," \
"delete_trigger and list_triggers all still work." >&2
exit 2
