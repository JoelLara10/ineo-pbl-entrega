def test_patients_requires_authentication(client):
    response = client.get("/api/v1/patients")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Token no proporcionado"


def test_administrative_patients_requires_authentication(client):
    response = client.get("/api/v1/gestion-pacientes")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Token no proporcionado"
