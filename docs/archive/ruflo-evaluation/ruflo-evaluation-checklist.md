# Ruflo evaluation checklist

Status as of 2026-05-22, on branch `claude/ruflo-sandbox-setup-LUW4n` in this sandbox.

## Setup

- [x] Repository attached to Claude Code.
- [x] Node and npm available (Node 22.22.2, npm 10.9.7, npx 10.9.7).
- [x] Claude Code CLI present (2.1.148).
- [x] Ruflo documentation inspected (README, USERGUIDE, STATUS, install.sh; verification.md does not exist upstream).
- [x] Install plan written before any install command (`docs/ruflo-install-plan.md`).

## Install behaviour

- [x] `npx ruflo@3.5.21 --version` runs and exits 0.
- [x] Wrapper finding: `ruflo` is a thin wrapper that delegates to `@claude-flow/cli`. Declared dep is `">=3.0.0-alpha.1"` (unbounded). Reported binary version (`v3.6.30`) is the resolved underlying CLI, not the wrapper. **Pinning `ruflo` does not pin behaviour.**
- [x] `npx ruflo@3.5.21 init --full --no-global` exits 0 and creates: `.claude/`, `.claude-flow/`, `.mcp.json`, `CLAUDE.md` in repo (12 dirs, 119 files reported).
- [ ] **`--no-global` flag is broken.** Despite being passed, Ruflo created `~/.claude/CLAUDE.md` (a global pointer block) outside this repo. Manually deleted to restore sandbox isolation. **Open issue against `ruflo@3.5.21` / `@claude-flow/cli@3.6.30`.**
- [ ] **`init` silently registers extra MCP servers.** Default `.mcp.json` includes `ruv-swarm` (third-party swarm, not requested) and `flow-nexus` (`requiresAuth: true`, would prompt for credentials). Manually sanitised to only the `claude-flow` entry. **Open issue.**
- [ ] **`init` writes the MCP entry pinned to `ruflo@latest`** even when we ran init with a pinned version. `@latest` currently resolves to alpha. Manually re-pinned to `ruflo@3.5.21`. **Open issue.**
- [x] `.gitignore` not modified.
- [x] No `.env*`, `*.key`, `*.pem`, `credentials*`, `secrets*`, `*.token` written.

## Post-install verification

- [x] `claude mcp list` after sanitisation: exactly one server (`claude-flow`), status `✓ Connected`.
- [x] Manual MCP server start (`ruflo@3.5.21 mcp start`) initialises in stdio mode without error.
- [x] `ruflo doctor` exit 0. 9 passed, 6 warnings — all expected for an isolated sandbox.
- [x] `ruflo verify` exit 0. Manifest signature trust chain valid. **44 capabilities pass, 9 drift, 2 missing.**
- [ ] **Verify output is internally inconsistent.** Closing line is `[OK] All fixes verified` while listing 9 drift + 2 missing capabilities. Consistent with STATUS.md upstream calling functional smoke tests for verification "pending (task #26)".
- [x] Files created/modified are listed in `docs/ruflo-install-log.md` with hashes/sizes where useful.
- [x] No secrets written. Confirmed by name-pattern scan of repo.
- [x] Sandbox material only. No connections to GT/Shopify/finance/customer/supplier/inventory systems were created, and the `flow-nexus` server that would have required external auth was removed.

## Readiness gates

**Ready to use in this sandbox?** Yes, with caveats:

- Use only via the sanitised `.mcp.json` we wrote. Do not re-run `ruflo init` without first replanning — it will re-register the unrequested servers and re-create the global pointer.
- Treat the `verify` "OK" line as untrustworthy. Read the drift/missing list directly.
- Treat `ruflo` version pinning as cosmetic; behaviour is set by whatever `@claude-flow/cli` npm resolves at run time.

**Ready to use on another repo?** Not yet:

- The three open install-behaviour issues above must be either fixed upstream or worked around with a written wrapper. Until then, every new repo install will re-introduce the unrequested servers and the global pointer.
- The `verify` inconsistency means we cannot trust its summary for production gating.
- A repeatable install procedure (with `.mcp.json` template + post-init cleanup) needs to be documented before pointing Ruflo at any non-sandbox repo.

**Hard "do not yet" list:**

- Do not connect Ruflo to any production GT repo.
- Do not enable `flow-nexus`, federation, or any auth-required Ruflo capability.
- Do not run `ruflo daemon start`, `ruflo memory init`, `ruflo swarm init`, or `init --start-all` until we have a written daemon-management plan.
- Do not let Ruflo run unattended (its hooks are active per `.claude/settings.json`, and we observed a UserPromptSubmit hook that routed a user reply to a "coder" agent without our approval).
