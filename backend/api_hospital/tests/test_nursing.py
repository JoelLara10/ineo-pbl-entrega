NURSING_NOTES_URL = "/api/v1/appointments/1/nursing-notes"


def test_nursing_notes_read_requires_authentication(client):
    response = client.get(NURSING_NOTES_URL)

    assert response.status_code == 401
    assert response.get_json()["error"] == "Token no proporcionado"


def test_nursing_notes_write_requires_authentication(client):
    response = client.post(
        NURSING_NOTES_URL,
        json={"nota_enfermeria": "Control de prueba"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Token no proporcionado"
