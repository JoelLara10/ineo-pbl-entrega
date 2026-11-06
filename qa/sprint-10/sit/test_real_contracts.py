"""SIT through real HTTP, database persistence, schema and async worker."""
import json
import os
from datetime import datetime, timezone
import subprocess
import time
import uuid
from pathlib import Path

import pytest
import requests
from pymongo import MongoClient
from jsonschema import Draft202012Validator, FormatChecker

BASE = 'http://127.0.0.1:5029'
SCHEMA = json.loads((Path(__file__).resolve().parents[3] / 'contracts/v1/api.schema.json').read_text())
ROOT = Path(__file__).resolve().parents[3]


def record(case, values):
    out = ROOT / 'evidence/sprint-10/campaign-583-584/sit'
    out.mkdir(parents=True, exist_ok=True)
    (out / (case + '.json')).write_text(json.dumps({
        'case':case, 'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'api':BASE,'database':'ineo_test_s10','data':values,
    },ensure_ascii=False,indent=2,default=str),encoding='utf-8')


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
    username = os.getenv('INEO_QA_USERNAME')
    password = os.getenv('INEO_QA_PASSWORD')
    if not username or not password:
        pytest.skip('BLOCKED: define INEO_QA_USERNAME e INEO_QA_PASSWORD para SIT autenticado')
    response = requests.post(BASE + '/api/v1/auth/login', json={
        'username': username, 'password': password}, timeout=20)
    assert response.status_code == 200
    validate('auth_login', response.json())
    class SessionHeaders(dict):
        def __repr__(self):
            return '<synthetic session headers redacted>'
    return SessionHeaders(Authorization='Bearer ' + response.json()['token'])


def test_cp_s10_sit_01_patient_persistence(db, auth):
    suffix = uuid.uuid4().hex[:8].upper()
    payload = {'curp': 'SINT' + suffix, 'papell': 'PRUEBA',
               'nom_pac': 'PACIENTE SINTETICO', 'fecnac': '2000-01-01'}
    response = requests.post(BASE + '/api/v1/patients', json=payload, headers=auth, timeout=20)
    assert response.status_code == 201, response.text
    patient = response.json()['rawPatient']
    identifier = patient.get('Id_exp') or patient.get('id_exp') or patient.get('id')
    assert identifier
    fetched = requests.get(BASE + '/api/v1/patients/' + str(identifier), headers=auth, timeout=20)
    assert fetched.status_code == 200
    stored = db.pacientes.find_one({'Id_exp': int(identifier)})
    assert stored is not None
    for key in ('curp', 'papell', 'nom_pac'):
        assert fetched.json()['rawPatient'][key] == stored[key] == payload[key]
    record('CP-S10-SIT-01', {'create_status':response.status_code,'read_status':fetched.status_code,
           'identifier':identifier,'expected':payload,'persisted':{k:stored[k] for k in payload if k!='fecnac'},
           'api_record':fetched.json()['rawPatient']})
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
    stored_assessment = db.nursing_assessment.find_one({'id_valoracion': valid.json()['id_valoracion']})
    assert stored_assessment['valoracion'] == payload
    record('CP-S10-SIT-02', {'invalid_status':invalid.status_code,'valid_status':valid.status_code,
        'before':before,'after_invalid':before,'after_valid':before+1,'persisted':stored_assessment['valoracion']})


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
    record('CP-S10-SIT-03', {'states_observed':states,'duration_seconds':time.monotonic()-started,
        'expected_total':expected,'actual_total':result.json()['summary']['total'],
        'engine':'lightweight','result':result.json()})


def test_cp_s10_sit_04_cors_and_credentials(auth):
    url = BASE + '/api/v1/patients'
    observations=[]
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
        observations.append({'origin':origin,'preflight_status':preflight.status_code,
            'allow_origin':preflight.headers.get('Access-Control-Allow-Origin'),
            'allow_credentials':preflight.headers.get('Access-Control-Allow-Credentials'),
            'actual_status':actual.status_code})
    denied = requests.get(url, timeout=20)
    assert denied.status_code == 401
    validate('error', denied.json())
    record('CP-S10-SIT-04', {'origins':observations,'without_session':denied.status_code})
