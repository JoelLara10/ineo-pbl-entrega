import json
import os
from pathlib import Path

import pytest

from pages.login_page import LoginPage
from pages.turno_page import TurnoPage
from conftest import require_env


@pytest.mark.ui
@pytest.mark.mutation
def test_cp_s11_ui_01_turno_completo(browser, require_mutation_enabled):
    require_env("QA_URL", "ENFERMERIA_LOGIN_USR", "ENFERMERIA_LOGIN_PSW", "TURN_ROUTE")
    fixture=json.loads(Path("qa/sprint-11/fixtures/turno_sintetico.json").read_text(encoding="utf-8"))
    LoginPage(browser).open(os.environ["QA_URL"]).login(
        os.environ["ENFERMERIA_LOGIN_USR"], os.environ["ENFERMERIA_LOGIN_PSW"]
    )
    page=TurnoPage(browser); page.open_route(os.environ["QA_URL"],os.environ["TURN_ROUTE"])
    page.registrar_turno_sintetico(fixture)
    browser.refresh()
    assert page.contains_fixture(fixture), "Los datos del turno no persistieron después de recargar"

