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
