"""PBL-37: dependency health and recovery with synthetic in-memory Mongo.

These are component OAT checks, not Docker/real-Mongo certification or UAT.
"""
import pytest
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


def test_oat_liveness_has_version_and_timestamp(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'
    assert response.json['timestamp']
    assert response.json['version']


def test_oat_ready_when_database_responds(client):
    assert client.get('/ready').status_code == 200
    assert client.get('/ready').json == {'status': 'ready', 'database': 'available'}


@pytest.mark.parametrize('error', [ConnectionFailure, ServerSelectionTimeoutError])
def test_oat_database_failure_is_503_and_sanitized(client, isolated_database, monkeypatch, error, caplog):
    def unavailable(*args, **kwargs):
        raise error('mongodb://demo:secret-canary@private-host/clinical')
    monkeypatch.setattr(isolated_database, 'command', unavailable)
    response = client.get('/ready')
    assert response.status_code == 503
    assert response.json == {'status': 'not_ready', 'database': 'unavailable'}
    for secret in ['secret-canary', 'private-host', 'mongodb', 'clinical', 'Traceback']:
        assert secret not in response.get_data(as_text=True)
        assert secret not in caplog.text
    assert client.get('/health').status_code == 200


def test_oat_dependency_recovers_without_restarting_api(client, isolated_database, monkeypatch):
    original = isolated_database.command
    def unavailable(*args, **kwargs):
        raise ConnectionFailure('synthetic outage')
    monkeypatch.setattr(isolated_database, 'command', unavailable)
    assert client.get('/ready').status_code == 503
    monkeypatch.setattr(isolated_database, 'command', original)
    assert client.get('/ready').status_code == 200


def test_oat_health_checks_do_not_mutate_patient_data(client, isolated_database):
    before = list(isolated_database.pacientes.find())
    for _ in range(5):
        assert client.get('/ready').status_code == 200
        assert client.get('/health').status_code == 200
    assert list(isolated_database.pacientes.find()) == before
