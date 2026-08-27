# Dev Workflow Decision Log

Append-only, dated log of engineering decisions and completed work.
`specs/workflow.md` stays normative-only; **append new dated entries
here**, newest at the bottom. The fast "what's next" pointer is
`specs/NEXT.md`; durable facts are in `specs/memory.md`.

- __DATE__: Created the repo's governance scaffolding via the
  `python-repo-init` skill (ported from the pattern established in
  `47688-columbia-school-district` / `junos-set-tree-sitter`):
  `specs/workflow.md` + this log, `specs/memory.md`, `specs/NEXT.md`,
  minimal `AGENTS.md` + thin pointers, `docs/README.md`,
  `scripts/check_repo_conventions.py` + `scripts/split_spec_history.py` +
  `.githooks/` + CI, and the `data/` + `src/`/`tests/` layout. No skills
  implemented yet — see `specs/NEXT.md`.
