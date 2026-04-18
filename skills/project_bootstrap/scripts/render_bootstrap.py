#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT = ROOT / '_shared' / 'assets' / 'generic-project-harness-blueprint'


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def dump_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def customize_root_readme(path: Path, slots: dict) -> None:
    project_name = slots.get('project_identity') or 'Unnamed Project'
    summary = slots.get('project_summary') or 'Project summary pending refinement.'
    primary_goal = slots.get('primary_goal') or 'Primary goal pending clarification.'
    success = slots.get('first_iteration_success_condition') or 'A valid first iteration success condition still needs refinement.'
    main_artifacts = slots.get('expected_main_artifacts') or 'No explicit artifact list supplied yet.'
    content = f"""# {project_name}

{summary}

## Primary goal

{primary_goal}

## First iteration success condition

{success}

## Expected main artifacts

{main_artifacts}

## Harness status

This repository was initialized from the Generic Project Harness blueprint by `project_bootstrap`.
"""
    write_text(path, content)


def create_memory_records(root: Path, slots: dict, now: str) -> tuple[str, str]:
    event_rel = 'memory/active/events/MEM-BOOTSTRAP-0001.md'
    snapshot_rel = 'memory/active/snapshots/SNAPSHOT-primary_iteration-0001.md'
    event = f"""---
id: MEM-BOOTSTRAP-0001
event_type: bootstrap_decision
formal_stage: primary_iteration
active_subflow_stage: stage_identification
pipeline_anchor: PIPELINE:stage.primary_iteration
subflow_anchor: PIPELINE:subflow.stage_identification
status: active
artifact_refs:
  - docs/BOOTSTRAP_GAP_REPORT.md
  - docs/BOOTSTRAP_DECISION_LOG.md
replacement_ref: ""
created_at: {now}
---

# Summary

Bootstrap generated the first-operable harness for `{slots.get('project_identity') or 'this project'}` and promoted the repository into `primary_iteration`.

# Evidence

- file: `docs/BOOTSTRAP_GAP_REPORT.md`
  observation: the normalized brief and gap classification were recorded before generation.
- file: `docs/BOOTSTRAP_DECISION_LOG.md`
  observation: defaults and deferrals were frozen before core harness files were modified.

# Consequence

The next action is to start `stage_identification` inside `primary_iteration` and refine the first narrow target using the generated harness.

# Preserved Lesson

Bootstrap should optimize for a truthful starting harness, not for perfect future completeness.
"""
    snapshot = f"""---
id: SNAPSHOT-primary_iteration-0001
formal_stage: primary_iteration
pipeline_anchor: PIPELINE:stage.primary_iteration
snapshot_scope: bootstrap_handoff
source_event_refs:
  - {event_rel}
created_at: {now}
---

# Current Understanding

The repository now has a valid harness kernel and can continue in `primary_iteration` with `stage_identification` as the active subflow.

# What Improved

- kernel files exist
- initial state exists
- first memory event and snapshot exist
- bootstrap assumptions are recorded

# What Failed

No post-bootstrap execution artifact exists yet. The first working iteration must still validate project-specific behavior.

# What Must Be Preserved

- truthful state anchors
- recorded bootstrap assumptions
- no silent transition into downstream stages

# Next Action Boundary

The next round may inspect the repository, refine project-specific stage semantics if needed, and create the first concrete working target. It must not pretend that primary iteration execution has already happened.
"""
    write_text(root / event_rel, event)
    write_text(root / snapshot_rel, snapshot)
    return event_rel, snapshot_rel


def render(target: Path, slots: dict, gap_report_rel: str = 'docs/BOOTSTRAP_GAP_REPORT.md', decision_log_rel: str = 'docs/BOOTSTRAP_DECISION_LOG.md') -> dict:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(BLUEPRINT, target)
    now = utc_now()
    project_name = (slots.get('project_identity') or target.name or 'Generic_Project').strip() or 'Generic_Project'
    customize_root_readme(target / 'README.md', slots)
    event_rel, snapshot_rel = create_memory_records(target, slots, now)
    state = load_json(target / 'state' / 'CURRENT_STATE.json')
    state.update({
        'project_name': project_name,
        'bootstrap_mode': False,
        'formal_stage': 'primary_iteration',
        'active_subflow_stage': 'stage_identification',
        'current_pipeline_anchor': 'PIPELINE:stage.primary_iteration',
        'current_subflow_anchor': 'PIPELINE:subflow.stage_identification',
        'latest_snapshot_ref': snapshot_rel,
        'active_memory_refs': [event_rel],
        'required_artifact_refs': [gap_report_rel, decision_log_rel],
        'last_verification': {
            'status': 'not_yet_run',
            'source': 'render_bootstrap.py staged render only',
            'checked_at': now,
        },
        'blocked': False,
        'blocking_reason': '',
        'next_action': 'Read AGENTS.md, resolve the current anchors in PIPELINE.md, inspect the repository, and complete stage_identification for the first real working target.',
        'updated_at': now,
    })
    dump_json(target / 'state' / 'CURRENT_STATE.json', state)
    mem_index = load_json(target / 'memory' / 'index.json')
    mem_index.update({'project_name': project_name, 'active_snapshot': snapshot_rel, 'recent_events': [event_rel], 'updated_at': now})
    dump_json(target / 'memory' / 'index.json', mem_index)
    garbage_index = load_json(target / 'garbage' / 'index.json')
    garbage_index.update({'project_name': project_name})
    dump_json(target / 'garbage' / 'index.json', garbage_index)
    (target / 'docs').mkdir(parents=True, exist_ok=True)
    return {'project_name': project_name, 'event_ref': event_rel, 'snapshot_ref': snapshot_rel, 'checked_at': now}


def main() -> int:
    parser = argparse.ArgumentParser(description='Render a Generic Project Harness into a staging directory.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--slots-json', required=True)
    args = parser.parse_args()
    target = Path(args.target).resolve()
    slots = json.loads(Path(args.slots_json).read_text(encoding='utf-8'))
    payload = render(target, slots)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
