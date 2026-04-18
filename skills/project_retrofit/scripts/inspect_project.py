#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EXCLUDE_DIRS = {
    '.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.venv', 'venv',
    '.idea', '.vscode', '.agents', '.codex-plugin'
}
EXCLUDE_FILES = {'.DS_Store'}
TOP_LEVEL_ROLE_HINTS = {
    'src': 'code_core',
    'source': 'code_core',
    'app': 'code_core',
    'lib': 'code_core',
    'scripts': 'workflow_scripts',
    'bin': 'workflow_scripts',
    'docs': 'documentation',
    'doc': 'documentation',
    'config': 'config_candidates',
    'configs': 'config_candidates',
    'data': 'data_assets',
    'datasets': 'data_assets',
    'results': 'results_zone',
    'outputs': 'outputs_zone',
    'reports': 'reports_zone',
    'notebooks': 'notebook_zone',
    'tests': 'test_suite',
}
CORE_CONTROL_PATHS = [
    'AGENTS.md',
    'PIPELINE.md',
    'state/CURRENT_STATE.json',
    'memory/index.json',
    'config/stage_defaults.json',
    'garbage/index.json',
]


def should_skip(path: Path) -> bool:
    if path.name in EXCLUDE_FILES:
        return True
    return any(part in EXCLUDE_DIRS for part in path.parts)


HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$')


def readme_title_and_sections(root: Path) -> tuple[str, list[str]]:
    readme = root / 'README.md'
    if not readme.exists():
        return '', []
    title = ''
    sections: list[str] = []
    for line in readme.read_text(encoding='utf-8').splitlines():
        match = HEADING_RE.match(line.strip())
        if not match:
            continue
        heading = match.group(2).strip()
        if not title and match.group(1) == '#':
            title = heading
        sections.append(heading)
    return title, sections


def classify_file_bucket(rel: str) -> str:
    path = Path(rel)
    top = path.parts[0].lower() if path.parts else ''
    ext = path.suffix.lower()
    if ext == '.ipynb':
        return 'notebooks'
    if top in {'results', 'outputs', 'reports', 'notebooks', 'docs', 'config', 'configs', 'data', 'datasets', 'scripts', 'src', 'tests'}:
        return top
    if ext in {'.py', '.sh', '.ps1', '.bat'}:
        return 'code_and_scripts'
    if ext in {'.md', '.rst', '.txt'}:
        return 'docs_and_notes'
    if ext in {'.json', '.yaml', '.yml', '.toml', '.ini'}:
        return 'config_like'
    return 'other'


def inventory_repo(root: Path) -> dict:
    root = root.resolve()
    title, readme_sections = readme_title_and_sections(root)
    files: list[str] = []
    bucket_counts: dict[str, int] = {}
    top_level_entries: list[dict] = []

    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if should_skip(child):
            continue
        top_level_entries.append({
            'name': child.name,
            'kind': 'directory' if child.is_dir() else 'file',
            'detected_role': TOP_LEVEL_ROLE_HINTS.get(child.name.lower(), 'legacy_root_file' if child.is_file() else 'legacy_working_zone'),
        })

    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if should_skip(Path(rel)):
            continue
        files.append(rel)
        bucket = classify_file_bucket(rel)
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

    significant_dirs = [entry['name'] for entry in top_level_entries if entry['kind'] == 'directory']
    harness_markers = {rel: (root / rel).exists() for rel in CORE_CONTROL_PATHS}
    present_controls = [rel for rel, exists in harness_markers.items() if exists]
    return {
        'repo_root': str(root),
        'project_title': title or root.name,
        'readme_sections': readme_sections,
        'file_count': len(files),
        'files': files,
        'top_level_entries': top_level_entries,
        'significant_dirs': significant_dirs,
        'bucket_counts': bucket_counts,
        'harness_markers': harness_markers,
        'present_controls': present_controls,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Inspect an existing repository for retrofit planning.')
    parser.add_argument('--target', default='.')
    args = parser.parse_args()
    payload = inventory_repo(Path(args.target))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
