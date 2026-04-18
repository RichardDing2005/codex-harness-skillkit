#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARED_VALIDATOR = ROOT / '_shared' / 'scripts' / 'validate_harness.py'
RENDERER = Path(__file__).with_name('render_bootstrap.py')
SLOT_ORDER = [
    'project_identity', 'project_summary', 'domain_and_problem_type', 'primary_goal', 'first_iteration_success_condition',
    'non_goals', 'known_inputs', 'known_constraints', 'expected_main_artifacts', 'expected_reports_or_logs',
    'execution_style', 'candidate_direction_of_work', 'validation_logic', 'blocking_risks_or_unknowns', 'bootstrap_preference'
]
HEADING_MAP = {
    'project name': 'project_identity',
    'short project summary': 'project_summary',
    'primary goal': 'primary_goal',
    'first iteration success condition': 'first_iteration_success_condition',
    'in scope for the first iteration': 'domain_and_problem_type',
    'out of scope / non-goals': 'non_goals',
    'known inputs': 'known_inputs',
    'known constraints': 'known_constraints',
    'external tools, datasets, or systems that must be represented': 'known_constraints',
    'expected main artifacts': 'expected_main_artifacts',
    'expected reports or logs': 'expected_reports_or_logs',
    'execution style or workflow preference': 'execution_style',
    'candidate direction of work': 'candidate_direction_of_work',
    'validation logic for the first iteration': 'validation_logic',
    'blocking risks or unknowns': 'blocking_risks_or_unknowns',
    'bootstrap preference (strict questions / allow placeholders / unsure)': 'bootstrap_preference',
}
PROTECTED_CORE = ['AGENTS.md','PIPELINE.md','CONTRIBUTIONS.md','README.md','state/CURRENT_STATE.json','memory/index.json','garbage/index.json','config/stage_defaults.json']


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def parse_brief(brief_text: str) -> dict:
    slots = {key: '' for key in SLOT_ORDER}
    for raw_line in brief_text.splitlines():
        line = raw_line.strip()
        if not line.startswith('- ') or ':' not in line:
            continue
        key_part, value_part = line[2:].split(':', 1)
        key = HEADING_MAP.get(key_part.strip().lower())
        if not key:
            continue
        value = value_part.strip()
        if value.upper() == 'UNKNOWN':
            value = ''
        if key == 'known_constraints' and slots[key] and value:
            slots[key] = slots[key] + '; ' + value
        elif value:
            slots[key] = value
    return slots


def normalize_slots(slots: dict, target: Path) -> dict:
    result = dict(slots)
    if not result.get('project_identity'):
        result['project_identity'] = target.name or 'Generic_Project'
    if not result.get('project_summary'):
        result['project_summary'] = 'Bootstrap brief did not include a short summary; generated from available project cues.'
    if not result.get('bootstrap_preference'):
        result['bootstrap_preference'] = 'strict_questions'
    return result


def classify_slots(slots: dict) -> dict:
    statuses = {key: 'resolved' for key in SLOT_ORDER}
    blocking_keys = {'primary_goal', 'first_iteration_success_condition'}
    for key in SLOT_ORDER:
        value = (slots.get(key) or '').strip()
        if value:
            statuses[key] = 'resolved'
            continue
        if key in blocking_keys:
            statuses[key] = 'blocking'
        elif key in {'expected_main_artifacts', 'validation_logic', 'candidate_direction_of_work'}:
            statuses[key] = 'defaultable'
        else:
            statuses[key] = 'deferrable'
    if not slots.get('expected_main_artifacts') and not slots.get('first_iteration_success_condition'):
        statuses['expected_main_artifacts'] = 'blocking'
    if not slots.get('validation_logic') and not slots.get('first_iteration_success_condition'):
        statuses['validation_logic'] = 'blocking'
    return statuses


