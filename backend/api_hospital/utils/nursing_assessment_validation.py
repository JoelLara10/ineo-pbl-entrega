"""Validate assessment fields before allocating an ID or writing clinical records."""
import re

REQUIRED_FIELDS = ('estado_general', 'dolor', 'movilidad', 'riesgo_caidas', 'riesgo_upp')
MAX_TEXT_LENGTH = 1000
NUMERIC_PAIN = re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z')


def validate_nursing_assessment(data):
    if not isinstance(data, dict):
        return None, 'La valoración debe ser un objeto JSON.'
    normalized = {}
    for field in (*REQUIRED_FIELDS, 'observaciones'):
        value = data.get(field, '')
        if not isinstance(value, str):
            return None, f'El campo {field} debe ser texto.'
        value = value.strip()
        if field in REQUIRED_FIELDS and not value:
            return None, f'El campo {field} es obligatorio.'
        if len(value) > MAX_TEXT_LENGTH:
            return None, f'El campo {field} no puede exceder {MAX_TEXT_LENGTH} caracteres.'
        normalized[field] = value
    # The existing UI accepts either a 0-10 score or a free-text description.
    pain = normalized['dolor']
    if NUMERIC_PAIN.fullmatch(pain) and not 0 <= float(pain) <= 10:
        return None, 'El dolor numérico debe estar entre 0 y 10; también puedes escribir una descripción.'
    return normalized, None
