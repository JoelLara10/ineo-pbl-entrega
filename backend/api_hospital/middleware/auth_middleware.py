from functools import wraps
from flask import request, jsonify, g
import jwt
from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4
from utils.database import get_collection

INSECURE_SECRET_KEYS = {
    '',
    'tu-clave-secreta',
    'tu-clave-secreta-muy-segura-cambiar-en-produccion',
    'jwt-secret-key-cambiar',
    'cambia-esta-clave-en-tu-entorno-local',
    'cambia-esta-clave-jwt-en-tu-entorno-local',
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
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': str(user_id),
        'username': username,
        'role': role,
        'jti': str(uuid4()),
        'exp': now + timedelta(hours=8),
        'iat': now,
        'nbf': now,
        'iss': 'ineo-api',
        'aud': 'ineo-clients',
    }
    return jwt.encode(payload, _get_secret_key(), algorithm='HS256')

def verify_token(token):
    """Verifica el token JWT"""
    try:
        payload = jwt.decode(
            token,
            _get_secret_key(),
            algorithms=['HS256'],
            issuer='ineo-api',
            audience='ineo-clients',
            options={'require': ['exp', 'iat', 'nbf', 'jti']},
        )
        if get_collection('revoked_tokens').find_one({'jti': payload['jti']}):
            return None
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
        auth_header = request.headers.get('Authorization', '')
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]
        
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

        # El rol se toma de la base actual, no del JWT manipulable o desactualizado.
        payload['role'] = current_user.get('role', 'user')
        payload['username'] = current_user.get('username', payload.get('username'))
        g.user = payload
        g.token = token
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


def revoke_current_token(payload):
    """Revoca el jti actual hasta su expiración sin almacenar el JWT completo."""
    jti = payload.get('jti')
    exp = payload.get('exp')
    if not jti or not exp:
        return False
    get_collection('revoked_tokens').update_one(
        {'jti': jti},
        {'$set': {'expires_at': datetime.fromtimestamp(exp, timezone.utc)}},
        upsert=True,
    )
    return True
