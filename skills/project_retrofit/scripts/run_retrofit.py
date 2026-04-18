#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

INSPECT = Path(__file__).with_name('inspect_project.py')


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description='Create retrofit inventory and mapping documents.')
    parser.add_argument('--target', default='.')
    parser.add_argument('--overlay-missing-harness', action='store_true')
    args = parser.parse_args()
    target = Path(args.target).resolve()
    inspect = load_module(INSPECT, 'inspect_project')
    inventory = inspect.inventory(target)
    docs = target / 'docs'
    docs.mkdir(parents=True, exist_ok=True)
    inspect_output = docs / 'PROJECT_INVENTORY.md'
    lines = ['# PROJECT_INVENTORY', '', f'- file_count: {inventory["file_count"]}', '', '## Top level', '']
    lines.extend([f'- {item}' for item in inventory['top_level']])
    lines += ['', '## Files', '']
    lines.extend([f'- {item}' for item in inventory['files']])
    inspect_output.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (docs / 'RETROFIT_INVENTORY.md').write_text('''# RETROFIT_INVENTORY

- status: inventory_created
- file_count: %d
''' % inventory['file_count'], encoding='utf-8')
    (docs / 'RETROFIT_MAPPING.md').write_text('''# RETROFIT_MAPPING

- control docs: to be overlaid or mapped
- legacy assets: preserve until explicitly archived
''', encoding='utf-8')
    (docs / 'RETROFIT_DECISION_LOG.md').write_text('''# RETROFIT_DECISION_LOG

- status: planning_only
- overlay_requested: %s
''' % ('true' if args.overlay_missing_harness else 'false'), encoding='utf-8')
    print(json.dumps({'status': 'planned', 'inventory_docs': ['docs/PROJECT_INVENTORY.md','docs/RETROFIT_INVENTORY.md','docs/RETROFIT_MAPPING.md','docs/RETROFIT_DECISION_LOG.md'], 'next_action': 'Resolve preservation and authority questions before overlaying harness files.'}, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
