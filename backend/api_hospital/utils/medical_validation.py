"""Validate clinical payloads before allocating IDs or writing records."""

HISTORY_FIELDS = ('motivo_consulta', 'sintomatologia', 'sintomatologia_otros', 'heredo', 'heredo_otros', 'nopat', 'nopat_otros', 'pat_enfermedades', 'pat_medicamentos', 'pat_alergias', 'pat_oculares', 'pat_cirugias')


def validate_medical_text(data, kind):
    if not isinstance(data, dict):
        return None, 'Se requiere un objeto JSON válido.'
    fields, required = {
        'history': (HISTORY_FIELDS, 'motivo_consulta'),
        'note': (('subjetivo', 'objetivo', 'analisis', 'plan'), 'subjetivo'),
        'diagnosis': (('diagnostico_principal', 'diagnosticos_secundarios', 'observaciones'), 'diagnostico_principal'),
    }[kind]
    result = {}
    for field in fields:
        value = data.get(field, '')
        if not isinstance(value, str):
            return None, 'Los campos clínicos deben contener texto.'
        limit = 500 if field == 'motivo_consulta' else 2000
        if len(value.strip()) > limit:
            return None, f'Un campo excede el límite de {limit} caracteres.'
        result[field] = value.strip()
    if not result[required] or (kind == 'history' and len(result[required]) < 3):
        return None, 'Completa el campo obligatorio antes de guardar.'
    return result, None


def validate_prescription(data):
    medications = data.get('medicamentos') if isinstance(data, dict) else None
    if not isinstance(medications, list) or not 1 <= len(medications) <= 10:
        return None, 'La receta debe contener entre 1 y 10 medicamentos.'
    result = []
    for medication in medications:
        if not isinstance(medication, dict):
            return None, 'Cada medicamento debe ser un objeto válido.'
        row = {}
        for field, limit in [('medicamento', 120), ('dosis', 80), ('frecuencia', 120), ('duracion', 80), ('indicaciones', 1000)]:
            value = medication.get(field, '')
            if not isinstance(value, str) or len(value.strip()) > limit:
                return None, 'Uno o más datos de la receta no son válidos.'
            row[field] = value.strip()
        if any(not row[field] for field in ('medicamento', 'dosis', 'frecuencia', 'duracion')):
            return None, 'Cada medicamento requiere nombre, dosis, frecuencia y duración.'
        result.append(row)
    return {'medicamentos': result}, None