def blocking_questions(statuses: dict) -> list[str]:
    questions = []
    if statuses['primary_goal'] == 'blocking':
        questions.append('What is the primary goal of this project in one sentence?')
    if statuses['first_iteration_success_condition'] == 'blocking':
        questions.append('What concrete result would count as success for the first iteration?')
    if statuses['expected_main_artifacts'] == 'blocking':
        questions.append('What main artifact should the first iteration produce: code, data pipeline, report, or another concrete output?')
    if statuses['validation_logic'] == 'blocking':
        questions.append('How should the first iteration be validated: artifact existence, execution success, numeric quality check, human review, or something else?')
    return questions[:4]


def write_gap_report(target: Path, slots: dict, statuses: dict, questions: list[str]) -> None:
    lines = ['# BOOTSTRAP_GAP_REPORT', '', '## Normalized slots', '']
    for key in SLOT_ORDER:
        lines.append(f'- {key}: {slots.get(key) or ""}')
    lines += ['', '## Slot status', '']
    for key in SLOT_ORDER:
        lines.append(f'- {key}: {statuses[key]}')
    lines += ['', '## Blocking questions', '']
    if questions:
        for q in questions:
            lines.append(f'- {q}')
    else:
        lines.append('- none')
    lines += ['', '## Default plan', '', '- Default project summary, direction of work, validation details, and later refinements only when safe.', '', '## Deferred plan', '', '- Defer broader process refinements and long-range optimization to `project_evolution`.']
    path = target / 'docs' / 'BOOTSTRAP_GAP_REPORT.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_decision_log(target: Path, statuses: dict, allow_placeholders: bool, phase: str, validation: dict | None = None) -> None:
    defaults = [key for key, status in statuses.items() if status == 'defaultable']
    deferred = [key for key, status in statuses.items() if status == 'deferrable']
    blocked = [key for key, status in statuses.items() if status == 'blocking']
    status_label = 'blocked' if blocked and not allow_placeholders else ('placeholders-approved' if blocked else 'cleared')
    lines = ['# BOOTSTRAP_DECISION_LOG', '', '## Inputs used', '', '- brief file: BOOTSTRAP_BRIEF.md', '- user message summary: bootstrap via structured brief', '', '## Frozen defaults', '']
    if defaults:
        lines.extend([f'- {item}: safe bootstrap default' for item in defaults])
    else:
        lines.append('- none')
    lines += ['', '## Deferred items', '']
    if deferred:
        lines.extend([f'- {item}: reserve for project_evolution' for item in deferred])
    else:
        lines.append('- none')
    lines += ['', '## Blocking disposition', '', f'- status: {status_label}', f'- notes: blocking_keys={blocked if blocked else []}', '', '## Planned writes before apply', '']
    planned = ['README.md','AGENTS.md','PIPELINE.md','CONTRIBUTIONS.md','state/CURRENT_STATE.json','config/stage_defaults.json','memory/index.json','memory/active/events/MEM-BOOTSTRAP-0001.md','memory/active/snapshots/SNAPSHOT-primary_iteration-0001.md','garbage/index.json']
    lines.extend([f'- {p}: required bootstrap output' for p in planned])
    lines += ['', '## Validation result after apply', '']
    if validation:
        lines.append(f"- status: {'pass' if validation.get('valid') else 'fail'}")
        lines.append('- source: skills/_shared/scripts/validate_harness.py')
        lines.append(f'- checked_at: {utc_now()}')
    else:
        lines += ['- status: pending', '- source: not yet run', f'- checked_at: {utc_now()}']
    lines += ['', '## Phase marker', '', f'- phase: {phase}']
    path = target / 'docs' / 'BOOTSTRAP_DECISION_LOG.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def ensure_safe_target(target: Path, force: bool) -> None:
    existing = [rel for rel in PROTECTED_CORE if (target / rel).exists()]
    if existing and not force:
        raise RuntimeError('protected harness files already exist; use project_evolution or pass --force with explicit approval: ' + ', '.join(existing))


