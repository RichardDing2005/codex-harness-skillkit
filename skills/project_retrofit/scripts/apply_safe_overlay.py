#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from patch_readme_structure import patch_readme_structure, build_section

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_RENDERER = ROOT / 'project_bootstrap' / 'scripts' / 'render_bootstrap.py'

CONTROL_FILES = [
    'AGENTS.md',
    'PIPELINE.md',
    'CONTRIBUTIONS.md',
    'state/CURRENT_STATE.json',
    'config/stage_defaults.json',
    'memory/index.json',
    'garbage/index.json',
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_renderer():
    spec = importlib.util.spec_from_file_location('render_bootstrap', BOOTSTRAP_RENDERER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def retrofit_slots(plan: dict) -> dict:
    inventory = plan['inventory']
    project_name = inventory.get('project_title') or Path(inventory.get('repo_root', '.')).name
    summary = 'This repository entered the Generic Project Harness through project_retrofit while keeping existing legacy working directories in place.'
    return {
        'project_identity': project_name,
        'project_summary': summary,
        'primary_goal': 'Add a minimal Generic Project Harness control layer around the existing repository without moving or deleting legacy material.',
        'first_iteration_success_condition': 'The harness control files validate successfully and the next action points to stage_identification.',
        'expected_main_artifacts': 'validated harness control files plus retrofit planning documents',
    }


def write_retrofit_memory(root: Path, plan: dict) -> tuple[str, str]:
    now = utc_now()
    event_rel = 'memory/active/events/MEM-RETROFIT-0001.md'
    snapshot_rel = 'memory/active/snapshots/SNAPSHOT-primary_iteration-retrofit-0001.md'
    event = f'''---
id: MEM-RETROFIT-0001
event_type: retrofit_safe_overlay
formal_stage: primary_iteration
active_subflow_stage: stage_identification
pipeline_anchor: PIPELINE:stage.primary_iteration
subflow_anchor: PIPELINE:subflow.stage_identification
status: active
artifact_refs:
  - docs/PROJECT_INVENTORY.md
  - docs/RETROFIT_INVENTORY.md
  - docs/RETROFIT_MAPPING.md
  - docs/RETROFIT_DECISION_LOG.md
replacement_ref: ""
created_at: {now}
---

# Summary

`project_retrofit` applied a safe overlay and moved the repository into the Generic Project Harness without relocating legacy working directories.

# Evidence

- file: `docs/RETROFIT_MAPPING.md`
  observation: directory-level preservation and mapping rules were frozen before the overlay.
- file: `docs/RETROFIT_DECISION_LOG.md`
  observation: overlay eligibility and README patch approval were recorded before apply.

# Consequence

The repository now has harness control files and the next action is `stage_identification`.
'''
    snapshot = f'''---
id: SNAPSHOT-primary_iteration-retrofit-0001
formal_stage: primary_iteration
pipeline_anchor: PIPELINE:stage.primary_iteration
snapshot_scope: retrofit_safe_overlay
source_event_refs:
  - {event_rel}
created_at: {now}
---

# Current Understanding

The repository has entered the Generic Project Harness through a safe overlay while preserving legacy working zones in place.

# What Improved

- harness control files now exist
- retrofit planning documents now anchor the migration truth
- next action is fixed to `stage_identification`

# What Must Be Preserved

- legacy working directories remain in place
- control-file conflicts should be reconciled through `project_evolution`, not by forcing another retrofit overlay
'''
    event_path = root / event_rel
    snapshot_path = root / snapshot_rel
    event_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    event_path.write_text(event, encoding='utf-8')
    snapshot_path.write_text(snapshot, encoding='utf-8')
    return event_rel, snapshot_rel


def customize_state_and_indexes(stage: Path, plan: dict) -> None:
    event_rel, snapshot_rel = write_retrofit_memory(stage, plan)
    now = utc_now()
    state_path = stage / 'state' / 'CURRENT_STATE.json'
    state = json.loads(state_path.read_text(encoding='utf-8'))
    state.update({
        'bootstrap_mode': False,
        'formal_stage': 'primary_iteration',
        'active_subflow_stage': 'stage_identification',
        'current_pipeline_anchor': 'PIPELINE:stage.primary_iteration',
        'current_subflow_anchor': 'PIPELINE:subflow.stage_identification',
        'latest_snapshot_ref': snapshot_rel,
        'active_memory_refs': [event_rel],
        'required_artifact_refs': [
            'docs/PROJECT_INVENTORY.md',
            'docs/RETROFIT_INVENTORY.md',
            'docs/RETROFIT_MAPPING.md',
            'docs/RETROFIT_DECISION_LOG.md',
        ],
        'last_action': 'retrofit_safe_overlay',
        'last_verification': {
            'status': 'not_yet_run',
            'source': 'retrofit stage render only',
            'checked_at': now,
        },
        'blocked': False,
        'blocking_reason': '',
        'next_action': 'Read AGENTS.md, resolve the current anchors in PIPELINE.md, inspect preserved legacy directories, and complete stage_identification.',
        'updated_at': now,
    })
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    memory_index_path = stage / 'memory' / 'index.json'
    memory_index = json.loads(memory_index_path.read_text(encoding='utf-8'))
    memory_index.update({
        'active_snapshot': snapshot_rel,
        'recent_events': [event_rel],
        'updated_at': now,
    })
    memory_index_path.write_text(json.dumps(memory_index, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def copy_control_files(stage: Path, target: Path) -> list[str]:
    created: list[str] = []
    for rel in CONTROL_FILES:
        src = stage / rel
        dst = target / rel
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        created.append(rel)
    for rel in [
        'memory/active/events/MEM-RETROFIT-0001.md',
        'memory/active/snapshots/SNAPSHOT-primary_iteration-retrofit-0001.md',
    ]:
        src = stage / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        created.append(rel)
    return created


def write_harness_entry(root: Path, plan: dict) -> str:
    path = root / 'docs' / 'HARNESS_ENTRY.md'
    content = build_section(2, 'Project Structure', plan['mapping'], plan['inventory'].get('project_title') or root.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    return 'docs/HARNESS_ENTRY.md'


def apply_safe_overlay(target: Path, plan: dict, approve_readme_patch: bool = False) -> dict:
    renderer = load_renderer()
    slots = retrofit_slots(plan)
    with tempfile.TemporaryDirectory(prefix='retrofit_stage_') as tmp:
        stage = Path(tmp) / 'repo'
        renderer.render(stage, slots, gap_report_rel='docs/RETROFIT_INVENTORY.md', decision_log_rel='docs/RETROFIT_DECISION_LOG.md')
        customize_state_and_indexes(stage, plan)
        created = copy_control_files(stage, target)

    readme_result = {'patched': False, 'fallback_created': False, 'matched_heading': ''}
    readme = target / 'README.md'
    if readme.exists() and approve_readme_patch:
        readme_result = patch_readme_structure(readme, plan['mapping'], plan['inventory'].get('project_title') or target.name)
        if not readme_result.get('patched'):
            write_harness_entry(target, plan)
            readme_result['fallback_created'] = True
    elif not readme.exists():
        harness_entry = write_harness_entry(target, plan)
        created.append(harness_entry)
        # create a minimal README because the shared validator requires it
        readme.write_text(
            f"# {plan['inventory'].get('project_title') or target.name}\n\nThis repository has entered the Generic Project Harness through project_retrofit.\n\nSee `{harness_entry}` for the current harness structure summary.\n",
            encoding='utf-8',
        )
        created.append('README.md')
    return {'created': created, 'readme_result': readme_result}


def main() -> int:
    parser = argparse.ArgumentParser(description='Apply a safe retrofit overlay to a repository.')
    parser.add_argument('--target', default='.')
    parser.add_argument('--plan-json', required=True)
    parser.add_argument('--approve-readme-patch', action='store_true')
    args = parser.parse_args()
    plan = json.loads(Path(args.plan_json).read_text(encoding='utf-8'))
    payload = apply_safe_overlay(Path(args.target).resolve(), plan, approve_readme_patch=args.approve_readme_patch)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
