# GitHub release guide

## What to publish

Publish the repository as a plugin-first Codex package. Keep the following at the root:

- `.codex-plugin/plugin.json`
- `skills/`
- `scripts/`
- `docs/`
- `.agents/plugins/marketplace.json` for repo-local development

## What to say in the GitHub README

- this is a Codex plugin that bundles three explicit-use skills
- the recommended installation path is personal-marketplace plugin install
- repo-local opening is supported for plugin development because `.agents/plugins/marketplace.json` is included
- raw user-level skills installation is developer-only
- `project_bootstrap` is the most mature skill
- `project_retrofit` and `project_evolution` are preview skills

## Before tagging a release

1. Run `python3 scripts/self_check.py`.
2. Verify `CHANGELOG.md` and `.codex-plugin/plugin.json` version match.
3. Verify installation instructions still match the repository name.
4. Replace placeholder repository URLs in `.codex-plugin/plugin.json` when the GitHub location is finalized.
