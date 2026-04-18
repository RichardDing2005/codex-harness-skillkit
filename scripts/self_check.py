#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    '.codex-plugin/plugin.json',
    '.agents/plugins/marketplace.json',
    'README.md',
    'docs/USE.md',
    'skills/project_bootstrap/SKILL.md',
    'skills/project_bootstrap/agents/openai.yaml',
    'skills/project_bootstrap/scripts/run_bootstrap.py',
    'skills/project_bootstrap/scripts/render_bootstrap.py',
    'skills/project_retrofit/SKILL.md',
    'skills/project_retrofit/README.md',
    'skills/project_retrofit/agents/openai.yaml',
    'skills/project_retrofit/scripts/run_retrofit.py',
    'skills/project_retrofit/scripts/build_retrofit_plan.py',
    'skills/project_retrofit/scripts/apply_safe_overlay.py',
    'skills/project_retrofit/scripts/validate_retrofit.py',
    'skills/project_retrofit/assets/templates/RETROFIT_MAPPING.template.md',
    'skills/project_retrofit/assets/templates/RETROFIT_CONFLICT_REPORT.template.md',
    'skills/project_evolution/SKILL.md',
    'skills/project_evolution/README.md',
    'skills/project_evolution/agents/openai.yaml',
    'skills/project_evolution/scripts/run_evolution.py',
    'skills/_shared/scripts/validate_harness.py',
]


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def parse_json_output(cp: subprocess.CompletedProcess) -> tuple[dict | None, str | None]:
    try:
        return json.loads(cp.stdout), None
    except Exception as exc:
        return None, str(exc)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, object] = {}

    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append(f'missing required package file: {rel}')

    with tempfile.TemporaryDirectory(prefix='plugin_self_check_') as tmp:
        tmp_root = Path(tmp)

        # Bootstrap smoke test
        bootstrap_target = tmp_root / 'bootstrap_target'
        bootstrap_target.mkdir()
        shutil.copy2(ROOT / 'examples' / 'bootstrap_minimal' / 'BOOTSTRAP_BRIEF.md', bootstrap_target / 'BOOTSTRAP_BRIEF.md')
        bootstrap = run(['python3', str(ROOT / 'skills' / 'project_bootstrap' / 'scripts' / 'run_bootstrap.py'), '--target', str(bootstrap_target), '--brief', 'BOOTSTRAP_BRIEF.md'], cwd=ROOT)
        payload, parse_error = parse_json_output(bootstrap)
        checks['bootstrap_stdout'] = payload if payload is not None else bootstrap.stdout
        if bootstrap.returncode != 0 or parse_error:
            errors.append('bootstrap smoke test failed')
        elif payload.get('status') != 'generated':
            errors.append('bootstrap smoke test did not generate a harness')
        else:
            validation = run(['python3', str(ROOT / 'skills' / '_shared' / 'scripts' / 'validate_harness.py'), str(bootstrap_target), '--require-bootstrap-docs'], cwd=ROOT)
            val_payload, parse_error = parse_json_output(validation)
            checks['bootstrap_validation'] = val_payload if val_payload is not None else validation.stdout
            if validation.returncode != 0 or parse_error:
                errors.append('shared validator failed on bootstrap target')
            elif val_payload.get('state_summary', {}).get('last_verification', {}).get('status') != 'pass':
                errors.append('bootstrap target state did not record pass verification')

        # Retrofit apply should fail before planning
        no_plan_src = ROOT / 'examples' / 'retrofit_legacy'
        no_plan = tmp_root / 'retrofit_without_plan'
        shutil.copytree(no_plan_src, no_plan)
        apply_without_plan = run(['python3', str(ROOT / 'skills' / 'project_retrofit' / 'scripts' / 'run_retrofit.py'), '--target', str(no_plan), '--mode', 'apply-safe-overlay'], cwd=ROOT)
        no_plan_payload, parse_error = parse_json_output(apply_without_plan)
        checks['retrofit_apply_without_plan'] = no_plan_payload if no_plan_payload is not None else apply_without_plan.stdout
        if apply_without_plan.returncode != 2 or parse_error:
            errors.append('retrofit apply-safe-overlay did not block when no plan documents existed')
        elif no_plan_payload.get('status') != 'blocked':
            errors.append('retrofit apply-safe-overlay without planning did not return blocked status')

        # Retrofit planning and safe overlay
        legacy_src = ROOT / 'examples' / 'retrofit_legacy'
        legacy = tmp_root / 'retrofit_legacy'
        shutil.copytree(legacy_src, legacy)
        before_analysis = (legacy / 'analysis.py').read_text(encoding='utf-8')
        before_notes = (legacy / 'notes.txt').read_text(encoding='utf-8')
        plan = run(['python3', str(ROOT / 'skills' / 'project_retrofit' / 'scripts' / 'run_retrofit.py'), '--target', str(legacy), '--mode', 'plan'], cwd=ROOT)
        plan_payload, parse_error = parse_json_output(plan)
        checks['retrofit_plan'] = plan_payload if plan_payload is not None else plan.stdout
        if plan.returncode != 0 and plan.returncode != 2:
            errors.append('retrofit planning run crashed')
        elif parse_error:
            errors.append('retrofit planning run returned non-JSON output')
        elif plan_payload.get('status') != 'plan_complete_overlay_eligible':
            errors.append('retrofit planning did not finish with apply-safe-overlay allowed on the legacy example')

        apply = run(['python3', str(ROOT / 'skills' / 'project_retrofit' / 'scripts' / 'run_retrofit.py'), '--target', str(legacy), '--mode', 'apply-safe-overlay', '--approve-readme-patch'], cwd=ROOT)
        apply_payload, parse_error = parse_json_output(apply)
        checks['retrofit_apply'] = apply_payload if apply_payload is not None else apply.stdout
        if apply.returncode != 0 or parse_error:
            errors.append('retrofit safe overlay failed')
        elif apply_payload.get('status') != 'applied':
            errors.append('retrofit safe overlay did not report applied status')
        else:
            retrofit_validation = apply_payload.get('validation', {})
            if not retrofit_validation.get('valid'):
                errors.append('retrofit validation did not pass after safe overlay')
            readme_text = (legacy / 'README.md').read_text(encoding='utf-8')
            if 'Harness Control Files' not in readme_text:
                errors.append('retrofit README patch did not inject the standard harness structure section')
            if (legacy / 'analysis.py').read_text(encoding='utf-8') != before_analysis:
                errors.append('retrofit safe overlay modified legacy analysis.py')
            if (legacy / 'notes.txt').read_text(encoding='utf-8') != before_notes:
                errors.append('retrofit safe overlay modified legacy notes.txt')
            state = json.loads((legacy / 'state' / 'CURRENT_STATE.json').read_text(encoding='utf-8'))
            if state.get('current_subflow_anchor') != 'PIPELINE:subflow.stage_identification':
                errors.append('retrofit safe overlay did not hand off to stage_identification')

        # Retrofit conflict redirect
        conflict_target = tmp_root / 'retrofit_conflict'
        shutil.copytree(legacy_src, conflict_target)
        (conflict_target / 'AGENTS.md').write_text('# existing partial control file\n', encoding='utf-8')
        conflict = run(['python3', str(ROOT / 'skills' / 'project_retrofit' / 'scripts' / 'run_retrofit.py'), '--target', str(conflict_target), '--mode', 'plan'], cwd=ROOT)
        conflict_payload, parse_error = parse_json_output(conflict)
        checks['retrofit_conflict'] = conflict_payload if conflict_payload is not None else conflict.stdout
        if conflict.returncode != 2 or parse_error:
            errors.append('retrofit conflict path did not stop with the expected redirect status')
        elif conflict_payload.get('status') != 'plan_conflict_redirect_to_evolution':
            errors.append('retrofit conflict path did not redirect to project_evolution')
        elif not (conflict_target / 'docs' / 'RETROFIT_CONFLICT_REPORT.md').exists():
            errors.append('retrofit conflict path did not write RETROFIT_CONFLICT_REPORT.md')

        # Evolution smoke test on a valid harnessed repository
        evo = run(['python3', str(ROOT / 'skills' / 'project_evolution' / 'scripts' / 'run_evolution.py'), '--target', str(bootstrap_target), '--summary', 'smoke evolution request'], cwd=ROOT)
        evo_payload, parse_error = parse_json_output(evo)
        checks['evolution'] = evo_payload if evo_payload is not None else evo.stdout
        if evo.returncode != 0 or parse_error:
            errors.append('evolution planning script failed on generated harness')
        elif evo_payload.get('status') != 'planned':
            errors.append('evolution planning script did not return planned status')

    payload = {'package_root': str(ROOT), 'valid': not errors, 'errors': errors, 'warnings': warnings, 'checks': checks}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
