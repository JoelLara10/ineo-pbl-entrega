"""Scopes, comparisons and human interpretation use isolated synthetic records."""
from datetime import datetime
from unittest.mock import Mock
import pytest
from middleware.auth_middleware import generate_token
from services import spark_service as service
from services.analysis_filters import normalize_filters, previous_filters
from services.analysis_lightweight import analyze
from services.analysis_dashboard import build_dashboard


def headers(role='admin', user_id='000000000000000000000001'):
    return {'Authorization': 'Bearer ' + generate_token(user_id, 'test', role)}


def run_inline(monkeypatch, kind, filters=None):
    monkeypatch.setattr(service.EXECUTOR, 'submit', lambda *_: None)
    monkeypatch.setattr(service, 'run_engine', analyze)
    state, _ = service.start(kind, filters)
    service.execute(kind, state['job_id'])
    assert service.read_job(kind)['state'] == 'completed'
    return service.results(kind)


@pytest.mark.parametrize('payload', [[], {'start_date': False, 'end_date': False}, {'start_date': '2026-01-01'},
    {'start_date': '2026-02-30', 'end_date': '2026-03-01'}, {'start_date': '2026-02-02', 'end_date': '2026-01-01'},
    {'start_date': '2000-01-01', 'end_date': '2026-01-01'}, {'area': {'$ne': ''}}, {'compare_previous': 'true'},
    {'compare_previous': True}, {'command': 'x'}])
def test_bad_filters_rejected_before_start(client, payload):
    assert client.post('/api/v1/spark/run/analytics', headers=headers(), json=payload).status_code == 400
    assert service.read_job('analytics') is None


def test_inclusive_dates_and_area_apply_to_both_engines(isolated_database):
    isolated_database.atencion.delete_many({})
    isolated_database.atencion.insert_many([
        {'id_atencion': 1, 'area': 'CONSULTA', 'status': 'ABIERTA', 'fecha_ing': datetime(2026, 10, 1)},
        {'id_atencion': 2, 'area': 'CONSULTA', 'status': 'CERRADA', 'fecha_ing': '2026-10-02T23:59:59Z'},
        {'id_atencion': 3, 'area': 'RECUPERACION', 'fecha_ing': datetime(2026, 10, 2)},
        {'id_atencion': 4, 'area': 'CONSULTA', 'fecha_ing': '2026-10-02T23:30:00-06:00'},
        {'id_atencion': 5, 'area': 'CONSULTA', 'fecha_ing': 'invalid'},
    ])
    isolated_database.signos_vitales.delete_many({})
    isolated_database.signos_vitales.insert_many([
        {'id_atencion': 1, 'fecha_registro': '2026-10-02T23:59:00Z', 'fc': 80.},
        {'id_atencion': 3, 'fecha_registro': '2026-10-02', 'fc': 120.},
        {'id_atencion': 2, 'fecha_registro': '2026-10-03', 'fc': 90.},
    ])
    filters = normalize_filters({'start_date': '2026-10-01', 'end_date': '2026-10-02', 'area': 'CONSULTA'}, 'analytics')
    rows, metadata = service.collect_source('analytics', True, filters)
    assert [row['status'] for row in rows] == ['ABIERTA', 'CERRADA']
    assert metadata['period'] == {'start': '2026-10-01', 'end': '2026-10-02'}
    assert metadata['excluded_undated_rows'] == 1
    clinical = service.collect_source('clinical', filters=filters)
    assert len(clinical) == 1 and clinical[0]['fc'] == 80.
    assert not any('id_atencion' in row for row in clinical)


def test_previous_period_is_same_length_including_leap_day():
    previous = previous_filters({'start_date': '2024-03-01', 'end_date': '2024-03-31', 'area': 'CONSULTA', 'compare_previous': True})
    assert previous == {'start_date': '2024-01-30', 'end_date': '2024-02-29', 'area': 'CONSULTA'}


def test_comparison_does_not_invent_percentage_from_zero_baseline(monkeypatch):
    result = run_inline(monkeypatch, 'analytics', {'start_date': '2026-01-01', 'end_date': '2026-01-08', 'compare_previous': True})
    assert result['comparison']['current'] == 8
    assert result['comparison']['previous'] == 0
    assert result['comparison']['change_percent'] is None
    assert result['metadata']['filters']['compare_previous'] is True


def test_comparison_known_counts_and_empty_calendar_days(monkeypatch):
    result = run_inline(monkeypatch, 'met', {'start_date': '2026-01-05', 'end_date': '2026-01-10', 'compare_previous': True})
    assert result['comparison']['current'] == 4 and result['comparison']['previous'] == 4
    assert result['comparison']['change_percent'] == 0
    daily = next(chart for chart in result['dashboard']['charts'] if chart['key'] == 'daily')
    assert len(daily['rows']) == 6
    assert daily['rows'][-1] == {'label': '2026-01-10', 'value': 0}
    average = next(row for row in result['dashboard']['kpis'] if row['key'] == 'calendarAverage')
    assert average['value'] == 4 / 6


