# Ruflo session final report

Date: 2026-05-22
Repo: `tomw200082-collab/TEST-GT-START`
Branch: `claude/ruflo-sandbox-setup-LUW4n`
Operator: Claude Code session for tom@gteveryday.com

## 1. What was installed

- `ruflo@3.5.21` via `npx`. The on-disk wrapper is exactly `3.5.21`. The underlying CLI it delegates to is `@claude-flow/cli@3.6.30` (resolved from the unbounded `">=3.0.0-alpha.1"` range declared by the wrapper).
- Repo-local Ruflo configuration: `.claude/`, `.claude-flow/`, `.mcp.json`, `CLAUDE.md`.
- One MCP server registered via `.mcp.json` at the project level: `claude-flow`, pinned (after manual sanitisation) to `npx -y ruflo@3.5.21 mcp start`.
- No global npm install. No user-level `claude mcp add` was run.

## 2. Exact commands run (in order)

| #  | Command                                                                                 | Phase  | Exit |
| -- | --------------------------------------------------------------------------------------- | ------ | ---- |
| 1  | `npx -y ruflo@3.5.21 --version`                                                         | 2      | 0    |
| 2  | `npx ruflo@3.5.21 --help`                                                               | 2      | 0    |
| 3  | `npx ruflo@3.5.21 init --help`                                                          | 2      | 0    |
| 4  | `npx ruflo@3.5.21 init --full --no-global`                                              | 2      | 0    |
| 5  | `rm ~/.claude/CLAUDE.md` (manual cleanup; `--no-global` was ignored by Ruflo)           | 2      | 0    |
| 6  | `cat .mcp.json` (inspect)                                                               | 2      | 0    |
| 7  | `claude mcp list` (initial — 3 servers registered)                                      | 2      | 0    |
| 8  | Edit `.mcp.json`: remove `ruv-swarm`, remove `flow-nexus`, re-pin `claude-flow` → 3.5.21| 2      | n/a  |
| 9  | `claude mcp list` (after sanitisation — 1 server, Connected)                            | 2      | 0    |
| 10 | `timeout 15 npx ruflo@3.5.21 mcp start < /dev/null` (diagnostic)                        | 2      | 0    |
| 11 | `npx ruflo@3.5.21 doctor`                                                               | 2/3    | 0    |
| 12 | `npx ruflo@3.5.21 verify`                                                               | 2/3    | 0    |

Plus the documentation writes in Phases 1, 3, 4, 5, 6 (this file).

## 3. Files created or changed

### In this repo, by Ruflo's installer

- `.claude/` — 25 sub-trees including `agents/`, `commands/`, `helpers/`, `skills/`, plus `settings.json` (7088 B). 98 agent templates, 35 skill packages, 10+ command groups, ~40 helper scripts (some marked executable).
- `.claude-flow/` — `config.yaml`, `CAPABILITIES.md` (12815 B), `agents/`, `data/`, `hooks/`, `learning/`, `logs/`, `metrics/`, `security/`, `sessions/`, `workflows/`, plus its own `.gitignore` for runtime artifacts.
- `.mcp.json` — initially 3 servers, **sanitised to 1**.
- `CLAUDE.md` — repo-level Claude Code guidance, 6426 B.
- 272 files staged in total at the install checkpoint commit (`97d6894`).

### In this repo, by me

- `docs/ruflo-install-plan.md` — written before any install command.
- `docs/ruflo-install-log.md` — command-by-command record with findings.
- `docs/ruflo-evaluation-checklist.md` — checklist for this sandbox and future repos.
- `docs/how-to-use-ruflo-with-claude-code.md` — operating guide.
- `docs/ruflo-operating-prompts.md` — 10 reusable prompts.
- `docs/ruflo-session-final-report.md` — this file.
- `.mcp.json` — sanitised after Ruflo wrote it.

### Outside this repo

