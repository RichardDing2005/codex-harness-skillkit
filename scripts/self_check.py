#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    '.codex-plugin/plugin.json', '.agents/plugins/marketplace.json', 'README.md',
    'skills/project_bootstrap/SKILL.md', 'skills/project_bootstrap/agents/openai.yaml', 'skills/project_bootstrap/scripts/run_bootstrap.py', 'skills/project_bootstrap/scripts/render_bootstrap.py',
    'skills/project_retrofit/SKILL.md', 'skills/project_retrofit/agents/openai.yaml', 'skills/project_retrofit/scripts/run_retrofit.py',
    'skills/project_evolution/SKILL.md', 'skills/project_evolution/agents/openai.yaml', 'skills/project_evolution/scripts/run_evolution.py',
    'skills/_shared/scripts/validate_harness.py'
]


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def main() -> int:
    errors = []
    warnings = []
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append(f'missing required package file: {rel}')

    with tempfile.TemporaryDirectory(prefix='plugin_self_check_') as tmp:
        target = Path(tmp) / 'bootstrap_target'
        target.mkdir()
        shutil.copy2(ROOT / 'examples' / 'bootstrap_minimal' / 'BOOTSTRAP_BRIEF.md', target / 'BOOTSTRAP_BRIEF.md')
        bootstrap = run(['python3', str(ROOT / 'skills' / 'project_bootstrap' / 'scripts' / 'run_bootstrap.py'), '--target', str(target), '--brief', 'BOOTSTRAP_BRIEF.md'], cwd=ROOT)
        if bootstrap.returncode != 0:
            errors.append('bootstrap smoke test failed')
        else:
            try:
                payload = json.loads(bootstrap.stdout)
                if payload.get('status') != 'generated':
                    errors.append('bootstrap smoke test did not generate harness')
            except Exception:
                errors.append('bootstrap smoke test returned non-JSON output')
            validation = run(['python3', str(ROOT / 'skills' / '_shared' / 'scripts' / 'validate_harness.py'), str(target), '--require-bootstrap-docs'], cwd=ROOT)
            if validation.returncode != 0:
                errors.append('shared validator failed on generated harness')
            else:
                val = json.loads(validation.stdout)
                if val.get('state_summary', {}).get('last_verification', {}).get('status') != 'pass':
                    errors.append('generated state did not record a passing verification result')
        legacy_src = ROOT / 'examples' / 'retrofit_legacy'
        legacy = Path(tmp) / 'retrofit_legacy'
        shutil.copytree(legacy_src, legacy)
        retrofit = run(['python3', str(ROOT / 'skills' / 'project_retrofit' / 'scripts' / 'run_retrofit.py'), '--target', str(legacy)], cwd=ROOT)
        if retrofit.returncode != 0:
            errors.append('retrofit planning script failed on legacy example')
        evo = run(['python3', str(ROOT / 'skills' / 'project_evolution' / 'scripts' / 'run_evolution.py'), '--target', str(target), '--summary', 'smoke evolution request'], cwd=ROOT)
        if evo.returncode != 0:
            errors.append('evolution planning script failed on generated harness')

    payload = {'package_root': str(ROOT), 'valid': not errors, 'errors': errors, 'warnings': warnings}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
