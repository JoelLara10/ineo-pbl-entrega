import bcrypt
import pytest

def test_health_endpoint_reports_api_available(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_login_requires_credentials(client):
    response = client.post("/api/v1/auth/login", json={})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_current_user_rejects_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == 401
    assert "error" in response.get_json()


def test_login_rejects_malformed_json(client):
    response = client.post(
        "/api/v1/auth/login",
        data="{",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Solicitud de inicio de sesión inválida"
    }


def test_login_rejects_oversized_password_before_authentication(
    client, monkeypatch
):
    def unexpected_login(*_args):
        raise AssertionError("AuthService.login no debe ejecutarse")

    monkeypatch.setattr(
        "routes.auth.AuthService.login",
        unexpected_login,
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "demo", "password": "x" * 73},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Solicitud de inicio de sesión inválida"
    }


def test_login_uses_generic_error_for_unknown_user(client, monkeypatch):
    monkeypatch.setattr(
        "routes.auth.AuthService.login",
        lambda *_args: (None, "Usuario no encontrado"),
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "usuario-inexistente", "password": "secreto"},
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Credenciales inválidas"}


def test_login_normalizes_username(client, monkeypatch):
    received = {}

    def fake_login(username, password):
        received.update(username=username, password=password)
        return {
            "token": "token-prueba",
            "user": {"id": "1", "username": username, "role": "admin"},
        }, None

    monkeypatch.setattr("routes.auth.AuthService.login", fake_login)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "  admin  ", "password": "secreto"},
    )

    assert response.status_code == 200
    assert received == {"username": "admin", "password": "secreto"}


def test_password_verification_does_not_print_hash(capsys):
    from models.user import UserModel

    password_hash = bcrypt.hashpw(b"secreto-seguro", bcrypt.gensalt())
    user = {"password": password_hash}

    assert UserModel.verify_password(user, "secreto-seguro") is True

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_malformed_password_hash_is_rejected_without_leaking_value(capsys):
    from models.user import UserModel

    sensitive_value = "hash-invalido-no-exponer"

    assert UserModel.verify_password(
        {"password": sensitive_value},
        "secreto",
    ) is False

    captured = capsys.readouterr()
    assert sensitive_value not in captured.out
    assert sensitive_value not in captured.err


def test_jwt_configuration_rejects_default_secret(monkeypatch):
    from middleware.auth_middleware import validate_jwt_configuration

    monkeypatch.setenv("SECRET_KEY", "tu-clave-secreta")

    with pytest.raises(RuntimeError, match="32 caracteres"):
        validate_jwt_configuration()


def test_jwt_configuration_accepts_strong_environment_secret(monkeypatch):
    from middleware.auth_middleware import validate_jwt_configuration

    monkeypatch.setenv("SECRET_KEY", "clave-prueba-segura-de-32-caracteres-minimo")

    assert validate_jwt_configuration() is None


def test_inactive_user_cannot_obtain_new_token(monkeypatch):
    from services.auth_service import AuthService
    from models.user import UserModel

    inactive_user = {
        "_id": "507f1f77bcf86cd799439011",
        "username": "usuario-inactivo",
        "role": "medico",
        "activo": False,
        "password": b"hash-no-usado",
    }

    monkeypatch.setattr(
        UserModel,
        "find_by_username",
        lambda _username: inactive_user,
    )
    monkeypatch.setattr(
        UserModel,
        "verify_password",
        lambda _user, _password: True,
    )

    result, error = AuthService.login("usuario-inactivo", "correcta")

    assert result is None
    assert error == "Credenciales inválidas"


def test_existing_token_is_revoked_when_user_is_inactive(client, monkeypatch):
    from middleware.auth_middleware import generate_token
    from models.user import UserModel

    monkeypatch.setattr(
        UserModel,
        "find_by_id",
        lambda _user_id: {"activo": False},
    )
    token = generate_token(
        "507f1f77bcf86cd799439011",
        "usuario-inactivo",
        "medico",
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Token inválido o expirado"}
