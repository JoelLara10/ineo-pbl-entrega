from copy import deepcopy

import pytest
from bson import ObjectId

from middleware.auth_middleware import generate_token
from services.spark_service import SparkService


class MemorySparkJobs:
    """Almacén en memoria compatible con claves `_id` del SparkService actual."""

    def __init__(self):
        self.docs = {}

    def find_one(self, query):
        key = query.get('_id') or query.get('type')
        document = self.docs.get(key)
        return deepcopy(document) if document else None

    def update_one(self, query, update, upsert=False):
        key = query.get('_id') or query.get('type')
        current = deepcopy(self.docs.get(key) or {'_id': key})

        if '$setOnInsert' in update and key not in self.docs:
            current.update(update['$setOnInsert'])

        # Respetar filtros de estado / job_id cuando existen
        if 'job_id' in query and current.get('job_id') != query.get('job_id'):
            return type('R', (), {'modified_count': 0})()
        if 'state' in query and not isinstance(query.get('state'), dict):
            if current.get('state') != query['state']:
                return type('R', (), {'modified_count': 0})()
        state_filter = query.get('state')
        if isinstance(state_filter, dict) and '$nin' in state_filter:
            if current.get('state') in state_filter['$nin']:
                return type('R', (), {'modified_count': 0})()

        if '$set' in update:
            current.update(update['$set'])
        self.docs[key] = current
        return type('R', (), {'modified_count': 1})()

    def find_one_and_update(self, query, update, return_document=None, upsert=False):
        key = query.get('_id') or query.get('type')
        current = self.docs.get(key) or {'_id': key, 'state': 'idle'}

        state_filter = query.get('state')
        if isinstance(state_filter, dict) and '$nin' in state_filter:
            if current.get('state') in state_filter['$nin']:
                return None

        if '$set' in update:
            current = {**current, **update['$set']}
        self.docs[key] = current
        return deepcopy(current)

    def delete_many(self, query):
        return type('R', (), {'deleted_count': 0})()

    def find(self, *args, **kwargs):
        return iter([])


@pytest.fixture
def spark_jobs(monkeypatch):
    store = MemorySparkJobs()
    monkeypatch.setattr(
        'services.spark_service.get_collection',
        lambda name: store,
    )
    # token_required consulta el usuario actual
    monkeypatch.setattr(
        'models.user.UserModel.find_by_id',
        lambda _user_id: {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'activo': True,
            'username': 'tester',
            'role': 'admin',
        },
    )
    return store


def auth_header(role='admin', username='tester'):
    # ObjectId válido de 24 hex (TEST-USER rompe bson.ObjectId)
    token = generate_token('507f1f77bcf86cd799439011', username, role)
    return {'Authorization': f'Bearer {token}'}


def test_spark_routes_are_registered(app):
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert '/api/v1/spark/overview' in routes
    assert '/api/v1/spark/run/<analysis_type>' in routes
    assert '/api/v1/spark/status/<analysis_type>' in routes
    assert '/api/v1/spark/<analysis_type>' in routes


def test_clinical_status_without_job_is_idle(client, spark_jobs):
    """Sin job: contrato exige idle + running false (no pending)."""
    response = client.get('/api/v1/spark/status/clinical', headers=auth_header())

    assert response.status_code == 200
    body = response.get_json()
    assert body['state'] == 'idle'
    assert body['running'] is False
    assert body['type'] == 'clinical'


def test_clinical_result_without_job_is_unavailable(client, spark_jobs):
    response = client.get('/api/v1/spark/clinical', headers=auth_header())

    assert response.status_code == 200
    body = response.get_json()
    assert body['available'] is False
    assert body['timestamp'] is None
    assert body['type'] == 'clinical'


def test_run_clinical_returns_pending_running(client, spark_jobs, monkeypatch):
    monkeypatch.setattr(
        'services.spark_service.EXECUTOR.submit',
        lambda *args, **kwargs: None,
    )

    response = client.post('/api/v1/spark/run/clinical', headers=auth_header())

    assert response.status_code == 202
    status = response.get_json()['status']
    # API actual: pending (no "processing")
    assert status['state'] == 'pending'
    assert status['running'] is True
    assert status['job_id']


def test_status_during_job_is_running_flag(client, spark_jobs, monkeypatch):
    monkeypatch.setattr(
        'services.spark_service.EXECUTOR.submit',
        lambda *args, **kwargs: None,
    )
    client.post('/api/v1/spark/run/clinical', headers=auth_header())

    response = client.get('/api/v1/spark/status/clinical', headers=auth_header())

    assert response.status_code == 200
    body = response.get_json()
    assert body['state'] in ('pending', 'running')
    assert body['running'] is True


def test_run_while_busy_returns_existing_job(client, spark_jobs, monkeypatch):
    """Rutas actuales: segundo run es idempotente (200 + mismo job), no 409."""
    monkeypatch.setattr(
        'services.spark_service.EXECUTOR.submit',
        lambda *args, **kwargs: None,
    )
    first = client.post('/api/v1/spark/run/clinical', headers=auth_header())
    job_id = first.get_json()['status']['job_id']

    second = client.post('/api/v1/spark/run/clinical', headers=auth_header())

    assert second.status_code == 200
    assert second.get_json()['status']['job_id'] == job_id


def test_invalid_type_returns_bad_request(client, spark_jobs):
    response = client.post('/api/v1/spark/run/no-existe', headers=auth_header())

    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_spark_requires_token(client):
    response = client.post('/api/v1/spark/run/clinical')

    assert response.status_code == 401
    assert response.get_json()['error'] == 'Token no proporcionado'


def test_spark_rejects_unauthorized_role(client, spark_jobs):
    response = client.post(
        '/api/v1/spark/run/clinical',
        headers=auth_header('enfermero'),
    )

    assert response.status_code == 403
    assert response.get_json()['error'] == 'Permisos insuficientes'


def test_overview_lists_types(client, spark_jobs):
    response = client.get('/api/v1/spark/overview', headers=auth_header('administrativo'))

    assert response.status_code == 200
    body = response.get_json()
    assert 'clinical' in body
    assert 'met' in body
    assert body['clinical']['available'] is False
    assert body['met']['available'] is False