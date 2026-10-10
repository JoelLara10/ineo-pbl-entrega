from flask import Blueprint, request, jsonify, g
from services.auth_service import AuthService
from middleware.auth_middleware import token_required, revoke_current_token
from security.login_limiter import login_limiter
from security.password_policy import validate_password
from config import config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/users', methods=['OPTIONS'])
def users_options():
    return '', 204


@auth_bp.route('/users/<user_id>', methods=['OPTIONS'])
def user_options(user_id):
    return '', 204


MAX_USERNAME_LENGTH = 80
MAX_PASSWORD_BYTES = 72


def _validated_login_payload():
    """Retorna credenciales normalizadas o None sin procesar entradas inseguras."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None

    username = data.get('username')
    password = data.get('password')

    if not isinstance(username, str) or not isinstance(password, str):
        return None

    username = username.strip()

    if (
        not username
        or not password
        or len(username) > MAX_USERNAME_LENGTH
        or len(password.encode('utf-8')) > MAX_PASSWORD_BYTES
    ):
        return None

    return username, password


@auth_bp.route('/login', methods=['POST'])
def login():
    credentials = _validated_login_payload()

    if credentials is None:
        return jsonify({'error': 'Solicitud de inicio de sesión inválida'}), 400

    username, password = credentials
    limiter_key = login_limiter.key(username, request.remote_addr)
    allowed, retry_after = login_limiter.check(
        limiter_key,
        config.LOGIN_MAX_ATTEMPTS,
        config.LOGIN_WINDOW_SECONDS,
    )
    if not allowed:
        response = jsonify({
            'error': 'Demasiados intentos. Intenta nuevamente más tarde'
        })
        response.status_code = 429
        response.headers['Retry-After'] = str(retry_after)
        return response

    result, error = AuthService.login(username, password)

    if error:
        login_limiter.failure(limiter_key, config.LOGIN_WINDOW_SECONDS)
        # Respuesta deliberadamente genérica para impedir enumeración de usuarios.
        return jsonify({'error': 'Credenciales inválidas'}), 401

    login_limiter.success(limiter_key)
    return jsonify(result), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    from models.user import UserModel

    user = UserModel.find_by_id(g.user['user_id'])

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({
        'id': str(user.get('_id') or user.get('id')),
        'username': user.get('username'),
        'role': user.get('role'),
        'nombre': user.get('nombre'),
        'papell': user.get('papell'),
        'sapell': user.get('sapell'),
        'email': user.get('email'),
        'telefono': user.get('telefono'),
        'activo': user.get('activo', True)
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'error': 'Solicitud inválida'}), 400

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if (
        not isinstance(old_password, str)
        or not isinstance(new_password, str)
        or not old_password
        or not new_password
    ):
        return jsonify({'error': 'Contraseñas requeridas'}), 400

    valid, message = validate_password(new_password, g.user.get('username', ''))
    if not valid:
        return jsonify({'error': message}), 400

    success, message = AuthService.change_password(
        g.user['user_id'],
        old_password,
        new_password
    )

    if not success:
        return jsonify({'error': message}), 400

    return jsonify({'message': message}), 200


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    revoke_current_token(g.user)
    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200


def is_admin():
    return g.user.get('role') == 'admin'


@auth_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    from utils.database import get_collection, serialize_doc

    if not is_admin():
        return jsonify({'error': 'No autorizado'}), 403

    try:
        collection = get_collection('users')
        users = list(collection.find({}, {'password': 0}).limit(100))

        return jsonify({
            'total': len(users),
            'page': 1,
            'page_size': 100,
            'total_pages': 1,
            'data': [serialize_doc(user) for user in users]
        }), 200

    except Exception as e:
        print("ERROR GET USERS", flush=True)
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth_bp.route('/users', methods=['POST'])
@token_required
def create_user():
    from models.user import UserModel

    if not is_admin():
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'error': 'Solicitud inválida'}), 400

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400

    username = data.get('username')
    if not isinstance(username, str) or not username.strip() or len(username) > 80:
        return jsonify({'error': 'Nombre de usuario inválido'}), 400
    data['username'] = username.strip()

    allowed_roles = {'admin', 'administrativo', 'medico', 'enfermero', 'estudios'}
    if data.get('role', 'estudios') not in allowed_roles:
        return jsonify({'error': 'Rol inválido'}), 400
    data['role'] = data.get('role', 'estudios')

    valid, message = validate_password(data.get('password'), data['username'])
    if not valid:
        return jsonify({'error': message}), 400

    existing = UserModel.find_by_username(data.get('username'))

    if existing:
        return jsonify({'error': 'El usuario ya existe'}), 400

    user = UserModel.create(data)

    if 'password' in user:
        del user['password']

    return jsonify(user), 201


@auth_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    from bson import ObjectId
    from utils.database import get_collection

    if not is_admin():
        return jsonify({'error': 'No autorizado'}), 403

    if str(g.user.get('user_id')) == str(user_id) and (
        request.get_json(silent=True) or {}
    ).get('activo') is False:
        return jsonify({'error': 'No puedes desactivar tu propia cuenta'}), 409

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Solicitud inválida'}), 400
    collection = get_collection('users')

    allowed_fields = [
        'username',
        'role',
        'nombre',
        'papell',
        'sapell',
        'email',
        'telefono',
        'activo'
    ]

    update_data = {}

    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]

    if 'role' in update_data and update_data['role'] not in {
        'admin', 'administrativo', 'medico', 'enfermero', 'estudios'
    }:
        return jsonify({'error': 'Rol inválido'}), 400

    if not update_data:
        return jsonify({'error': 'No hay datos para actualizar'}), 400

    try:
        result = collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    except Exception:
        try:
            result = collection.update_one(
                {'id': int(user_id)},
                {'$set': update_data}
            )
        except Exception:
            result = collection.update_one(
                {'id': user_id},
                {'$set': update_data}
            )

    if result.matched_count == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({'message': 'Usuario actualizado correctamente'}), 200


@auth_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    from bson import ObjectId
    from utils.database import get_collection

    if not is_admin():
        return jsonify({'error': 'No autorizado'}), 403

    if str(g.user.get('user_id')) == str(user_id):
        return jsonify({'error': 'No puedes eliminar tu propia cuenta'}), 409

    collection = get_collection('users')

    try:
        result = collection.delete_one({'_id': ObjectId(user_id)})
    except Exception:
        try:
            result = collection.delete_one({'id': int(user_id)})
        except Exception:
            result = collection.delete_one({'id': user_id})

    if result.deleted_count == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({'message': 'Usuario eliminado correctamente'}), 200
