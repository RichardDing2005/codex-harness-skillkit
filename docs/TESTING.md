# Testing

## Package self-check

```bash
python3 scripts/self_check.py
```

The self-check verifies:

- required plugin files exist
- each skill has `SKILL.md` and `agents/openai.yaml`
- the shared validator exists
- the repo-local marketplace is present
- `project_bootstrap` can render a temporary harness from the bundled example brief
- the rendered harness passes shared validation

## Manual repo-local plugin test

1. Open this repository in Codex.
2. Run `/plugins` and confirm `project-harness-codex` appears.
3. Open `examples/bootstrap_minimal/` as a target or create a temporary empty directory.
4. Add a `BOOTSTRAP_BRIEF.md`.
5. Explicitly invoke `$project_bootstrap`.
6. Confirm that the target receives the required harness files and that `state/CURRENT_STATE.json` shows a real verification result.

## Manual personal-marketplace test

Install the plugin with `scripts/install_plugin_local.*`, restart Codex, and repeat the explicit skill invocation from any target repository.