def test_running_job_with_different_filters_is_a_conflict(client, monkeypatch):
    monkeypatch.setattr(service.EXECUTOR, 'submit', lambda *_: None)
    service.start('clinical', {'area': 'CONSULTA'})
    assert client.post('/api/v1/spark/run/clinical', headers=headers(), json={'area': 'RECUPERACION'}).status_code == 409
    assert client.post('/api/v1/spark/run/clinical', headers=headers(), json={'area': 'CONSULTA'}).status_code == 200


def test_group_reference_is_weighted_by_observation_count():
    result = {'clusters': [{'cluster': 0, 'count': 1, 'means': {'fc': 60.}}, {'cluster': 1, 'count': 3, 'means': {'fc': 100.}}]}
    dashboard = build_dashboard('unsupervised', [], result)
    chart = next(row for row in dashboard['charts'] if row['key'] == 'profile_fc')
    assert chart['reference_value'] == 90
    missing = next(row for row in dashboard['charts'] if row['key'] == 'profile_temp')
    assert 'reference_value' not in missing


def review_payload(timestamp):
    return {'result_timestamp': timestamp, 'interpretation': 'En este periodo se registraron ocho atenciones.',
            'decision': 'Revisar la programación de recursos en las áreas con más carga.', 'clarity': 'clear', 'notes': 'Etiquetas comprensibles.'}


def test_review_saved_against_snapshot_with_actual_reference_evidence(client, monkeypatch, isolated_database):
    result = run_inline(monkeypatch, 'analytics', {'start_date': '2026-01-01', 'end_date': '2026-01-08', 'compare_previous': True})
    payload = review_payload(result['timestamp'])
    response = client.post('/api/v1/spark/reviews/analytics', headers=headers(), json=payload)
    assert response.status_code == 200
    doc = isolated_database.analysis_reviews.find_one({})
    assert doc['evidence']['comparison']['current'] == 8
    assert doc['evidence']['period'] == {'start': '2026-01-01', 'end': '2026-01-08'}
    assert doc['clarity'] == 'clear'
    assert client.post('/api/v1/spark/reviews/analytics', headers=headers(), json=payload).status_code == 200
    assert isolated_database.analysis_reviews.count_documents({}) == 1
    saved = client.get('/api/v1/spark/reviews/analytics', headers=headers(), query_string={'result_timestamp': result['timestamp']})
    assert saved.json['review']['decision'] == payload['decision']
    isolated_database.spark_jobs.update_one({'_id': 'analytics'}, {'$set': {'result.timestamp': 'newer-result'}})
    assert client.post('/api/v1/spark/reviews/analytics', headers=headers(), json=payload).status_code == 409


@pytest.mark.parametrize('role,code', [(None, 401), ('medico', 403), ('enfermeria', 403), ('estudios', 403)])
@pytest.mark.parametrize('path,method', [('options', 'get'), ('reviews/analytics', 'get'), ('reviews/analytics', 'post')])
def test_filter_options_and_reviews_require_administration(client, role, code, path, method):
    response = getattr(client, method)('/api/v1/spark/' + path, headers=headers(role) if role else {})
    assert response.status_code == code


def test_administrative_reviews_are_personal(client, monkeypatch, isolated_database):
    from bson import ObjectId
    isolated_database.users.insert_one({'_id': ObjectId('000000000000000000000099'), 'role': 'administrativo', 'activo': True})
    result = run_inline(monkeypatch, 'analytics')
    other = headers('administrativo', '000000000000000000000099')
    assert client.post('/api/v1/spark/reviews/analytics', headers=other, json=review_payload(result['timestamp'])).status_code == 200
    assert client.get('/api/v1/spark/reviews/analytics', headers=headers(), query_string={'result_timestamp': result['timestamp']}).json['review'] is None


def test_empty_selected_operational_period_is_a_known_zero(monkeypatch):
    result = run_inline(monkeypatch, 'met', {'start_date': '2027-01-01', 'end_date': '2027-01-03'})
    assert result['available'] and result['summary']['total'] == 0
    daily = next(row for row in result['dashboard']['charts'] if row['key'] == 'daily')
    assert [row['value'] for row in daily['rows']] == [0, 0, 0]
    from tests.test_spark_contract import validate
    validate('spark_result', result)


@pytest.mark.parametrize('patch', [{'clarity': 'excellent'}, {'decision': 'x'}, {'interpretation': ' ' * 30}, {'notes': 'x' * 1001}, {'user_id': 'someone-else'}])
def test_review_requires_a_real_qualitative_assessment(client, monkeypatch, patch):
    result = run_inline(monkeypatch, 'analytics')
    payload = {**review_payload(result['timestamp']), **patch}
    assert client.post('/api/v1/spark/reviews/analytics', headers=headers(), json=payload).status_code == 400
