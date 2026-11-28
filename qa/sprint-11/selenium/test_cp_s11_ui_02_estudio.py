import hashlib
import os
import time
from pathlib import Path

import pytest

from pages.estudios_page import EstudiosPage
from pages.login_page import LoginPage
from conftest import DOWNLOADS, require_env


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.mark.ui
@pytest.mark.mutation
def test_cp_s11_ui_02_estudio_y_archivo(browser, require_mutation_enabled):
    require_env("QA_URL", "ENFERMERIA_LOGIN_USR", "ENFERMERIA_LOGIN_PSW", "STUDIES_ROUTE")
    source = Path("qa/sprint-11/fixtures/estudio_sintetico.txt").resolve()
    previous_downloads = {path.resolve() for path in DOWNLOADS.glob("*")}
    LoginPage(browser).open(os.environ["QA_URL"]).login(
        os.environ["ENFERMERIA_LOGIN_USR"], os.environ["ENFERMERIA_LOGIN_PSW"]
    )
    page = EstudiosPage(browser)
    page.open_route(os.environ["QA_URL"], os.environ["STUDIES_ROUTE"])
    page.upload(source)
    link = page.download_link()
    assert link is not None, "No apareció el enlace de descarga del archivo cargado"
    assert source.name.lower() in browser.page_source.lower(), "No se conservaron los metadatos visibles"

    browser.execute_script("arguments[0].click();", link)
    deadline = time.time() + 30
    downloaded = None
    while time.time() < deadline:
        candidates = [
            path
            for path in DOWNLOADS.glob("*")
            if path.resolve() not in previous_downloads
            and not path.name.endswith((".crdownload", ".part"))
            and path.is_file()
        ]
        if candidates:
            downloaded = max(candidates, key=lambda path: path.stat().st_mtime)
            break
        time.sleep(0.5)

    assert downloaded is not None, "El archivo no se descargó dentro de 30 segundos"
    assert sha256(downloaded) == sha256(source), (
        "El contenido descargado es diferente al archivo sintético cargado"
    )

