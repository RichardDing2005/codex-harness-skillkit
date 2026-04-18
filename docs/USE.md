# Use the plugin

## Check discovery

1. Restart Codex after installation.
2. Open `/plugins` to verify that `project-harness-codex` is available.
3. Open `/skills` to verify the three skills are visible.

## Safety first

Before using `project_retrofit` or `project_evolution`, back up the current project files and data.

## Explicit-use workflow

### Bootstrap

Create or edit `BOOTSTRAP_BRIEF.md` in the target repository, then explicitly invoke:

```text
$project_bootstrap Read BOOTSTRAP_BRIEF.md, identify only blocking gaps, then generate a first-operable Generic Project Harness when the blocking information is sufficient.
```

### Retrofit

Retrofit has two modes.

#### 1. Plan

```text
$project_retrofit Inventory this existing repository, classify its current control-layer state, build a directory-level retrofit plan, preserve legacy working directories in place, and stop if any control-file conflicts require project_evolution.
```

#### 2. Apply safe overlay

Only continue after planning is complete, no blocking questions remain, and the repository has no conflicting harness control files.

```text
$project_retrofit Apply a safe overlay for the completed retrofit plan. Add the missing harness control files, keep legacy directories in place, do not change results/outputs/reports/notebooks, and only patch README structure sections if I explicitly approve that change.
```

Safe overlay rules:

- default mapping is directory-level
- `results/`, `outputs/`, `reports/`, and `notebooks/` are preserved in place
- `README.md` may be patched only after explicit approval
- if conflicting `AGENTS.md`, `PIPELINE.md`, or `state/` signals are detected, retrofit stops and recommends `project_evolution`
- after a successful safe overlay, the next step is `stage_identification`

### Evolution

```text
$project_evolution Read the current harness state, write an impact report, and make the requested controlled change without breaking state or memory continuity.
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
