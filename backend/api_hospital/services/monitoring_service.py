"""Patient monitoring: existing clinical records, device identity and durable alerts."""
from datetime import datetime, timezone, timedelta
import hashlib
import math
import os
import secrets
import re
from threading import Lock
from bson import ObjectId
from pymongo import ReturnDocument
from utils.database import get_collection, serialize_doc
from models.patient import PatientModel


def now():
    return datetime.now(timezone.utc)


def output(document):
    if document is None:
        return None
    document = dict(document)
    for key, value in document.items():
        if isinstance(value, datetime):
            document[key] = value.replace(tzinfo=timezone.utc).isoformat()
    result = serialize_doc(document)
    result.pop('token_hash', None)
    result.pop('active_sid', None)
    return result


def patient_id(value):
    if isinstance(value, bool):
        raise ValueError('El expediente debe ser numérico')
    value = int(str(value))
    if value <= 0 or not PatientModel.find_by_id(value):
        raise ValueError('Paciente no encontrado')
    return value


def provision(data):
    pid = patient_id(data.get('patient_id'))
    raw_id = data.get('device_id')
    if not isinstance(raw_id, str):
        raise ValueError('device_id debe ser texto')
    did = raw_id.strip()
    if not did or len(did) > 100:
        raise ValueError('device_id es obligatorio (máximo 100 caracteres)')
    devices = get_collection('monitoring_devices')
    devices.create_index('device_id', unique=True)
    devices.create_index('patient_id', unique=True, partialFilterExpression={'enabled': True})
    assigned = devices.find_one({'patient_id': pid, 'enabled': True})
    if assigned and assigned['device_id'] != did:
        raise ValueError('El paciente ya tiene un dispositivo asignado')
    existing = devices.find_one({'device_id': did})
    if existing and existing.get('patient_id') != pid:
        raise ValueError('El dispositivo ya está asignado a otro paciente')
    token = secrets.token_urlsafe(32)
    devices.update_one({'device_id': did}, {'$set': {
        'patient_id': pid, 'enabled': True,
        'token_hash': hashlib.sha256(token.encode()).hexdigest(),
    }}, upsert=True)
    return {'device': output(devices.find_one({'device_id': did})), 'device_token': token}


def authenticate_device(did, token):
    if not isinstance(did, str) or not isinstance(token, str) or not token:
        return None
    device = get_collection('monitoring_devices').find_one({'device_id': did, 'enabled': True})
    if device and secrets.compare_digest(device.get('token_hash', ''), hashlib.sha256(token.encode()).hexdigest()):
        if PatientModel.find_by_id(device['patient_id']):
            return device
    return None


def number(data, key, minimum, maximum, optional=False):
    value = data.get(key)
    if value is None and optional:
        return None
    if isinstance(value, bool):
        raise ValueError(f'{key} debe ser numérico')
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f'{key} debe ser numérico')
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f'{key} fuera de rango')
    return value


def boolean(data, key, default=False):
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f'{key} debe ser booleano')
    return value


def alert(device, kind, message, severity, event_id=None):
    collection = get_collection('monitoring_alerts')
    # One pending episode per device/type prevents duplicate immediate + telemetry falls.
    collection.create_index([('device_id', 1), ('type', 1)], unique=True,
                            partialFilterExpression={'acknowledged': False})
    collection.create_index([('device_id', 1), ('event_id', 1)], unique=True,
                            partialFilterExpression={'event_id': {'$type': 'string'}})
    identity = {'device_id': device['device_id'], 'type': kind, 'acknowledged': False}
    if event_id and collection.find_one({'device_id': device['device_id'], 'event_id': event_id}):
        return None
    document = {**identity, 'patient_id': device['patient_id'], 'message': message,
                'severity': severity, 'status': 'pending', 'timestamp': now()}
    if event_id:
        document['event_id'] = event_id
    from pymongo.errors import DuplicateKeyError
    try:
        result = collection.find_one_and_update(identity, {'$setOnInsert': document},
                                                upsert=True, return_document=ReturnDocument.AFTER)
    except DuplicateKeyError:
        result = collection.find_one(identity)
    return output(result)