def sync_tree(src: Path, dst: Path) -> None:
    for path in src.rglob('*'):
        rel = path.relative_to(src)
        target = dst / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def apply_validation_to_state(target: Path, validation: dict) -> None:
    state_path = target / 'state' / 'CURRENT_STATE.json'
    state = json.loads(state_path.read_text(encoding='utf-8'))
    state['last_verification'] = {'status': 'pass' if validation.get('valid') else 'fail', 'source': 'skills/_shared/scripts/validate_harness.py', 'checked_at': utc_now()}
    state['blocked'] = not validation.get('valid')
    state['blocking_reason'] = '; '.join(validation.get('errors', [])) if validation.get('errors') else ''
    state['updated_at'] = utc_now()
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Run the full bootstrap contract for a target repository.')
    parser.add_argument('--target', default='.')
    parser.add_argument('--brief', default='BOOTSTRAP_BRIEF.md')
    parser.add_argument('--allow-placeholders', action='store_true')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    target = Path(args.target).resolve()
    brief_path = (target / args.brief).resolve() if not os.path.isabs(args.brief) else Path(args.brief).resolve()
    target.mkdir(parents=True, exist_ok=True)
    ensure_safe_target(target, args.force)
    if not brief_path.exists():
        target.joinpath('BOOTSTRAP_BRIEF.md').write_text((ROOT / 'project_bootstrap' / 'assets' / 'templates' / 'BOOTSTRAP_BRIEF.template.md').read_text(encoding='utf-8'), encoding='utf-8')
        print(json.dumps({'status': 'blocked', 'reason': 'BOOTSTRAP_BRIEF.md missing; template created at target root.', 'created': ['BOOTSTRAP_BRIEF.md']}, indent=2, ensure_ascii=False))
        return 2
    raw_slots = parse_brief(brief_path.read_text(encoding='utf-8'))
    slots = normalize_slots(raw_slots, target)
    statuses = classify_slots(slots)
    questions = blocking_questions(statuses)
    write_gap_report(target, slots, statuses, questions)
    write_decision_log(target, statuses, args.allow_placeholders, phase='pre_apply', validation=None)
    blocked = [key for key, status in statuses.items() if status == 'blocking']
    if blocked and not args.allow_placeholders:
        print(json.dumps({'status': 'blocked', 'blocking_keys': blocked, 'questions': questions, 'gap_report': 'docs/BOOTSTRAP_GAP_REPORT.md', 'decision_log': 'docs/BOOTSTRAP_DECISION_LOG.md'}, indent=2, ensure_ascii=False))
        return 2
    renderer = load_module(RENDERER, 'render_bootstrap')
    validator = load_module(SHARED_VALIDATOR, 'validate_harness')
    with tempfile.TemporaryDirectory(prefix='bootstrap_stage_') as tmp:
        stage = Path(tmp) / 'repo'
        renderer.render(stage, slots)
        for rel in ['docs/BOOTSTRAP_GAP_REPORT.md', 'docs/BOOTSTRAP_DECISION_LOG.md']:
            src = target / rel
            dst = stage / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        validation = validator.validate_repo(stage, require_bootstrap_docs=True)
        if not validation.get('valid'):
            write_decision_log(target, statuses, args.allow_placeholders, phase='validation_failed', validation=validation)
            print(json.dumps({'status': 'failed_validation', 'validation': validation}, indent=2, ensure_ascii=False))
            return 1
        sync_tree(stage, target)
    apply_validation_to_state(target, validation)
    final_validation = validator.validate_repo(target, require_bootstrap_docs=True)
    write_decision_log(target, statuses, args.allow_placeholders, phase='applied', validation=final_validation)
    print(json.dumps({'status': 'generated', 'target': str(target), 'validation': final_validation, 'next_action': 'Start a new Codex run in the target repository so the generated AGENTS.md is loaded, then continue with stage_identification.'}, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
