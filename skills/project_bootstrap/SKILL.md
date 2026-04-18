---
name: project_bootstrap
description: Use explicitly when a project is new, nearly empty, or only exists as a concept or brief and must be initialized into a first-operable Generic Project Harness. Do not use for projects that already contain meaningful material that must be preserved or for repositories that already follow the harness.
---

# Project Bootstrap

## Purpose

Turn a new or nearly empty project into a first-operable Generic Project Harness repository.

## Maturity

Beta. This skill has a scripted runner, renderer, and validator.

## When to use

Use this skill only when the repository is empty or near-empty and the main input is a brief, concept note, or short project description.

If the repository already contains substantial code, outputs, scripts, notebooks, reports, or history that must be preserved, stop and switch to `$project_retrofit`.

## Must read

1. `BOOTSTRAP_BRIEF.md` in the target repository if present.
2. User-provided project description if the brief is missing.
3. `references/bootstrap_contract.md`.
4. `../_shared/references/harness_runtime_contract.md`.
5. Embedded blueprint assets at `../_shared/assets/generic-project-harness-blueprint/` only when generation is required.

## Question policy

- Ask only blocking questions.
- Ask at most 4 questions by default.
- Use project language, not harness jargon.
- Default safe items and record them in the decision log.
- Do not ask the user to design anchors, state schema, or memory internals.

## Required order

1. Normalize the brief into bootstrap slots.
2. Write `docs/BOOTSTRAP_GAP_REPORT.md`.
3. Write `docs/BOOTSTRAP_DECISION_LOG.md` before core harness files are modified.
4. Stop for blocking gaps unless placeholders are approved.
5. Render in staging.
6. Validate the staged harness.
7. Sync validated files into the target repository.
8. Return a concrete handoff and advise a new Codex run.

## Scripted entrypoint

Preferred runner:

```bash
python3 skills/project_bootstrap/scripts/run_bootstrap.py --target . --brief BOOTSTRAP_BRIEF.md
```

Allow placeholders only with explicit approval:

```bash
python3 skills/project_bootstrap/scripts/run_bootstrap.py --target . --brief BOOTSTRAP_BRIEF.md --allow-placeholders
```

## Required generated files

A successful bootstrap round should leave at least:

- `README.md`
- `AGENTS.md`
- `PIPELINE.md`
- `CONTRIBUTIONS.md`
- `state/CURRENT_STATE.json`
- `config/stage_defaults.json`
- `memory/index.json`
- `memory/active/events/MEM-BOOTSTRAP-0001.md`
- `memory/active/snapshots/SNAPSHOT-primary_iteration-0001.md`
- `garbage/index.json`
- `docs/BOOTSTRAP_GAP_REPORT.md`
- `docs/BOOTSTRAP_DECISION_LOG.md`

## Forbidden actions

Do not overwrite an existing harness without explicit approval. Do not skip the gap report. Do not skip the decision log. Do not leave `last_verification.status` as `not_yet_run` after a successful scripted bootstrap.

## Human-facing result format

### Stage Result
One sentence: generated, blocked, or switched to retrofit.

### Evidence
- brief source
- normalized slot statuses
- files generated
- validation result

### Next Choice
- concrete next action in the new harness
- whether to start a new Codex run
- deferred items reserved for `project_evolution`
