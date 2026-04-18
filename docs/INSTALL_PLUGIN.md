# Install the plugin

## Recommended: personal marketplace install

### Linux / macOS

```bash
bash scripts/install_plugin_local.sh
```

### Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_plugin_local.ps1
```

The scripts copy this repository into `~/.codex/plugins/project-harness-codex`, create or update `~/.agents/plugins/marketplace.json`, and point the plugin entry at the copied plugin directory.

Restart Codex after installation. Then use `/plugins` to confirm the plugin is visible and enabled.

## Repo-local development install

This repository already includes `.agents/plugins/marketplace.json` that points to `./`. Open this repository in Codex, run `/plugins`, and confirm that `project-harness-codex` is available. This mode is intended for developing or testing the plugin itself.

## Developer-only raw skills install

```bash
bash scripts/install_user_skills.sh
```

or

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_user_skills.ps1
```

This links or copies `skills/` into `~/.agents/skills/project-harness-codex`. Use this only when you intentionally want raw user-level skills rather than plugin installation.
