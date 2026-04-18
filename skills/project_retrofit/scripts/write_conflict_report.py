#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def write_conflict_report(root: Path, conflict: dict, classification: dict) -> str:
    lines = ['# RETROFIT_CONFLICT_REPORT', '', '## Conflict summary', '']
    lines.append('- conflict_status: detected')
    lines.append(f"- reason: {conflict.get('reason')}")
    lines += ['', '## Conflicting control signals', '']
    for item in conflict.get('conflicting_controls', []):
        lines.append(f'- `{item}`')
    lines += ['', '## Why retrofit stopped', '']
    lines.append(f"- repository classification: {classification.get('repo_classification')}")
    lines.append('- retrofit only overlays a harness shell onto legacy repositories with no conflicting control layer')
    lines += ['', '## Recommended next skill', '']
    lines.append('- `project_evolution`')
    lines += ['', '## Recommended next action', '']
    lines.append('- Back up the current project files and data.')
    lines.append('- Start `project_evolution` and use this report as reference.')
    path = root / 'docs' / 'RETROFIT_CONFLICT_REPORT.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 'docs/RETROFIT_CONFLICT_REPORT.md'


def main() -> int:
    parser = argparse.ArgumentParser(description='Write a retrofit conflict report.')
    parser.add_argument('--target', default='.')
    parser.add_argument('--conflict-json', required=True)
    parser.add_argument('--classification-json', required=True)
    args = parser.parse_args()
    conflict = json.loads(Path(args.conflict_json).read_text(encoding='utf-8'))
    classification = json.loads(Path(args.classification_json).read_text(encoding='utf-8'))
    rel = write_conflict_report(Path(args.target).resolve(), conflict, classification)
    print(json.dumps({'report': rel}, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
