from utils.database import get_collection, serialize_doc, get_next_sequence
from bson.binary import Binary
import base64
import binascii
import bcrypt

class UserModel:
    @staticmethod
    def create(data):
        """Crea un nuevo usuario"""
        collection = get_collection('users')
        
        # Encriptar contraseña
        password = data.get('password', '').encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        
        user = {
            'id': get_next_sequence('users_id'),
            'username': data.get('username'),
            'password': hashed,
            'role': data.get('role', 'user'),
            'nombre': data.get('nombre', ''),
            'papell': data.get('papell', ''),
            'sapell': data.get('sapell', ''),
            'email': data.get('email', ''),
            'telefono': data.get('telefono', ''),
            'activo': True
        }
        
        result = collection.insert_one(user)
        return serialize_doc(user)
    
    @staticmethod
    def find_by_username(username):
        """Busca usuario por username"""
        collection = get_collection('users')
        user = collection.find_one({'username': username})
        return user
    
    @staticmethod
    def find_by_id(user_id):
        """Busca usuario por ID"""
        collection = get_collection('users')
        from bson import ObjectId
        try:
            user = collection.find_one({'_id': ObjectId(user_id)})
        except:
            user = collection.find_one({'id': int(user_id)})
        return user
    
    @staticmethod
    def get_all(page=1, page_size=20, role=None):
        """Obtiene todos los usuarios paginados"""
        collection = get_collection('users')
        
        query = {}
        if role:
            query['role'] = role
        
        skip = (page - 1) * page_size
        
        total = collection.count_documents(query)
        users = list(collection.find(query).skip(skip).limit(page_size))
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'data': [serialize_doc(u) for u in users]
        }
    
    @staticmethod
    def verify_password(user, password):
        """Verifica la contraseña sin exponer hashes ni detalles internos."""

        if not user or 'password' not in user:
            return False

        try:
            stored = UserModel._normalize_password_hash(user['password'])

            # SEGURIDAD (Jaime): el hash y el resultado de bcrypt nunca se imprimen.
            # Los registros de producción podrían ser consultados por terceros y
            # un hash filtrado permitiría ataques de fuerza bruta fuera del sistema.
            return bcrypt.checkpw(password.encode("utf-8"), stored)

        except (TypeError, ValueError):
            # SEGURIDAD (Jaime): un hash malformado se trata como credencial
            # inválida sin mostrar el valor recibido ni el detalle de la excepción.
            return False
        
    @staticmethod
    def _normalize_password_hash(stored):
        """Convierte cualquier formato de password almacenado a bytes válidos"""

        # Caso 1: bytes reales
        if isinstance(stored, bytes):
            return stored

        # Caso 2: BSON Binary (MongoDB)
        if isinstance(stored, Binary):
            return bytes(stored)

        # Caso 3: string tipo "b'...'"
        if isinstance(stored, str):
            if stored.startswith("b'") and stored.endswith("'"):
                return stored[2:-1].encode("utf-8")

            # Caso 4: string base64
            try:
                decoded = base64.b64decode(stored, validate=True)
                if decoded.startswith(b"$2"):
                    return decoded
            except (binascii.Error, ValueError):
                decoded = None

            # Caso 5: string normal
            return stored.encode("utf-8")

        # Fallback
        return str(stored).encode("utf-8")