- `~/.claude/CLAUDE.md` — created by Ruflo despite `--no-global`. **Deleted by me.**
- `~/.claude/policy-limits.json` — mtime updated by Ruflo (same content). Left as-is.
- npx cache populated under `~/.npm/_npx/<hash>/`.

### Branch / commits

- All work committed to `claude/ruflo-sandbox-setup-LUW4n` and pushed to origin.
- Commits (in order): `b46dba4` (initial), `c8c6426` `.gitignore`, `788fd56` install-log scaffold, `e8371e5` install-plan scaffold, `080d7f1` evaluation-checklist scaffold, `934e89f` Phase 1 inspection, `7c46f92` version + wrapper findings, `97d6894` install checkpoint (272 files), `5c2f4ba` sanitise + doctor + verify. Phase 3–6 docs commit pending after this file.
- No PR was opened.

## 4. What succeeded

- Reproducible install via a single non-interactive command (`init --full --no-global`).
- MCP server registers correctly when pinned to `ruflo@3.5.21` and shows `✓ Connected`.
- `ruflo doctor` exits 0 with only the warnings we expect for a deliberately-isolated sandbox.
- `ruflo verify` validates the manifest signature trust chain (Ed25519, hash, public-key reproducibility).
- 44 of 55 capabilities pass the witness-byte check.
- No secrets, credentials, or production-system connections were created.
- Repo `.gitignore` not tampered with.
- Working tree is auditable end-to-end: every file Ruflo created is in git, every command we ran is logged.

## 5. What failed or is broken

1. **`--no-global` flag is broken in this version.** Ruflo wrote `~/.claude/CLAUDE.md` outside the repo. Filed in `docs/ruflo-evaluation-checklist.md` as an open issue against `ruflo@3.5.21` / `@claude-flow/cli@3.6.30`.
2. **`init` silently adds unrequested MCP servers.** Default `.mcp.json` registers `ruv-swarm` (third-party swarm) and `flow-nexus` (which has `requiresAuth: true` and would prompt for credentials). Sanitisation is mandatory after every `init`. Open issue.
3. **`init` pins the MCP entry to `ruflo@latest` regardless of the version used to invoke `init`.** `@latest` is currently alpha (`3.7.0-alpha.79`). When tested unsanitised, the alpha-pinned MCP server failed to connect (`✗ Failed to connect`). Pinning to `3.5.21` fixed it. Open issue.
4. **Version pinning of `ruflo` is cosmetic.** The wrapper declares `"@claude-flow/cli": ">=3.0.0-alpha.1"`. Behaviour comes from whatever `@claude-flow/cli` npm resolves at the moment of running. Same command tomorrow could resolve differently.
5. **`ruflo verify` output is internally inconsistent.** Closing line says `[OK] All fixes verified` even when there are 9 drift + 2 missing capabilities in the same run. Aligns with STATUS.md upstream calling functional smoke tests for verification "pending (task #26)".
6. **Hook system runs without explicit per-action consent.** We observed at least one `UserPromptSubmit` hook that routed a user reply to a "coder" agent automatically (50% confidence, "default routing"). The hook ran before any deliberate Ruflo invocation. This means once Ruflo is active in a repo, some Ruflo logic runs on every user message.

## 6. Is Ruflo ready to use in this sandbox?

**Yes, conditionally.** The sandbox install is in a known, sanitised state and is auditable. Useable for:

- Read-only repo analysis.
- Plan generation.
- Reviewing diffs.
- Documentation drafts.
- Test/coverage gap analysis.
- Practising the operating prompts in `docs/ruflo-operating-prompts.md`.

Conditions:

- Do not re-run `ruflo init` without re-sanitising `.mcp.json` immediately afterwards.
- Treat `ruflo verify`'s "OK" summary as untrustworthy; read its drift/missing list.
- Treat Ruflo hooks as active. They run on user messages. If you want to know what they do, read `.claude/settings.json` and the helper scripts in `.claude/helpers/`.

## 7. Is Ruflo ready to use on another repo?

