from copy import deepcopy

import pytest

from middleware.auth_middleware import generate_token
from services.spark_service import SparkService


CLINICAL_RESULT = {
    'top_diagnosis': [{'diagnosis': 'J18.9', 'count': 12}],
    'age_distribution': [{'range': '30', 'count': 8}],
    'average_stay_days': 3.4,
}

EMPTY_RESULT = {
    'top_diagnosis': [],
    'age_distribution': [],
    'average_stay_days': 0,
}


class MemorySparkJobs:
    def __init__(self):
        self.docs = {}

    def find_one(self, query):
        document = self.docs.get(query.get('type'))
        return deepcopy(document) if document else None

    def update_one(self, query, update, upsert=False):
        key = query.get('type')
        current = deepcopy(self.docs.get(key) or {})
        current.update(update.get('$set') or {})
        if upsert or key in self.docs:
            current['type'] = key
            self.docs[key] = current
        return None


@pytest.fixture
def spark_jobs(monkeypatch):
    store = MemorySparkJobs()
    monkeypatch.setattr(
        'services.spark_service.get_collection',
        lambda name: store,
    )
    return store


def auth_header(role='admin', username='tester'):
    token = generate_token('TEST-USER', username, role)
    return {'Authorization': f'Bearer {token}'}


def test_spark_routes_are_registered(app):
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert '/api/v1/spark/overview' in routes
    assert '/api/v1/spark/run/<analysis_type>' in routes
    assert '/api/v1/spark/status/<analysis_type>' in routes
    assert '/api/v1/spark/<analysis_type>' in routes


def test_clinical_status_without_job_is_pending(client, spark_jobs):
    response = client.get('/api/v1/spark/status/clinical', headers=auth_header())

    assert response.status_code == 200
    body = response.get_json()
    assert body['state'] == 'pending'
    assert body['running'] is False
    assert body['type'] == 'clinical'


def test_clinical_result_without_job_is_unavailable(client, spark_jobs):
    response = client.get('/api/v1/spark/clinical', headers=auth_header())

    assert response.status_code == 200
    body = response.get_json()
    assert body['available'] is False
    assert body['timestamp'] is None
    assert body['type'] == 'clinical'


def test_run_clinical_returns_processing_status(client, spark_jobs, monkeypatch):
    monkeypatch.setattr(SparkService, '_launch', lambda analysis_type: None)

    response = client.post('/api/v1/spark/run/clinical', headers=auth_header('medico'))

    assert response.status_code == 202
    status = response.get_json()['status']
    assert status['state'] == 'processing'
    assert status['running'] is True


def test_status_during_job_is_processing(client, spark_jobs, monkeypatch):
    monkeypatch.setattr(SparkService, '_launch', lambda analysis_type: None)
    client.post('/api/v1/spark/run/clinical', headers=auth_header())

    response = client.get('/api/v1/spark/status/clinical', headers=auth_header())

    assert response.status_code == 200
    body = response.get_json()
    assert body['state'] == 'processing'
    assert body['running'] is True


def test_run_clinical_while_processing_returns_conflict(client, spark_jobs, monkeypatch):
    monkeypatch.setattr(SparkService, '_launch', lambda analysis_type: None)
    client.post('/api/v1/spark/run/clinical', headers=auth_header())

    response = client.post('/api/v1/spark/run/clinical', headers=auth_header())

    assert response.status_code == 409
    assert 'error' in response.get_json()


def test_completed_job_returns_real_clinical_payload(client, spark_jobs, monkeypatch):
    monkeypatch.setattr(
        SparkService,
        '_launch',
        lambda analysis_type: SparkService._execute_clinical(analysis_type),
    )
    monkeypatch.setattr(
        'services.spark_service.AnalyticsService.get_clinical_analytics',
        staticmethod(lambda: CLINICAL_RESULT),
    )

    run_response = client.post('/api/v1/spark/run/clinical', headers=auth_header())
    status = client.get('/api/v1/spark/status/clinical', headers=auth_header())
    result = client.get('/api/v1/spark/clinical', headers=auth_header())

    assert run_response.status_code == 202
    assert status.get_json()['state'] == 'completed'
    assert status.get_json()['running'] is False
    body = result.get_json()
    assert body['available'] is True
    assert body['top_diagnosis'] == CLINICAL_RESULT['top_diagnosis']
    assert body['age_distribution'] == CLINICAL_RESULT['age_distribution']
    assert body['average_stay_days'] == CLINICAL_RESULT['average_stay_days']
    assert body['visualizations'] == []


def test_completed_job_without_data_is_unavailable(client, spark_jobs, monkeypatch):
    monkeypatch.setattr(
        SparkService,
        '_launch',
        lambda analysis_type: SparkService._execute_clinical(analysis_type),
    )
    monkeypatch.setattr(
        'services.spark_service.AnalyticsService.get_clinical_analytics',
        staticmethod(lambda: EMPTY_RESULT),
    )

    client.post('/api/v1/spark/run/clinical', headers=auth_header())
    status = client.get('/api/v1/spark/status/clinical', headers=auth_header()).get_json()
    result = client.get('/api/v1/spark/clinical', headers=auth_header()).get_json()

    assert status['state'] == 'completed'
    assert result['available'] is False


def test_failed_job_keeps_failed_status_and_log(client, spark_jobs, monkeypatch):
    def fail():
        raise RuntimeError('Mongo no disponible')

    monkeypatch.setattr(
        SparkService,
        '_launch',
        lambda analysis_type: SparkService._execute_clinical(analysis_type),
    )
    monkeypatch.setattr(
        'services.spark_service.AnalyticsService.get_clinical_analytics',
        staticmethod(fail),
    )

    client.post('/api/v1/spark/run/clinical', headers=auth_header())
    status = client.get('/api/v1/spark/status/clinical', headers=auth_header()).get_json()

    assert status['state'] == 'failed'
    assert status['running'] is False
    assert 'Mongo no disponible' in status['log']


def test_invalid_type_returns_bad_request(client, spark_jobs):
    response = client.post('/api/v1/spark/run/no-existe', headers=auth_header())

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Tipo de análisis no válido'


def test_unimplemented_type_returns_bad_request(client, spark_jobs):
    response = client.post('/api/v1/spark/run/met', headers=auth_header())

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Tipo de análisis no implementado en PBL-03'


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


def test_overview_reports_clinical_availability(client, spark_jobs, monkeypatch):
    monkeypatch.setattr(
        SparkService,
        '_launch',
        lambda analysis_type: SparkService._execute_clinical(analysis_type),
    )
    monkeypatch.setattr(
        'services.spark_service.AnalyticsService.get_clinical_analytics',
        staticmethod(lambda: CLINICAL_RESULT),
    )
    client.post('/api/v1/spark/run/clinical', headers=auth_header())

    response = client.get('/api/v1/spark/overview', headers=auth_header('administrativo'))
    body = response.get_json()

    assert response.status_code == 200
    assert body['clinical']['available'] is True
    assert body['clinical']['state'] == 'completed'
    assert body['met']['available'] is False
