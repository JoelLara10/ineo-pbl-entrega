"""ESP32 Socket.IO compatibility; devices register using their provisioned token."""
from flask import request, session
from flask_socketio import SocketIO, emit
from services import monitoring_service as service

socketio = SocketIO(async_mode='threading')

@socketio.on('register_wearable')
def register(data):
    if not isinstance(data, dict):
        emit('wearable_error', {'success': False, 'message': 'Registro inválido'})
        return
    device = service.authenticate_device(data.get('device_id'), data.get('device_token'))
    if not device or ('patient_id' in data and str(data['patient_id']) != str(device['patient_id'])):
        emit('wearable_error', {'success': False, 'message': 'Dispositivo no autorizado'})
        return
    session['monitoring_device_id'] = device['device_id']
    session['monitoring_device_token'] = data['device_token']
    service.get_collection('monitoring_devices').update_one({'device_id': device['device_id']},
        {'$set': {'last_seen': service.now(), 'online': True, 'active_sid': request.sid}})
    emit('wearable_registered', {'success': True, 'device': service.output(device)})


def receive(data, fall_only=False):
    device = service.authenticate_device(session.get('monitoring_device_id'), session.get('monitoring_device_token'))
    if not device or not isinstance(data, dict) or data.get('device_id') != device['device_id']:
        emit('wearable_error', {'success': False, 'message': 'Dispositivo no autorizado'})
        return {'success': False}
    try:
        result = service.ingest(device, data, fall_only)
    except ValueError as error:
        emit('wearable_error', {'success': False, 'message': str(error)})
        return {'success': False}
    # Confirm persistence; clinical clients query protected REST (no public broadcast).
    event = 'wearable_fall_alert_received' if fall_only else 'wearable_data_received'
    emit(event, {'success': True, **result})
    return {'success': True, **result}

@socketio.on('wearable_data')
def data(payload):
    return receive(payload)

@socketio.on('wearable_fall_alert')
def fall(payload):
    return receive(payload, True)

@socketio.on('disconnect')
def disconnect(reason=None):
    did = session.get('monitoring_device_id')
    if did:
        service.get_collection('monitoring_devices').update_one({'device_id': did, 'active_sid': request.sid}, {'$set': {'online': False}})
