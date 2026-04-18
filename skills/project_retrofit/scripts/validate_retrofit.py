#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

SHARED_VALIDATOR = Path(__file__).resolve().parents[2] / '_shared' / 'scripts' / 'validate_harness.py'
REQUIRED_DOCS = [
    'docs/PROJECT_INVENTORY.md',
    'docs/RETROFIT_INVENTORY.md',
    'docs/RETROFIT_MAPPING.md',
    'docs/RETROFIT_DECISION_LOG.md',
]


def load_validator():
    spec = importlib.util.spec_from_file_location('validate_harness', SHARED_VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def validate_retrofit(root: Path) -> dict:
    validator = load_validator()
    shared = validator.validate_repo(root, require_bootstrap_docs=False)
    errors = list(shared.get('errors', []))
    warnings = list(shared.get('warnings', []))
    for rel in REQUIRED_DOCS:
        if not (root / rel).exists():
            errors.append(f'missing retrofit doc: {rel}')
    state_path = root / 'state' / 'CURRENT_STATE.json'
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding='utf-8'))
        if state.get('current_subflow_anchor') != 'PIPELINE:subflow.stage_identification':
            errors.append('retrofit state did not hand off to stage_identification')
        if state.get('last_action') != 'retrofit_safe_overlay':
            warnings.append('state last_action is not retrofit_safe_overlay')
    return {
        'repo_root': str(root),
        'valid': not errors,
        'errors': errors,
        'warnings': warnings,
        'shared_validation': shared,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate retrofit output.')
    parser.add_argument('--target', default='.')
    args = parser.parse_args()
    payload = validate_retrofit(Path(args.target).resolve())
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
