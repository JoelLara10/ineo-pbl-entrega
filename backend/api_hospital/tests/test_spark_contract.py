from datetime import timedelta
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from jsonschema import Draft202012Validator
from middleware.auth_middleware import generate_token
from services import spark_service as service

CONTRACT = json.loads((Path(__file__).parents[3] / 'contracts/v1/api.schema.json').read_text())


def validate(name, value):
    Draft202012Validator({**CONTRACT, '$ref': '#/$defs/' + name}).validate(value)


def headers(role='admin'):
    return {'Authorization': 'Bearer ' + generate_token('000000000000000000000001', 'admin.test', role)}


@pytest.fixture(autouse=True)
def executor(monkeypatch):
    mock = Mock()
    monkeypatch.setattr(service, 'EXECUTOR', mock)
    return mock


@pytest.mark.parametrize('kind', service.TYPES)
def test_lifecycle_contract(client, monkeypatch, executor, kind):
    base = '/api/v1/spark'
    initial = client.get(f'{base}/status/{kind}', headers=headers())
    validate('spark_status', initial.json)
    assert initial.json['state'] == 'idle'
    result = client.get(f'{base}/{kind}', headers=headers())
    validate('spark_result', result.json)
    assert result.json['available'] is False
    response = client.post(f'{base}/run/{kind}', headers=headers())
    assert response.status_code == 202
    validate('spark_run', response.json)
    job_id = response.json['status']['job_id']
    duplicate = client.post(f'{base}/run/{kind}', headers=headers())
    assert duplicate.status_code == 200
    assert duplicate.json['status']['job_id'] == job_id
    assert executor.submit.call_count == 1

    def compute(_kind, rows):
        assert client.get(f'{base}/status/{kind}', headers=headers()).json['state'] == 'running'
        assert rows and not any('Id_exp' in row for row in rows)
        return {**service.empty_result(), 'available': True, 'summary': {'total': len(rows)}}

    monkeypatch.setattr(service, 'run_engine', compute)
    service.execute(kind, job_id)
    completed = client.get(f'{base}/status/{kind}', headers=headers())
    validate('spark_status', completed.json)
    assert completed.json['state'] == 'completed'
    result = client.get(f'{base}/{kind}', headers=headers())
    validate('spark_result', result.json)
    assert result.json['summary']['total'] == 8
    overview = client.get(f'{base}/overview', headers=headers())
    validate('spark_overview', overview.json)
    assert overview.json[kind]['available'] is True


@pytest.mark.parametrize('path,method', [('overview', 'get')] + [
    (prefix + kind, method) for kind in service.TYPES
    for prefix, method in [('', 'get'), ('status/', 'get'), ('run/', 'post')]])
@pytest.mark.parametrize('role,code', [(None, 401), ('medico', 403), ('enfermeria', 403), ('estudios', 403)])
def test_permissions_all_endpoints(client, path, method, role, code):
    response = getattr(client, method)('/api/v1/spark/' + path, headers=headers(role) if role else {})
    assert response.status_code == code
    validate('spark_error', response.json)


def test_failure_empty_retry_and_expired_job(client, monkeypatch, isolated_database):
    monkeypatch.setattr(service, 'run_engine', Mock(side_effect=RuntimeError('SECRET INTERNAL ERROR')))
    state, _ = service.start('clinical')
    service.execute('clinical', state['job_id'])
    failed = client.get('/api/v1/spark/status/clinical', headers=headers())
    validate('spark_status', failed.json)
    assert failed.json['state'] == 'failed'
    assert 'SECRET' not in json.dumps(failed.json)
    state, created = service.start('clinical')
    assert created
    monkeypatch.setattr(service, 'run_engine', lambda *_: service.empty_result())
    service.execute('clinical', state['job_id'])
    assert service.read_job('clinical')['state'] == 'completed'
    assert not service.results('clinical')['available']
    state, _ = service.start('clinical')
    isolated_database.spark_jobs.update_one({'_id': 'clinical'}, {'$set': {'expires_at': service.now() - timedelta(seconds=1)}})
    assert service.read_job('clinical')['state'] == 'failed'
    service.execute('clinical', state['job_id'])
    assert service.read_job('clinical')['state'] == 'failed'


def test_invalid_type_body_and_token(client):
    for method, route in [('get', 'unknown'), ('get', 'status/unknown'), ('post', 'run/unknown')]:
        response = getattr(client, method)('/api/v1/spark/' + route, headers=headers())
        assert response.status_code == 400
        validate('spark_error', response.json)
    assert client.post('/api/v1/spark/run/clinical', headers=headers(), json={'command': 'x'}).status_code == 400
    response = client.get('/api/v1/spark/overview', headers={'Authorization': 'Bearer invalid'})
    assert response.status_code == 401
    validate('spark_error', response.json)


def test_database_failure_is_503(client, monkeypatch):
    from pymongo.errors import ConnectionFailure
    monkeypatch.setattr(service, 'get_collection', Mock(side_effect=ConnectionFailure('private-host')))
    response = client.get('/api/v1/spark/clinical', headers=headers())
    assert response.status_code == 503
    validate('spark_error', response.json)
    assert 'private-host' not in response.text


