# Bootstrap contract

`project_bootstrap` is for new or nearly empty projects only.

It must:

1. read a project-language brief
2. normalize it into bootstrap slots
3. classify each slot as resolved, blocking, defaultable, or deferrable
4. write `docs/BOOTSTRAP_GAP_REPORT.md`
5. write `docs/BOOTSTRAP_DECISION_LOG.md` before core harness files are modified
6. ask only the minimum blocking questions required to proceed truthfully
7. render a first-operable harness in staging
8. validate the staged harness
9. sync the validated harness into the target repository
10. return a concrete next action and advise a new Codex run
