#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

IGNORED = {'.git', '__pycache__', '.DS_Store'}


def inventory(root: Path) -> dict:
    files = []
    for path in sorted(root.rglob('*')):
        if any(part in IGNORED for part in path.parts):
            continue
        if path.is_file():
            files.append(str(path.relative_to(root)).replace('\\', '/'))
    return {'repo_root': str(root), 'file_count': len(files), 'top_level': sorted({p.split('/')[0] for p in files}), 'files': files}


def main() -> int:
    parser = argparse.ArgumentParser(description='Inventory an existing project for retrofit.')
    parser.add_argument('repo_root', nargs='?', default='.')
    parser.add_argument('--output', default='docs/PROJECT_INVENTORY.md')
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    payload = inventory(root)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = ['# PROJECT_INVENTORY', '', f'- file_count: {payload["file_count"]}', '', '## Top level', '']
    for item in payload['top_level']:
        lines.append(f'- {item}')
    lines += ['', '## Files', '']
    for item in payload['files']:
        lines.append(f'- {item}')
    output.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'ok', 'output': str(output.relative_to(root))}, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
