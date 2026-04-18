# Harness runtime contract

A valid Generic Project Harness repository must expose the control kernel through:

- `AGENTS.md`
- `PIPELINE.md`
- `state/CURRENT_STATE.json`
- `config/stage_defaults.json`
- `memory/index.json`
- `garbage/index.json`

For a non-bootstrap active repository, state must point to valid pipeline anchors and a real latest snapshot.

For bootstrap-generated repositories in this plugin, the minimum required generated docs are:

- `docs/BOOTSTRAP_GAP_REPORT.md`
- `docs/BOOTSTRAP_DECISION_LOG.md`

The shared validator checks these conditions and reports JSON output with `valid`, `errors`, and `warnings`.
