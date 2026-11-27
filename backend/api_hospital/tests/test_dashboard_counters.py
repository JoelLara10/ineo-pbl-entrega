from bson.decimal128 import Decimal128
import pytest

from middleware.auth_middleware import generate_token


def headers():
    return {'Authorization': 'Bearer ' + generate_token(
        '000000000000000000000001', 'admin.test', 'admin')}


def test_dashboard_accepts_decimal_income_and_missing_area(client, isolated_database, monkeypatch):
    db = isolated_database
    db.atencion.delete_many({})
    db.atencion.insert_many([
        {'status': 'ABIERTA', 'area': 'Consulta'},
        {'status': 'ABIERTA'},
        {'status': 'CERRADA', 'area': 'Consulta'},
    ])
    db.camas.delete_many({})
    db.camas.insert_many([{'ocupada': 1}, {'ocupada': 0}])
    monkeypatch.setattr(db.cuenta_paciente, 'aggregate',
                        lambda _pipeline: iter([{'total': Decimal128('1740.50')}]))
    response = client.get('/api/v1/analytics/dashboard', headers=headers())
    assert response.status_code == 200
    assert response.json['active_patients'] == {
        'total': 2, 'by_area': {'Consulta': 1, 'Sin área': 1}}
    assert response.json['bed_occupancy']['occupied'] == 1
    assert response.json['bed_occupancy']['total'] == 2
    assert response.json['today_income'] == 1740.5


def test_dashboard_database_failure_is_safe(client, monkeypatch):
    def unavailable():
        raise RuntimeError('private-database-host token secret')
    monkeypatch.setattr('services.analytics_service.AnalyticsService.get_dashboard_stats', unavailable)
    response = client.get('/api/v1/analytics/dashboard', headers=headers())
    assert response.status_code == 500
    assert response.json == {'error': 'Error interno del servidor'}


@pytest.mark.parametrize('route', ['/analytics/dashboard', '/dashboard'])
def test_dashboard_requires_authentication(client, route):
    assert client.get('/api/v1' + route).status_code == 401
