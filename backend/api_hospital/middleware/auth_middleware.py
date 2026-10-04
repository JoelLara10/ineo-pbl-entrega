from functools import wraps
from flask import request, jsonify, g
import jwt
from datetime import datetime, timedelta
import os
from utils.database import get_collection

INSECURE_SECRET_KEYS = {
    '',
    'tu-clave-secreta',
    'tu-clave-secreta-muy-segura-cambiar-en-produccion',
    'jwt-secret-key-cambiar',
}


def _get_secret_key():
    """Obtiene una clave JWT fuerte o detiene la aplicación de forma segura."""
    secret_key = os.getenv('SECRET_KEY', '').strip()

    # SEGURIDAD (Zahid): una clave corta o predeterminada permite que un
    # atacante fabrique tokens válidos. Se exige un secreto real de 32
    # caracteres como mínimo y configurado mediante variable de entorno.
    if (
        secret_key in INSECURE_SECRET_KEYS
        or len(secret_key) < 32
    ):
        raise RuntimeError(
            'SECRET_KEY debe configurarse con al menos 32 caracteres seguros'
        )

    return secret_key


def validate_jwt_configuration():
    """Valida la configuración JWT durante el arranque de la API."""
    _get_secret_key()

def generate_token(user_id, username, role):
    """Genera un token JWT"""
    payload = {
        'user_id': str(user_id),
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=8),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, _get_secret_key(), algorithm='HS256')

def verify_token(token):
    """Verifica el token JWT"""
    try:
        payload = jwt.decode(token, _get_secret_key(), algorithms=['HS256'])
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

        # SEGURIDAD (Jesús): el JWT por sí solo no garantiza que la cuenta siga
        # autorizada. Se consulta el estado actual para revocar inmediatamente
        # los tokens de usuarios eliminados o desactivados.
        from models.user import UserModel
        current_user = UserModel.find_by_id(payload.get('user_id'))

        if not current_user or not current_user.get('activo', True):
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