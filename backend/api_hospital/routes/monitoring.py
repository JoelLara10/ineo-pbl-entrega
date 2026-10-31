from flask import Blueprint, jsonify, request, g
from pymongo.errors import DuplicateKeyError
from middleware.auth_middleware import token_required, role_required
from models.patient import PatientModel
from utils.database import get_collection
from services import monitoring_service as service

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.get('/monitoring/patients')
@token_required
@role_required('admin', 'medico', 'enfermeria', 'enfermero')
def patients():
    if 'page' in request.args:
        try:
            return jsonify(service.patients_page(bounded('page', 1), bounded('page_size', 10, 50), search_term()))
        except (ValueError, TypeError):
            return jsonify(error='Paginación o filtro inválido'), 400
    return jsonify(success=True, data=[service.summary(p) for p in
        get_collection('pacientes').find().sort('Id_exp', -1).limit(100)])

@monitoring_bp.get('/monitoring/patients/<int:pid>')
@token_required
@role_required('admin', 'medico', 'enfermeria', 'enfermero')
def patient(pid):
    record = PatientModel.find_by_id(pid)
    if not record:
        return jsonify(error='Paciente no encontrado'), 404
    if 'history_page' in request.args or 'alerts_page' in request.args:
        try:
            result = service.patient_page(record, bounded('history_page', 1), bounded('alerts_page', 1), bounded('page_size', 10, 50), request.args.get('history_before'))
            return jsonify(success=True, data=result)
        except (ValueError, TypeError, OverflowError):
            return jsonify(error='Paginación o fecha inválida'), 400
    return jsonify(success=True, data=service.summary(record, history=True))

@monitoring_bp.post('/monitoring/devices')
@token_required
@role_required('admin')
def provision():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='Se requiere un objeto JSON'), 400
    try:
        return jsonify(success=True, data=service.provision(data)), 201
    except (ValueError, TypeError, DuplicateKeyError):
        return jsonify(error='Dispositivo o expediente inválido; verifica la asignación'), 400

@monitoring_bp.patch('/monitoring/alerts/<identifier>/acknowledge')
@token_required
@role_required('admin', 'medico', 'enfermeria', 'enfermero')
def acknowledge(identifier):
    result = service.acknowledge(identifier, g.user['user_id'])
    if not result:
        return jsonify(error='Alerta no encontrada'), 404
    return jsonify(success=True, data=result)

@monitoring_bp.post('/monitoring/data')
def ingest():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='Se requiere un objeto JSON'), 400
    device = service.authenticate_device(data.get('device_id'), request.headers.get('X-Device-Token'))
    if not device:
        return jsonify(error='Dispositivo no autorizado'), 401
    try:
        fall_only = data.get('type') == 'fall'
        return jsonify(success=True, data=service.ingest(device, data, fall_only)), 201
    except ValueError as error:
        return jsonify(error='Datos del dispositivo inválidos'), 400




def bounded(key, default, maximum=100000):
    value = int(request.args.get(key, default))
    if not 1 <= value <= maximum:
        raise ValueError(key)
    return value


def search_term():
    value = request.args.get('q', '').strip()
    if len(value) > 100:
        raise ValueError('q')
    return value


@monitoring_bp.route('/monitoring/push-devices', methods=['PUT', 'DELETE'])
@token_required
@role_required('admin', 'medico', 'enfermeria', 'enfermero')
def push_device():
    from services import monitoring_push
    data = request.get_json(silent=True)
    try:
        monitoring_push.register(g.user, data) if request.method == 'PUT' else monitoring_push.unregister(g.user, data)
        return jsonify(success=True), 200
    except (ValueError, TypeError):
        return jsonify(error='Registro de notificaciones inválido'), 400
