#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / '_shared' / 'scripts' / 'validate_harness.py'


def load_validator():
    spec = importlib.util.spec_from_file_location('validate_harness', VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description='Create an evolution impact report and validate the harness.')
    parser.add_argument('--target', default='.')
    parser.add_argument('--summary', required=True)
    args = parser.parse_args()
    target = Path(args.target).resolve()
    validator = load_validator()
    validation = validator.validate_repo(target, require_bootstrap_docs=False)
    docs = target / 'docs'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'EVOLUTION_IMPACT_REPORT.md').write_text('''# EVOLUTION_IMPACT_REPORT

- requested_change: %s
- validation_before_change: %s
''' % (args.summary, 'pass' if validation.get('valid') else 'fail'), encoding='utf-8')
    print(json.dumps({'status': 'planned', 'impact_report': 'docs/EVOLUTION_IMPACT_REPORT.md', 'validation': validation}, indent=2, ensure_ascii=False))
    return 0 if validation.get('valid') else 1


if __name__ == '__main__':
    raise SystemExit(main())
