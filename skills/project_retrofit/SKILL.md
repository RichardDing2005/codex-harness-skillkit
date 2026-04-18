---
name: project_retrofit
description: Use explicitly when an existing repository already contains meaningful legacy files, outputs, notebooks, reports, or workflow traces that must remain in place while a Generic Project Harness control layer is planned and, when safe, overlaid. Do not use for empty projects. Stop and redirect to project_evolution when conflicting control files are already present.
---

# Project Retrofit

## Purpose

Inventory an existing repository, build a directory-level retrofit plan, preserve legacy working zones in place, and add a minimal Generic Project Harness control layer only when safe to do so.

## Backup recommendation

Before using this skill, strongly back up the current project files and data.

## Modes

### `plan`

Required sequence:

1. inventory existing material
2. classify the repository control-layer state
3. detect control-file conflicts
4. write `docs/PROJECT_INVENTORY.md`
5. write `docs/RETROFIT_INVENTORY.md`
6. write `docs/RETROFIT_MAPPING.md`
7. write `docs/RETROFIT_DECISION_LOG.md`
8. stop for blocking questions or conflict redirection

### `apply-safe-overlay`

Allowed only when:

- `plan` has already completed in the same repository
- there are no blocking questions
- there are no conflicting control files
- the user has approved safe overlay
- any README patch has explicit user approval

Required sequence:

1. read the completed retrofit planning documents
2. regenerate the minimal harness shell in staging
3. validate the staged harness shell
4. overlay only the missing harness control files
5. patch README structure content only when explicit approval is recorded
6. validate the overlaid repository
7. write runtime truth into `state/CURRENT_STATE.json`
8. hand off to `stage_identification`

## Entrypoints

```bash
python3 skills/project_retrofit/scripts/run_retrofit.py --target . --mode plan
python3 skills/project_retrofit/scripts/run_retrofit.py --target . --mode apply-safe-overlay
```

## Allowed modifications in `apply-safe-overlay`

- add `AGENTS.md`
- add `PIPELINE.md`
- add `CONTRIBUTIONS.md`
- add `state/CURRENT_STATE.json`
- add `config/stage_defaults.json`
- add `memory/index.json`
- add `memory/active/events/MEM-RETROFIT-0001.md`
- add `memory/active/snapshots/SNAPSHOT-primary_iteration-retrofit-0001.md`
- add `garbage/index.json`
- patch the repository structure section of `README.md` only when explicit approval exists

## Default preservation policy

The following directories default to `preserve_in_place` and are not auto-promoted to authority zones:

- `results/`
- `outputs/`
- `reports/`
- `notebooks/`

## Blocking and conflict rules

- stop when control-file conflicts are detected
- stop when `AGENTS.md`, `PIPELINE.md`, or `state/` already exist in a conflicting or partial form
- stop when the repository is already harnessed or partially harnessed and should instead be reconciled through `project_evolution`
- do not patch an existing `README.md` unless explicit approval is present

## README patch policy

When README patching is approved, patch only a repository-structure section and use the standard harness explanation style. Do not rewrite project background, research content, historical narrative, or authorship sections.

## Forbidden actions

Do not move legacy working directories. Do not delete legacy material. Do not rewrite `results/`, `outputs/`, `reports/`, or `notebooks/`. Do not infer authoritative outputs from file recency alone. Do not continue through a control-file conflict instead of redirecting to `project_evolution`.

## Handoff

A successful safe overlay means the repository has entered the Generic Project Harness. The next action is always `stage_identification` in `primary_iteration`.
