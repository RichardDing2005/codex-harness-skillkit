#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from classify_repo import classify_repo
from inspect_project import inventory_repo

SHARED_VALIDATOR = Path(__file__).resolve().parents[2] / '_shared' / 'scripts' / 'validate_harness.py'


def load_validator():
    spec = importlib.util.spec_from_file_location('validate_harness', SHARED_VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def detect_control_conflicts(root: Path, inventory: dict | None = None, classification: dict | None = None) -> dict:
    inventory = inventory or inventory_repo(root)
    classification = classification or classify_repo(inventory)
    present = classification.get('present_controls', [])
    if not present:
        return {
            'has_conflict': False,
            'reason': '',
            'conflicting_controls': [],
            'recommended_skill': '',
        }

    validator = load_validator()
    target = Path(root)
    if len(present) == 6:
        validation = validator.validate_repo(target, require_bootstrap_docs=False)
        if validation.get('valid'):
            return {
                'has_conflict': True,
                'reason': 'repository already contains a valid harness control layer',
                'conflicting_controls': present,
                'recommended_skill': 'project_evolution',
                'validation': validation,
            }
        return {
            'has_conflict': True,
            'reason': 'repository contains a full but inconsistent harness control layer',
            'conflicting_controls': present,
            'recommended_skill': 'project_evolution',
            'validation': validation,
        }

    return {
        'has_conflict': True,
        'reason': 'repository contains partial or conflicting harness control files',
        'conflicting_controls': present,
        'recommended_skill': 'project_evolution',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Detect retrofit control-file conflicts.')
    parser.add_argument('--target', default='.')
    args = parser.parse_args()
    inventory = inventory_repo(Path(args.target))
    classification = classify_repo(inventory)
    payload = detect_control_conflicts(Path(args.target), inventory=inventory, classification=classification)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not payload.get('has_conflict') else 1


if __name__ == '__main__':
    raise SystemExit(main())
