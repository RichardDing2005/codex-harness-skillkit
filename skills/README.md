# Skills overview

This plugin exposes exactly three user-facing skills:

- `project_bootstrap`
- `project_retrofit`
- `project_evolution`

All three are **explicit-use** skills. Each skill includes `agents/openai.yaml` with `allow_implicit_invocation: false` because these workflows can create, restructure, or reinterpret repositories.

The skills share one support layer:

- `skills/_shared/assets/generic-project-harness-blueprint/` — embedded reference blueprint
- `skills/_shared/scripts/validate_harness.py` — shared harness validator
- `skills/_shared/references/harness_runtime_contract.md` — common runtime contract
