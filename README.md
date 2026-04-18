# Project Harness Codex

A publishable Codex plugin that bundles three explicit-use skills:

- `project_bootstrap` — create a first-operable Generic Project Harness from a new or nearly empty project brief.
- `project_retrofit` — inventory and migrate an existing non-harness project into the harness without silently discarding history.
- `project_evolution` — make controlled changes to an already harnessed repository while preserving state and memory continuity.

## Package model

This repository is a **plugin-first distribution**. The reusable workflows live under `skills/`, and the plugin manifest lives at `.codex-plugin/plugin.json`.

The repository also includes a **repo-local marketplace** at `.agents/plugins/marketplace.json` for development and self-testing. When you open this repository itself in Codex, that marketplace gives Codex a local path to this plugin.

## Skill maturity

- `project_bootstrap`: beta — fully scripted runner, renderer, validator, and smoke test.
- `project_retrofit`: preview — report-first workflow with a conservative overlay helper.
- `project_evolution`: preview — impact-report-first workflow with controlled validation.

## Supported installation modes

### 1. Personal marketplace install (recommended for normal use)

Use the install scripts in `scripts/` or follow `docs/INSTALL_PLUGIN.md`.

### 2. Repo-local plugin development

Open this repository in Codex and use `/plugins` to confirm that the repo-local marketplace exposes `project-harness-codex`.

### 3. Raw user-level skills install (developer-only)

Supported for iteration and debugging through `scripts/install_user_skills.*`, but not the recommended end-user distribution path.

## Explicit invocation

All three skills disable implicit invocation. Use them explicitly:

- `$project_bootstrap`
- `$project_retrofit`
- `$project_evolution`

The package also ships with skill-specific default prompts in the plugin manifest and in each skill's `agents/openai.yaml`.

## Self-check

Run:

```bash
python3 scripts/self_check.py
```

This checks package structure and runs a bootstrap smoke test into a temporary repository.

## Important operational note

After `project_bootstrap` or a first-time `project_retrofit` writes a new `AGENTS.md`, start a new Codex run in the target repository so the new project instructions are loaded for the next round.
