from datetime import datetime, timedelta, timezone
from bson import BSON
import pytest
from utils.clinical_dates import serialize_clinical_record


def test_mongo_naive_utc_is_serialized_with_offset():
    original = datetime(2026, 10, 29, 18, 30, tzinfo=timezone.utc)
    decoded = BSON.encode({'fecha_registro': original}).decode()
    assert decoded['fecha_registro'].tzinfo is None
    assert serialize_clinical_record(decoded)['fecha_registro'] == '2026-10-29T18:30:00+00:00'


def test_explicit_offset_converts_once_and_calendar_fields_are_unchanged():
    local = datetime(2026, 10, 29, 12, 30, tzinfo=timezone(timedelta(hours=-6)))
    result = serialize_clinical_record({'fecha_registro': local, 'fecnac': '2000-01-01'})
    assert result == {'fecha_registro': '2026-10-29T18:30:00+00:00', 'fecnac': '2000-01-01'}


@pytest.mark.parametrize('endpoint,payload', [
    ('nursing-assessment', dict(estado_general='Estable', dolor='2', movilidad='Independiente',
                              riesgo_caidas='Bajo', riesgo_upp='Bajo', observaciones='QA fechas')),
    ('fluid-balance', dict(ingresos_orales=200, egresos_orina=100, observaciones='QA fechas')),
    ('nursing-care', dict(diagnostico_enfermeria='QA fechas', objetivos='Confort',
                         intervenciones='Vigilancia', evaluacion='Estable', estado='EN_PROCESO')),
])
def test_saved_clinical_history_reports_current_utc_instant(client, endpoint, payload):
    response = client.post('/api/v1/auth/login', json={'username': 'enfermeria.test', 'password': 'Prueba-Sprint7!'})
    headers = {'Authorization': 'Bearer ' + response.json['token']}
    url = '/api/v1/appointments/1/' + endpoint
    before = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert client.post(url, headers=headers, json=payload).status_code == 201
    history = client.get(url, headers=headers)
    assert history.status_code == 200
    stamp = history.json[0]['fecha_registro']
    assert stamp.endswith('+00:00')
    value = datetime.fromisoformat(stamp)
    assert before <= value <= datetime.now(timezone.utc) + timedelta(seconds=1)
