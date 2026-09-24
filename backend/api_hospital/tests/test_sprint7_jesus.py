"""PBL-26-T3: real HTTP cases against isolated, repeatable synthetic data."""
import pytest


@pytest.mark.parametrize('role', ['admin', 'medico', 'enfermeria', 'estudios'])
def test_each_seeded_role_logs_in_and_resolves_its_own_identity(client, isolated_database, role):
    response = client.post('/api/v1/auth/login', json={
        'username': role + '.test', 'password': 'Prueba-Sprint7!',
    })
    assert response.status_code == 200
    token = response.json['token']
    identity = client.get('/api/v1/auth/me', headers={'Authorization': 'Bearer ' + token})
    assert identity.status_code == 200
    assert identity.json['role'] == role
    assert identity.json['username'] == role + '.test'
    assert 'password' not in identity.json
    spark = client.get('/api/v1/spark/overview', headers={'Authorization': 'Bearer ' + token})
    assert spark.status_code == (200 if role == 'admin' else 403)
    assert isolated_database.users.count_documents({}) == 4


@pytest.mark.parametrize('username,password', [
    ('admin.test', 'incorrecta'), ('inexistente.test', 'Prueba-Sprint7!'),
])
def test_bad_credentials_cannot_access_synthetic_data(client, username, password):
    login = client.post('/api/v1/auth/login', json={'username': username, 'password': password})
    assert login.status_code == 401
    assert 'token' not in login.json
    assert client.get('/api/v1/spark/overview').status_code == 401


def test_database_is_restored_for_the_next_test(isolated_database):
    assert isolated_database.users.count_documents({}) == 4
    assert isolated_database.pacientes.count_documents({}) == 8
    assert isolated_database.spark_jobs.count_documents({}) == 0


def test_mutations_do_not_escape_isolated_test(isolated_database):
    isolated_database.users.delete_many({})
    isolated_database.pacientes.delete_many({})
    isolated_database.spark_jobs.insert_one({'_id': 'synthetic-only'})
    assert isolated_database.users.count_documents({}) == 0


def test_image_contract_accepts_synthetic_relative_url_and_rejects_external_url():
    from jsonschema import ValidationError
    from tests.test_spark_contract import validate
    from services.spark_service import empty_result

    result = empty_result()
    validate('spark_result', result)  # Este incremento puede entregar visualizations=[].
    result['visualizations'] = [{
        'filename': 'synthetic.png', 'name': 'Gráfica sintética',
        'url': '/spark/images/synthetic.png',
    }]
    validate('spark_result', result)
    result['visualizations'][0]['url'] = 'https://externo.example/synthetic.png'
    with pytest.raises(ValidationError):
        validate('spark_result', result)
    del result['visualizations'][0]['filename']
    with pytest.raises(ValidationError):
        validate('spark_result', result)
