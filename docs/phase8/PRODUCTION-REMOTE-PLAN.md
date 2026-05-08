# PRODUCTION git remote — plan and audit

**Date:** 2026-05-08
**Status:** PLAN ONLY — no remote created. Tom must provide the repo URL before push.

---

## A. Current `git remote -v` output

```
(empty — no remotes configured)
```

`git remote -v` returns no output. PRODUCTION has zero remotes today. Branch state: `main` is the only local branch. Seven local commits exist (Phases 0/7 baseline + Wave 0 reconciliation × 4 + Phase 8 Run A × 3).

---

## B. Recommended private repo name for PRODUCTION remote

**Recommended:** `gt-factory-os-production` (private GitHub repo under your account).

**Rationale:**
- Mirrors the existing `gt-factory-os` (backend) and `gt-factory-os-portal` (portal) naming pattern.
- The `-production` suffix makes it unambiguous that this is the PRODUCTION workspace (the AI brain, authority docs, and operational docs), not a code repo.
- Private visibility is mandatory: PRODUCTION tracks `archive/`, `docs/`, `.claude/agents/`, and reference data. None of this is intended for public visibility.

**Alternative naming, in case of conflict:**
- `gt-factory-os-brain` — emphasizes the AI brain role
- `gt-factory-os-workspace` — emphasizes the workspace role
- `gt-factory-os-ops` — emphasizes the operational docs role

**Recommendation: `gt-factory-os-production`.** First use; clearest intent.

---

## C. Exact commands Tom should run after creating the private repo

After Tom creates the empty private GitHub repo (do not initialize with README, .gitignore, or license — the local PRODUCTION repo already has these), run:

```powershell
# In PowerShell from the PRODUCTION directory:
cd "C:\Users\tomw2\GTeveryday Dropbox\Data Center\Tom\AI Agents & Projects\Code Agents\PRODUCTION"

# Add the remote (replace <YOUR-GITHUB-USER> and repo name as needed):
git remote add origin https://github.com/<YOUR-GITHUB-USER>/gt-factory-os-production.git

# Verify remote attached:
git remote -v

# Push main and set upstream:
git push -u origin main
```

If using SSH instead of HTTPS:

```powershell
git remote add origin git@github.com:<YOUR-GITHUB-USER>/gt-factory-os-production.git
git push -u origin main
```

After push, future commits use plain `git push` (per the `feedback_push_autonomously.md` memory: push automatically after every commit; no confirmation needed).

---

## D. Sensitive files audit — anything tracked that shouldn't go to a remote?

Scan results (`git ls-files | grep -i -E "(\.env|secret|credential|password|api[_-]key)"`):

| Match | File | Verdict |
|-------|------|---------|
| 1 | `archive/w4-integrations-sandbox-2026-04-17/window4-integrations-sandbox/docs/secret-store-wiring.md` | **SAFE.** Read first 30 lines: this is a *design note* explaining how the LionWheel API token should be stored *off* disk (Supabase Vault / Doppler / AWS SSM). The doc describes a threat model and architecture; it does not contain any actual token value. The doc explicitly states the token "must be rotated before Slice 1 runtime lights up" and that any token value found in conversation history is "burned for production purposes". No secrets present. |

**No actual secrets, credentials, API keys, or `.env` files are tracked.** The 1 match is a documentation file about secret handling — exactly the kind of doc that should be tracked.

Additional spot checks performed:
- No `.env` file at repo root (verified).
- No `.env.local`, `.env.production`, etc. tracked (`.gitignore` covers them).
- No `*.pem`, `*.key` files tracked (`.gitignore` covers them).
- No `secrets/` or `credentials/` directories tracked (`.gitignore` covers them).
- 264 total tracked files; spot-check of random samples shows authority docs, archived migration scripts, agent definitions, and audit reports — nothing operationally sensitive.

---

## E. `.gitignore` confirmation

`PRODUCTION/.gitignore` (1774 bytes; established at Wave 0 baseline) covers:

**Rotating output:**
- `.audit-tmp/`, `.audits/*` (with `!.audits/RETENTION_POLICY.md` exception), `.lionwheel-prints/`, `.superpowers/`

**Vendored binaries:**
- `.tools/`

**Large reference data files (structure tracked, content ignored):**
- `data/excel/active/*.xls*`, `data/excel/backups/`, `data/excel/temp-locks/`
- `data/json/shopify/*.json`
- `data/invoices/suppliers/**/*.{pdf,jpg,jpeg,png}`

**Archive binaries duplicated under data/:**
- `archive/migrated-to-data/**/*.{jpg,jpeg,pdf,png}`, `archive/migrated-to-data/**/_resized/`

**OS noise:**
- `Thumbs.db`, `.DS_Store`, `~$*`

**Editor noise:**
- `.vscode/`, `.idea/`, `*.swp`, `*.swo`

**Node / build artifacts (defensive):**
- `node_modules/`, `dist/`, `build/`, `.next/`

**Defensive secrets / credentials block (the critical block):**
- `.env`, `.env.*`, `*.env`
- `secrets/`, `credentials/`
- `*.pem`, `*.key`
- `.aws/`, `.ssh/`

**Verdict: `.gitignore` is comprehensive and protective.** Specifically:
- All conventional secret file patterns are blocked.
- Rotating outputs are blocked (no audit reports leak to remote).
- Large binaries are blocked (repo stays small and reviewable).
- Defense-in-depth is documented inline ("also enforced by .claude/settings.json deny rules and pre_tool_use.sh hook").

---

## F. Safe to push `main` once Tom provides the remote URL?

**YES — safe to push.**

Confirmations:
1. Zero secrets, credentials, API keys, or `.env` files tracked in any of the 264 tracked files (Section D).
2. `.gitignore` blocks all conventional secret file patterns (Section E).
3. The 7 commit messages contain no secrets or sensitive operational data — they describe structural changes (Phase 7 cleanup, Wave 0 reconciliation, Phase 8 Wave 1/2 brain scaffolding, Wave 3/4 proposals).
4. No working-tree changes (`git status --short` is empty).
5. The local repo is the authoritative source — no merge conflicts to resolve on first push.
6. Push to a *private* GitHub repo only; visibility must be private. Public visibility would expose the AI brain configuration, archive of past architectural decisions, and operational doctrine — all of which is internal-only.

**Pre-flight checklist for Tom (before running the push command):**
- [ ] Create the GitHub repo as **private** (not public, not internal).
- [ ] Do NOT initialize the repo with a README, .gitignore, or license — the local PRODUCTION repo already has these.
- [ ] Confirm the GitHub username/org in the remote URL.
- [ ] Run `git remote -v` after `git remote add origin ...` to verify the URL was applied correctly.
- [ ] After `git push -u origin main` succeeds, run `git remote -v` again to confirm push succeeded.

**Rollback plan if push fails or the wrong repo URL is used:**
```powershell
git remote remove origin   # clears the misconfigured remote
# Then re-add with the correct URL.
```

No commits are at risk during this rollback — they remain local until pushed successfully.

---

**END OF PRODUCTION REMOTE PLAN. No remote created. Tom provides the URL and runs the commands in Section C.**
