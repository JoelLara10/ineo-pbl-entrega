import os

import pytest

from pages.login_page import LoginPage
from conftest import require_env


@pytest.mark.ui
def test_cp_s11_ui_05_cache_no_expone_sesion(browser):
    require_env("QA_URL", "ADMIN_LOGIN_USR", "ADMIN_LOGIN_PSW")
    page=LoginPage(browser).open(os.environ["QA_URL"])
    page.login(os.environ["ADMIN_LOGIN_USR"],os.environ["ADMIN_LOGIN_PSW"])
    before=browser.execute_script("return {local:{...localStorage},session:{...sessionStorage}}")
    assert before is not None
    page.logout()
    after=browser.execute_script("return {local:{...localStorage},session:{...sessionStorage}}")
    sensitive=("token","jwt","patient","paciente","expediente","clinical","clinico")
    serialized=str(after).lower()
    assert not any(key in serialized for key in sensitive), "La caché conserva claves potencialmente sensibles tras cerrar sesión"
    assert "/login" in browser.current_url

