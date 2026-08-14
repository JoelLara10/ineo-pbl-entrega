from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import token_required, role_required
from utils.database import get_collection
from datetime import datetime

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

def registrar_log(accion, usuario_id=None, usuario_nombre=None, detalles=None):
    """Registra una acción en el log"""
    collection = get_collection('logs')
    
    log = {
        'accion': accion,
        'fecha': datetime.now(),
        'usuario_id': usuario_id or g.user.get('user_id') if hasattr(g, 'user') else None,
        'usuario_nombre': usuario_nombre or g.user.get('username') if hasattr(g, 'user') else None,
        'detalles': detalles or {},
        'ip': request.remote_addr
    }
    
    collection.insert_one(log)

@logs_bp.route('', methods=['GET'])
@token_required
@role_required('admin')
def get_logs():
    """Obtiene logs paginados"""
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', 50)), 100)
    usuario = request.args.get('usuario')
    accion = request.args.get('accion')
    
    collection = get_collection('logs')
    
    query = {}
    if usuario:
        query['usuario_nombre'] = {'$regex': usuario, '$options': 'i'}
    if accion:
        query['accion'] = {'$regex': accion, '$options': 'i'}
    
    skip = (page - 1) * page_size
    total = collection.count_documents(query)
    
    logs = list(collection.find(query).sort('fecha', -1).skip(skip).limit(page_size))
    
    # Convertir ObjectId a string
    for log in logs:
        log['_id'] = str(log['_id'])
        if log.get('fecha'):
            log['fecha'] = log['fecha'].isoformat()
    
    return jsonify({
        'total': total,
        'page': page,
        'page_size': page_size,
        'data': logs
    }), 200

@logs_bp.route('/user/<usuario>', methods=['GET'])
@token_required
@role_required('admin')
def get_user_logs(usuario):
    """Obtiene logs de un usuario específico"""
    collection = get_collection('logs')
    
    logs = list(collection.find({'usuario_nombre': usuario}).sort('fecha', -1).limit(100))
    
    for log in logs:
        log['_id'] = str(log['_id'])
        if log.get('fecha'):
            log['fecha'] = log['fecha'].isoformat()
    
    return jsonify(logs), 200