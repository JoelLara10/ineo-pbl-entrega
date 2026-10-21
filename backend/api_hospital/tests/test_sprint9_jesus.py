"""Pruebas unitarias de PBL-27 asignadas a Jesús en el Sprint 9."""

from io import BytesIO

import pytest


def auth_headers(role="admin"):
    """Genera un token sintético sin depender de usuarios o servicios externos."""
    from middleware.auth_middleware import generate_token

    role_ids = {
        "admin": "000000000000000000000001",
        "medico": "000000000000000000000002",
        "enfermero": "000000000000000000000003",
        "estudios": "000000000000000000000004",
    }
    token = generate_token(
        role_ids[role],
        f"{role}.sprint9",
        role,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({"username": "usuario", "password": "correcta"}, 200),
        ({"username": "usuario", "password": "incorrecta"}, 401),
        ({}, 400),
    ],
)
def test_cp_ut_001_auth_valid_and_invalid_credentials(
    client, monkeypatch, payload, expected_status
):
    """CP-UT-001: solo las credenciales válidas generan un token."""

    def fake_login(username, password):
        if username == "usuario" and password == "correcta":
            return {
                "token": "token-sintetico",
                "user": {"id": "1", "username": username, "role": "enfermero"},
            }, None
        return None, "Credenciales inválidas"

    monkeypatch.setattr("routes.auth.AuthService.login", fake_login)
    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.get_json()["token"] == "token-sintetico"
    else:
        assert "error" in response.get_json()


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [("admin", 200), ("medico", 403), ("enfermero", 403), ("estudios", 403)],
)
def test_cp_ut_002_admin_endpoint_applies_role_permissions(client, role, expected_status):
    """CP-UT-002: el listado de usuarios respeta la matriz de permisos."""
    response = client.get("/api/v1/auth/users", headers=auth_headers(role))

    assert response.status_code == expected_status
    if expected_status == 403:
        assert "error" in response.get_json()


@pytest.mark.parametrize(
    ("filename", "is_allowed"),
    [
        ("resultado.pdf", True),
        ("radiografia.PNG", True),
        ("informe.docx", True),
        ("sin-extension", False),
        ("script.exe", False),
        ("archivo.pdf.exe", False),
    ],
)
def test_cp_ut_003_study_file_extension_validation(filename, is_allowed):
    """CP-UT-003: acepta extensiones clínicas válidas y rechaza las inseguras."""
    from routes.studies import allowed_file

    assert allowed_file(filename) is is_allowed


def test_cp_ut_003_rejected_upload_does_not_persist_file(client, monkeypatch, tmp_path):
    """Un archivo inseguro se rechaza antes de llamar al servicio de persistencia."""
    monkeypatch.setattr("routes.studies.UPLOAD_FOLDER_GAB", str(tmp_path))
    monkeypatch.setattr("routes.studies.UPLOAD_FOLDER_LAB", str(tmp_path))
    persisted = False

    def unexpected_save(*_args, **_kwargs):
        nonlocal persisted
        persisted = True

    monkeypatch.setattr("routes.studies.StudyService.save_results", unexpected_save)
    response = client.post(
        '/api/v1/25/upload',
        headers=auth_headers('estudios'),
        data={'files': (BytesIO(b'synthetic unsafe file'), 'resultado.pdf.exe')},
        content_type='multipart/form-data',
    )
    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert persisted is False
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('filename', ['resultado.pdf', 'radiografia.PNG'])
def test_cp_ut_003_valid_upload_uses_temporary_storage(client, monkeypatch, tmp_path, filename):
    from unittest.mock import Mock
    import routes.studies as studies

    save_results = Mock(return_value=True)
    monkeypatch.setattr(studies, 'UPLOAD_FOLDER_GAB', str(tmp_path))
    monkeypatch.setattr(studies.StudyService, 'get_study_details', lambda _id: {'tipo': 'GABINETE'})
    monkeypatch.setattr(studies.StudyService, 'save_results', save_results)
    payload = b'synthetic clinical attachment'
    response = client.post(
        '/api/v1/25/upload', headers=auth_headers('estudios'),
        data={'files': (BytesIO(payload), filename), 'observaciones': 'Datos sinteticos'},
        content_type='multipart/form-data',
    )
    expected = tmp_path / f'25_{filename}'
    assert response.status_code == 200
    assert response.json['files'] == [str(expected)]
    assert expected.read_bytes() == payload
    save_results.assert_called_once_with(25, [str(expected)], 'Datos sinteticos')


