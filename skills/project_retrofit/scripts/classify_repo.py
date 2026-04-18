#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from inspect_project import inventory_repo

REQUIRED_CONTROL_COUNT = 6


def classify_repo(inventory: dict) -> dict:
    present = inventory.get('present_controls', [])
    count = len(present)
    if count == 0:
        repo_classification = 'legacy'
        control_layer_status = 'no_harness_signals_detected'
    elif count == REQUIRED_CONTROL_COUNT:
        repo_classification = 'already_harnessed_candidate'
        control_layer_status = 'all_core_harness_signals_present'
    elif count < REQUIRED_CONTROL_COUNT:
        repo_classification = 'partial_harness'
        control_layer_status = 'partial_control_layer_detected'
    else:
        repo_classification = 'hybrid'
        control_layer_status = 'mixed_control_signals_detected'
    return {
        'repo_classification': repo_classification,
        'control_layer_status': control_layer_status,
        'present_controls': present,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Classify the retrofit state of a repository.')
    parser.add_argument('--target', default='.')
    args = parser.parse_args()
    payload = classify_repo(inventory_repo(Path(args.target)))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
