"""Real HTTP + Docker Mongo + Terraform lifecycle. No production endpoints."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    tf = out / 'terraform'
    tf.mkdir(exist_ok=True)
    for name in ('main.tf', '.terraform.lock.hcl'):
        shutil.copy2(Path(__file__).with_name(name), tf / name)
    run_id = 's10-' + uuid.uuid4().hex[:12]
    env = dict(os.environ, TF_VAR_run_id=run_id, TF_IN_AUTOMATION='1')
    records, processes, streams = [], [], []
    started = datetime.now(timezone.utc).isoformat()

    def command(cmd, name, timeout=300):
        result = subprocess.run(cmd, env=env, cwd=ROOT, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=timeout, encoding='utf8', errors='replace')
        (out / (name + '.log')).write_text(result.stdout, encoding='utf8')
        if result.returncode:
            raise RuntimeError(f'{name} exited {result.returncode}; see sanitized log')
        return result.stdout.strip()

    def terraform(*args):
        if os.getenv('S10_TERRAFORM_DOCKER') == '1':
            certificates = []
            if os.getenv('CA_BUNDLE'):
                certificates = ['-v', f'{Path(os.environ["CA_BUNDLE"]).resolve()}:/certs/trusted.pem:ro',
                                '-e', 'SSL_CERT_FILE=/certs/trusted.pem']
            return command(['docker', 'run', '--rm',
                            '-v', f'{tf}:/work', '-v', '/var/run/docker.sock:/var/run/docker.sock',
                            '-w', '/work', '-e', f'TF_VAR_run_id={run_id}',
                            *certificates, 'hashicorp/terraform:1.13.5', *args], 'tf-' + args[0])
        return command(['terraform', f'-chdir={tf}', *args], 'tf-' + args[0])

    def request(port, path, headers=None):
        req = urllib.request.Request(f'http://127.0.0.1:{port}{path}', headers=headers or {})
        try:
            response = urllib.request.urlopen(req, timeout=8)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.code, response.read().decode(), dict(response.headers)

    def wait_ready(port, expected=200, limit=45):
        begin = time.monotonic()
        while time.monotonic() - begin < limit:
            try:
                value = request(port, '/ready')
                if value[0] == expected:
                    return value, round(time.monotonic() - begin, 3)
            except (OSError, TimeoutError):
                pass
            time.sleep(.25)
        raise RuntimeError(f'Readiness did not reach {expected} within {limit}s')

    def launch(port, mongo_port):
        stream = (out / f'api-{len(processes)}.log').open('w', encoding='utf8')
        streams.append(stream)
        process = subprocess.Popen([sys.executable, str(Path(__file__).with_name('api_server.py')),
                                    '--mongo-port', str(mongo_port), '--port', str(port)],
                                   cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
        processes.append(process)
        return process

    def record(identifier, description, action):
        begin = time.monotonic()
        try:
            detail = action()
            records.append(dict(id=identifier, title=description, status='Aprobado', detail=detail,
                                seconds=round(time.monotonic() - begin, 3)))
        except Exception as error:
            records.append(dict(id=identifier, title=description, status='Fallido',
                                detail=str(error), seconds=round(time.monotonic() - begin, 3)))
            raise

    baseline = command(['docker', 'ps', '-q'], 'unrelated-before').splitlines()
    sha = command(['git', 'rev-parse', 'HEAD'], 'source-sha')
    error = None
    try:
        terraform('init', '-input=false', '-no-color')
        terraform('validate', '-no-color')
        terraform('apply', '-auto-approve', '-input=false', '-no-color')
        mongo_port = int(terraform('output', '-raw', 'mongo_port'))
        container = 'ineo-' + run_id + '-mongo'
        label = command(['docker', 'inspect', container, '--format', '{{index .Config.Labels "ineo.qa.run"}}'], 'label')
        assert label == run_id
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        process = launch(port, mongo_port)

        def health():
            good, _ = wait_ready(port)
            assert request(port, '/health')[0] == 200
            command(['docker', 'stop', container], 'mongo-stop')
            bad, elapsed = wait_ready(port, 503)
            assert json.loads(bad[1]) == {'status': 'not_ready', 'database': 'unavailable'}
            assert request(port, '/health')[0] == 200
            command(['docker', 'start', container], 'mongo-start')
            restored, recovery = wait_ready(port)
            return {'healthy': good[:2], 'outage': bad[:2], 'recovered': restored[:2],
                    'outage_detection_seconds': elapsed, 'recovery_seconds': recovery,
                    'database': 'real MongoDB 7 Docker', 'api': 'real Flask app over HTTP'}
        record('CP-S10-OAT-01', 'Salud y readiness', health)

        def logs():
            status, body, headers = request(port, '/patient-canary?token=token-canary',
                                           {'Authorization': 'Bearer auth-canary'})
            assert status == 404
            correlation = headers.get('X-Request-ID') or headers.get('X-Request-Id')
            assert correlation and len(correlation) == 32
            time.sleep(.2)
            text = (out / 'api-0.log').read_text(encoding='utf8')
            # Werkzeug access logging also receives the original URL. It is disabled
            # by api_server; application logs retain the generated correlation only.
            assert correlation in text
            for marker in ('patient-canary', 'token-canary', 'auth-canary'):
                assert marker not in text and marker not in body
            return {'http': status, 'request_id': correlation,
                    'markers_absent': ['patient-canary', 'token-canary', 'auth-canary']}
        record('CP-S10-OAT-02', 'Logs sanitizados', logs)

        def restart():
            old = process.pid
            process.terminate()
            process.wait(timeout=10)
            begin = time.monotonic()
            new = launch(port, mongo_port)
            wait_ready(port)
            elapsed = round(time.monotonic() - begin, 3)
            assert elapsed < 45 and new.pid != old
            assert request(port, '/health')[0] == 200
            assert request(port, '/api/v1/patients')[0] == 401
            return {'old_pid': old, 'new_pid': new.pid, 'same_port': port,
                    'recovery_seconds': elapsed, 'technical_target_seconds': 45,
                    'smoke_health': 200, 'smoke_unauthenticated': 401}
        record('CP-S10-OAT-03', 'Reinicio controlado', restart)
    except Exception as caught:
        error = str(caught)
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
        for stream in streams:
            stream.close()
        def cleanup():
            # Only this invocation's private Terraform state, never global prune.
            terraform('destroy', '-auto-approve', '-input=false', '-no-color')
            remaining = command(['docker', 'ps', '-aq', '--filter', f'label=ineo.qa.run={run_id}'], 'owned-after')
            assert not remaining
            after = command(['docker', 'ps', '-q'], 'unrelated-after').splitlines()
            assert set(baseline).issubset(after), 'An unrelated container stopped'
            return {'run_id': run_id, 'owned_remaining': 0, 'unrelated_running_preserved': baseline}
        try:
            record('CP-S10-OAT-04', 'Limpieza IaC', cleanup)
        except Exception as caught:
            error = error or str(caught)
        for i in range(1, 5):
            identifier = f'CP-S10-OAT-{i:02}'
            if not any(r['id'] == identifier for r in records):
                records.append(dict(id=identifier, title='Dependencia previa', status='Bloqueado', detail=error, seconds=0))
        summary = dict(started=started, finished=datetime.now(timezone.utc).isoformat(),
                       sha=sha, run_id=run_id, environment='local QA aislado',
                       executor='Agente en representación de Joel', reviewer='Jaime pendiente',
                       records=records, error=error)
        (out / 'oat.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf8')
        suite = ET.Element('testsuite', name='Sprint10 OAT real', tests='4')
        for row in records:
            case = ET.SubElement(suite, 'testcase', name=row['id'], classname='Sprint10.OAT', time=str(row['seconds']))
            if row['status'] != 'Aprobado':
                ET.SubElement(case, 'failure', message=row['status']).text = str(row['detail'])
            ET.SubElement(case, 'system-out').text = json.dumps(row['detail'], ensure_ascii=False)
        ET.ElementTree(suite).write(out / 'oat.xml', encoding='utf8', xml_declaration=True)
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if error else 0


if __name__ == '__main__':
    raise SystemExit(main())
