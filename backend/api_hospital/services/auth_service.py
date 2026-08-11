from models.user import UserModel
from middleware.auth_middleware import generate_token
from utils.database import get_collection
import bcrypt


class AuthService:
    @staticmethod
    def login(username, password):
        """Autentica un usuario y retorna token"""
        user = UserModel.find_by_username(username)
        
        if not user:
            print(f"❌ Usuario no encontrado: {username}")
            return None, 'Usuario no encontrado'
        
        # Verificación más robusta de contraseña
        if not UserModel.verify_password(user, password):
            print(f"❌ Contraseña incorrecta para usuario: {username}")
            return None, 'Contraseña incorrecta'
        
        print(f"✅ Login exitoso para usuario: {username} - Rol: {user.get('role')}")
        
        token = generate_token(
            user['_id'],
            user['username'],
            user.get('role', 'user')
        )
        
        return {
            'token': token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'role': user.get('role'),
                'nombre': user.get('nombre'),
                'papell': user.get('papell')
            }
        }, None

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Cambia la contraseña del usuario"""
        user = UserModel.find_by_id(user_id)
        
        if not user:
            return False, 'Usuario no encontrado'
        
        if not UserModel.verify_password(user, old_password):
            return False, 'Contraseña actual incorrecta'
        
        # Generar hash correctamente
        hashed = bcrypt.hashpw(
            new_password.encode('utf-8'), 
            bcrypt.gensalt()
        )
        
        # Guardar como bytes (recomendado con bcrypt)
        collection = get_collection('users')
        from bson import ObjectId
        
        collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password': hashed}}
        )
        
        print(f"✅ Contraseña actualizada para usuario: {user_id}")
        return True, 'Contraseña actualizada exitosamente'