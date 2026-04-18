---
name: project_evolution
description: Use explicitly when a repository already follows the Generic Project Harness structure and needs a controlled change to content, process, outputs, templates, config, state, or memory while preserving continuity. Do not use for first-time creation or legacy migration.
---

# Project Evolution

## Purpose

Apply controlled changes to an existing harness without breaking runtime continuity.

## Maturity

Preview. Impact-report-first workflow plus shared validation.

## Required order

1. read current kernel and state
2. write `docs/EVOLUTION_IMPACT_REPORT.md`
3. freeze in-scope and out-of-scope items
4. apply only necessary changes
5. update memory or state when runtime truth changes
6. validate and hand off

## Entrypoint

```bash
python3 skills/project_evolution/scripts/run_evolution.py --target . --summary "<requested change>"
```

## Forbidden actions

Do not rebuild as bootstrap. Do not treat legacy migration as evolution. Do not change pipeline semantics without recording why.
