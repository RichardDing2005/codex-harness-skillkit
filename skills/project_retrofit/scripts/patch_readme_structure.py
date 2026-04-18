#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STRUCTURE_TITLES = {
    'project structure', 'repository structure', 'directory layout', 'project layout',
    '项目结构', '目录结构', '仓库结构'
}
HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$')


def build_section(heading_level: int, heading_text: str, mapping: list[dict], project_title: str) -> str:
    sub = '#' * min(6, heading_level + 1)
    lines = [f"{'#' * heading_level} {heading_text}", '', 'This repository now preserves the legacy working directories in place and adds a Generic Project Harness control layer around them.', '', f'{sub} Preserved legacy working directories', '']
    for item in mapping:
        if item['action'] == 'preserve_in_place':
            lines.append(f"- `{item['directory']}` — {item['notes']}")
    lines += ['', f'{sub} Harness Control Files', '', '- `AGENTS.md` — repository operating contract', '- `PIPELINE.md` — stage and subflow contract', '- `CONTRIBUTIONS.md` — contribution and repository maintenance guidance', '- `state/` — current execution pointer and runtime truth', '- `memory/` — active events and snapshots', '- `config/` — stable configuration references', '- `garbage/` — retired or superseded records', '', f'{sub} Current Retrofit Status', '', f'The repository **{project_title}** has entered the Generic Project Harness through a safe overlay. Existing legacy project files remain in place.', '', f'{sub} Next Step', '', 'Run `stage_identification` to determine the current authoritative working zone and first narrow target.']
    return '\n'.join(lines) + '\n'


def patch_readme_structure(readme_path: Path, mapping: list[dict], project_title: str) -> dict:
    original = readme_path.read_text(encoding='utf-8')
    lines = original.splitlines()
    heading_positions: list[tuple[int, int, str]] = []
    for idx, line in enumerate(lines):
        match = HEADING_RE.match(line.strip())
        if match:
            heading_positions.append((idx, len(match.group(1)), match.group(2).strip()))
    for pos, level, title in heading_positions:
        if title.lower() not in STRUCTURE_TITLES:
            continue
        end = len(lines)
        for next_pos, next_level, _ in heading_positions:
            if next_pos > pos and next_level <= level:
                end = next_pos
                break
        replacement = build_section(level, title, mapping, project_title).splitlines()
        updated = lines[:pos] + replacement + lines[end:]
        readme_path.write_text('\n'.join(updated).rstrip() + '\n', encoding='utf-8')
        return {'patched': True, 'fallback_created': False, 'matched_heading': title}
    return {'patched': False, 'fallback_created': False, 'matched_heading': ''}


def main() -> int:
    parser = argparse.ArgumentParser(description='Patch a README structure section with harness information.')
    parser.add_argument('--readme', required=True)
    parser.add_argument('--mapping-json', required=True)
    parser.add_argument('--project-title', required=True)
    args = parser.parse_args()
    mapping = json.loads(Path(args.mapping_json).read_text(encoding='utf-8'))
    payload = patch_readme_structure(Path(args.readme), mapping, args.project_title)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get('patched') else 2


if __name__ == '__main__':
    raise SystemExit(main())
