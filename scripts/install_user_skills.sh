#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST_DIR="${HOME}/.agents/skills/project-harness-codex"
mkdir -p "${HOME}/.agents/skills"
rm -rf "${DEST_DIR}"
ln -s "${ROOT_DIR}/skills" "${DEST_DIR}"
echo "Linked raw skills to ${DEST_DIR}"
echo "This mode is developer-only. Plugin installation remains the recommended distribution path."
