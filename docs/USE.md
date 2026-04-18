# Use the plugin

## Check discovery

1. Restart Codex after installation.
2. Open `/plugins` to verify that `project-harness-codex` is available.
3. Open `/skills` to verify the three skills are visible.

## Explicit-use workflow

### Bootstrap

Create or edit `BOOTSTRAP_BRIEF.md` in the target repository, then explicitly invoke:

```text
$project_bootstrap Read BOOTSTRAP_BRIEF.md, identify only blocking gaps, then generate a first-operable Generic Project Harness when the blocking information is sufficient.
```

### Retrofit

```text
$project_retrofit Inventory this existing project, identify preservation constraints and migration mapping, and do not modify files until the migration plan is explicit.
```

### Evolution

```text
$project_evolution Read the current harness state and make the requested controlled change without breaking state or memory continuity.
```

## Bootstrap execution contract

The scripted bootstrap runner follows this order:

1. normalize the brief
2. write `docs/BOOTSTRAP_GAP_REPORT.md`
3. write `docs/BOOTSTRAP_DECISION_LOG.md`
4. stop for blocking gaps unless placeholders are allowed
5. render the harness in a staging directory
6. validate the staged harness
7. sync validated files into the target directory
8. return a concrete handoff

That ordering is enforced by `skills/project_bootstrap/scripts/run_bootstrap.py`.
