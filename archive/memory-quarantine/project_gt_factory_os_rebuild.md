---
name: GT Factory OS rebuild — structure
description: Multi-window parallel rebuild of GT Factory OS from Excel to cloud. Window roles, locked decisions, and current stage.
type: project
---

GT Factory OS is being rebuilt from an Excel workbook into a cloud platform. Work is split across multiple "windows" (parallel assistant sessions), each with a scoped ownership area. Window 2 owns portal/forms/auth/roles/approvals. Window 1 owns schema. Window 5 is coordination. Windows 3/4 cover planning engine, jobs, integrations (exact split TBD).

**Why:** The rebuild is staged to prevent architectural drift; each window must not invent facts outside its boundary. Foundation doc is `GT_FACTORY_OS_PROJECT_FOUNDATION.md`. Section 17 explicitly forbids building until architecture is internally consistent.

**How to apply:** When asked to act as a specific window, stay inside that window's ownership and surface `TODO-WINDOW<N>` markers rather than inventing cross-boundary decisions. Locked foundation decisions: Supabase + Node/Fastify + Next.js; Postgres ledger with `event_at` authoritative; RM batch schema present but ignored in v1; SQL-first planning engine; stock-truth works first as cutover gate; roles are `operator|planner|admin|viewer`; Excel is transitional read-only export only; LionWheel feeds open orders; Shopify is downstream of our stock; Green Invoice feeds price history under threshold-guarded auto-update.

**Working directory state (as of 2026-04-14):** `PRODUCTION/` contains only the two legacy xlsx files and `window2-portal-spec.md` (the portal skeleton spec — contract-level, no code). No repo, no scaffolding, no git. Nothing is implemented yet.