def ingest(device, data, fall_only=False):
    if not isinstance(data, dict):
        raise ValueError('Se requiere un objeto JSON')
    if 'patient_id' in data and str(data['patient_id']) != str(device['patient_id']):
        raise ValueError('El paciente no corresponde al dispositivo')
    timestamp = now()
    measurement = {'device_id': device['device_id'], 'patient_id': device['patient_id'],
                   'timestamp': timestamp, 'source': 'esp32',
                   'fall': True if fall_only else boolean(data, 'fall'),
                   'movement': boolean(data, 'movement'),
                   'finger_detected': boolean(data, 'finger_detected'),
                   'temperature': number(data, 'temperature', -40, 125, True),
                   'acceleration': number(data, 'acceleration', 0, 100, True)}
    generated = []
    event_id = data.get('event_id')
    if event_id is not None and (not isinstance(event_id, str) or not 1 <= len(event_id) <= 100):
        raise ValueError('event_id inválido')
    if not fall_only:
        if measurement['finger_detected']:
            measurement['heart_rate'] = number(data, 'heart_rate', 1, 250)
            measurement['spo2'] = number(data, 'spo2', 1, 100)
        else:
            measurement.update(heart_rate=None, spo2=None)
        get_collection('monitoring_measurements').insert_one(measurement)
        hr, oxygen = measurement['heart_rate'], measurement['spo2']
        hr_min = float(os.getenv('MONITORING_HEART_RATE_MIN', '50'))
        hr_max = float(os.getenv('MONITORING_HEART_RATE_MAX', '120'))
        oxygen_min = float(os.getenv('MONITORING_SPO2_MIN', '92'))
        if hr is not None and (hr < hr_min or hr > hr_max):
            generated.append(alert(device, 'low_heart_rate' if hr < hr_min else 'high_heart_rate',
                                   'Frecuencia cardiaca fuera del rango configurado', 'high'))
        if oxygen is not None and oxygen < oxygen_min:
            generated.append(alert(device, 'low_spo2', 'SpO₂ fuera del rango configurado', 'high'))
    if measurement['fall']:
        generated.append(alert(device, 'fall', 'Posible caída detectada', 'critical', event_id))
    get_collection('monitoring_devices').update_one({'device_id': device['device_id']},
        {'$set': {'last_seen': timestamp, 'online': True}})
    return {'measurement': None if fall_only else output(measurement),
            'alerts': [item for item in generated if item]}


def summary(patient, history=False, include_alerts=True):
    pid = patient['Id_exp']
    device = get_collection('monitoring_devices').find_one({'patient_id': pid, 'enabled': True})
    latest = get_collection('monitoring_measurements').find_one({'patient_id': pid}, sort=[('timestamp', -1)])
    result = {'patient_id': pid,
              'name': ' '.join(str(patient.get(key) or '') for key in ('nom_pac', 'papell', 'sapell')).strip(),
              'device': output(device), 'latest': output(latest),
              'alerts': [output(item) for item in get_collection('monitoring_alerts').find(
                  {'patient_id': pid, 'acknowledged': False}).sort('timestamp', -1).limit(50)] if include_alerts else []}
    if device:
        seen = device.get('last_seen')
        result['device']['online'] = bool(device.get('online', False) and seen and seen.replace(tzinfo=timezone.utc) > now() - timedelta(seconds=30))
    if latest:
        result['latest']['stale'] = latest['timestamp'].replace(tzinfo=timezone.utc) < now() - timedelta(seconds=30)
    if history:
        result['history'] = [output(item) for item in get_collection('monitoring_measurements').find(
            {'patient_id': pid}).sort('timestamp', -1).limit(50)]
    return result


def acknowledge(identifier, user_id):
    try:
        oid = ObjectId(identifier)
    except Exception:
        return None
    collection = get_collection('monitoring_alerts')
    collection.update_one({'_id': oid, 'acknowledged': False}, {'$set': {
        'acknowledged': True, 'status': 'acknowledged', 'acknowledged_at': now(),
        'acknowledged_by': str(user_id)}})
    return output(collection.find_one({'_id': oid}))



_indexed_database = None
_index_lock = Lock()


