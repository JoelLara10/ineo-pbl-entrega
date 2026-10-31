"""Run independent security/code gates and retain evidence even on failures."""
import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def finding_locations(scan, reviewed):
    """An exception matches one reviewed hash/type/file, never a whole directory."""
    allowed = {(x['file'], x['type'], x['hashed_secret']) for x in reviewed}
    return [{'file': name.replace('\\', '/'), 'type': hit['type'], 'line': hit['line_number']}
            for name, hits in scan.get('results', {}).items() for hit in hits
            if (name.replace('\\', '/'), hit['type'], hit['hashed_secret']) not in allowed]


def validate_reviewed(reviewed):
    for item in reviewed:
        if set(item) != {'file', 'type', 'hashed_secret', 'reason'}:
            raise ValueError('Invalid reviewed fixture fields')
        if not re.fullmatch(r'[a-f0-9]{40}', item['hashed_secret']):
            raise ValueError('Fixture exception must contain a SHA1 digest, never its value')
        if item['type'] not in {'Secret Keyword', 'Hex High Entropy String', 'Basic Auth Credentials'}:
            raise ValueError('Unsupported fixture detector type')
        if item['reason'] not in {
            'SHA de version o checksum de evidencia; no es credencial',
            'Texto de interfaz traducido; no es credencial',
            'Dato sintetico de test o demo local; nunca usar en produccion',
        } or not item['file'] or item['file'].startswith('/') or '..' in item['file'].split('/') or not (ROOT / item['file']).is_file():
            raise ValueError('Fixture exception must have a relative path and review reason')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--test-python', default=sys.executable)
    args = parser.parse_args()
    args.test_python = str(Path(args.test_python).resolve()) if Path(args.test_python).exists() else args.test_python
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = []
    npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm') or 'npm'
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip())
    (out / 'source.json').write_text(json.dumps({'sha': sha, 'tracked_changes': dirty,
        'time_utc': dt.datetime.now(dt.timezone.utc).isoformat()}, indent=2), encoding='utf8')

    def run(name, command, cwd=ROOT, mode='text'):
        start = time.monotonic()
        try:
            proc = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                                  encoding='utf8', errors='replace', timeout=600,
                                  env={**os.environ, 'PYTHONUTF8': '1'})
            rc, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
            detail = 'Exit code ' + str(rc)
            if mode == 'bandit':
                report = json.loads((out / 'python-static.json').read_text(encoding='utf8'))
                for item in report.get('results', []):
                    item.pop('code', None)  # Do not publish source literals in scan evidence.
                if report.get('errors'):
                    rc = 2
                stdout = json.dumps(report, ensure_ascii=False, indent=2)
                detail = f"{len(report.get('results', []))} findings at medium/high severity; scan errors={len(report.get('errors', []))}"
            elif mode == 'secrets':
                scan = json.loads(stdout)
                if rc:
                    raise ValueError('Secret scanner failed')
                reviewed = json.loads((ROOT / 'ci/security-reviewed-fixtures.json').read_text(encoding='utf8'))
                validate_reviewed(reviewed)
                findings = finding_locations(scan, reviewed)
                rc = 1 if findings else 0
                stdout = json.dumps({'unreviewed_findings': findings, 'reviewed_fixture_count': len(reviewed)}, indent=2)
                if findings:
                    print('Unreviewed detector locations: ' + ', '.join(
                        str(item['file']) + ':' + str(item['line']) for item in findings), flush=True)
                detail = f'{len(findings)} unreviewed suspected secrets'
            elif mode == 'audit':
                report = json.loads(stdout)
                if 'error' in report or 'metadata' not in report:
                    raise ValueError('npm audit did not return a valid complete report')
                counts = report['metadata']['vulnerabilities']
                rc = 1 if counts.get('high', 0) or counts.get('critical', 0) else 0
                detail = f"high={counts.get('high', 0)}, critical={counts.get('critical', 0)}; lower severities retained in report"
            (out / (name + ('.json' if mode != 'text' else '.log'))).write_text(stdout, encoding='utf8')
            # Commands here never contain credentials. Scanner stderr is operational metadata.
            (out / (name + '-stderr.log')).write_text(stderr, encoding='utf8')
        except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
            rc, detail = 2, type(exc).__name__ + ': ' + str(exc)
            (out / (name + '-error.log')).write_text(detail, encoding='utf8')
        results.append({'name': name, 'passed': rc == 0, 'exit_code': rc,
                        'seconds': round(time.monotonic() - start, 3), 'detail': detail})
        print(name + ': ' + ('PASS' if rc == 0 else 'FAIL') + ' — ' + detail, flush=True)

    run('python-static', [sys.executable, '-m', 'bandit', '-r', 'app.py', 'config.py',
        'middleware', 'models', 'routes', 'services', 'utils', 'security', 'scripts',
        '-x', 'tests', '-ll', '-f', 'json', '-o', str(out / 'python-static.json')], ROOT / 'backend/api_hospital', 'bandit')
    run('python-dependencies', [sys.executable, '-m', 'pip_audit', '-r', 'requirements.txt',
        '--format', 'json', '--progress-spinner', 'off'], ROOT / 'backend/api_hospital')
    run('web-dependencies', [npm, 'audit', '--json', '--audit-level=high'], ROOT / 'frontend/clinica-web-react', 'audit')
    # Only this schema-validated digest catalog is excluded; source/test folders stay scanned.
    run('secret-scan', [sys.executable, '-m', 'detect_secrets', 'scan', '--no-verify',
        '--exclude-files', r'^ci[/\\]security-reviewed-fixtures\.json$'], mode='secrets')
    run('web-static', [npm, 'run', 'lint'], ROOT / 'frontend/clinica-web-react')
    run('auth-web-tests', [npm, 'test', '--', 'src/tests/auth-session.test.jsx',
        'src/tests/study-request-safety.test.jsx',
        '--reporter=default', '--reporter=junit', '--outputFile=' + str(out / 'auth-web.xml')], ROOT / 'frontend/clinica-web-react')
    run('security-api-tests', [args.test_python, '-m', 'pytest', 'tests/test_security_hardening.py',
        'tests/test_security_remediation.py',
        '-v', '-p', 'no:cacheprovider', '--basetemp=' + str(out / 'pytest-tmp'),
        '--junitxml=' + str(out / 'security-api.xml')], ROOT / 'backend/api_hospital')
    suite = ET.Element('testsuite', name='Security and code gates', tests=str(len(results)),
                       failures=str(sum(not x['passed'] for x in results)))
    for result in results:
        case = ET.SubElement(suite, 'testcase', classname='OftalCore.Security',
                             name=result['name'], time=str(result['seconds']))
        if not result['passed']:
            ET.SubElement(case, 'failure', message=result['detail']).text = 'Review the archived report; failed or unavailable checks block acceptance.'
    ET.ElementTree(suite).write(out / 'security-gates.xml', encoding='utf8', xml_declaration=True)
    (out / 'summary.json').write_text(json.dumps({'sha': sha, 'checks': results,
        'passed': all(x['passed'] for x in results)}, indent=2), encoding='utf8')
    (out / 'summary.md').write_text('# Security and code review\n\nSHA: ' + sha + '\n\n' +
        '\n'.join('- ' + x['name'] + ': ' + ('PASS' if x['passed'] else 'FAIL') + ' — ' + x['detail'] for x in results) +
        '\n\nAutomated checks do not establish human UAT acceptance or complete security assurance.\n', encoding='utf8')
    return 0 if all(x['passed'] for x in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
