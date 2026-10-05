from middleware.auth_middleware import generate_token


def auth(role="admin"):
    token = generate_token("000000000000000000000001", f"{role}.test", role)
    return {"Authorization": f"Bearer {token}"}


def test_spark_endpoint_matrix_200_401_403_and_404(client):
    assert client.get("/api/v1/spark/overview", headers=auth()).status_code == 200
    assert client.get("/api/v1/spark/overview").status_code == 401
    assert client.get("/api/v1/spark/overview", headers=auth("medico")).status_code == 403
    assert client.get("/api/v1/route-that-does-not-exist", headers=auth()).status_code == 404


def test_cors_preflight_allows_versioned_api_from_web_origin(client):
    response = client.options(
        "/api/v1/spark/overview",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization, Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert "GET" in response.headers["Access-Control-Allow-Methods"]
    assert "Authorization" in response.headers["Access-Control-Allow-Headers"]
