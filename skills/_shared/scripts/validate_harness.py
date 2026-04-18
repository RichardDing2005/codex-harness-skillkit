#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

ANCHOR_RE = re.compile(r"\[([A-Z_]+:[A-Za-z0-9_.:-]+)\]")
REQUIRED_COMMON = [
    'README.md',
    'AGENTS.md',
    'PIPELINE.md',
    'CONTRIBUTIONS.md',
    'state/CURRENT_STATE.json',
    'config/stage_defaults.json',
    'memory/index.json',
    'garbage/index.json',
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def load_anchors(pipeline_path: Path) -> set[str]:
    anchors: set[str] = set()
    for line in pipeline_path.read_text(encoding='utf-8').splitlines():
        for match in ANCHOR_RE.finditer(line):
            anchors.add(match.group(1))
    return anchors


def rel_exists(root: Path, rels: Iterable[str]) -> list[str]:
    missing: list[str] = []
    for rel in rels:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def validate_repo(root: Path, require_bootstrap_docs: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    missing_common = rel_exists(root, REQUIRED_COMMON)
    if missing_common:
        errors.extend(f'missing required file: {rel}' for rel in missing_common)
        return {'repo_root': str(root), 'valid': False, 'errors': errors, 'warnings': warnings}

    state = load_json(root / 'state' / 'CURRENT_STATE.json')
    memory_index = load_json(root / 'memory' / 'index.json')
    anchors = load_anchors(root / 'PIPELINE.md')
    current_anchor = state.get('current_pipeline_anchor')
    subflow_anchor = state.get('current_subflow_anchor')
    latest_snapshot_ref = state.get('latest_snapshot_ref')
    active_memory_refs = state.get('active_memory_refs', [])

    if current_anchor and current_anchor not in anchors:
        errors.append(f'invalid current_pipeline_anchor: {current_anchor}')
    if subflow_anchor and subflow_anchor not in anchors:
        errors.append(f'invalid current_subflow_anchor: {subflow_anchor}')

    for ref in state.get('required_config_refs', []):
        if not (root / ref).exists():
            errors.append(f'missing required config ref: {ref}')

    if state.get('bootstrap_mode') is False:
        if not latest_snapshot_ref:
            errors.append('non-bootstrap state requires latest_snapshot_ref')
        elif not (root / latest_snapshot_ref).exists():
            errors.append(f'missing latest_snapshot_ref target: {latest_snapshot_ref}')
        for ref in active_memory_refs:
            if not (root / ref).exists():
                errors.append(f'missing active_memory_ref target: {ref}')

    idx_snapshot = memory_index.get('active_snapshot')
    if latest_snapshot_ref and idx_snapshot and idx_snapshot != latest_snapshot_ref:
        warnings.append('state latest_snapshot_ref differs from memory/index.json active_snapshot')

    if require_bootstrap_docs:
        for rel in ['docs/BOOTSTRAP_GAP_REPORT.md', 'docs/BOOTSTRAP_DECISION_LOG.md']:
            if not (root / rel).exists():
                errors.append(f'missing bootstrap doc: {rel}')

    return {
        'repo_root': str(root),
        'valid': not errors,
        'errors': errors,
        'warnings': warnings,
        'state_summary': {
            'bootstrap_mode': state.get('bootstrap_mode'),
            'formal_stage': state.get('formal_stage'),
            'current_pipeline_anchor': current_anchor,
            'current_subflow_anchor': subflow_anchor,
            'last_verification': state.get('last_verification', {}),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate a Generic Project Harness repository.')
    parser.add_argument('repo_root', nargs='?', default='.')
    parser.add_argument('--require-bootstrap-docs', action='store_true')
    args = parser.parse_args()
    payload = validate_repo(Path(args.repo_root).resolve(), require_bootstrap_docs=args.require_bootstrap_docs)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
