import os
import time
import uuid

import pytest
import requests


API = os.getenv("INEO_API_URL", "https://api-clinica-jx4m.onrender.com").rstrip("/")
TOKEN = os.getenv("INEO_QA_TOKEN")


def headers():
    if not TOKEN:
        pytest.skip("Defina INEO_QA_TOKEN de una cuenta sintética admin/administrativo")
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


@pytest.mark.sit
def test_cp_s10_sit_01_paciente_persiste():
    suffix = uuid.uuid4().hex[:8].upper()
    payload = {"curp": f"SINT{suffix}HMCQA", "papell": "PRUEBA", "nom_pac": "PACIENTE SINTETICO", "fecnac": "2000-01-01"}
    created = requests.post(f"{API}/api/v1/patients", json=payload, headers=headers(), timeout=30)
    assert created.status_code == 201, created.text
    patient = created.json()
    patient_id = patient.get("id_exp") or patient.get("id")
    assert patient_id
    read = requests.get(f"{API}/api/v1/patients/{patient_id}", headers=headers(), timeout=30)
    assert read.status_code == 200, read.text
    assert read.json().get("curp") == payload["curp"]


@pytest.mark.sit
def test_cp_s10_sit_02_contrato_valoracion():
    invalid = requests.post(f"{API}/api/v1/nursing/assessment", json={}, headers=headers(), timeout=30)
    assert invalid.status_code == 400, invalid.text
    valid_payload = {"id_exp": int(os.getenv("INEO_QA_PATIENT_ID", "0")), "observaciones": "Fixture sintético Sprint 10"}
    if not valid_payload["id_exp"]:
        pytest.skip("Defina INEO_QA_PATIENT_ID para ejecutar el camino válido")
    valid = requests.post(f"{API}/api/v1/nursing/assessment", json=valid_payload, headers=headers(), timeout=30)
    assert valid.status_code in (200, 201), valid.text


@pytest.mark.sit
def test_cp_s10_sit_03_estado_y_resultado_spark():
    kind = os.getenv("INEO_SPARK_KIND", "general")
    run = requests.post(f"{API}/api/v1/spark/run/{kind}", json={}, headers=headers(), timeout=30)
    assert run.status_code in (200, 202), run.text
    terminal = None
    for _ in range(24):
        status = requests.get(f"{API}/api/v1/spark/status/{kind}", headers=headers(), timeout=30)
        assert status.status_code == 200, status.text
        terminal = status.json()
        if str(terminal).lower().find("completed") >= 0 or str(terminal).lower().find("failed") >= 0:
            break
        time.sleep(5)
    assert "completed" in str(terminal).lower(), terminal
    result = requests.get(f"{API}/api/v1/spark/{kind}", headers=headers(), timeout=30)
    assert result.status_code == 200 and result.json(), result.text

