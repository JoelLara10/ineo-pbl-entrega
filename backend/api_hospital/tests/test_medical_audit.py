import pytest
from middleware.auth_middleware import generate_token

HEADERS = {'Authorization': 'Bearer ' + generate_token('000000000000000000000002', 'qa.medico', 'medico')}
CASES = [
    ('/historia-clinica/1/1', 'historia_clinica', {'motivo_consulta': 'PRUEBA SINTETICA'}),
    ('/appointments/1/medical-notes', 'notas_medicas', {'subjetivo': 'PRUEBA SINTETICA'}),
    ('/appointments/1/diagnosis', 'diagnosticos', {'diagnostico_principal': 'PRUEBA SINTETICA'}),
    ('/appointments/1/prescriptions', 'recetas', {'medicamentos': [{'medicamento': 'QA SIN USO CLINICO', 'dosis': 'QA', 'frecuencia': 'QA', 'duracion': 'QA'}]}),
    ('/exams/request', 'examenes', {'id_atencion': 1, 'exams': [1], 'type': 'LABORATORIO'}),
]

@pytest.mark.parametrize('url,collection,payload', CASES)
def test_empty_payload_never_writes(client, isolated_database, url, collection, payload):
    before = list(isolated_database[collection].find())
    counters = list(isolated_database.counters.find())
    assert client.post('/api/v1' + url, headers=HEADERS, json={}).status_code == 400
    assert list(isolated_database[collection].find()) == before
    assert list(isolated_database.counters.find()) == counters

@pytest.mark.parametrize('url,collection,payload', CASES)
@pytest.mark.parametrize('attention,status', [(2, 409), (99999, 404)])
def test_closed_or_missing_attention(client, isolated_database, url, collection, payload, attention, status):
    url = url.replace('/1/', f'/{attention}/')
    if url.startswith('/historia-clinica/'):
        url = f'/historia-clinica/{attention}/{attention}'
    if url == '/exams/request':
        payload = {**payload, 'id_atencion': attention}
    before = list(isolated_database[collection].find())
    assert client.post('/api/v1' + url, headers=HEADERS, json=payload).status_code == status
    assert list(isolated_database[collection].find()) == before

@pytest.mark.parametrize('url,collection,payload', CASES[:4])
def test_valid_write_read(client, isolated_database, url, collection, payload):
    assert client.post('/api/v1' + url, headers=HEADERS, json=payload).status_code in (200, 201)
    assert client.get('/api/v1' + url, headers=HEADERS).status_code == 200

def test_history_does_not_cross_patient(client, isolated_database):
    assert client.post('/api/v1/historia-clinica/1/999', headers=HEADERS, json={'motivo_consulta': 'QA PRUEBA'}).status_code == 404

@pytest.mark.parametrize('payload', [None, [], 'texto', {'medicamentos': [{}]}, {'medicamentos': [{'medicamento': 'QA'}]}])
def test_malformed_prescription(client, payload):
    assert client.post('/api/v1/appointments/1/prescriptions', headers=HEADERS, json=payload).status_code == 400

@pytest.mark.parametrize('exams', [[], [99999], [1, 1], ['1x']])
def test_invalid_exam_never_creates_header_or_details(client, isolated_database, exams):
    before = [list(isolated_database[name].find()) for name in ('examenes', 'examenes_det', 'counters')]
    response = client.post('/api/v1/exams/request', headers=HEADERS, json={'id_atencion': 1, 'exams': exams, 'type': 'LABORATORIO'})
    assert response.status_code == 400
    assert [list(isolated_database[name].find()) for name in ('examenes', 'examenes_det', 'counters')] == before

@pytest.mark.parametrize('url,collection,payload', CASES)
def test_auth_and_role_guards(client, isolated_database, url, collection, payload):
    before = isolated_database[collection].count_documents({})
    assert client.post('/api/v1' + url, json=payload).status_code == 401
    denied = {'Authorization': 'Bearer ' + generate_token('000000000000000000000004', 'qa.estudios', 'estudios')}
    assert client.post('/api/v1' + url, headers=denied, json=payload).status_code == 403
    assert isolated_database[collection].count_documents({}) == before

@pytest.mark.parametrize('kind', ['LABORATORIO', 'GABINETE'])
def test_valid_exam_has_exact_requested_details(client, isolated_database, kind):
    isolated_database.catalogo_examenes.insert_one({'id_catalogo': 2, 'nombre': 'QA SIN USO CLINICO', 'tipo': kind, 'precio': 1})
    response = client.post('/api/v1/exams/request', headers=HEADERS, json={'id_atencion': 1, 'exams': [2], 'type': kind})
    assert response.status_code == 201
    record = isolated_database.examenes.find_one({'id_examen': response.json['id_examen']})
    details = list(isolated_database.examenes_det.find({'id_examen': response.json['id_examen'], 'id_catalogo': 2}))
    assert record['id_atencion'] == 1 and record['tipo'] == kind
    assert len(details) == 1 and details[0]['tipo'] == kind

def test_medical_note_uses_explicit_utc_timestamp(client):
    result = client.post('/api/v1/appointments/1/medical-notes', headers=HEADERS, json={'subjetivo': 'QA SINTETICO'})
    assert result.status_code == 201
    assert result.json['fecha_registro'].endswith('+00:00')

def test_database_error_does_not_expose_internal_details(client, monkeypatch):
    def offline(*args, **kwargs):
        raise RuntimeError('private password mongodb')
    monkeypatch.setattr('services.medical_service.get_collection', offline)
    response = client.get('/api/v1/appointments/1/medical-notes', headers=HEADERS)
    assert response.status_code == 500
    assert response.json == {'error': 'Error interno del servidor'}
