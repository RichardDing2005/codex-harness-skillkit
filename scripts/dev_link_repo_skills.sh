#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "${ROOT_DIR}/.agents/skills"
rm -rf "${ROOT_DIR}/.agents/skills/project-harness-codex"
ln -s "${ROOT_DIR}/skills" "${ROOT_DIR}/.agents/skills/project-harness-codex"
echo "Linked repo-local raw skills for development at .agents/skills/project-harness-codex"
