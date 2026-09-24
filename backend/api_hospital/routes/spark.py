from flask import Blueprint, jsonify, request, g
from pymongo.errors import PyMongoError

from middleware.auth_middleware import token_required, role_required
from services.spark_service import (
    SparkJobConflict,
    SparkNotImplemented,
    SparkService,
    SparkTypeError,
)

spark_bp = Blueprint('spark', __name__)

SPARK_ROLES = ('admin', 'administrativo', 'medico')


def _error(message, code, http_status):
    return jsonify(
        contract_version=SparkService.VERSION,
        error=message,
        code=code,
    ), http_status


@spark_bp.errorhandler(PyMongoError)
def unavailable(_error):
    return _error('Servicio de análisis temporalmente no disponible.',
                  'unavailable', 503)


@spark_bp.route('/overview', methods=['GET'])
@token_required
@role_required(*SPARK_ROLES)
def get_overview():
    try:
        return jsonify(SparkService.get_overview()), 200
    except Exception:
        return _error('No se pudo consultar el resumen de análisis',
                      'overview_failed', 500)


@spark_bp.route('/run/<analysis_type>', methods=['POST'])
@token_required
@role_required(*SPARK_ROLES)
def run_analysis(analysis_type):
    if request.get_data():
        return _error('Esta versión no acepta parámetros de ejecución.',
                      'invalid_request', 400)
    try:
        payload = SparkService.run(
            analysis_type,
            requested_by=g.user.get('username'),
            role=g.user.get('role'),
        )
        return jsonify(payload), 202
    except SparkTypeError as exc:
        return _error(str(exc), 'invalid_type', 400)
    except SparkNotImplemented as exc:
        return _error(str(exc), 'not_implemented', 400)
    except SparkJobConflict as exc:
        return _error(str(exc), 'conflict', 409)
    except Exception:
        return _error('No se pudo ejecutar el análisis clínico',
                      'run_failed', 500)


@spark_bp.route('/status/<analysis_type>', methods=['GET'])
@token_required
@role_required(*SPARK_ROLES)
def get_status(analysis_type):
    try:
        return jsonify(SparkService.get_status(analysis_type)), 200
    except SparkTypeError as exc:
        return _error(str(exc), 'invalid_type', 400)
    except Exception:
        return _error('No se pudo consultar el estado del análisis',
                      'status_failed', 500)


@spark_bp.route('/<analysis_type>', methods=['GET'])
@token_required
@role_required(*SPARK_ROLES)
def get_result(analysis_type):
    try:
        return jsonify(SparkService.get_result(analysis_type)), 200
    except SparkTypeError as exc:
        return _error(str(exc), 'invalid_type', 400)
    except Exception:
        return _error('No se pudo cargar el resultado clínico',
                      'result_failed', 500)