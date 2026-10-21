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


def test_cp_ut_003_rejected_upload_does_not_persist_file(client, monkeypatch):
    """Un archivo inseguro se rechaza antes de llamar al servicio de persistencia."""
    persisted = False

    def unexpected_save(*_args, **_kwargs):
        nonlocal persisted
        persisted = True

    monkeypatch.setattr("routes.studies.StudyService.save_results", unexpected_save)