**Not yet.** Three blocking issues:

1. The three install-behaviour issues (broken `--no-global`, unrequested MCP servers, alpha-pinned MCP entry) will recur on every new install until upstream fixes them.
2. We have not yet written a reusable, scripted install procedure that includes the post-init sanitisation. Without it, a future install will violate the sandbox isolation contract again.
3. We have not yet exercised Ruflo on a realistic codebase. We do not know how the hooks, agents, and memory subsystems behave under load in this version, only that they install and the MCP server connects.

What needs to happen before pointing Ruflo at another repo:

- Write a `setup-ruflo.sh` (or equivalent) that runs `init --full --no-global`, immediately rewrites `.mcp.json` to a sanitised template, and verifies via `claude mcp list` + `ruflo doctor`.
- Add a check that `~/.claude/CLAUDE.md` was not created (or remove it).
- Run the audit prompt (prompt #10 in `docs/ruflo-operating-prompts.md`) on the target repo first.
- Confirm the target repo has no production credentials, no exposed secrets, and branch protection on `main`.
- Start with read-only Ruflo usage. Do not enable daemon, memory, swarm, or autopilot.

## 8. Risks that remain

- **Version drift.** `@claude-flow/cli` can resolve to a different version on any future `npx` invocation. We have no version lock.
- **Hook surface.** Ruflo's hooks intercept user prompts and tool calls. We have not audited the helper scripts under `.claude/helpers/` line by line. Several are shell scripts marked executable; one is named `auto-commit.sh`.
- **Verification untrustworthy at the summary level.** `verify` says OK while listing drift. Production gating must read the structured output, not the summary.
- **Default `init` writes outside the repo and registers auth-required services.** Anyone running `init` casually in a new repo will violate the same hard safety rules we just had to clean up.
- **Upstream alpha churn.** npm `latest` is alpha. The docs tell users to install `@latest`. New users will get the alpha by default.
- **No upstream uninstall path.** Rollback is manual.

## 9. Recommended next step

Before doing anything else with Ruflo:

1. **Read `.claude/settings.json` and the helper scripts.** Understand what the hooks do. In particular, audit `.claude/helpers/auto-commit.sh`, `.claude/helpers/pre-commit`, `.claude/helpers/post-commit`, `.claude/helpers/setup-mcp.sh`, and `.claude/helpers/health-monitor.sh`. Decide which hooks you actually want active in this sandbox.
2. **Run prompt #1 (Analyze a repository without modifying files) on this sandbox**, using the prompt verbatim. This is a low-stakes way to see how Ruflo actually behaves in a session, and to compare what its analyzer agents do against what we already know about the repo. Stop and review before going further.
3. Once #1 is satisfactory, run prompt #3 (Review a PR for risk and missing tests) on the existing branch (`claude/ruflo-sandbox-setup-LUW4n` against `main`). This exercises the review agents without any code changes.
4. Only after both of those produce reasonable, bounded output, consider building the `setup-ruflo.sh` automation in section 7.

Do not yet: enable daemon, memory init, swarm init, federation, flow-nexus, or any unsanitised re-init.

## 10. Copy-paste prompt to start your first real Ruflo-assisted task

Open a Claude Code session in this repo (Ruflo will load automatically via `.mcp.json`). Verify with `claude mcp list` that `claude-flow` shows `✓ Connected`. Then paste:

> I'm in the TEST-GT-START sandbox with Ruflo active (pinned to ruflo@3.5.21 via .mcp.json). Treat this as a read-only evaluation. Use Ruflo's analyzer/researcher/reviewer agents — never coder, implementer, tester. Forbidden actions: any file write, any git mutation, any network calls beyond reading public docs, any MCP server other than claude-flow, any auth step. Task: produce a written report on what this repo currently contains, what Ruflo added during install, and what the active hooks (in .claude/settings.json) do. End with three concrete next-step suggestions for low-risk Ruflo usage. Stop after the report and ask me before any further action.
