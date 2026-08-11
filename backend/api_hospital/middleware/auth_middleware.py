from functools import wraps
from flask import request, jsonify, g
import jwt
from datetime import datetime, timedelta
import os
from utils.database import get_collection

SECRET_KEY = os.getenv('SECRET_KEY', 'tu-clave-secreta')

def generate_token(user_id, username, role):
    """Genera un token JWT"""
    payload = {
        'user_id': str(user_id),
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=8),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verifica el token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar token en headers
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        g.user = payload
        return f(*args, **kwargs)
    
    return decorated

def role_required(*roles):
    """Decorador para requerir roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'user') or g.user.get('role') not in roles:
                return jsonify({'error': 'Permisos insuficientes'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator