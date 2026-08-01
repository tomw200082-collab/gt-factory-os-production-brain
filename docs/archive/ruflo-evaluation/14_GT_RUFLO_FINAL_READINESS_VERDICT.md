# 14 — GT Ruflo final readiness verdict

**Status:** v1, based on sandbox hardening, production-brain audit, and read-only probes of factory-os / portal.
**Date:** 2026-05-22

---

## Executive verdict

Ruflo can now be used as a controlled assistant for GT read-only and planning workflows, governed by production-brain.

It is **not** approved for autonomous implementation or installation in production repos.

---

## Readiness classifications

| Question | Verdict | Explanation |
|----------|---------|-------------|
| Can Tom now start using Ruflo with production-brain? | GO_WITH_CONSTRAINTS | Yes for read-only and planning. Production-brain is structurally compatible and governs routing. |
| Can Tom use Ruflo to improve existing Factory OS? | GO_WITH_CONSTRAINTS | Yes for audits, plans, PR reviews, and docs proposals. Implementation remains separate approval. |
| Can Tom use Ruflo to plan CRM? | GO_WITH_CONSTRAINTS | Yes: draft CRM module declaration proposal only. |
| Can Tom use Ruflo to build CRM? | NO_GO | Requires `MODULE_TEMPLATE.md` declaration + Tom written approval + router update first. |
| Can Ruflo perform controlled implementation? | BLOCKED_PENDING_TOM | Not in production repos yet. Needs branch protection validation, one small approved task, test plan, rollback, and explicit Tom approval. |
| Can Ruflo be installed in production repos? | NO_GO | Sandbox proved full install is too broad and must not be repeated in production repos. |
| Can Ruflo perform read-only audits of factory-os? | GO_WITH_CONSTRAINTS | Yes, after production-brain routing block. |
| Can Ruflo perform read-only audits of factory-os-portal? | GO_WITH_CONSTRAINTS | Yes, after production-brain routing block. |

---

## What remains blocked

1. Installing Ruflo in `gt-factory-os-production-brain`.
2. Installing Ruflo in `gt-factory-os`.
3. Installing Ruflo in `gt-factory-os-portal`.
4. Running `ruflo init` in any production repo.
5. Daemon, swarm, memory init, federation, flow-nexus, autopilot.
6. Generic coder / implementer / tester / pr-manager agents not sanctioned by production-brain.
7. Autonomous push, merge, deploy.
8. Any production DB migration without Tom approval.
9. Any external integration write without Tom approval and dry-run.
10. CRM build before module declaration approval.

---

## Biggest remaining risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Production-brain current-state freshness may lag live repo/runtime | High | Start with source-of-truth freshness audit. |
| Branch protection not verified | High | Manual GitHub check before implementation. |
| Routing schema mismatch | Medium | Use production-brain `AI_BRAIN_ROUTER.md` schema as normative. |
| Legacy agents remain active | Medium | Default to new production agents unless Tom says otherwise. |
| Ruflo MCP tool surface remains broad | Medium | Keep safe prompt discipline; do not call mutating MCP tools. |
| CRM scope creep | High | Require module declaration before any build. |

---

## Safest next task

Run the production-brain source-of-truth freshness audit from `13_FIRST_REAL_GT_TASKS_RECOMMENDATION.md`.

Do not start with backend implementation or CRM build.

---

## Single operating rule never to break

```text
Production-brain is law. Ruflo is labor. Tom approves. One repo, one mode, one task.
```

---

## Practical go-forward path

1. Run source-of-truth freshness audit.
2. Run `factory-os` read-only backend/domain map.
3. Run `factory-os-portal` read-only UI/workflow map.
4. Pick one small task.
5. Produce plan-only.
6. Tom approves or rejects.
7. Only later, controlled implementation with branch/test/rollback gates.

---

## Final note

The system is now ready to start serious work, but only because the operating model is conservative. The point is not to let Ruflo run faster; the point is to let Ruflo make GT work more visible, auditable, and less dependent on undocumented memory.
