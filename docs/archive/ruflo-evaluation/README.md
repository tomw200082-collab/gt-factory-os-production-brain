# Ruflo evaluation — closed 2026-05-22, repo retired 2026-08-01

Verdict (doc 14): **NO_GO** for install in any production repo; sandbox proved
full install too broad (272 files, 98 agent templates, global writes ignoring
`--no-global`). GO_WITH_CONSTRAINTS existed only for read-only/planning use —
never exercised in the 10 weeks since. Nothing active references the sandbox;
the one `CURRENT_STATE.md` citation pointed at a file that did not exist
(`26_PROPOSED_BRAIN_PATCH_DIFF.md`) and was removed in the 2026-07-31 doc-lean.

These 3 files are the durable decision record. Everything else lives read-only
in the archived GitHub repo `tomw200082-collab/TEST-GT-START`.
