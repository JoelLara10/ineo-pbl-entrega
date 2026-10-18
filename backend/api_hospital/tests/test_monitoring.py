import pytest
from middleware.auth_middleware import generate_token
from services.monitoring_socket import socketio
from services import monitoring_service as service


def headers(role='admin'):
    ids = {'admin': 1, 'medico': 2, 'enfermeria': 3, 'estudios': 4}
    token = generate_token(f'{ids[role]:024x}', role + '.test', role)
    return {'Authorization': 'Bearer ' + token}


def device(client):
    response = client.post('/api/v1/monitoring/devices', headers=headers(),
        json={'device_id': 'QA-ESP32', 'patient_id': 1})
    assert response.status_code == 201
    return response.json['data']['device_token']


def payload(**changes):
    return dict(device_id='QA-ESP32', patient_id=1, heart_rate=75, spo2=98,
                finger_detected=True, movement=False, fall=False, **changes)


def test_monitoring_permissions(client):
    assert client.get('/api/v1/monitoring/patients').status_code == 401
    assert client.get('/api/v1/monitoring/patients', headers=headers('estudios')).status_code == 403
    assert client.post('/api/v1/monitoring/devices', headers=headers('medico'), json={}).status_code == 403
    assert client.post('/api/v1/monitoring/data', json=payload()).status_code == 401
    assert client.get('/api/v1/monitoring/patients', headers=headers('enfermeria')).status_code == 200


def test_fall_without_vitals_and_deduplication(client, isolated_database):
    token = device(client)
    auth = {'X-Device-Token': token}
    fall = {'device_id': 'QA-ESP32', 'patient_id': 1, 'type': 'fall', 'event_id': 'fall-1'}
    assert client.post('/api/v1/monitoring/data', headers=auth, json=fall).status_code == 201
    assert client.post('/api/v1/monitoring/data', headers=auth, json=fall).status_code == 201
    data = payload()
    data['fall'] = True
    assert client.post('/api/v1/monitoring/data', headers=auth, json=data).status_code == 201
    assert isolated_database.monitoring_alerts.count_documents({'type': 'fall'}) == 1
    response = client.get('/api/v1/monitoring/patients/1', headers=headers('medico'))
    assert response.json['data']['alerts'][0]['type'] == 'fall'
    alert_id = response.json['data']['alerts'][0]['id']
    for _ in range(2):
        assert client.patch(f'/api/v1/monitoring/alerts/{alert_id}/acknowledge', headers=headers()).status_code == 200
    assert client.get('/api/v1/monitoring/patients/1', headers=headers()).json['data']['alerts'] == []
    # An already acknowledged event cannot be recreated by a queued retry.
    client.post('/api/v1/monitoring/data', headers=auth, json=fall)
    assert isolated_database.monitoring_alerts.count_documents({'type': 'fall'}) == 1


@pytest.mark.parametrize('change', [{'heart_rate': float('nan')}, {'spo2': 101},
    {'movement': 'false'}, {'patient_id': 2}, {'finger_detected': 'true'}])
def test_invalid_readings_not_saved(client, isolated_database, change):
    token = device(client)
    data = payload()
    data.update(change)
    assert client.post('/api/v1/monitoring/data', headers={'X-Device-Token': token}, json=data).status_code == 400
    assert isolated_database.monitoring_measurements.count_documents({}) == 0


def test_contact_loss_clears_vitals_and_secrets_not_exposed(client):
    token = device(client)
    data = payload()
    data.update(finger_detected=False, heart_rate=0, spo2=0)
    assert client.post('/api/v1/monitoring/data', headers={'X-Device-Token': token}, json=data).status_code == 201
    result = client.get('/api/v1/monitoring/patients/1', headers=headers()).json['data']
    assert result['latest']['heart_rate'] is None
    assert result['latest']['spo2'] is None
    assert result['latest']['timestamp'].endswith('+00:00')
    assert 'token_hash' not in result['device']
    assert result['alerts'] == []


def test_socket_fall_is_persisted_and_confirmed(app, client, isolated_database):
    token = device(client)
    sensor = socketio.test_client(app)
    sensor.emit('register_wearable', {'device_id': 'QA-ESP32', 'patient_id': 1, 'device_token': token})
    assert any(event['name'] == 'wearable_registered' for event in sensor.get_received())
    response = sensor.emit('wearable_fall_alert', {'device_id': 'QA-ESP32', 'patient_id': 1}, callback=True)
    assert response['success']
    assert isolated_database.monitoring_alerts.count_documents({'type': 'fall'}) == 1
    unauthorized = socketio.test_client(app)
    assert not unauthorized.emit('wearable_data', payload(), callback=True)['success']
    sensor.disconnect()
    unauthorized.disconnect()
    assert not client.get('/api/v1/monitoring/patients/1', headers=headers()).json['data']['device']['online']


def test_wrong_assignment_and_token_rotation(client):
    old = device(client)
    assert client.post('/api/v1/monitoring/devices', headers=headers(),
        json={'device_id': 'QA-ESP32', 'patient_id': 2}).status_code == 400
    device(client)
    assert client.post('/api/v1/monitoring/data', headers={'X-Device-Token': old}, json=payload()).status_code == 401


def test_configured_alerts_and_patient_isolation(client, monkeypatch):
    monkeypatch.setenv('MONITORING_HEART_RATE_MAX', '100')
    token = device(client)
    data = payload()
    data.update(heart_rate=110, spo2=88)
    response = client.post('/api/v1/monitoring/data', headers={'X-Device-Token': token}, json=data)
    assert response.status_code == 201
    assert {a['type'] for a in response.json['data']['alerts']} == {'high_heart_rate', 'low_spo2'}
    other = client.get('/api/v1/monitoring/patients/2', headers=headers('medico')).json['data']
    assert other['latest'] is None and other['alerts'] == []


def test_stale_and_missing_device_states(client, isolated_database):
    from datetime import datetime, timezone, timedelta
    token = device(client)
    client.post('/api/v1/monitoring/data', headers={'X-Device-Token': token}, json=payload())
    old = datetime.now(timezone.utc) - timedelta(minutes=2)
    isolated_database.monitoring_devices.update_one({'device_id': 'QA-ESP32'}, {'$set': {'last_seen': old}})
    isolated_database.monitoring_measurements.update_many({}, {'$set': {'timestamp': old}})
    result = client.get('/api/v1/monitoring/patients/1', headers=headers()).json['data']
    assert result['latest']['stale']
    assert not result['device']['online']
    assert client.get('/api/v1/monitoring/patients/999999', headers=headers()).status_code == 404


@pytest.mark.parametrize('did', [None, 123, '', '   '])
def test_invalid_device_identity(client, did):
    assert client.post('/api/v1/monitoring/devices', headers=headers(),
        json={'device_id': did, 'patient_id': 1}).status_code == 400


def test_existing_nurse_role_has_access(client, isolated_database):
    isolated_database.users.update_one({'username': 'enfermeria.test'}, {'$set': {'role': 'enfermero'}})
    auth = headers('enfermeria')
    assert client.get('/api/v1/monitoring/patients', headers=auth).status_code == 200
    assert client.get('/api/v1/monitoring/patients/1', headers=auth).status_code == 200
    assert client.post('/api/v1/monitoring/devices', headers=auth, json={}).status_code == 403


def test_patient_device_assignment_is_unambiguous(client):
    device(client)
    response = client.post('/api/v1/monitoring/devices', headers=headers(),
        json={'device_id': 'SECOND-ESP32', 'patient_id': 1})
    assert response.status_code == 400
