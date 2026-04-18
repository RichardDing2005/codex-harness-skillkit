#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from classify_repo import classify_repo
from inspect_project import TOP_LEVEL_ROLE_HINTS, inventory_repo
from detect_control_conflicts import detect_control_conflicts

PRESERVE_IN_PLACE_NAMES = {'results', 'outputs', 'reports', 'notebooks'}


def infer_mapping(entry: dict) -> dict:
    name = entry['name']
    lowered = name.lower()
    detected_role = entry.get('detected_role') or TOP_LEVEL_ROLE_HINTS.get(lowered, 'legacy_working_zone')
    if lowered in PRESERVE_IN_PLACE_NAMES:
        planned_harness_role = f'preserved_{lowered}_zone'
        action = 'preserve_in_place'
        preservation_policy = 'preserve_in_place'
        notes = 'legacy working content stays where it is and is not auto-promoted to authority.'
    elif lowered in {'src', 'source', 'app', 'lib'}:
        planned_harness_role = 'preserved_code_core'
        action = 'preserve_in_place'
        preservation_policy = 'preserve_in_place'
        notes = 'existing implementation remains in place under harness control.'
    elif lowered in {'scripts', 'bin'}:
        planned_harness_role = 'preserved_workflow_scripts'
        action = 'preserve_in_place'
        preservation_policy = 'preserve_in_place'
        notes = 'workflow scripts remain callable from their current locations.'
    elif lowered in {'docs', 'doc'}:
        planned_harness_role = 'preserved_documentation_zone'
        action = 'preserve_in_place'
        preservation_policy = 'preserve_in_place'
        notes = 'legacy documentation remains visible and may be referenced by the harness.'
    elif lowered in {'config', 'configs'}:
        planned_harness_role = 'preserved_config_zone'
        action = 'preserve_in_place'
        preservation_policy = 'preserve_in_place'
        notes = 'legacy config material remains in place until a later evolution step.'
    elif entry['kind'] == 'file':
        planned_harness_role = 'root_file_preserved'
        action = 'preserve_in_place'
        preservation_policy = 'preserve_in_place'
        notes = 'root file stays in place unless a later evolution step changes it deliberately.'
    else:
        planned_harness_role = 'preserved_legacy_zone'
        action = 'preserve_in_place'
        preservation_policy = 'preserve_in_place'
        notes = 'legacy directory remains where it is during retrofit.'
    return {
        'directory': name,
        'detected_role': detected_role,
        'planned_harness_role': planned_harness_role,
        'action': action,
        'preservation_policy': preservation_policy,
        'needs_confirmation': 'no',
        'notes': notes,
    }


def build_plan(root: Path, approve_readme_patch: bool = False) -> dict:
    inventory = inventory_repo(root)
    classification = classify_repo(inventory)
    conflict = detect_control_conflicts(root, inventory=inventory, classification=classification)
    mapping = [infer_mapping(entry) for entry in inventory.get('top_level_entries', [])]
    apply_allowed = not conflict.get('has_conflict')
    blocking_questions: list[str] = []
    if conflict.get('has_conflict'):
        blocking_questions.append('Control-file conflicts were detected; continue through project_evolution instead of project_retrofit apply-safe-overlay.')
    return {
        'inventory': inventory,
        'classification': classification,
        'conflict': conflict,
        'mapping': mapping,
        'blocking_questions': blocking_questions,
        'apply_safe_overlay_eligible': apply_allowed,
        'readme_patch_approved': approve_readme_patch,
    }


def write_project_inventory(root: Path, plan: dict) -> str:
    inventory = plan['inventory']
    lines = ['# PROJECT_INVENTORY', '', '## Repository summary', '']
    lines.append(f"- project_title: {inventory.get('project_title')}")
    lines.append(f"- file_count: {inventory.get('file_count')}")
    lines.append(f"- top_level_entry_count: {len(inventory.get('top_level_entries', []))}")
    lines += ['', '## Top level entries', '']
    for entry in inventory.get('top_level_entries', []):
        lines.append(f"- {entry['name']} ({entry['kind']}): {entry['detected_role']}")
    lines += ['', '## Bucket counts', '']
    for key, value in sorted(inventory.get('bucket_counts', {}).items()):
        lines.append(f'- {key}: {value}')
    lines += ['', '## Harness markers', '']
    for rel, exists in inventory.get('harness_markers', {}).items():
        lines.append(f'- {rel}: {"present" if exists else "absent"}')
    lines += ['', '## Files', '']
    for rel in inventory.get('files', []):
        lines.append(f'- {rel}')
    path = root / 'docs' / 'PROJECT_INVENTORY.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 'docs/PROJECT_INVENTORY.md'


