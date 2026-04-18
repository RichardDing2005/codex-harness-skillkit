# Architecture

## Package layers

1. `.codex-plugin/plugin.json` identifies the plugin and points Codex at `./skills/`.
2. `skills/` contains the three user-facing skills and one shared support layer.
3. `skills/_shared/` holds the embedded Generic Project Harness blueprint, shared validation, and runtime contracts.
4. `scripts/` at the repository root contains installation and self-check utilities.
5. `.agents/plugins/marketplace.json` provides a repo-local development marketplace that points back to the plugin root.

## Why plugin-first

The package contains more than one skill and is intended for distribution on GitHub. That makes plugin packaging the correct outer form. Raw skills remain present because a plugin contains a `skills/` directory, but plugin installation is the primary supported path.

## Why three skills

The bundle routes work by project state rather than by internal subflow names:

- bootstrap: no harness yet
- retrofit: project exists but no valid harness
- evolution: harness already exists

This keeps discovery stable and prevents the end user from having to think in low-level stage names before a harness exists.
