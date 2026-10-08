"""PBL-02/PBL-13: gaps after reusing Sprint 7 (updated planning workbook)."""
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from bson import ObjectId
from jsonschema import ValidationError
from pymongo.errors import ConnectionFailure

from routes import spark
from services import spark_service as service
from tests.test_spark_contract import headers, validate

ENDPOINTS = [('get', 'overview')] + [
    (method, prefix + kind) for kind in service.TYPES
    for method, prefix in [('get', ''), ('get', 'status/'), ('post', 'run/')]]


@pytest.mark.parametrize('method,path', ENDPOINTS)
@pytest.mark.parametrize('change,code', [('disabled', 401), ('deleted', 401), ('demoted', 403)])
def test_current_account_controls_spark_access(client, isolated_database, monkeypatch, method, path, change, code):
    auth = headers()  # Token issued before changing the account.
    query = {'_id': ObjectId('000000000000000000000001')}
    if change == 'deleted':
        isolated_database.users.delete_one(query)
    else:
        isolated_database.users.update_one(query, {'$set': {'activo': False} if change == 'disabled' else {'role': 'medico'}})
    executor = Mock()
    monkeypatch.setattr(service, 'EXECUTOR', executor)
    response = getattr(client, method)('/api/v1/spark/' + path, headers=auth)
    assert response.status_code == code
    validate('spark_error', response.json)
    executor.submit.assert_not_called()


def test_account_database_failure_preserves_json_error(client, monkeypatch):
    monkeypatch.setattr(spark, 'get_collection', Mock(side_effect=ConnectionFailure('PRIVATE DATABASE')))
    response = client.get('/api/v1/spark/overview', headers=headers())
    assert response.status_code == 503
    validate('spark_error', response.json)
    assert 'PRIVATE' not in response.text


@pytest.mark.parametrize('user_id', ['', 'invalid-id', '9' * 5000])
def test_invalid_signed_identity_is_401(client, user_id):
    from middleware.auth_middleware import generate_token
    response = client.get('/api/v1/spark/overview', headers={
        'Authorization': 'Bearer ' + generate_token(user_id, 'test', 'admin')})
    assert response.status_code == 401
    validate('spark_error', response.json)


@pytest.mark.parametrize('kind', service.TYPES)
def test_executor_failure_finishes_job_and_allows_retry(client, monkeypatch, isolated_database, kind):
    previous = {**service.empty_result(), 'available': True, 'summary': {'total': 8}}
    isolated_database.spark_jobs.insert_one({'_id': kind, 'state': 'completed', 'result': previous})
    executor = Mock()
    executor.submit.side_effect = RuntimeError('PRIVATE EXECUTOR DETAIL')
    monkeypatch.setattr(service, 'EXECUTOR', executor)
    response = client.post('/api/v1/spark/run/' + kind, headers=headers())
    assert response.status_code == 503
    validate('spark_error', response.json)
    state = client.get('/api/v1/spark/status/' + kind, headers=headers()).json
    validate('spark_status', state)
    assert state['state'] == 'failed' and state['running'] is False
    assert state['finished_at'] is not None and state['started_at'] is None
    assert 'PRIVATE' not in str(state)
    assert client.get('/api/v1/spark/' + kind, headers=headers()).json == previous
    executor.submit.side_effect = None
    retried = client.post('/api/v1/spark/run/' + kind, headers=headers())
    assert retried.status_code == 202
    validate('spark_run', retried.json)
    assert retried.json['status']['job_id'] != state['job_id']
    assert retried.json['status']['finished_at'] is None


def test_overview_uses_one_consistent_snapshot_per_type(client, monkeypatch):
    read = Mock(return_value={'state': 'completed', 'result': {**service.empty_result(), 'available': True}})
    monkeypatch.setattr(service, 'read_job', read)
    response = client.get('/api/v1/spark/overview', headers=headers())
    assert response.status_code == 200
    validate('spark_overview', response.json)
    assert [call.args[0] for call in read.call_args_list] == list(service.TYPES)
    assert all(entry['available'] and entry['status']['state'] == 'completed' for entry in response.json.values())


@pytest.mark.parametrize('value', [datetime(2026, 10, 8, 12),
    datetime(2026, 10, 8, 6, tzinfo=timezone(timedelta(hours=-6)))])
def test_status_dates_preserve_instant_as_utc(value):
    state = service.status_of({'state': 'completed', 'started_at': value, 'finished_at': value})
    validate('spark_status', state)
    assert state['started_at'] == state['finished_at'] == '2026-10-08T12:00:00+00:00'


@pytest.mark.parametrize('name,field', [('spark_status', 'started_at'), ('spark_status', 'finished_at'), ('spark_result', 'timestamp')])
def test_date_contract_rejects_malformed_dates(name, field):
    value = service.status_of(None) if name == 'spark_status' else service.empty_result()
    validate(name, value)
    for invalid in ['yesterday', '2026-99-99T12:00:00Z', '2026-10-08']:
        with pytest.raises(ValidationError):
            validate(name, {**value, field: invalid})


def test_image_contract_positive_and_negative_examples():
    image = {'filename': 'chart.png', 'name': 'Gráfica sintética', 'url': '/spark/images/chart.png'}
    result = {**service.empty_result(), 'visualizations': [image]}
    validate('spark_result', result)
    for field in image:
        with pytest.raises(ValidationError):
            validate('image', {key: value for key, value in image.items() if key != field})
    for url in ['https://example.com/chart.png', '/patients', 'chart.png']:
        with pytest.raises(ValidationError):
            validate('spark_result', {**result, 'visualizations': [{**image, 'url': url}]})
    with pytest.raises(ValidationError):
        validate('spark_result', {**result, 'contract_version': '2.0'})


@pytest.mark.parametrize('method,path', ENDPOINTS)
def test_cors_preflight_does_not_require_token_or_start_job(client, monkeypatch, method, path):
    executor = Mock()
    monkeypatch.setattr(service, 'EXECUTOR', executor)
    response = client.options('/api/v1/spark/' + path, headers={
        'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': method.upper(),
        'Access-Control-Request-Headers': 'Authorization'})
    assert response.status_code == 200
    assert 'Authorization' in response.headers['Access-Control-Allow-Headers']
    executor.submit.assert_not_called()


def test_legacy_numeric_account_id_remains_supported(client):
    from middleware.auth_middleware import generate_token
    response = client.get('/api/v1/spark/overview', headers={
        'Authorization': 'Bearer ' + generate_token('1', 'admin.test', 'admin')})
    assert response.status_code == 200
    validate('spark_overview', response.json)


def test_expired_admin_token_cannot_start_work(client, monkeypatch):
    import os
    import jwt
    executor = Mock()
    monkeypatch.setattr(service, 'EXECUTOR', executor)
    token = jwt.encode({'user_id': '000000000000000000000001', 'role': 'admin',
                        'exp': service.now() - timedelta(seconds=1)},
                       os.environ['SECRET_KEY'], algorithm='HS256')
    response = client.post('/api/v1/spark/run/clinical', headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 401
    validate('spark_error', response.json)
    executor.submit.assert_not_called()
