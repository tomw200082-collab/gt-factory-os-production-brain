# GT Factory OS — Lessons Learned

> **Purpose:** Non-obvious things that caused rework. Calibration data for future estimates. Only record surprises — things that were obviously true in hindsight but cost real time when they weren't known.

---

## Format

```
### [Date]: [Short title]
**What happened:** [Situation]
**Why it was surprising:** [What the naive assumption was]
**Corrective:** [What to do differently next time]
```

---

## Entries

### 2026-04-23: Wrong portal directory analyzed, led to incorrect Layer 0 estimate

**What happened:** An exploration agent analyzed `PRODUCTION/portal/` instead of the canonical portal at `C:/Users/tomw2/Projects/window2-portal-sandbox/`. Concluded that auth was "completely unimplemented" and portal made "zero real API calls". Layer 0 was estimated as 2-4 weeks of bridge work. Direct investigation found fully implemented auth + API proxy, 86/100 scorecard, and deployed system. Layer 0 revised to 3-5 days validation sprint.

**Why it was surprising:** There are two portal directories in the repo layout. `PRODUCTION/portal/` is an older, separate mock-only workstream. The canonical portal is a separate project in `C:/Users/tomw2/Projects/`. The memory file `reference_gt_factory_paths.md` documents this distinction, but the exploration agent didn't have access to memory and made the wrong inference from the directory structure.

**Corrective:** Before any portal audit, explicitly verify which directory is canonical by reading `PRODUCTION/docs/reference_gt_factory_paths.md` or MEMORY.md. The canonical portal is ALWAYS `C:/Users/tomw2/Projects/window2-portal-sandbox/`. `PRODUCTION/portal/` is a dead branch for W2 purposes.

---

### 2026-04-23: Railway project named "accomplished-learning" — not "gt-factory-os"

**What happened:** Railway project is named `accomplished-learning`, not the expected `gt-factory-os-api`. This caused `railway list` to appear to not contain the GT Factory OS project.

**Why it was surprising:** The Railway public domain (`gt-factory-os-api-production.up.railway.app`) and service name (`gt-factory-os-api`) both match the expected naming. The project-level name is different and was auto-generated.

**Corrective:** When using Railway CLI, always use `railway link --project [UUID]` with the actual project ID (`807cf50c-2629-445f-ae80-83a2f5abe9b0`), not the project name. The service name `gt-factory-os-api` is reliable; the project name is not.

---

### 2026-04-23: Vercel env pull cannot decrypt encrypted ("sensitive") variables

**What happened:** `vercel env pull` downloads encrypted production vars as empty strings (`""`). `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_API_BASE`, and others appeared empty in the pulled `.env` file even though they are confirmed set via `vercel env ls`.

**Why it was surprising:** The CLI pull is documented as the way to get production env vars for local dev. It works for plain-text vars (e.g., `API_BASE` was correctly pulled as the Railway URL) but silently omits values for vars created with the "Sensitive" type.

**Corrective:** Use `vercel env ls` to confirm presence; use a live portal smoke test (login, form submission) to confirm values are correct at runtime. Never rely on `vercel env pull` for sensitive vars.

---

*Log initiated: 2026-04-23.*
