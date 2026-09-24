from flask import Blueprint, jsonify, request
from middleware.auth_middleware import verify_token
from services import spark_service as service
from pymongo.errors import PyMongoError

spark_bp = Blueprint('spark', __name__)


def error(message, code, http_status):
    return jsonify(contract_version=service.VERSION, error=message, code=code), http_status


@spark_bp.before_request
def authorize():
    if request.method == 'OPTIONS':
        return None
    header = request.headers.get('Authorization', '').split()
    user = verify_token(header[1]) if len(header) == 2 and header[0] == 'Bearer' else None
    if user is None:
        return error('Token no proporcionado, inválido o expirado.', 'unauthorized', 401)
    if user.get('role') != 'admin':
        return error('Permisos insuficientes.', 'forbidden', 403)


@spark_bp.errorhandler(PyMongoError)
def unavailable(_error):
    return error('Servicio de análisis temporalmente no disponible.', 'unavailable', 503)


@spark_bp.route('/overview')
def overview():
    return jsonify({kind: {'available': service.results(kind)['available'],
                           'status': service.status_of(service.read_job(kind))} for kind in service.TYPES})


@spark_bp.route('/<kind>')
def result(kind):
    if kind not in service.TYPES:
        return error('Tipo de análisis no válido.', 'invalid_type', 400)
    return jsonify(service.results(kind))


@spark_bp.route('/status/<kind>')
def status(kind):
    if kind not in service.TYPES:
        return error('Tipo de análisis no válido.', 'invalid_type', 400)
    return jsonify(service.status_of(service.read_job(kind)))


@spark_bp.route('/run/<kind>', methods=['POST'])
def run(kind):
    if kind not in service.TYPES:
        return error('Tipo de análisis no válido.', 'invalid_type', 400)
    if request.get_data():
        return error('Esta versión no acepta parámetros de ejecución.', 'invalid_request', 400)
    try:
        current, created = service.start(kind)
    except RuntimeError:
        return error('Ejecutor no disponible.', 'unavailable', 503)
    return jsonify(contract_version=service.VERSION, status=current), 202 if created else 200
