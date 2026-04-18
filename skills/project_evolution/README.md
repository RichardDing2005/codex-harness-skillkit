# Project Evolution

Use `project_evolution` when a repository already follows the Generic Project Harness structure, or when a retrofit attempt has stopped because the repository contains conflicting or partial control files.

## Backup recommendation

Before using this skill, strongly back up the current project files and data.

## Typical use cases

- change process or pipeline details without breaking runtime continuity
- update state, memory, config, or templates in a controlled way
- reconcile a repository that already contains harness signals but is not internally consistent
- continue after `project_retrofit` writes a conflict report and recommends evolution
