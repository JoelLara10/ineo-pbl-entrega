"""SIT through real HTTP, database persistence, schema and async worker."""
import json
import time
import uuid
from pathlib import Path

import pytest
import requests
from pymongo import MongoClient
from jsonschema import Draft202012Validator, FormatChecker

BASE = 'http://127.0.0.1:5029'
SCHEMA = json.loads((Path(__file__).resolve().parents[3] / 'contracts/v1/api.schema.json').read_text())


def validate(name, value):
    Draft202012Validator({**SCHEMA, '$ref': '#/$defs/' + name},
                        format_checker=FormatChecker()).validate(value)


@pytest.fixture(scope='module')
def db():
    with MongoClient('mongodb://127.0.0.1:27029/', serverSelectionTimeoutMS=5000) as mongo:
        mongo.admin.command('ping')
        yield mongo['ineo_test_s10']


@pytest.fixture(scope='module')
def auth():
    response = requests.post(BASE + '/api/v1/auth/login', json={
        'username': 'admin.test', 'password': 'Prueba-Sprint7!'}, timeout=20)
    assert response.status_code == 200
    validate('auth_login', response.json())
    return {'Authorization': 'Bearer ' + response.json()['token']}


def test_cp_s10_sit_01_patient_persistence(db, auth):
    suffix = uuid.uuid4().hex[:8].upper()
    payload = {'curp': 'SINT' + suffix, 'papell': 'PRUEBA',
               'nom_pac': 'PACIENTE SINTETICO', 'fecnac': '2000-01-01'}
    response = requests.post(BASE + '/api/v1/patients', json=payload, headers=auth, timeout=20)
    assert response.status_code == 201, response.text
    patient = response.json()
    identifier = patient.get('Id_exp') or patient.get('id_exp') or patient.get('id')
    assert identifier
    fetched = requests.get(BASE + '/api/v1/patients/' + str(identifier), headers=auth, timeout=20)
    assert fetched.status_code == 200
    stored = db.pacientes.find_one({'Id_exp': int(identifier)})
    assert stored is not None
    for key in ('curp', 'papell', 'nom_pac'):
        assert fetched.json()[key] == stored[key] == payload[key]
    # The browser consumer is exercised separately against this same real server.


def test_cp_s10_sit_02_assessment_contract(db, auth):
    url = BASE + '/api/v1/appointments/1/nursing-assessment'
    before = db.nursing_assessment.count_documents({})
    invalid = requests.post(url, json={}, headers=auth, timeout=20)
    assert invalid.status_code == 400
    validate('error', invalid.json())
    assert db.nursing_assessment.count_documents({}) == before
    payload = dict(estado_general='Estable', dolor='2', movilidad='Independiente',
                   riesgo_caidas='Bajo', riesgo_upp='Bajo', observaciones='Fixture sintético SIT')
    valid = requests.post(url, json=payload, headers=auth, timeout=20)
    assert valid.status_code == 201, valid.text
    assert db.nursing_assessment.count_documents({}) == before + 1
    record = db.nursing_assessment.find_one({'id_valoracion': valid.json()['id_valoracion']})
    assert record['valoracion'] == payload


def test_cp_s10_sit_03_spark_worker_and_result(db, auth):
    db.spark_jobs.delete_many({'_id': 'analytics'})
    expected = db.atencion.count_documents({})
    started = time.monotonic()
    run = requests.post(BASE + '/api/v1/spark/run/analytics', headers=auth, timeout=20)
    assert run.status_code == 202, run.text
    validate('spark_run', run.json())
    states = [run.json()['status']['state']]
    while time.monotonic() - started < 120:
        status = requests.get(BASE + '/api/v1/spark/status/analytics', headers=auth, timeout=20)
        assert status.status_code == 200
        value = status.json()
        validate('spark_status', value)
        states.append(value['state'])
        if value['state'] in ('completed', 'failed'):
            break
        time.sleep(.25)
    assert states[-1] == 'completed', states
    assert all(state in ('pending', 'running', 'completed') for state in states)
    result = requests.get(BASE + '/api/v1/spark/analytics', headers=auth, timeout=20)
    assert result.status_code == 200
    validate('spark_result', result.json())
    assert result.json()['summary']['total'] == expected
    job = db.spark_jobs.find_one({'_id': 'analytics'})
    assert job['state'] == 'completed'
    assert job['result']['summary']['total'] == expected


def test_cp_s10_sit_04_cors_and_credentials(auth):
    url = BASE + '/api/v1/patients'
    for origin, allowed in [('http://localhost:5173', True), ('https://untrusted.invalid', False)]:
        preflight = requests.options(url, headers={'Origin': origin,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization'}, timeout=20)
        assert preflight.status_code == 200
        assert preflight.headers.get('Access-Control-Allow-Origin') == (origin if allowed else None)
        assert preflight.headers.get('Access-Control-Allow-Credentials') != 'true'
        actual = requests.get(url, headers={**auth, 'Origin': origin}, timeout=20)
        assert actual.status_code == 200
        assert actual.headers.get('Access-Control-Allow-Origin') == (origin if allowed else None)
    denied = requests.get(url, timeout=20)
    assert denied.status_code == 401
    validate('error', denied.json())
