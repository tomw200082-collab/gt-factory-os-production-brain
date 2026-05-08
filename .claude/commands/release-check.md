# /release-check

Invoke the `release-verifier` to verify PR, branch, or release readiness before a human merge or deploy.

## Purpose

Produces a structured safety verdict (safe for human review / conditionally safe / not safe) by
checking git state, changed-file scope, lane crossings, frozen flag proximity, CI status, and
contract alignment. Designed to be readable on GitHub, mobile, or Slack without local tooling.

Clearly separates CI-backed facts from local / manual validation claims.

## Usage

```
/release-check
/release-check <branch-name>
/release-check pr:<number>
/release-check <base>..<head>
/release-check <commit-sha>
```

**With no argument:** checks current branch HEAD against its upstream or base branch.

**With branch name:** checks the named branch.

**With pr:<number>:** attempts to read PR metadata from git remote; falls back to local branch if
GitHub API is unavailable.

## Agents involved

Primary: `release-verifier`
Supporting: `factory-os-governor` (if a lane crossing or frozen flag is detected)

## Required inputs

The verifier reads:
1. Target branch / PR / commit range.
2. `git status --short` and `git log --oneline -10` on the target.
3. `git diff --stat <base>..<head>` for changed-file scope.
4. `PRODUCTION/CLAUDE.md` — locked decisions for contract alignment.
5. `PRODUCTION/EXECUTION_POLICY.md` — lane policy.
6. `PRODUCTION/CURRENT_STATE.md` — live gate status.
7. CI run status if available (GitHub CLI or environment); falls back to manual if not.

## Required outputs

```
## release-verifier report

### Target
<branch / PR / commit range>

### Git state
- Branch / Dirty worktree / Untracked sensitive files

### Changed files (scope analysis)
| File | Lane | Risk | CI-backed / manual |

### Lane crossing
### Frozen flag check
### CI / test status
### Authority doc integrity

### Risk summary
### Verdict: SAFE_FOR_HUMAN_REVIEW | CONDITIONALLY_SAFE | NOT_SAFE | BLOCKED

### Conditions / Blockers
### Next action for Tom
```

## Write policy

**Read-only.** No file writes except optional report saved to `PRODUCTION/docs/phase8/dry-runs/`
when run with `--save` or in dry-run mode. No git mutations. No merges. No deploys.

## GitHub / mobile compatibility

Output is structured markdown. Safe to paste into a GitHub PR review comment or share on mobile.
CI-backed vs manual labels are explicit — reviewers can distinguish automated from manual claims.

## Stop conditions

- `.env*`, secrets, or credentials in diff → `NOT_SAFE` immediately.
- Frozen flag at risk without documented Tom authorization → `NOT_SAFE`.
- Changes touch `CLAUDE.md` → `NOT_SAFE` (Tom-only).
- Cross-repo changes (gt-factory-os + gt-factory-os-portal) in single PR without authorization → `NOT_SAFE`.
- Production migration alongside portal source in one PR → `NOT_SAFE`.

## Not usable for

- Actually merging a PR.
- Deploying to Railway or Vercel.
- Running database migrations.
- Approving a change that requires Tom's explicit authorization.
- Replacing a human code review.
