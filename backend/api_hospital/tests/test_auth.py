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
