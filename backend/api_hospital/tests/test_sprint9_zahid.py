from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
from unittest.mock import Mock
import json
import pytest
from middleware.auth_middleware import generate_token
from services import spark_service as service


def headers(index=1, role='admin'):
    return {'Authorization': 'Bearer ' + generate_token(f'{index:024x}', 'test', role)}


@pytest.mark.parametrize('kind', service.TYPES)
def test_pbl11_metadata_snapshot(client, isolated_database, monkeypatch, kind):
    collection = isolated_database.signos_vitales if kind in ('clinical', 'unsupervised') else isolated_database.atencion
    field = 'fecha_registro' if kind in ('clinical', 'unsupervised') else 'fecha_ing'
    collection.delete_many({})
    collection.insert_many([
        {field: datetime(2026, 10, 12, 23, tzinfo=timezone(timedelta(hours=-6))), 'fc': 60, 'status': 'ABIERTA'},
        {field: '2026-10-15T10:00:00Z', 'fc': 70, 'status': 'CERRADA'},
        {field: 'invalid', 'fc': 80, 'nombre': 'PRIVATE'},
    ])
    monkeypatch.setattr(service, 'EXECUTOR', Mock())
    monkeypatch.setattr(service, 'run_engine', lambda *_: {**service.empty_result(), 'available': True})
    job, _ = service.start(kind)
    service.execute(kind, job['job_id'])
    response = client.get('/api/v1/spark/' + kind, headers=headers())
    assert response.status_code == 200
    metadata = response.json['metadata']
    assert metadata['period'] == {'start': '2026-10-13', 'end': '2026-10-15'}
    assert metadata['last_updated_at'] == '2026-10-15T10:00:00+00:00'
    assert metadata['generated_at'] == response.json['timestamp']
    assert metadata['undated_rows'] == 1
    assert 'PRIVATE' not in response.text
    assert response.headers['Cache-Control'] == 'no-store'


def test_pbl11_unknown_and_failed_rerun_preserves_metadata(client, isolated_database, monkeypatch):
    monkeypatch.setattr(service, 'EXECUTOR', Mock())
    isolated_database.atencion.delete_many({})
    monkeypatch.setattr(service, 'run_engine', lambda *_: service.empty_result())
    job, _ = service.start('analytics')
    service.execute('analytics', job['job_id'])
    metadata = service.results('analytics')['metadata'].copy()
    assert metadata['period'] == {'start': None, 'end': None}
    assert metadata['last_updated_at'] is None
    monkeypatch.setattr(service, 'run_engine', Mock(side_effect=RuntimeError('private')))
    job, _ = service.start('analytics')
    service.execute('analytics', job['job_id'])
    assert service.results('analytics')['metadata'] == metadata


def test_pbl11_legacy_result_exposes_unknown_source_dates(client, isolated_database):
    old = {**service.empty_result(), 'timestamp': '2026-10-12T10:00:00+00:00', 'available': True}
    del old['metadata']
    isolated_database.spark_jobs.insert_one({'_id': 'analytics', 'state': 'completed', 'result': old})
    response = client.get('/api/v1/spark/analytics', headers=headers())
    assert response.json['metadata']['generated_at'] == old['timestamp']
    assert response.json['metadata']['period'] == {'start': None, 'end': None}
    assert response.json['metadata']['last_updated_at'] is None
    assert 'metadata' not in isolated_database.spark_jobs.find_one({'_id': 'analytics'})['result']


def test_pbl25_preferences_idempotent_and_isolated(client, isolated_database):
    for _ in range(2):
        response = client.put('/api/v1/auth/preferences', json={'language': 'en'}, headers=headers())
        assert response.status_code == 200 and response.json == {'language': 'en'}
    assert isolated_database.user_preferences.count_documents({}) == 1
    assert client.get('/api/v1/auth/preferences', headers=headers()).json == {'language': 'en'}
    assert client.get('/api/v1/auth/preferences', headers=headers(2, 'medico')).json == {'language': 'es'}


@pytest.mark.parametrize('payload', [None, [], {'language': 'fr'}, {'language': 'en', 'patient': 1}, {'language': {'es': 1}}])
def test_pbl25_rejects_non_allowlisted_payloads(client, payload):
    assert client.put('/api/v1/auth/preferences', json=payload, headers=headers()).status_code == 400


def test_pbl25_revoked_or_inactive_accounts_cannot_sync(client, isolated_database):
    assert client.put('/api/v1/auth/preferences', json={'language': 'en'}).status_code == 401
    isolated_database.users.update_one({'username': 'admin.test'}, {'$set': {'activo': False}})
    assert client.put('/api/v1/auth/preferences', json={'language': 'en'}, headers=headers()).status_code == 401
    assert isolated_database.user_preferences.count_documents({}) == 0


