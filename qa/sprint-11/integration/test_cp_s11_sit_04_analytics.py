import json
import os
from pathlib import Path

import pytest
import requests


@pytest.mark.sit
def test_cp_s11_sit_04_datos_parciales_analytics():
    endpoint=os.getenv("SIT_ANALYTICS_ENDPOINT")
    if not endpoint:
        pytest.skip("Configure SIT_ANALYTICS_ENDPOINT para ejecutar contra la API real")
    fixture=json.loads(Path("qa/sprint-11/fixtures/analytics_parcial.json").read_text(encoding="utf-8"))
    response=requests.post(endpoint,json=fixture,timeout=60)
    assert response.status_code==200, response.text
    payload=response.json()
    assert payload is not None
    assert "error" not in payload or not payload["error"]
    valid=[item["valor"] for item in fixture["registros"] if item.get("valor") is not None]
    expected=sum(valid)/len(valid)
    metric=payload.get("promedio",payload.get("average"))
    assert metric is not None, "La API no devolvió una métrica comprobable"
    assert abs(float(metric)-expected)<0.0001