def test_partial_source_no_sensitive_fields(isolated_database):
    isolated_database.signos_vitales.delete_many({})
    isolated_database.signos_vitales.insert_one({'fc': 'nan', 'fr': '18', 'temp': 'bad', 'spo2': True, 'nombre': 'PRIVATE'})
    assert service.collect_source('clinical') == [{'fc': None, 'fr': 18.0, 'temp': None, 'spo2': None}]


def test_auth_patients_studies_analytics_contract(client):
    response = client.post('/api/v1/auth/login', json={'username': 'admin.test', 'password': 'Prueba-Sprint7!'})
    assert response.status_code == 200
    validate('auth_login', response.json)
    auth = {'Authorization': 'Bearer ' + response.json['token']}
    for path, name in [('/patients', 'patients'), ('/studies/counts', 'studies_counts'), ('/analytics/dashboard', 'analytics')]:
        response = client.get('/api/v1' + path, headers=auth)
        assert response.status_code == 200, (path, response.json)
        validate(name, response.json)
    for path in ('/patients', '/studies/counts', '/analytics/dashboard'):
        response = client.get('/api/v1' + path)
        assert response.status_code == 401
        validate('error', response.json)
    response = client.post('/api/v1/auth/login', json={'username': 'admin.test', 'password': 'wrong'})
    assert response.status_code == 401
    validate('error', response.json)


def test_schema_detects_breaking_changes():
    from jsonschema import ValidationError
    with pytest.raises(ValidationError):
        validate('spark_status', {**service.status_of(None), 'running': 'false'})
    with pytest.raises(ValidationError):
        validate('spark_result', {'available': True})


def test_seed_repeatable_and_protected(isolated_database):
    from testing.seed import reset
    isolated_database.pacientes.delete_many({})
    reset(isolated_database)
    assert isolated_database.pacientes.count_documents({}) == 8
    reset(isolated_database)
    assert isolated_database.users.count_documents({}) == 4
    with pytest.raises(ValueError):
        reset(isolated_database.client['production'])


def test_timeout_retains_previous_result(monkeypatch):
    import subprocess
    previous = {**service.empty_result(), 'available': True, 'summary': {'total': 8}}
    monkeypatch.setattr(service, 'run_engine', lambda *_: previous.copy())
    first, _ = service.start('analytics')
    service.execute('analytics', first['job_id'])
    monkeypatch.setattr(service, 'run_engine', Mock(side_effect=subprocess.TimeoutExpired('spark', 180)))
    second, _ = service.start('analytics')
    service.execute('analytics', second['job_id'])
    assert service.read_job('analytics')['state'] == 'failed'
    assert service.results('analytics')['summary']['total'] == 8


def test_missing_pyspark_fails_fast_with_actionable_message(monkeypatch):
    monkeypatch.setattr(service.importlib.util, 'find_spec', lambda _name: None)
    with pytest.raises(service.SparkRuntimeError, match='PySpark no está instalado'):
        service.run_engine('analytics', [])


def test_missing_java_fails_fast_with_actionable_message(monkeypatch):
    monkeypatch.setattr(service.importlib.util, 'find_spec', lambda _name: object())
    monkeypatch.setattr(service.shutil, 'which', lambda _name: None)
    with pytest.raises(service.SparkRuntimeError, match='Java no está disponible'):
        service.run_engine('analytics', [])


def test_runtime_failure_is_persisted_for_the_user(monkeypatch):
    message = 'Java 17 no está configurado correctamente para ejecutar Spark.'
    monkeypatch.setattr(service, 'run_engine', Mock(side_effect=service.SparkRuntimeError(message)))
    state, created = service.start('analytics')
    assert created
    service.execute('analytics', state['job_id'])
    saved = service.read_job('analytics')
    assert saved['state'] == 'failed'
    assert saved['error'] == message


def test_new_job_has_a_bounded_recovery_window(executor):
    before = service.now()
    state, created = service.start('met')
    assert created
    job = service.read_job('met')
    stored_before = before.replace(tzinfo=None) if job['expires_at'].tzinfo is None else before
    assert job['expires_at'] <= stored_before + timedelta(seconds=service.JOB_TTL + 1)
    assert state['state'] == 'pending'


def test_old_job_cannot_overwrite_replacement(monkeypatch, isolated_database):
    first, _ = service.start('clinical')

    def replace_job(*_):
        isolated_database.spark_jobs.update_one({'_id': 'clinical'}, {'$set': {'job_id': 'replacement', 'state': 'pending'}})
        return service.empty_result()

    monkeypatch.setattr(service, 'run_engine', replace_job)
    service.execute('clinical', first['job_id'])
    current = service.read_job('clinical')
    assert current['job_id'] == 'replacement'
    assert current['state'] == 'pending'
    assert 'result' not in current


def test_dataset_limit_is_explicit(monkeypatch):
    monkeypatch.setattr(service, 'MAX_ROWS', 2)
    with pytest.raises(ValueError, match='dataset_limit'):
        service.collect_source('clinical')


def test_concurrent_requests_share_one_job(executor):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as pool:
        states = list(pool.map(lambda _: service.start('met'), range(8)))
    assert len({state['job_id'] for state, _ in states}) == 1
    assert sum(created for _, created in states) == 1
    assert executor.submit.call_count == 1
