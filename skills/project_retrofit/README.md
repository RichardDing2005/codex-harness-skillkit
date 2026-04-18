# Project Retrofit

Use `project_retrofit` when a repository already contains meaningful legacy material that must remain visible while a Generic Project Harness control layer is added around it.

## Backup recommendation

Before using this skill, strongly back up the current project files and data.

## Operating modes

### `plan`

- inventory the existing repository
- classify the current control-layer state
- build a directory-level retrofit map
- preserve legacy working directories in place
- stop when control-file conflicts or blocking questions require user input

### `apply-safe-overlay`

Only available after `plan` succeeds with no blocking questions and no conflicting control files.

This mode may:

- add missing harness control files
- initialize `state/`, `memory/`, `config/`, and `garbage/`
- patch an existing README structure section only when explicit approval is already recorded

This mode does **not**:

- move legacy working directories
- delete legacy material
- rewrite `results/`, `outputs/`, `reports/`, or `notebooks/`
- continue when conflicting control files suggest the repository should be handled by `project_evolution`

## Default preservation policy

The following directories default to `preserve_in_place`:

- `results/`
- `outputs/`
- `reports/`
- `notebooks/`

## Conflict redirect

If retrofit detects conflicting or partial control files, it stops and writes `docs/RETROFIT_CONFLICT_REPORT.md` with a recommendation to continue through `project_evolution`.
