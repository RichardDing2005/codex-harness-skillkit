#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_NAME="project-harness-codex"
DEST_PLUGIN_DIR="${HOME}/.codex/plugins/${PLUGIN_NAME}"
MARKETPLACE="${HOME}/.agents/plugins/marketplace.json"

mkdir -p "${HOME}/.codex/plugins" "${HOME}/.agents/plugins"
rm -rf "${DEST_PLUGIN_DIR}"
cp -R "${ROOT_DIR}" "${DEST_PLUGIN_DIR}"

python3 - <<'PY'
import json
from pathlib import Path
plugin_name = 'project-harness-codex'
marketplace = Path.home() / '.agents' / 'plugins' / 'marketplace.json'
marketplace.parent.mkdir(parents=True, exist_ok=True)
if marketplace.exists():
    data = json.loads(marketplace.read_text(encoding='utf-8'))
else:
    data = {'name': 'personal-local-plugins', 'interface': {'displayName': 'Personal Local Plugins'}, 'plugins': []}
plugins = [p for p in data.get('plugins', []) if p.get('name') != plugin_name]
plugins.append({
    'name': plugin_name,
    'source': {'source': 'local', 'path': './.codex/plugins/project-harness-codex'},
    'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
    'category': 'Productivity'
})
data['plugins'] = plugins
marketplace.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
PY

echo "Installed ${PLUGIN_NAME} into ${DEST_PLUGIN_DIR}"
echo "Updated ${MARKETPLACE}"
echo "Restart Codex, then use /plugins to enable project-harness-codex."
