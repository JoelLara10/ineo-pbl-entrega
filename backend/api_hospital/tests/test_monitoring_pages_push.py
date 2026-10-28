from datetime import timedelta
import pytest
from tests.test_monitoring import headers, device
from services import monitoring_service as service
from services import monitoring_push as push

TOKEN = 'ExpoPushToken[synthetic_test_token_12345]'


def test_patient_pages_and_search(client, isolated_database):
    isolated_database.pacientes.insert_many([{'Id_exp': i, 'nom_pac': 'Paging', 'papell': str(i)} for i in range(1000, 1025)])
    first = client.get('/api/v1/monitoring/patients?page=1&page_size=10&q=Paging', headers=headers()).json
    second = client.get('/api/v1/monitoring/patients?page=2&page_size=10&q=Paging', headers=headers()).json
    assert first['pagination'] == {'page': 1, 'page_size': 10, 'total': 25, 'total_pages': 3}
    assert len(first['data']) == len(second['data']) == 10
    assert not {p['patient_id'] for p in first['data']} & {p['patient_id'] for p in second['data']}
    assert client.get('/api/v1/monitoring/patients?page=1&q=OFTALCORE-001010', headers=headers()).json['data'][0]['patient_id'] == 1010
    for query in ['page=0', 'page=-1', 'page=abc', 'page=1&page_size=51']:
        assert client.get('/api/v1/monitoring/patients?' + query, headers=headers()).status_code == 400


def test_history_pages_use_a_stable_snapshot_and_no_other_patient(client, isolated_database):
    stamp = service.now() - timedelta(minutes=5)
    isolated_database.monitoring_measurements.insert_many([
        {'patient_id': 1, 'device_id': 'D', 'timestamp': stamp + timedelta(seconds=i), 'heart_rate': 70 + i} for i in range(25)])
    isolated_database.monitoring_measurements.insert_one({'patient_id': 2, 'timestamp': stamp, 'heart_rate': 999})
    first = client.get('/api/v1/monitoring/patients/1?history_page=1&page_size=10', headers=headers()).json['data']
    before = first['history_pagination']['as_of']
    isolated_database.monitoring_measurements.insert_one({'patient_id': 1, 'timestamp': service.now() + timedelta(seconds=1), 'heart_rate': 123})
    second = client.get('/api/v1/monitoring/patients/1', query_string={'history_page': 2, 'page_size': 10, 'history_before': before}, headers=headers()).json['data']
    assert first['history_pagination']['total'] == second['history_pagination']['total'] == 25
    assert len(second['history']) == 10
    assert not {x['id'] for x in first['history']} & {x['id'] for x in second['history']}
    assert all(x['patient_id'] == 1 for x in second['history'])
    assert client.get('/api/v1/monitoring/patients/1?history_page=1&history_before=bad', headers=headers()).status_code == 400


def test_batched_list_has_latest_and_full_pending_count(client, isolated_database):
    device(client)
    stamp = service.now()
    isolated_database.monitoring_measurements.insert_many([{'patient_id': 1, 'timestamp': stamp - timedelta(seconds=i), 'heart_rate': 70+i} for i in range(3)])
    isolated_database.monitoring_alerts.insert_many([{'patient_id': 1, 'acknowledged': False, 'timestamp': stamp} for _ in range(53)])
    row = next(p for p in client.get('/api/v1/monitoring/patients?page=1', headers=headers()).json['data'] if p['patient_id'] == 1)
    assert row['latest']['heart_rate'] == 70
    assert row['pending_alert_count'] == 53
    assert 'token_hash' not in row['device']
    detail = client.get('/api/v1/monitoring/patients/1?alerts_page=2&page_size=10', headers=headers()).json['data']
    assert len(detail['alerts']) == 10 and detail['alerts_pagination']['total'] == 53


