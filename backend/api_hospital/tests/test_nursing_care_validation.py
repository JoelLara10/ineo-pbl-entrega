from utils.nursing_care_validation import validate_nursing_care_payload


VALID = {
    'diagnostico_enfermeria': ' Riesgo de caída ',
    'objetivos': 'Evitar incidentes',
    'intervenciones': 'Mantener barandales elevados',
    'evaluacion': 'Paciente estable',
    'estado': 'EN_PROCESO',
    'observaciones': '',
}


def test_accepts_and_normalizes_valid_payload():
    normalized, error = validate_nursing_care_payload(VALID)
    assert error is None
    assert normalized['diagnostico_enfermeria'] == 'Riesgo de caída'


def test_rejects_missing_required_fields():
    normalized, error = validate_nursing_care_payload({'estado': 'EN_PROCESO'})
    assert normalized is None
    assert 'diagnostico_enfermeria' in error


def test_rejects_unapproved_state():
    normalized, error = validate_nursing_care_payload({**VALID, 'estado': 'BORRADO'})
    assert normalized is None
    assert 'estado' in error.lower()


def test_rejects_oversized_text():
    normalized, error = validate_nursing_care_payload({
        **VALID, 'observaciones': 'x' * 1001
    })
    assert normalized is None
    assert '1000' in error