@pytest.mark.parametrize('data', [{}, {'files': (BytesIO(b''), '')}])
def test_cp_ut_003_missing_file_does_not_persist(client, monkeypatch, tmp_path, data):
    from unittest.mock import Mock
    import routes.studies as studies

    save_results = Mock()
    monkeypatch.setattr(studies, 'UPLOAD_FOLDER_GAB', str(tmp_path))
    monkeypatch.setattr(studies, 'UPLOAD_FOLDER_LAB', str(tmp_path))
    monkeypatch.setattr(studies.StudyService, 'save_results', save_results)
    response = client.post('/api/v1/25/upload', headers=auth_headers('estudios'),
                           data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert 'error' in response.json
    save_results.assert_not_called()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('role', ['medico', 'enfermero'])
def test_cp_ut_002_upload_denied_before_persistence(client, monkeypatch, role):
    from unittest.mock import Mock

    save_results = Mock()
    monkeypatch.setattr('routes.studies.StudyService.save_results', save_results)
    response = client.post('/api/v1/25/upload', headers=auth_headers(role),
                           data={'files': (BytesIO(b'synthetic'), 'resultado.pdf')})
    assert response.status_code == 403
    save_results.assert_not_called()


@pytest.mark.parametrize(
    ('diagnoses', 'ages', 'stays', 'expected'),
    [
        ([], [], [], {'top_diagnosis': [], 'age_distribution': [], 'average_stay_days': 0}),
        ([{'_id': 'Sintetico', 'count': 1}], [], [],
         {'top_diagnosis': [{'diagnosis': 'Sintetico', 'count': 1}],
          'age_distribution': [], 'average_stay_days': 0}),
        ([{'_id': 'Sintetico', 'count': 3}], [{'_id': 18, 'count': 2}], [{'promedio': 2.345}],
         {'top_diagnosis': [{'diagnosis': 'Sintetico', 'count': 3}],
          'age_distribution': [{'range': '18', 'count': 2}], 'average_stay_days': 2.35}),
    ], ids=['empty', 'partial', 'valid'],
)
def test_cp_ut_004_clinical_analytics_schema_and_values(
    client, monkeypatch, diagnoses, ages, stays, expected
):
    """Ejecuta el servicio real con agregaciones simuladas, sin Mongo ni Spark."""
    from unittest.mock import MagicMock

    db = {name: MagicMock() for name in ('diagnosticos', 'atencion', 'expedientes')}
    db['diagnosticos'].aggregate.return_value = iter(diagnoses)
    db['atencion'].aggregate.return_value = iter(ages)
    db['expedientes'].aggregate.return_value = iter(stays)
    collection = MagicMock()
    collection.database = db
    monkeypatch.setattr('services.analytics_service.get_collection', lambda _name: collection)
    # Route + real service: do not mock the result being verified.
    response = client.get('/api/v1/clinical', headers=auth_headers('medico'))
    assert response.status_code == 200
    assert response.json == expected
    assert set(response.json) == {'top_diagnosis', 'age_distribution', 'average_stay_days'}
    db['diagnosticos'].aggregate.assert_called_once()
    db['atencion'].aggregate.assert_called_once()
    db['expedientes'].aggregate.assert_called_once()


@pytest.mark.parametrize('role', ['enfermero', 'estudios'])
def test_cp_ut_004_clinical_analytics_rejects_unauthorized_roles(client, monkeypatch, role):
    from unittest.mock import Mock

    service = Mock()
    monkeypatch.setattr('routes.analytics.AnalyticsService.get_clinical_analytics', service)
    response = client.get('/api/v1/clinical', headers=auth_headers(role))
    assert response.status_code == 403
    service.assert_not_called()
