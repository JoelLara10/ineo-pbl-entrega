"""Validate nursing input before allocating identifiers or writing records."""
from datetime import datetime
import math
import re

VOLUME_FIELDS = ('ingresos_orales', 'ingresos_iv', 'egresos_orina', 'egresos_drenajes')


def number(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError('Número inválido')
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('Número inválido')
    return result


def validate_vitals(data):
    if not isinstance(data, dict):
        return None, 'Los signos vitales deben ser un objeto JSON.'
    result = {}
    ta = data.get('ta', '')
    if not isinstance(ta, str):
        return None, 'La presión arterial debe usar el formato 120/80.'
    if ta.strip():
        if not re.fullmatch(r'[1-9]\d{0,2}/[1-9]\d{0,2}', ta.strip()):
            return None, 'La presión arterial debe usar el formato 120/80.'
        result['ta'] = ta.strip()
    for field in ('fc', 'fr', 'temp', 'spo2', 'peso', 'talla'):
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        try:
            value = number(value)
        except (ValueError, TypeError, OverflowError):
            return None, f'El campo {field} debe ser un número válido.'
        if value < 0 or (field != 'spo2' and value == 0) or (field == 'spo2' and value > 100):
            return None, f'El campo {field} está fuera del rango permitido.'
        if field in ('fc', 'fr') and not value.is_integer():
            return None, f'El campo {field} debe ser entero.'
        result[field] = value
    if not result:
        return None, 'Captura al menos un signo vital.'
    return result, None


def validate_medications(data):
    rows = data.get('medicamentos') if isinstance(data, dict) else None
    if not isinstance(rows, list) or not 1 <= len(rows) <= 10:
        return None, 'El registro debe contener entre 1 y 10 medicamentos.'
    result = []
    limits = {'nombre': 120, 'dosis': 80, 'frecuencia': 120, 'via': 60, 'fecha_aplicacion': 10}
    for row in rows:
        if not isinstance(row, dict):
            return None, 'Cada medicamento debe ser un objeto JSON.'
        clean = {}
        for field, limit in limits.items():
            value = row.get(field)
            if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
                return None, 'Completa medicamento, dosis, frecuencia, vía y fecha de aplicación.'
            clean[field] = value.strip()
        try:
            date = datetime.strptime(clean['fecha_aplicacion'], '%d/%m/%Y').date()
            if date.strftime('%d/%m/%Y') != clean['fecha_aplicacion'] or date > datetime.now().date():
                raise ValueError()
        except ValueError:
            return None, 'La fecha debe ser válida, usar DD/MM/AAAA y no estar en el futuro.'
        result.append(clean)
    return {'medicamentos': result}, None


def validate_balance(data):
    if not isinstance(data, dict):
        return None, 'El balance debe ser un objeto JSON.'
    result = {}
    for field in VOLUME_FIELDS:
        raw = data.get(field, '')
        try:
            value = 0 if raw == '' else number(raw)
        except (ValueError, TypeError, OverflowError):
            return None, 'Los volúmenes deben ser números entre 0 y 100000 ml.'
        if not 0 <= value <= 100000:
            return None, 'Los volúmenes deben ser números entre 0 y 100000 ml.'
        result[field] = value
    if not any(result.values()):
        return None, 'Captura al menos un ingreso o egreso mayor que cero.'
    text = data.get('observaciones', '')
    if not isinstance(text, str) or len(text.strip()) > 1000:
        return None, 'Las observaciones deben tener hasta 1000 caracteres.'
    result['observaciones'] = text.strip()
    return result, None
