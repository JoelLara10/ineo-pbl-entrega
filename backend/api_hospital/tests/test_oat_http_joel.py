"""Actual HTTP and process restart, with an explicitly simulated Mongo dependency."""
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
from urllib.error import HTTPError

import pytest


@pytest.fixture
def api_process(tmp_path):
    processes = []
    logs = []
    def start(port=0, database_down=False):
        ready = tmp_path / f'ready-{len(processes)}.json'
        log = (tmp_path / f'api-{len(processes)}.log').open('w', encoding='utf8')
        logs.append(log)
        command = [sys.executable, str(Path(__file__).resolve().parents[3] / 'ci/demo_api.py'),
                   '--ready-file', str(ready), '--port', str(port)]
        if database_down:
            command.append('--database-down')
        proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        processes.append(proc)
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            if ready.exists():
                return proc, json.loads(ready.read_text())['port']
            if proc.poll() is not None:
                pytest.fail('API demo no inició; revisar dependencias y log de proceso')
            time.sleep(.1)
        pytest.fail('Timeout iniciando API demo')
    yield start
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)
    for log in logs:
        log.close()


def get(port, path):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}{path}', timeout=8) as response:
            return response.status, response.read().decode()
    except HTTPError as error:
        return error.code, error.read().decode()


def test_oat_http_health_and_readiness(api_process):
    _, port = api_process()
    assert get(port, '/health')[0] == 200
    status, body = get(port, '/ready')
    assert status == 200 and json.loads(body)['status'] == 'ready'


def test_oat_http_dependency_outage_does_not_leak_credentials(api_process):
    _, port = api_process(database_down=True)
    status, body = get(port, '/ready')
    assert status == 503
    assert 'secret-canary' not in body and 'private-host' not in body
    assert get(port, '/health')[0] == 200


def test_oat_http_controlled_restart_on_same_port(api_process):
    proc, port = api_process()
    assert get(port, '/ready')[0] == 200
    proc.terminate()
    proc.wait(timeout=10)
    second, same_port = api_process(port=port)
    assert second.pid != proc.pid and same_port == port
    assert get(port, '/ready')[0] == 200
    # Restart of a disposable seeded fixture; not a durable-data restore test.


def test_oat_http_requires_session_for_clinical_records(api_process):
    _, port = api_process()
    assert get(port, '/api/v1/appointments/1/nursing-assessment')[0] == 401
