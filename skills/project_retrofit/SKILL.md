---
name: project_retrofit
description: Use explicitly when an existing project already contains meaningful files, outputs, notebooks, reports, or workflow traces that must be preserved and mapped into a Generic Project Harness. Do not use for empty projects or already-harnessed projects.
---

# Project Retrofit

## Purpose

Inventory an existing non-harness repository, identify preservation and authority constraints, and overlay a truthful harness without silently discarding history.

## Maturity

Preview. Inventory and mapping are scripted. Full migration is intentionally conservative.

## Required order

1. inventory existing material
2. write `docs/PROJECT_INVENTORY.md`
3. write `docs/RETROFIT_INVENTORY.md`
4. write `docs/RETROFIT_MAPPING.md`
5. write `docs/RETROFIT_DECISION_LOG.md`
6. ask only migration-safety questions
7. overlay missing harness files only after the mapping is explicit
8. validate and hand off

## Entrypoints

```bash
python3 skills/project_retrofit/scripts/run_retrofit.py --target .
```

## Forbidden actions

Do not delete or archive legacy files without explicit approval. Do not infer authoritative outputs from recency alone. Do not skip the inventory or mapping documents.
