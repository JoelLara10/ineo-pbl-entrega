import os
from pathlib import Path

import pytest
import requests


@pytest.mark.sit
@pytest.mark.mutation
def test_cp_s11_sit_02_fallo_no_deja_metadatos_falsos():
    endpoint=os.getenv("SIT_UPLOAD_ENDPOINT")
    metadata=os.getenv("SIT_FILE_METADATA_ENDPOINT")
    if not endpoint or not metadata:
        pytest.skip("Configure SIT_UPLOAD_ENDPOINT y SIT_FILE_METADATA_ENDPOINT para la API real")
    if os.getenv("S11_ENABLE_MUTATION_TESTS","false").lower()!="true":
        pytest.skip("Prueba bloqueada hasta habilitar S11_ENABLE_MUTATION_TESTS=true")
    fixture=Path("qa/sprint-11/fixtures/estudio_sintetico.txt")
    headers={"X-QA-Force-Storage-Failure":"true"}
    with fixture.open("rb") as handle:
        response=requests.post(endpoint,files={"file":(fixture.name,handle,"text/plain")},headers=headers,timeout=30)
    assert response.status_code in {400,409,422,500,503}, response.text
    lookup=requests.get(metadata,params={"filename":fixture.name},timeout=20)
    assert lookup.status_code in {200,404}
    if lookup.status_code==200:
        payload=lookup.json()
        assert not payload or payload.get("status") in {"failed","rolled_back","cancelled"}

