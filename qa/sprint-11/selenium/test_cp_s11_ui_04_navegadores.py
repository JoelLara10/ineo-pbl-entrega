import os

import pytest

from pages.login_page import LoginPage
from conftest import require_env


@pytest.mark.ui
def test_cp_s11_ui_04_mismo_smoke_en_dos_navegadores(browser, browser_name):
    require_env("QA_URL", "ADMIN_LOGIN_USR", "ADMIN_LOGIN_PSW")
    LoginPage(browser).open(os.environ["QA_URL"]).login(
        os.environ["ADMIN_LOGIN_USR"], os.environ["ADMIN_LOGIN_PSW"]
    )
    assert "/login" not in browser.current_url
    assert browser.execute_script("return document.readyState") == "complete"
    assert browser_name in {"chrome", "firefox"}

