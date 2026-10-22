"""Technical prerequisites for CP-UAT-001/002; never a human acceptance signature."""
import pytest
from services import spark_service as service
from services.analysis_lightweight import analyze


def login(client, role):
    response = client.post('/api/v1/auth/login', json={
        'username': role + '.test', 'password': 'Prueba-Sprint7!',
    })
    assert response.status_code == 200
    return {'Authorization': 'Bearer ' + response.json['token']}


def test_cp_uat_001_save_and_read_synthetic_assessment(client, isolated_database):
    headers = login(client, 'enfermeria')
    payload = dict(estado_general='Estable', dolor='2', movilidad='Independiente',
                   riesgo_caidas='Bajo', riesgo_upp='Bajo', observaciones='Caso sintetico UAT')
    url = '/api/v1/appointments/1/nursing-assessment'
    saved = client.post(url, headers=headers, json=payload)
    assert saved.status_code == 201
    history = client.get(url, headers=headers)
    assert history.status_code == 200
    record = next(row for row in history.json if row['id_valoracion'] == saved.json['id_valoracion'])
    assert record['valoracion'] == payload
    assert isolated_database.nursing_assessment.count_documents({'id_atencion': 1}) == 1
    assert client.get('/api/v1/auth/users', headers=headers).status_code == 403
    assert client.get('/api/v1/spark/overview', headers=headers).status_code == 403


def test_cp_uat_001_missing_attention_is_not_saved(client, isolated_database):
    response = client.post('/api/v1/appointments/999/nursing-assessment',
                           headers=login(client, 'enfermeria'), json={'estado_general': 'Estable'})
    assert response.status_code == 404
    assert isolated_database.nursing_assessment.count_documents({}) == 0


@pytest.mark.parametrize('method', ['get', 'post'])
def test_cp_uat_001_session_required(client, method):
    response = getattr(client, method)('/api/v1/appointments/1/nursing-assessment')
    assert response.status_code == 401


def test_cp_uat_001_empty_assessment_must_not_persist(client, isolated_database):
    response = client.post('/api/v1/appointments/1/nursing-assessment',
                           headers=login(client, 'enfermeria'), json={})
    assert response.status_code == 400
    assert isolated_database.nursing_assessment.count_documents({}) == 0


@pytest.mark.parametrize('patch', [
    {'estado_general': '   '}, {'dolor': '11'}, {'dolor': '-1'},
    {'movilidad': []}, {'riesgo_caidas': {'$ne': ''}},
    {'riesgo_upp': None}, {'observaciones': 'x' * 1001},
])
def test_cp_uat_001_invalid_fields_do_not_write_or_allocate_id(client, isolated_database, patch):
    payload = dict(estado_general='Estable', dolor='0', movilidad='Independiente',
                   riesgo_caidas='Bajo', riesgo_upp='Bajo')
    response = client.post('/api/v1/appointments/1/nursing-assessment',
                           headers=login(client, 'enfermeria'), json={**payload, **patch})
    assert response.status_code == 400
    assert isolated_database.nursing_assessment.count_documents({}) == 0
    assert isolated_database.counters.find_one({'_id': 'nursing_assessment_id'}) is None


@pytest.mark.parametrize('pain', ['0', '10', '2.5', 'Sin dolor', 'Dolor leve al movimiento'])
def test_cp_uat_001_accepts_score_or_description_and_trims_fields(client, isolated_database, pain):
    payload = dict(estado_general=' Estable ', dolor=pain, movilidad=' Independiente ',
                   riesgo_caidas=' Bajo ', riesgo_upp=' Bajo ', unexpected='ignored')
    response = client.post('/api/v1/appointments/1/nursing-assessment',
                           headers=login(client, 'enfermeria'), json=payload)
    assert response.status_code == 201
    record = isolated_database.nursing_assessment.find_one({})['valoracion']
    assert record['estado_general'] == 'Estable'
    assert record['dolor'] == pain
    assert record['observaciones'] == ''
    assert 'unexpected' not in record


@pytest.mark.parametrize('kind', ['analytics', 'met', 'clinical', 'unsupervised'])
def test_cp_uat_002_authenticated_known_indicators(client, monkeypatch, isolated_database, kind):
    # The generic seed has undated vital signs. UAT explicitly requires a known period.
    isolated_database.signos_vitales.update_many({}, {'$set': {'fecha_registro': '2026-01-05T12:00:00Z'}})
    headers = login(client, 'admin')
    monkeypatch.setattr(service.EXECUTOR, 'submit', lambda *_: None)
    monkeypatch.setattr(service, 'run_engine', analyze)
    response = client.post('/api/v1/spark/run/' + kind, headers=headers, json={})
    assert response.status_code in (200, 202)
    state = service.read_job(kind)
    service.execute(kind, state['job_id'])
    result = client.get('/api/v1/spark/' + kind, headers=headers)
    assert result.status_code == 200
    assert result.json['available'] is True
    assert result.json['metadata']['period']['start']
    assert result.json['metadata']['period']['end']
    dashboard = result.json['dashboard']
    assert dashboard['kpis']
    assert all(row['unit'] for row in dashboard['kpis'])
    assert all(row['unit'] for row in dashboard['charts'])
