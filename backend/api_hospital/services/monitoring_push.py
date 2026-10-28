"""Durable, opt-in Expo push delivery. Never send clinical data on lock screens."""
import json
import os
import re
import logging
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from pymongo import ReturnDocument
from utils.database import get_collection
from models.user import UserModel

CLINICAL_ROLES = {'admin', 'medico', 'enfermero', 'enfermeria'}
TOKEN = re.compile(r'^(?:Expo|Exponent)PushToken\[[A-Za-z0-9_-]{10,200}\]$')
log = logging.getLogger(__name__)


def now():
    return datetime.now(timezone.utc)


def token_from(data):
    if not isinstance(data, dict) or not isinstance(data.get('token'), str) or not TOKEN.fullmatch(data['token']):
        raise ValueError('token')
    return data['token']


def register(user, data):
    token = token_from(data)
    if data.get('language') not in {'es', 'en'} or data.get('platform') not in {'android', 'ios'}:
        raise ValueError('language/platform')
    collection = get_collection('monitoring_push_devices')
    collection.create_index('token', unique=True)
    collection.create_index('expires_at', expireAfterSeconds=0)
    collection.update_one({'token': token}, {'$set': {
        'user_id': str(user['user_id']), 'session_jti': user['jti'],
        'language': data['language'], 'platform': data['platform'], 'enabled': True,
        'updated_at': now(), 'expires_at': now() + timedelta(days=30),
    }}, upsert=True)


def unregister(user, data):
    get_collection('monitoring_push_devices').update_one(
        {'token': token_from(data), 'user_id': str(user['user_id'])}, {'$set': {'enabled': False}})


def logout_session(jti):
    get_collection('monitoring_push_devices').update_many({'session_jti': jti}, {'$set': {'enabled': False}})


def allowed(device):
    try:
        user = UserModel.find_by_id(device['user_id'])
        return bool(user and user.get('activo', True) and user.get('role') in CLINICAL_ROLES
                    and not get_collection('revoked_tokens').find_one({'jti': device.get('session_jti')}))
    except (ValueError, TypeError):
        return False


def expo_post(path, payload):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    access = os.getenv('EXPO_PUSH_ACCESS_TOKEN', '').strip()
    if access:
        headers['Authorization'] = 'Bearer ' + access
    req = Request('https://exp.host/--/api/v2/push/' + path,
                  data=json.dumps(payload).encode(), headers=headers)
    with urlopen(req, timeout=5) as response:  # nosec B310 -- fixed HTTPS Expo endpoint
        return json.loads(response.read(65536))


def prepare_deliveries():
    alerts = get_collection('monitoring_alerts')
    jobs = get_collection('monitoring_push_outbox')
    jobs.create_index([('alert_id', 1), ('token', 1)], unique=True)
    jobs.create_index([('state', 1), ('next_at', 1)])
    jobs.create_index('expires_at', expireAfterSeconds=0)
    devices = list(get_collection('monitoring_push_devices').find({'enabled': True, 'expires_at': {'$gt': now()}}))
    for alert in alerts.find({'acknowledged': False, 'push_prepared': {'$ne': True},
                              'timestamp': {'$gte': now() - timedelta(minutes=15)}}).limit(50):
        for device in devices:
            if not allowed(device):
                continue
            jobs.update_one({'alert_id': str(alert['_id']), 'token': device['token']}, {'$setOnInsert': {
                'user_id': device['user_id'], 'session_jti': device['session_jti'],
                'patient_id': alert['patient_id'], 'language': device['language'],
                'state': 'pending', 'attempts': 0, 'next_at': now(),
                'expires_at': now() + timedelta(days=1),
            }}, upsert=True)
        alerts.update_one({'_id': alert['_id']}, {'$set': {'push_prepared': True}})


def notification(job):
    english = job['language'] == 'en'
    return {'to': job['token'], 'title': 'OftalCore',
            'body': 'A monitoring alert needs review. Open OftalCore.' if english else 'Hay una alerta de monitoreo pendiente. Abre OftalCore.',
            'sound': 'default', 'priority': 'high', 'channelId': 'monitoring', 'ttl': 900,
            'data': {'kind': 'monitoring', 'patientId': job['patient_id'],
                     'alertId': job['alert_id'], 'recipientUserId': job['user_id']}}


def process_outbox():
    if os.getenv('MONITORING_PUSH_ENABLED', 'false').lower() != 'true':
        return
    prepare_deliveries()
    jobs = get_collection('monitoring_push_outbox')
    for _ in range(20):
        job = jobs.find_one_and_update({'expires_at': {'$gt': now()}, '$or': [
            {'state': {'$in': ['pending', 'receipt']}, 'next_at': {'$lte': now()}},
            {'state': 'processing', 'lease_until': {'$lt': now()}},
        ]}, {'$set': {'state': 'processing', 'lease_until': now() + timedelta(minutes=2)}}, return_document=ReturnDocument.BEFORE)
        if not job:
            break
        device = get_collection('monitoring_push_devices').find_one({'token': job['token'], 'enabled': True,
            'user_id': job['user_id'], 'session_jti': job['session_jti'], 'expires_at': {'$gt': now()}})
        if not device or not allowed(device):
            jobs.update_one({'_id': job['_id']}, {'$set': {'state': 'cancelled'}})
            continue
        try:
            if job.get('ticket_id'):
                ticket = expo_post('getReceipts', {'ids': [job['ticket_id']]}).get('data', {}).get(job['ticket_id'])
                if not ticket:
                    raise ValueError('receipt_pending')
                success_state = 'delivered'
            else:
                from bson import ObjectId
                alert = get_collection('monitoring_alerts').find_one({'_id': ObjectId(job['alert_id']), 'acknowledged': False})
                if not alert:
                    jobs.update_one({'_id': job['_id']}, {'$set': {'state': 'cancelled'}})
                    continue
                ticket = expo_post('send', notification(job)).get('data')
                success_state = 'receipt'
            if not isinstance(ticket, dict):
                raise ValueError('invalid_ticket')
            if ticket.get('status') == 'error':
                error = ticket.get('details', {}).get('error', 'Unknown')
                if error == 'DeviceNotRegistered':
                    get_collection('monitoring_push_devices').update_one({'token': job['token']}, {'$set': {'enabled': False}})
                if error not in {'MessageRateExceeded'}:
                    jobs.update_one({'_id': job['_id']}, {'$set': {'state': 'failed', 'error': error}})
                    log.warning('Monitoring push rejected: %s', error)
                    continue
                raise ValueError(error)
            if ticket.get('status') != 'ok' or (success_state == 'receipt' and not ticket.get('id')):
                raise ValueError('invalid_ticket')
            changes = {'state': success_state, 'next_at': now() + timedelta(minutes=15)}
            if success_state == 'receipt':
                changes['ticket_id'] = ticket['id']
            jobs.update_one({'_id': job['_id']}, {'$set': changes})
        except Exception:
            # Store no tokens, patient names, response bodies or exception text in logs.
            attempts = job.get('attempts', 0) + 1
            jobs.update_one({'_id': job['_id']}, {'$set': {
                'state': 'failed' if attempts >= 6 else ('receipt' if job.get('ticket_id') else 'pending'),
                'attempts': attempts, 'next_at': now() + timedelta(seconds=min(600, 10 * 2 ** attempts)),
            }})
