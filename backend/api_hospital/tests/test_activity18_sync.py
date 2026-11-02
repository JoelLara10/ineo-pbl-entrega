import pytest

URL = '/api/v1/appointments/1/nursing-notes'


def login(client, role='enfermeria'):
    result = client.post('/api/v1/auth/login', json={
        'username': role + '.test', 'password': 'Prueba-Sprint7!'
    })
    assert result.status_code == 200
    return {'Authorization': 'Bearer ' + result.get_json()['token']}


def test_query_create_query_persists(client, isolated_database):
    headers = login(client)
    before = client.get(URL, headers=headers)
    assert before.status_code == 200
    saved = client.post(URL, headers=headers, json={'nota_enfermeria': '  A18 registro sintético  '})
    assert saved.status_code == 201
    note_id = saved.get_json()['id_nota']
    records = client.get(URL, headers=headers).get_json()
    assert len(records) == len(before.get_json()) + 1
    assert any(n['id_nota'] == note_id and n['nota'] == 'A18 registro sintético' for n in records)
    assert isolated_database.nursing_notes.find_one({'id_nota': note_id})['id_atencion'] == 1


@pytest.mark.parametrize('payload', [{}, {'nota_enfermeria': ''}, {'nota_enfermeria': '   '},
    {'nota_enfermeria': 5}, {'nota_enfermeria': 'x' * 5001}, [], None])
def test_invalid_input_is_not_saved(client, isolated_database, payload):
    headers = login(client)
    result = client.post(URL, headers=headers, json=payload)
    assert result.status_code == 400
    assert isolated_database.nursing_notes.count_documents({}) == 0


def test_note_length_boundary_and_missing_appointment(client):
    headers = login(client)
    assert client.post(URL, headers=headers, json={'nota_enfermeria': 'x' * 5000}).status_code == 201
    assert client.post(URL.replace('/1/', '/999/'), headers=headers,
        json={'nota_enfermeria': 'Prueba'}).status_code == 404


@pytest.mark.parametrize('method', ['get', 'post'])
def test_protection_and_roles(client, method):
    operation = getattr(client, method)
    assert operation(URL).status_code == 401
    assert operation(URL, headers={'Authorization': 'Bearer invalid'}).status_code == 401
    assert operation(URL, headers=login(client, 'estudios')).status_code == 403


def test_failed_database_response_is_safe(client, monkeypatch):
    headers = login(client)
    def fail():
        raise RuntimeError('password=secret-private-host')
    monkeypatch.setattr('routes.medical.get_db', fail)
    result = client.post(URL, headers=headers, json={'nota_enfermeria': 'Prueba'})
    assert result.status_code == 500
    assert result.get_json() == {'error': 'Error interno del servidor'}
