"""PBL-30: provider contracts and deliberate incompatible mutations."""
from copy import deepcopy

import pytest
from jsonschema import ValidationError

from tests.test_spark_contract import CONTRACT, validate


@pytest.fixture
def session_headers(client):
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin.test', 'password': 'Prueba-Sprint7!'})
    assert response.status_code == 200
    validate('auth_login', response.json)
    return {'Authorization': 'Bearer ' + response.json['token']}


@pytest.mark.parametrize('path,schema', [
    ('/patients', 'patients'), ('/studies/counts', 'studies_counts'),
    ('/analytics/dashboard', 'analytics'), ('/spark/overview', 'spark_overview'),
])
def test_authenticated_provider_and_breaking_mutations(client, session_headers, path, schema):
    response = client.get('/api/v1' + path, headers=session_headers)
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    validate(schema, response.json)
    # Guard against vacuous schemas: removing each required field must fail.
    for field in CONTRACT['$defs'][schema]['required']:
        incompatible = deepcopy(response.json)
        del incompatible[field]
        with pytest.raises(ValidationError):
            validate(schema, incompatible)
    with pytest.raises(ValidationError):
        validate(schema, [])


@pytest.mark.parametrize('path,schema', [
    ('/patients', 'error'), ('/studies/counts', 'error'),
    ('/analytics/dashboard', 'error'), ('/spark/overview', 'spark_error'),
])
@pytest.mark.parametrize('authorization', [None, 'Bearer invalid'])
def test_unauthorized_contract(client, path, schema, authorization):
    response = client.get('/api/v1' + path,
                          headers={'Authorization': authorization} if authorization else {})
    assert response.status_code == 401
    validate(schema, response.json)


@pytest.mark.parametrize('payload,code', [({}, 400),
    ({'username': 'nobody.test', 'password': 'invalid'}, 401)])
def test_login_negative_contract(client, payload, code):
    response = client.post('/api/v1/auth/login', json=payload)
    assert response.status_code == code
    validate('error', response.json)


def test_login_contract_rejects_token_type_change(client):
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin.test', 'password': 'Prueba-Sprint7!'})
    assert response.status_code == 200
    validate('auth_login', response.json)
    with pytest.raises(ValidationError):
        validate('auth_login', {**response.json, 'token': 123})
