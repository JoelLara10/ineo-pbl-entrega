import re


MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_BYTES = 72


def validate_password(password, username=''):
    """Valida contraseñas nuevas; no cambia credenciales antiguas al iniciar sesión."""
    if not isinstance(password, str):
        return False, 'La contraseña no es válida'
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, 'La contraseña debe tener al menos 12 caracteres'
    if len(password.encode('utf-8')) > MAX_PASSWORD_BYTES:
        return False, 'La contraseña es demasiado larga'
    if not re.search(r'[a-z]', password):
        return False, 'La contraseña debe incluir una minúscula'
    if not re.search(r'[A-Z]', password):
        return False, 'La contraseña debe incluir una mayúscula'
    if not re.search(r'\d', password):
        return False, 'La contraseña debe incluir un número'
    if username and username.casefold() in password.casefold():
        return False, 'La contraseña no debe contener el nombre de usuario'
    return True, None
