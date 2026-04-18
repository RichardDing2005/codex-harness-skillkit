# Logical Codex flow validation

This repository is designed to satisfy both plugin discovery and explicit skill execution:

1. Codex can discover the plugin through either a personal marketplace install or the repo-local marketplace at `.agents/plugins/marketplace.json`.
2. The plugin points Codex at `./skills/` through `.codex-plugin/plugin.json`.
3. Each skill has required front matter (`name`, `description`) and `agents/openai.yaml` metadata.
4. `project_bootstrap` uses a true runner (`run_bootstrap.py`) that enforces the documented order: gap report -> decision log -> blocking stop if needed -> staged render -> validate -> sync -> handoff.
5. The shared self-check runs a bootstrap smoke test and verifies that the resulting `state/CURRENT_STATE.json` records a real passing validation result.

This logical validation is complemented by `scripts/self_check.py`.
