import os
import time
from pathlib import Path

import pytest

from pages.analytics_page import AnalyticsPage
from pages.login_page import LoginPage
from conftest import DOWNLOADS, require_env


@pytest.mark.ui
def test_cp_s11_ui_03_tabla_y_exportacion(browser):
    require_env("QA_URL", "ADMIN_LOGIN_USR", "ADMIN_LOGIN_PSW", "ANALYTICS_ROUTE")
    LoginPage(browser).open(os.environ["QA_URL"]).login(
        os.environ["ADMIN_LOGIN_USR"], os.environ["ADMIN_LOGIN_PSW"]
    )
    page=AnalyticsPage(browser); page.open_route(os.environ["QA_URL"],os.environ["ANALYTICS_ROUTE"])
    table_rows=page.visible_table_rows()
    assert table_rows, "La tabla de Analytics no contiene registros visibles"
    page.click_text("Exportar", "CSV", "Download")
    deadline=time.time()+30; csv_file=None
    while time.time()<deadline:
        files=sorted(DOWNLOADS.glob("*.csv"),key=lambda p:p.stat().st_mtime,reverse=True)
        if files: csv_file=files[0]; break
        time.sleep(.5)
    assert csv_file, "No se descargó el archivo CSV"
    csv_rows=page.csv_rows(csv_file)
    normalized=lambda rows:[[value.strip() for value in row] for row in rows]
    assert normalized(table_rows) in (normalized(csv_rows),normalized(csv_rows[1:])), "Tabla y CSV no coinciden"

