import pytest
from middleware.auth_middleware import generate_token

PATH = '/api/v1/catalog/services'


def headers(role='admin'):
    return {'Authorization': 'Bearer ' + generate_token('000000000000000000000001', 'admin.test', role)}


def payload(**changes):
    return dict(serv_cve='a15-demo', serv_desc='Consulta sintética', serv_costo=500, tipo=1, **changes)


def test_get_and_post_roundtrip(client):
    auth = headers()
    created = client.post(PATH, headers=auth, json=payload())
    assert created.status_code == 201
    assert created.get_json()['serv_cve'] == 'A15-DEMO'
    listing = client.get(PATH, headers=auth)
    assert listing.status_code == 200
    assert any(x['serv_cve'] == 'A15-DEMO' for x in listing.get_json())


@pytest.mark.parametrize('changes', [dict(serv_cve=' '), dict(serv_desc=''), dict(serv_costo=-1), dict(serv_costo='abc'), dict(serv_costo='Infinity'), dict(tipo=8), dict(iva=101)])
def test_invalid_form(client, changes):
    data = payload()
    data.update(changes)
    assert client.post(PATH, headers=headers(), json=data).status_code == 400


def test_missing_cost_and_malformed_json(client):
    data = payload()
    del data['serv_costo']
    assert client.post(PATH, headers=headers(), json=data).status_code == 400
    assert client.post(PATH, headers=headers(), data='{', content_type='application/json').status_code == 400


def test_zero_cost_is_valid(client):
    data = payload()
    data['serv_costo'] = 0
    assert client.post(PATH, headers=headers(), json=data).status_code == 201


def test_missing_and_invalid_token(client):
    assert client.get(PATH).status_code == 401
    assert client.get(PATH, headers={'Authorization': 'Bearer invalid'}).status_code == 401


def test_non_admin_cannot_create(client, isolated_database):
    from bson import ObjectId
    isolated_database['users'].update_one({'_id': ObjectId('000000000000000000000001')}, {'$set': {'role': 'medico'}})
    assert client.post(PATH, headers=headers('medico'), json=payload()).status_code == 403


def test_duplicate_key(client):
    auth = headers()
    assert client.post(PATH, headers=auth, json=payload()).status_code == 201
    assert client.post(PATH, headers=auth, json=payload()).status_code == 400


@pytest.mark.parametrize('empty', ['', None])
def test_existing_web_form_accepts_empty_optional_prices(client, empty):
    data = payload()
    data.update({f'serv_costo{i}': empty for i in range(2, 9)})
    data['iva'] = empty
    response = client.post(PATH, headers=headers(), json=data)
    assert response.status_code == 201
    assert response.get_json()['serv_costo2'] == 0
    assert response.get_json()['iva'] == .16


def test_negative_optional_price_is_rejected(client):
    data = payload()
    data['serv_costo2'] = -1
    assert client.post(PATH, headers=headers(), json=data).status_code == 400


def test_inactive_service_keeps_selected_state(client):
    data = payload(serv_activo='NO')
    auth = headers()
    created = client.post(PATH, headers=auth, json=data)
    assert created.status_code == 201
    assert created.get_json()['serv_activo'] == 'NO'
    listing = client.get(PATH, headers=auth).get_json()
    assert next(item for item in listing if item['serv_cve'] == 'A15-DEMO')['serv_activo'] == 'NO'


def test_invalid_service_state_is_rejected(client):
    assert client.post(PATH, headers=headers(), json=payload(serv_activo='UNKNOWN')).status_code == 400
