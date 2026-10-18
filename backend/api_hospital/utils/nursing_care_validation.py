"""Validación pura del módulo remoto de cuidados de enfermería."""

CARE_STATES = {'EN_PROCESO', 'PENDIENTE', 'COMPLETADO'}
REQUIRED_FIELDS = ('diagnostico_enfermeria', 'objetivos', 'intervenciones')
OPTIONAL_FIELDS = ('evaluacion', 'observaciones')
MAX_TEXT_LENGTH = 1000


def _clean_text(value):
    """Normaliza texto sin convertir listas u objetos en cadenas."""
    return value.strip() if isinstance(value, str) else ''


def validate_nursing_care_payload(data):
    """Devuelve (datos_normalizados, error) sin guardar información."""
    if not isinstance(data, dict):
        return None, 'El cuerpo de la solicitud debe ser un objeto JSON.'

    # Lista permitida: campos inesperados nunca llegan a la base de datos.
    normalized = {
        field: _clean_text(data.get(field))
        for field in REQUIRED_FIELDS + OPTIONAL_FIELDS
    }
    normalized['estado'] = _clean_text(data.get('estado')) or 'EN_PROCESO'

    for field in REQUIRED_FIELDS:
        length = len(normalized[field])
        if length < 3 or length > MAX_TEXT_LENGTH:
            return None, (
                f'El campo {field} debe tener entre 3 y '
                f'{MAX_TEXT_LENGTH} caracteres.'
            )

    if any(len(normalized[field]) > MAX_TEXT_LENGTH for field in OPTIONAL_FIELDS):
        return None, f'Los campos opcionales no pueden exceder {MAX_TEXT_LENGTH} caracteres.'

    if normalized['estado'] not in CARE_STATES:
        return None, 'El estado del cuidado no es válido.'

    return normalized, None