def ensure_monitoring_indexes():
    global _indexed_database
    database = get_collection('monitoring_measurements').database
    with _index_lock:
        if database == _indexed_database:
            return
        database.monitoring_measurements.create_index([('patient_id', 1), ('timestamp', -1), ('_id', -1)])
        database.monitoring_alerts.create_index([('patient_id', 1), ('acknowledged', 1), ('timestamp', -1)])
        database.pacientes.create_index('Id_exp')
        _indexed_database = database


def pagination(page, size, total):
    pages = max(1, (total + size - 1) // size)
    return {'page': min(page, pages), 'page_size': size, 'total': total, 'total_pages': pages}


def patients_page(page=1, size=10, search=''):
    ensure_monitoring_indexes()
    query = {}
    if search:
        fields = ['nom_pac', 'papell', 'sapell']
        query = {'$or': [{field: {'$regex': re.escape(search), '$options': 'i'}} for field in fields]}
        record = search.removeprefix('OFTALCORE-').removeprefix('oftalcore-')
        if record.isdigit():
            query['$or'].append({'Id_exp': int(record)})
    patients = get_collection('pacientes')
    meta = pagination(page, size, patients.count_documents(query))
    records = list(patients.find(query, {'Id_exp':1,'nom_pac':1,'papell':1,'sapell':1}).sort('Id_exp', -1).skip((meta['page'] - 1) * size).limit(size))
    ids = [p['Id_exp'] for p in records]
    devices = {d['patient_id']: d for d in get_collection('monitoring_devices').find({'patient_id': {'$in': ids}, 'enabled': True})}
    latest = {d['_id']: d['reading'] for d in get_collection('monitoring_measurements').aggregate([
        {'$match': {'patient_id': {'$in': ids}}}, {'$sort': {'patient_id': 1, 'timestamp': -1, '_id': -1}},
        {'$group': {'_id': '$patient_id', 'reading': {'$first': '$$ROOT'}}}])}
    counts = {d['_id']: d['count'] for d in get_collection('monitoring_alerts').aggregate([
        {'$match': {'patient_id': {'$in': ids}, 'acknowledged': False}},
        {'$group': {'_id': '$patient_id', 'count': {'$sum': 1}}}])}
    data = []
    for patient in records:
        pid = patient['Id_exp']
        device, reading = devices.get(pid), latest.get(pid)
        item = {'patient_id': pid, 'name': ' '.join(str(patient.get(k) or '') for k in ('nom_pac', 'papell', 'sapell')).strip(),
                'device': output(device), 'latest': output(reading), 'alerts': [], 'pending_alert_count': counts.get(pid, 0)}
        if device:
            seen = device.get('last_seen')
            item['device']['online'] = bool(device.get('online') and seen and seen.replace(tzinfo=timezone.utc) > now() - timedelta(seconds=30))
        if reading:
            item['latest']['stale'] = reading['timestamp'].replace(tzinfo=timezone.utc) < now() - timedelta(seconds=30)
        data.append(item)
    return {'success': True, 'data': data, 'pagination': meta}


def patient_page(patient, history_page=1, alerts_page=1, size=10, history_before=None):
    ensure_monitoring_indexes()
    result = summary(patient, include_alerts=False)
    pid = patient['Id_exp']
    before = datetime.fromisoformat(history_before.replace('Z', '+00:00')) if history_before else now()
    if before.tzinfo is None:
        raise ValueError('history_before requiere zona horaria')
    history_filter = {'patient_id': pid, 'timestamp': {'$lte': before}}
    collection = get_collection('monitoring_measurements')
    meta = pagination(history_page, size, collection.count_documents(history_filter))
    meta['as_of'] = before.isoformat()
    result['history'] = [output(d) for d in collection.find(history_filter).sort([('timestamp', -1), ('_id', -1)]).skip((meta['page'] - 1) * size).limit(size)]
    result['history_pagination'] = meta
    collection = get_collection('monitoring_alerts')
    alert_filter = {'patient_id': pid, 'acknowledged': False}
    meta = pagination(alerts_page, size, collection.count_documents(alert_filter))
    result['alerts'] = [output(d) for d in collection.find(alert_filter).sort([('timestamp', -1), ('_id', -1)]).skip((meta['page'] - 1) * size).limit(size)]
    result['alerts_pagination'] = meta
    result['pending_alert_count'] = meta['total']
    return result
