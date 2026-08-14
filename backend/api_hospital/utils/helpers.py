from functools import wraps
from flask import jsonify
import logging
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handle_exceptions(f):
    """Decorador para manejar excepciones en rutas"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error en {f.__name__}: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    return decorated

def log_request(f):
    """Decorador para loggear requests"""
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, g
        
        logger.info(f"Request: {request.method} {request.path} - User: {getattr(g, 'user', {}).get('username', 'Anonymous')}")
        
        return f(*args, **kwargs)
    return decorated

def paginate(data, page, page_size):
    """Pagina una lista de datos"""
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        'data': data[start:end],
        'page': page,
        'page_size': page_size,
        'total': len(data),
        'total_pages': (len(data) + page_size - 1) // page_size
    }

def generate_response(success, message=None, data=None, status_code=200):
    """Genera una respuesta estandarizada"""
    response = {'success': success}
    
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def parse_date(date_string, format='%Y-%m-%d'):
    """Parsea una fecha de string a datetime"""
    try:
        return datetime.strptime(date_string, format)
    except (ValueError, TypeError):
        return None

def get_date_range(period='today'):
    """Obtiene rango de fechas para diferentes períodos"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if period == 'today':
        start = today
        end = today.replace(hour=23, minute=59, second=59)
    elif period == 'yesterday':
        start = today - timedelta(days=1)
        end = start.replace(hour=23, minute=59, second=59)
    elif period == 'week':
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        end = end.replace(hour=23, minute=59, second=59)
    elif period == 'month':
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month+1, day=1) - timedelta(days=1)
        end = end.replace(hour=23, minute=59, second=59)
    else:
        start = None
        end = None
    
    return start, end