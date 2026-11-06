"""Capture real Terraform lifecycle, expected negatives and idempotency."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--phase', choices=('provision', 'cleanup'), default='provision')
    args = parser.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    tf = os.getenv('TF_EXE', 'terraform')
    work = ROOT / 'infra/terraform'
    records = []

    def run(label, arguments, expected=(0,)):
        result = subprocess.run([tf, *arguments], cwd=work, capture_output=True,
                                text=True, encoding='utf-8', errors='replace')
        text = (result.stdout + result.stderr).replace(str(ROOT), '[repo]')
        (out / (label + '.txt')).write_text(text, encoding='utf-8')
        records.append({'step': label, 'exit_code': result.returncode,
                        'expected_codes': list(expected), 'passed': result.returncode in expected})
        print(label, 'exit=' + str(result.returncode), flush=True)
        if result.returncode not in expected:
            raise RuntimeError(label + ' failed; see original report')
        return result.stdout

    try:
        if args.phase == 'cleanup':
            run('destroy', ['destroy', '-auto-approve', '-input=false', '-no-color'])
            state = run('empty-state', ['state', 'list'])
            assert not state.strip(), 'Resources remain in Terraform state'
        else:
            run('terraform-version', ['version', '-no-color'])
            run('fmt', ['fmt', '-check', '-recursive', '-no-color'])
            run('validate', ['validate', '-no-color'])
            run('negative-cases', ['test', '-filter=tests/negative.tftest.hcl', '-no-color'])
            # Direct invalid plans prove that no apply occurs for bad input.
            run('invalid-empty-name', ['plan', '-input=false', '-no-color', '-var=environment_name='], (1,))
            run('invalid-port', ['plan', '-input=false', '-no-color', '-var=mongo_port=70000'], (1,))
            run('plan', ['plan', '-input=false', '-no-color', '-out=real-qa.tfplan'])
            plan = json.loads(run('plan-json', ['show', '-json', 'real-qa.tfplan']))
            changes = plan['resource_changes']
            assert len(changes) == 3
            assert all(c['change']['actions'] == ['create'] for c in changes)
            container = next(c for c in changes if c['type'] == 'docker_container')['change']['after']
            assert container['name'].startswith('ineo-test-')
            assert container['ports'][0]['ip'] == '127.0.0.1'
            run('apply', ['apply', '-input=false', '-no-color', 'real-qa.tfplan'])
            run('idempotency', ['plan', '-input=false', '-detailed-exitcode', '-no-color'], (0,))
            run('state', ['state', 'list'])
    finally:
        (out / (args.phase + '-summary.json')).write_text(json.dumps({
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'tested_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'executor': 'Marcelino Zahid Galicia Bonifacio',
            'method': 'Terraform with real local Docker provider', 'steps': records,
        }, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
