import os

from flask import Blueprint, jsonify, request, send_file
from middleware.auth_middleware import role_required, token_required
from scheduler.jobs import configure_backup_job
from utils.backups import (
    BACKUP_DIR,
    VALID_FORMATS,
    VALID_TYPES,
    RestoreError,
    cargar_config_automatizacion,
    check_db_health,
    eliminar_backup,
    guardar_config_automatizacion,
    limpiar_backups,
    list_backups,
    obtener_colecciones,
    realizar_backup,
    restaurar_backup,
)

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')


@backup_bp.route('', methods=['GET'])
@token_required
@role_required('admin')
def get_backups():
    return jsonify(list_backups()), 200


@backup_bp.route('/collections', methods=['GET'])
@token_required
@role_required('admin')
def get_collections():
    return jsonify(obtener_colecciones()), 200


@backup_bp.route('/create', methods=['POST'])
@token_required
@role_required('admin')
def create_backup():
    data = request.get_json(silent=True) or {}
    tipo = data.get('tipo', 'completa')
    formato = data.get('formato', 'json')
    collections = data.get('colecciones') or None
    try:
        backup_file = realizar_backup(tipo=tipo, formato=formato, colecciones=collections)
        if not backup_file:
            return jsonify({
                'message': 'No hay cambios nuevos para incluir en este respaldo',
                'file': None,
            }), 200
        return jsonify({
            'message': 'Respaldo creado correctamente',
            'file': os.path.basename(backup_file),
        }), 201
    except (ValueError, OSError) as exc:
        return jsonify({'error': str(exc)}), 400


@backup_bp.route('/restore', methods=['POST'])
@token_required
@role_required('admin')
def restore_backup():
    data = request.get_json(silent=True) or {}
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'Selecciona un respaldo'}), 400
    try:
        restored = restaurar_backup(filename)
        return jsonify({
            'message': 'Restauración completada correctamente',
            'collections': restored,
        }), 200
    except FileNotFoundError as exc:
        return jsonify({'error': str(exc)}), 404
    except RestoreError as exc:
        return jsonify({
            'error': str(exc),
            'collections': exc.restored,
            'failed_collections': exc.failed,
        }), 409
    except (ValueError, OSError) as exc:
        return jsonify({'error': str(exc)}), 400


@backup_bp.route('/download/<path:filename>', methods=['GET'])
@token_required
@role_required('admin')
def download_backup(filename):
    try:
        backup_path = BACKUP_DIR / os.path.basename(filename)
        if filename != backup_path.name or not backup_path.is_file():
            return jsonify({'error': 'Archivo no encontrado'}), 404
        return send_file(backup_path, as_attachment=True, download_name=backup_path.name)
    except OSError as exc:
        return jsonify({'error': str(exc)}), 400


@backup_bp.route('/<path:filename>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_backup(filename):
    try:
        eliminar_backup(filename)
        return jsonify({'message': 'Respaldo eliminado'}), 200
    except FileNotFoundError as exc:
        return jsonify({'error': str(exc)}), 404
    except (ValueError, OSError) as exc:
        return jsonify({'error': str(exc)}), 400


@backup_bp.route('/clean', methods=['POST'])
@token_required
@role_required('admin')
def clean_backups():
    data = request.get_json(silent=True) or {}
    limpiar_backups(data.get('keep', 4))
    return jsonify({'message': 'Respaldos antiguos eliminados'}), 200


@backup_bp.route('/automation', methods=['GET'])
@token_required
@role_required('admin')
def get_automation():
    return jsonify(cargar_config_automatizacion()), 200


@backup_bp.route('/automation', methods=['PUT'])
@token_required
@role_required('admin')
def update_automation():
    data = request.get_json(silent=True) or {}
    try:
        interval = int(data.get('intervalo', 1440))
        if interval < 5 or interval > 525600:
            raise ValueError('El intervalo debe estar entre 5 y 525600 minutos')
        backup_type = data.get('tipo', 'completa')
        backup_format = data.get('formato', 'json')
        if backup_type not in VALID_TYPES:
            raise ValueError('Tipo de respaldo inválido')
        if backup_format == 'excel':
            backup_format = 'xlsx'
        if backup_format not in VALID_FORMATS:
            raise ValueError('Formato de respaldo inválido')
        selected_collections = data.get('colecciones') or []
        if backup_type == 'selectiva' and not selected_collections:
            raise ValueError('Selecciona al menos una colección para el respaldo selectivo')
        config = {
            'activo': bool(data.get('activo', False)),
            'tipo': backup_type,
            'formato': backup_format,
            'intervalo': interval,
            'colecciones': selected_collections,
            'max_backups': max(1, min(int(data.get('max_backups', 4)), 50)),
        }
        guardar_config_automatizacion(config)
        configure_backup_job(config)
        return jsonify(config), 200
    except (ValueError, TypeError) as exc:
        return jsonify({'error': str(exc)}), 400


@backup_bp.route('/health', methods=['GET'])
@token_required
def health_check():
    return jsonify(check_db_health()), 200