def write_retrofit_inventory(root: Path, plan: dict) -> str:
    inventory = plan['inventory']
    classification = plan['classification']
    conflict = plan['conflict']
    lines = ['# RETROFIT_INVENTORY', '', '## Repository classification', '']
    lines.append(f"- repo_classification: {classification['repo_classification']}")
    lines.append(f"- control_layer_status: {classification['control_layer_status']}")
    lines.append(f"- apply_safe_overlay_eligibility: {'allowed' if plan['apply_safe_overlay_eligible'] else 'blocked'}")
    lines += ['', '## Significant directories', '']
    for item in plan['mapping']:
        if item['directory'].startswith('.'):
            continue
        lines.append(f"- directory: `{item['directory']}`")
        lines.append(f"  - detected_role: {item['detected_role']}")
        lines.append(f"  - preservation_policy: {item['preservation_policy']}")
    lines += ['', '## Blocking items', '']
    if plan['blocking_questions']:
        for item in plan['blocking_questions']:
            lines.append(f'- {item}')
    else:
        lines.append('- none')
    if conflict.get('has_conflict'):
        lines += ['', '## Conflict redirect', '']
        lines.append(f"- recommended_skill: {conflict.get('recommended_skill')}")
        lines.append(f"- reason: {conflict.get('reason')}")
    lines += ['', '## Next recommendation', '']
    if conflict.get('has_conflict'):
        lines.append('- Stop retrofit apply-safe-overlay and continue through project_evolution after backup.')
    else:
        lines.append('- Safe overlay may proceed after explicit user approval for overlay and any README patch.')
    path = root / 'docs' / 'RETROFIT_INVENTORY.md'
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 'docs/RETROFIT_INVENTORY.md'


def write_retrofit_mapping(root: Path, plan: dict) -> str:
    lines = ['# RETROFIT_MAPPING', '', '| Directory | Detected role | Planned harness role | Action | Preservation policy | Needs confirmation | Notes |', '|---|---|---|---|---|---|---|']
    for item in plan['mapping']:
        lines.append(f"| `{item['directory']}` | {item['detected_role']} | {item['planned_harness_role']} | {item['action']} | {item['preservation_policy']} | {item['needs_confirmation']} | {item['notes']} |")
    lines += ['', '## Default preservation notes', '']
    lines.append('- `results/`, `outputs/`, `reports/`, and `notebooks/` remain in place by default.')
    lines.append('- Directory-level mapping is used for retrofit planning in this package.')
    path = root / 'docs' / 'RETROFIT_MAPPING.md'
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 'docs/RETROFIT_MAPPING.md'


def write_decision_log(root: Path, plan: dict, mode: str, applied: bool = False, validation: dict | None = None) -> str:
    conflict = plan['conflict']
    lines = ['# RETROFIT_DECISION_LOG', '', '## Mode', '']
    lines.append(f'- mode: {mode}')
    lines += ['', '## Recorded approvals', '']
    lines.append(f"- safe_overlay_approved: {'yes' if mode == 'apply-safe-overlay' else 'not_yet_requested'}")
    lines.append(f"- readme_patch_approved: {'yes' if plan['readme_patch_approved'] else 'no'}")
    lines += ['', '## Defaults frozen for this round', '']
    lines.append('- directory-level mapping')
    lines.append('- preserve `results/`, `outputs/`, `reports/`, and `notebooks/` in place')
    lines.append('- redirect control-file conflicts to `project_evolution`')
    lines += ['', '## Blocking disposition', '']
    if conflict.get('has_conflict'):
        lines.append('- status: blocked_conflict')
        lines.append(f"- notes: {conflict.get('reason')}")
    else:
        lines.append(f"- status: {'cleared' if plan['apply_safe_overlay_eligible'] else 'blocked'}")
        lines.append('- notes: no control-file conflict detected')
    lines += ['', '## Apply eligibility', '']
    lines.append(f"- apply_safe_overlay_eligible: {'yes' if plan['apply_safe_overlay_eligible'] else 'no'}")
    lines.append(f"- next_recommended_skill: {'project_evolution' if conflict.get('has_conflict') else 'project_retrofit'}")
    lines += ['', '## Legacy preservation reminder', '']
    lines.append('- Back up the repository before continuing with retrofit or evolution.')
    lines += ['', '## Apply result', '']
    if applied:
        lines.append(f"- apply_status: {'pass' if validation and validation.get('valid') else 'fail'}")
        lines.append('- handoff: stage_identification')
    else:
        lines.append('- apply_status: not_run')
        lines.append('- handoff: pending')
    path = root / 'docs' / 'RETROFIT_DECISION_LOG.md'
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 'docs/RETROFIT_DECISION_LOG.md'


def main() -> int:
    parser = argparse.ArgumentParser(description='Build retrofit planning documents for a repository.')
    parser.add_argument('--target', default='.')
    parser.add_argument('--approve-readme-patch', action='store_true')
    args = parser.parse_args()
    root = Path(args.target).resolve()
    plan = build_plan(root, approve_readme_patch=args.approve_readme_patch)
    docs = {
        'project_inventory': write_project_inventory(root, plan),
        'retrofit_inventory': write_retrofit_inventory(root, plan),
        'retrofit_mapping': write_retrofit_mapping(root, plan),
        'retrofit_decision_log': write_decision_log(root, plan, mode='plan'),
    }
    payload = {
        'status': 'plan_conflict_redirect_to_evolution' if plan['conflict'].get('has_conflict') else 'plan_complete_overlay_eligible',
        'apply_safe_overlay_eligible': plan['apply_safe_overlay_eligible'],
        'conflict': plan['conflict'],
        'docs': docs,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not plan['conflict'].get('has_conflict') else 2


if __name__ == '__main__':
    raise SystemExit(main())
