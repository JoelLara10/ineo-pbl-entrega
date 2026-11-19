import json
import os
from pathlib import Path

import pytest


@pytest.mark.sast
def test_cp_s11_sast_02_hotspot_revisado():
    path=Path(os.getenv("SONAR_REPORT_PATH","qa/sprint-11/reports/sonar-hotspots.json"))
    if not path.exists():
        pytest.skip(f"No existe el reporte real de SonarQube: {path}")
    report=json.loads(path.read_text(encoding="utf-8"))
    hotspots=report.get("hotspots",report.get("results",[]))
    assert hotspots, "El reporte no contiene el hotspot del fixture controlado"
    unresolved=[]
    for hotspot in hotspots:
        status=str(hotspot.get("status",hotspot.get("resolution",""))).upper()
        if status not in {"REVIEWED","SAFE","FIXED","ACKNOWLEDGED"}:
            unresolved.append(hotspot.get("key",hotspot.get("message","sin identificador")))
    assert not unresolved, f"Hotspots sin revisión: {unresolved}"

