import pytest
from middleware.auth_middleware import generate_token

CASES = [
    ('vital-signs', 'signos_vitales', {'ta': '120/80', 'fc': 72, 'temp': 36.5, 'spo2': 98.5}),
    ('nursing-notes', 'nursing_notes', {'nota_enfermeria': 'REGISTRO SINTETICO QA'}),
    ('medications', 'medications', {'medicamentos': [{'nombre': 'PRUEBA SIN USO CLINICO', 'dosis': 'PRUEBA',
      'frecuencia': 'PRUEBA', 'via': 'PRUEBA', 'fecha_aplicacion': '13/11/2026'}]}),
    ('nursing-assessment', 'nursing_assessment', {'estado_general': 'PRUEBA', 'dolor': '2',
      'movilidad': 'PRUEBA', 'riesgo_caidas': 'PRUEBA', 'riesgo_upp': 'PRUEBA'}),
    ('fluid-balance', 'fluid_balance', {'ingresos_orales': 200, 'egresos_orina': 100}),
    ('nursing-care', 'nursing_care', {'diagnostico_enfermeria': 'PRUEBA', 'objetivos': 'PRUEBA',
      'intervenciones': 'PRUEBA', 'estado': 'EN_PROCESO'}),
]


def headers(role='enfermero'):
    return {'Authorization': 'Bearer ' + generate_token('000000000000000000000004' if role == 'estudios' else '000000000000000000000003', 'qa.test', role)}


@pytest.mark.parametrize('endpoint,collection,payload', CASES)
def test_nursing_write_then_read_persists(client, isolated_database, endpoint, collection, payload):
    url = '/api/v1/appointments/1/' + endpoint
    before = isolated_database[collection].count_documents({})
    response = client.post(url, headers=headers(), json=payload)
    assert response.status_code == 201
    assert isolated_database[collection].count_documents({}) == before + 1
    history = client.get(url, headers=headers())
    assert history.status_code == 200
    assert isinstance(history.json, list) and len(history.json) >= 1
    if endpoint == 'vital-signs':
        assert history.json[0]['spo2'] == 98.5
        assert history.json[0]['fecha_registro'].endswith('+00:00')
    if endpoint == 'fluid-balance':
        assert history.json[0]['balance_neto'] == 100


@pytest.mark.parametrize('endpoint,collection,payload', CASES)
@pytest.mark.parametrize('attention,status', [(2, 409), (99999, 404)])
def test_closed_or_missing_attention_never_writes(client, isolated_database, endpoint, collection, payload, attention, status):
    before = isolated_database[collection].count_documents({})
    counters = list(isolated_database.counters.find())
    response = client.post(f'/api/v1/appointments/{attention}/{endpoint}', headers=headers(), json=payload)
    assert response.status_code == status
    assert isolated_database[collection].count_documents({}) == before
    assert list(isolated_database.counters.find()) == counters


@pytest.mark.parametrize('endpoint,payload', [
    ('vital-signs', {}), ('vital-signs', {'fc': '72abc'}), ('vital-signs', {'fc': True}),
    ('vital-signs', {'temp': 'Infinity'}), ('vital-signs', {'spo2': 101}),
    ('vital-signs', {'ta': 'texto'}), ('vital-signs', {'fc': 72.5}),
    ('medications', {}), ('medications', {'medicamentos': []}),
    ('medications', {'medicamentos': [{'nombre': 'SOLO NOMBRE'}]}),
    ('fluid-balance', {}), ('fluid-balance', {'ingresos_orales': -1}),
    ('fluid-balance', {'ingresos_iv': 'NaN'}), ('fluid-balance', {'ingresos_iv': True}),
    ('nursing-assessment', {'estado_general': 'INCOMPLETO'}),
    ('nursing-notes', {'nota_enfermeria': '  '}),
    ('nursing-care', {'diagnostico_enfermeria': 'INCOMPLETO'}),
])
def test_invalid_nursing_data_is_rejected_before_writing(client, isolated_database, endpoint, payload):
    collection = next(name for route, name, _data in CASES if route == endpoint)
    before = isolated_database[collection].count_documents({})
    response = client.post('/api/v1/appointments/1/' + endpoint, headers=headers(), json=payload)
    assert response.status_code == 400
    assert isolated_database[collection].count_documents({}) == before


@pytest.mark.parametrize('endpoint,collection,payload', CASES)
def test_authentication_and_write_roles(client, endpoint, collection, payload):
    url = '/api/v1/appointments/1/' + endpoint
    assert client.get(url).status_code == 401
    assert client.post(url, json=payload).status_code == 401
    assert client.post(url, headers=headers('estudios'), json=payload).status_code == 403


@pytest.mark.parametrize('endpoint,collection,payload', CASES)
def test_nursing_database_failure_has_safe_error(client, monkeypatch, endpoint, collection, payload):
    def offline():
        raise RuntimeError('private mongodb token password')
    monkeypatch.setattr('routes.medical.get_db', offline)
    result = client.post('/api/v1/appointments/1/' + endpoint, headers=headers(), json=payload)
    assert result.status_code == 500
    assert result.json == {'error': 'Error interno del servidor'}