def subscribe(client, auth=None):
    return client.put('/api/v1/monitoring/push-devices', headers=auth or headers(), json={'token': TOKEN, 'platform': 'android', 'language': 'es'})


def test_push_permission_validation_and_logout(client, isolated_database):
    assert client.put('/api/v1/monitoring/push-devices', json={}).status_code == 401
    assert subscribe(client, headers('estudios')).status_code == 403
    assert client.put('/api/v1/monitoring/push-devices', headers=headers(), json={'token':'https://untrusted.example'}).status_code == 400
    auth = headers()
    assert subscribe(client, auth).status_code == 200
    assert client.delete('/api/v1/monitoring/push-devices', headers=headers('medico'), json={'token':TOKEN}).status_code == 200
    assert isolated_database.monitoring_push_devices.find_one()['enabled']
    assert client.post('/api/v1/auth/logout', headers=auth).status_code == 200
    assert not isolated_database.monitoring_push_devices.find_one()['enabled']


def make_alert(client):
    token = device(client)
    client.post('/api/v1/monitoring/data', headers={'X-Device-Token':token}, json={'device_id':'QA-ESP32','type':'fall','event_id':'push-fall-1'})


def test_push_is_durable_deduplicated_and_contains_no_clinical_text(client, isolated_database, monkeypatch):
    monkeypatch.setenv('MONITORING_PUSH_ENABLED', 'true')
    subscribe(client); make_alert(client)
    messages = []
    monkeypatch.setattr(push, 'expo_post', lambda path,payload: messages.append((path,payload)) or {'data': {'id':'ticket-test','status':'ok'}})
    push.process_outbox(); push.process_outbox()
    assert len(messages) == 1
    assert messages[0][0] == 'send'
    assert 'Paciente' not in messages[0][1]['body']
    assert messages[0][1]['data']['patientId'] == 1
    assert isolated_database.monitoring_push_outbox.count_documents({}) == 1
    assert isolated_database.monitoring_push_outbox.find_one()['state'] == 'receipt'
    monkeypatch.setattr(push, 'expo_post', lambda *_: {'data':{'ticket-test':{'status':'ok'}}})
    isolated_database.monitoring_push_outbox.update_many({}, {'$set':{'next_at':push.now()-timedelta(seconds=1)}})
    push.process_outbox()
    assert isolated_database.monitoring_push_outbox.find_one()['state'] == 'delivered'


def test_push_retries_and_removes_unregistered_tokens(client, isolated_database, monkeypatch):
    monkeypatch.setenv('MONITORING_PUSH_ENABLED', 'true')
    subscribe(client); make_alert(client)
    def offline(*_):
        raise TimeoutError()
    monkeypatch.setattr(push, 'expo_post', offline)
    push.process_outbox()
    job = isolated_database.monitoring_push_outbox.find_one()
    assert job['state'] == 'pending' and job['attempts'] == 1
    isolated_database.monitoring_push_outbox.update_many({}, {'$set':{'next_at':push.now()-timedelta(seconds=1)}})
    monkeypatch.setattr(push, 'expo_post', lambda *_: {'data':{'status':'error','details':{'error':'DeviceNotRegistered'}}})
    push.process_outbox()
    assert not isolated_database.monitoring_push_devices.find_one()['enabled']
    assert isolated_database.monitoring_push_outbox.find_one()['state'] == 'failed'


def test_push_does_not_send_after_account_is_disabled(client, isolated_database, monkeypatch):
    monkeypatch.setenv('MONITORING_PUSH_ENABLED', 'true')
    subscribe(client); make_alert(client); push.prepare_deliveries()
    isolated_database.users.update_one({'username':'admin.test'},{'$set':{'activo':False}})
    def forbidden(*_):
        pytest.fail('No debe enviarse a usuarios desactivados')
    monkeypatch.setattr(push,'expo_post',forbidden)
    push.process_outbox()
    assert isolated_database.monitoring_push_outbox.find_one()['state'] == 'cancelled'

