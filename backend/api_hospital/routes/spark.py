from flask import Blueprint, jsonify, g

from middleware.auth_middleware import token_required, role_required
from services.spark_service import (
    SparkJobConflict,
    SparkNotImplemented,
    SparkService,
    SparkTypeError,
)

spark_bp = Blueprint('spark', __name__)

SPARK_ROLES = ('admin', 'administrativo', 'medico')


@spark_bp.route('/overview', methods=['GET'])
@token_required
@role_required(*SPARK_ROLES)
def get_overview():
    try:
        return jsonify(SparkService.get_overview()), 200
    except Exception:
        return jsonify({'error': 'No se pudo consultar el resumen de análisis'}), 500


@spark_bp.route('/run/<analysis_type>', methods=['POST'])
@token_required
@role_required(*SPARK_ROLES)
def run_analysis(analysis_type):
    try:
        payload = SparkService.run(
            analysis_type,
            requested_by=g.user.get('username'),
            role=g.user.get('role'),
        )
        return jsonify(payload), 202
    except SparkTypeError as error:
        return jsonify({'error': str(error)}), 400
    except SparkNotImplemented as error:
        return jsonify({'error': str(error)}), 400
    except SparkJobConflict as error:
        return jsonify({'error': str(error)}), 409
    except Exception:
        return jsonify({'error': 'No se pudo ejecutar el análisis clínico'}), 500


@spark_bp.route('/status/<analysis_type>', methods=['GET'])
@token_required
@role_required(*SPARK_ROLES)
def get_status(analysis_type):
    try:
        return jsonify(SparkService.get_status(analysis_type)), 200
    except SparkTypeError as error:
        return jsonify({'error': str(error)}), 400
    except Exception:
        return jsonify({'error': 'No se pudo consultar el estado del análisis'}), 500


@spark_bp.route('/<analysis_type>', methods=['GET'])
@token_required
@role_required(*SPARK_ROLES)
def get_result(analysis_type):
    try:
        return jsonify(SparkService.get_result(analysis_type)), 200
    except SparkTypeError as error:
        return jsonify({'error': str(error)}), 400
    except Exception:
        return jsonify({'error': 'No se pudo cargar el resultado clínico'}), 500