def load_traceability():
    path = Path(__file__).parents[3] / 'scripts/traceability.py'
    spec = importlib.util.spec_from_file_location('traceability', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pbl38_gate_requires_results_evidence_approval_and_no_open_defects(tmp_path, monkeypatch):
    module = load_traceability()
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    junit = tmp_path / 'tests.xml'
    junit.write_text('<testsuite><testcase classname="suite" name="PBL11"/></testsuite>')
    story = {'id': 'PBL-11', 'title': '<unsafe>', 'requirements': ['REQ-09'], 'cases': ['PBL11'], 'defects': [], 'approval': {}}
    manifest = {'sprint': 'Sprint 9', 'stories': [story]}
    report = module.build_report(manifest, [junit])
    assert report['stories'][0]['latest_result'] == 'passed'
    assert not report['ready_for_acceptance']
    assert '&lt;unsafe&gt;' in module.render_html(report)
    assert '<unsafe>' not in module.render_html(report)
    (tmp_path / 'approval.md').write_text('Revisado con evidencia de QA.')
    story['approval'] = {'by': 'reviewer', 'at': '2026-10-23', 'evidence': 'approval.md'}
    assert module.build_report(manifest, [junit])['ready_for_acceptance']
    story['defects'] = [{'id': 'DEF-1', 'status': 'open'}]
    assert not module.build_report(manifest, [junit])['ready_for_acceptance']
    story['defects'] = []
    junit.write_text('<testsuite><testcase classname="suite" name="PBL11"><failure/></testcase></testsuite>')
    assert not module.build_report(manifest, [junit])['ready_for_acceptance']
    story['cases'] = ['missing']
    assert module.build_report(manifest, [junit])['stories'][0]['cases'][0]['result'] == 'not_run'


def test_pbl38_latest_failure_wins_and_external_approval_blocked(tmp_path, monkeypatch):
    module = load_traceability()
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    first = tmp_path / 'first.xml'
    second = tmp_path / 'second.xml'
    first.write_text('<testsuite><testcase classname="s" name="PBL11"/></testsuite>')
    second.write_text('<testsuite><testcase classname="s" name="PBL11"><skipped/></testcase></testsuite>')
    results, _ = module.read_results([first, second])
    assert results['s::PBL11']['result'] == 'skipped'
    first.write_text('<!DOCTYPE x [<!ENTITY y "bad">]><testsuite/>')
    with pytest.raises(ValueError):
        module.read_results([first])


def test_pbl09_dated_projection_retains_utc_day_without_identifiers(isolated_database):
    isolated_database.signos_vitales.delete_many({})
    isolated_database.signos_vitales.insert_one({
        'fc': 80, 'temp': 39.5, 'fecha_registro': '2026-10-12T23:30:00-06:00',
        'Id_exp': 99, 'nombre': 'PRIVATE',
    })
    rows, metadata = service.collect_source('clinical', with_metadata=True)
    assert rows == [{'fc': 80., 'fr': None, 'temp': 39.5, 'spo2': None, 'day': '2026-10-13'}]
    assert metadata['period'] == {'start': '2026-10-13', 'end': '2026-10-13'}
    assert 'PRIVATE' not in json.dumps(rows)


def test_pbl38_cli_scope_leaves_other_owners_pending(tmp_path, monkeypatch):
    module = load_traceability()
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    evidence = tmp_path / 'tests.xml'
    evidence.write_text('<testsuite><testcase classname="suite" name="PBL09"/></testsuite>')
    (tmp_path / 'review.md').write_text('Revisión técnica automatizada, no UAT.', encoding='utf-8')
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'sprint':'Sprint 9', 'stories':[
        {'id':'PBL-09','title':'Joel','requirements':['REQ-09'],'cases':['PBL09'],
         'approval':{'by':'Codex','at':'2026-10-20','kind':'technical','evidence':'review.md'}},
        {'id':'PBL-33','title':'Jaime','requirements':['REQ-17'],'cases':['UAT pendiente']}]}))
    import sys
    output = tmp_path / 'scoped'
    args = ['traceability', '--manifest', str(manifest), '--junit', str(evidence), '--output', str(output)]
    monkeypatch.setattr(sys, 'argv', args + ['--story', 'PBL-09', '--strict'])
    module.main()
    assert json.loads(output.with_suffix('.json').read_text())['ready_for_acceptance']
    full = module.build_report(json.loads(manifest.read_text()), [evidence])
    assert not full['ready_for_acceptance']
    assert full['stories'][1]['latest_result'] == 'pending'
    monkeypatch.setattr(sys, 'argv', args + ['--story', 'PBL-unknown'])
    with pytest.raises(SystemExit) as error:
        module.main()
    assert error.value.code == 2
