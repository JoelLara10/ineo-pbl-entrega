from flask import Blueprint, jsonify
from middleware.auth_middleware import token_required, role_required
import psutil
import platform
from datetime import datetime

performance_bp = Blueprint('performance', __name__, url_prefix='/performance')

@performance_bp.route('/system', methods=['GET'])
@token_required
@role_required('admin')
def get_system_stats():
    """Obtiene estadísticas del sistema"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return jsonify({
        'cpu': {
            'percent': cpu_percent,
            'cores': psutil.cpu_count(),
            'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None
        },
        'memory': {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent,
            'used': memory.used
        },
        'disk': {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        },
        'system': {
            'platform': platform.system(),
            'release': platform.release(),
            'processor': platform.processor(),
            'hostname': platform.node()
        },
        'timestamp': datetime.now().isoformat()
    }), 200

@performance_bp.route('/process', methods=['GET'])
@token_required
@role_required('admin')
def get_process_stats():
    """Obtiene estadísticas del proceso actual"""
    process = psutil.Process()
    
    return jsonify({
        'pid': process.pid,
        'name': process.name(),
        'status': process.status(),
        'cpu_percent': process.cpu_percent(interval=1),
        'memory_percent': process.memory_percent(),
        'memory_info': {
            'rss': process.memory_info().rss,
            'vms': process.memory_info().vms
        },
        'threads': process.num_threads(),
        'open_files': len(process.open_files()),
        'connections': len(process.connections()),
        'create_time': datetime.fromtimestamp(process.create_time()).isoformat()
    }), 200

@performance_bp.route('/database', methods=['GET'])
@token_required
@role_required('admin')
def get_database_stats():
    """Obtiene estadísticas de la base de datos"""
    from utils.database import get_db
    
    db = get_db()
    stats = db.command('dbStats')
    
    collections = []
    for coll_name in db.list_collection_names():
        count = db[coll_name].count_documents({})
        collections.append({
            'name': coll_name,
            'documents': count
        })
    
    return jsonify({
        'db_name': stats.get('db'),
        'collections': stats.get('collections'),
        'objects': stats.get('objects'),
        'avg_obj_size': stats.get('avgObjSize'),
        'data_size': stats.get('dataSize'),
        'storage_size': stats.get('storageSize'),
        'indexes': stats.get('indexes'),
        'index_size': stats.get('indexSize'),
        'collections_detail': collections
    }), 200