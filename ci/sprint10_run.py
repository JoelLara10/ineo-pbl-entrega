"""Portable quality campaign, reports retained on any command failure."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--phase', choices=['metadata', 'quality', 'negative', 'oat', 'candidate'], required=True)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONUTF8='1')
    npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')

    def run(name, command, cwd=ROOT):
        result = subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, encoding='utf8', errors='replace')
        (out / (name + '.log')).write_text(result.stdout, encoding='utf8')
        print(f'{name}: exit={result.returncode}', flush=True)
        if result.returncode:
            print(result.stdout[-5000:], flush=True)
            raise SystemExit(result.returncode)

    if args.phase == 'metadata':
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        metadata = dict(sha=sha, branch=subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
                        date=datetime.now(timezone.utc).isoformat(),
                        stories=['PBL-37', 'PBL-47'], azure_ids=[440,532,497,498,499,533,534,535,536,581,582],
                        build=os.getenv('BUILD_URL'), build_number=os.getenv('BUILD_NUMBER'),
                        cause=os.getenv('SPRINT10_CAUSE', 'manual'), academic_sprint=4, azure_sprint=10)
        (out / 'source.json').write_text(json.dumps(metadata, indent=2), encoding='utf8')
    elif args.phase == 'quality':
        web = ROOT / 'frontend/clinica-web-react'
        for name, command in [('translations',[npm,'run','check:i18n']), ('lint',[npm,'run','lint']),
                              ('web-tests',[npm,'run','test:coverage','--','--reporter=default','--reporter=junit',f'--outputFile={out / "web.xml"}']),
                              ('build',[npm,'run','build']), ('bundle',[npm,'run','check:bundle'])]:
            run(name, command, web)
        shutil.copytree(web / 'coverage', out / 'web-coverage', dirs_exist_ok=True)
        run('api-tests',[sys.executable,'-m','pytest','tests','-q','--cov=.',
                         '--cov-report=term', f'--cov-report=xml:{out / "api-coverage.xml"}',
                         f'--junitxml={out / "api.xml"}', f'--basetemp={out / "tmp-api"}'], ROOT / 'backend/api_hospital')
        run('policy-tests',[sys.executable,'-m','pytest','ci/test_security_gate.py','-q',f'--junitxml={out / "policy.xml"}'])
    elif args.phase == 'negative':
        # Actual failing assertion in an isolated feature-branch rehearsal.
        run('negative-ut',[sys.executable,'-m','pytest','ci/test_gate_demo.py','-v',f'--junitxml={out / "negative-ut.xml"}'])
    elif args.phase == 'oat':
        run('oat',[sys.executable,'qa/sprint-10/oat/run_oat.py','--out',str(out / 'oat')])
    else:
        (out / 'candidate.txt').write_text('Technical candidate only. No deployment, merge or UAT acceptance.\n', encoding='utf8')


if __name__ == '__main__':
    main()
