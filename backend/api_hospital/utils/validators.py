import re
from datetime import datetime

def validate_curp(curp):
    """Valida formato de CURP"""
    if not curp or len(curp) != 18:
        return False
    
    pattern = r'^[A-Z]{4}\d{6}[A-Z]{6}\d{2}$'
    return bool(re.match(pattern, curp))

def validate_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """Valida número telefónico mexicano"""
    pattern = r'^(\d{10}|\d{3}-\d{3}-\d{4}|\d{10})$'
    return bool(re.match(pattern, phone))

def calculate_age(birth_date):
    """Calcula edad a partir de fecha de nacimiento"""
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
    
    today = datetime.now().date()
    age = today.year - birth_date.year
    
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age

def format_currency(amount):
    """Formatea un número como moneda"""
    return f"${amount:,.2f}"

def validate_date_range(start_date, end_date):
    """Valida que el rango de fechas sea válido"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    return start_date <= end_date

def sanitize_string(text):
    """Limpia y sanitiza strings"""
    if not text:
        return ''
    # Eliminar espacios extra
    text = ' '.join(text.split())
    # Escapar caracteres especiales si es necesario
    return text