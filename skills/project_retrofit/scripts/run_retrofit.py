#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from apply_safe_overlay import apply_safe_overlay
from build_retrofit_plan import build_plan, write_decision_log, write_project_inventory, write_retrofit_inventory, write_retrofit_mapping
from validate_retrofit import validate_retrofit
from write_conflict_report import write_conflict_report

REQUIRED_PLAN_DOCS = [
    'docs/PROJECT_INVENTORY.md',
    'docs/RETROFIT_INVENTORY.md',
    'docs/RETROFIT_MAPPING.md',
    'docs/RETROFIT_DECISION_LOG.md',
]


def ensure_plan_exists(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_PLAN_DOCS if not (root / rel).exists()]


def update_state_after_validation(root: Path, validation: dict) -> None:
    state_path = root / 'state' / 'CURRENT_STATE.json'
    if not state_path.exists():
        return
    state = json.loads(state_path.read_text(encoding='utf-8'))
    state['last_verification'] = {
        'status': 'pass' if validation.get('valid') else 'fail',
        'source': 'skills/project_retrofit/scripts/validate_retrofit.py',
        'checked_at': validation['shared_validation']['state_summary']['last_verification'].get('checked_at') if validation.get('shared_validation', {}).get('state_summary', {}).get('last_verification') else '',
    }
    state['blocked'] = not validation.get('valid')
    state['blocking_reason'] = '; '.join(validation.get('errors', [])) if validation.get('errors') else ''
    state['next_action'] = 'Start a new Codex run in this repository, then continue with stage_identification.'
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def write_plan_docs(root: Path, plan: dict, mode: str, applied: bool = False, validation: dict | None = None) -> dict:
    docs = {
        'project_inventory': write_project_inventory(root, plan),
        'retrofit_inventory': write_retrofit_inventory(root, plan),
        'retrofit_mapping': write_retrofit_mapping(root, plan),
        'retrofit_decision_log': write_decision_log(root, plan, mode=mode, applied=applied, validation=validation),
    }
    if plan['conflict'].get('has_conflict'):
        docs['retrofit_conflict_report'] = write_conflict_report(root, plan['conflict'], plan['classification'])
    return docs


def main() -> int:
    parser = argparse.ArgumentParser(description='Plan or apply a safe retrofit overlay for an existing repository.')
    parser.add_argument('--target', default='.')
    parser.add_argument('--mode', choices=['plan', 'apply-safe-overlay'], default='plan')
    parser.add_argument('--approve-readme-patch', action='store_true')
    args = parser.parse_args()

    target = Path(args.target).resolve()

    if args.mode == 'apply-safe-overlay':
        missing_plan_docs = ensure_plan_exists(target)
        if missing_plan_docs:
            print(json.dumps({
                'status': 'blocked',
                'reason': 'apply-safe-overlay requires an existing completed plan in the target repository',
                'missing_plan_docs': missing_plan_docs,
            }, indent=2, ensure_ascii=False))
            return 2

    plan = build_plan(target, approve_readme_patch=args.approve_readme_patch)
    docs = write_plan_docs(target, plan, mode=args.mode, applied=False, validation=None)

    if args.mode == 'plan':
        status = 'plan_conflict_redirect_to_evolution' if plan['conflict'].get('has_conflict') else 'plan_complete_overlay_eligible'
        next_action = 'Back up the repository and continue with project_evolution.' if plan['conflict'].get('has_conflict') else 'Safe overlay may proceed after explicit user approval.'
        print(json.dumps({
            'status': status,
            'apply_safe_overlay_eligible': plan['apply_safe_overlay_eligible'],
            'conflict': plan['conflict'],
            'docs': docs,
            'next_action': next_action,
        }, indent=2, ensure_ascii=False))
        return 0 if not plan['conflict'].get('has_conflict') else 2

    if plan['conflict'].get('has_conflict'):
        print(json.dumps({
            'status': 'blocked_conflict',
            'reason': plan['conflict'].get('reason'),
            'recommended_skill': 'project_evolution',
            'docs': docs,
        }, indent=2, ensure_ascii=False))
        return 2

    overlay = apply_safe_overlay(target, plan, approve_readme_patch=args.approve_readme_patch)
    validation = validate_retrofit(target)
    update_state_after_validation(target, validation)
    validation = validate_retrofit(target)
    docs = write_plan_docs(target, plan, mode=args.mode, applied=True, validation=validation)
    payload = {
        'status': 'applied' if validation.get('valid') else 'failed_validation',
        'docs': docs,
        'created': overlay.get('created', []),
        'readme_result': overlay.get('readme_result', {}),
        'validation': validation,
        'next_action': 'Start a new Codex run in the target repository so the new AGENTS.md is loaded, then continue with stage_identification.',
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if validation.get('valid') else 1

if __name__ == '__main__':
    raise SystemExit(main())
