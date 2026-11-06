import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL_LOGIN = os.getenv(
    "QA_URL",
    "https://ineo-web-qa.vercel.app/login",
)

RUTA_VALORACION = os.getenv(
    "ASSESSMENT_ROUTE",
    "/enfermeria/valoracion",
)

USERNAME = os.getenv("Jess")
PASSWORD = os.getenv("123456789J15ads05")

SCREENSHOTS = Path("qa/sprint-10/screenshots")
SCREENSHOTS.mkdir(parents=True, exist_ok=True)


def crear_navegador():
    opciones = webdriver.ChromeOptions()
    opciones.add_argument("--headless=new")
    opciones.add_argument("--window-size=1440,1000")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=opciones)


def test_ui_04_valoracion_sin_paciente():
    assert USERNAME, (
        "Jenkins no proporcionó ENFERMERIA_LOGIN_USR"
    )

    assert PASSWORD, (
        "Jenkins no proporcionó ENFERMERIA_LOGIN_PSW"
    )

    navegador = crear_navegador()
    espera = WebDriverWait(navegador, 30)

    try:
        navegador.get(URL_LOGIN)

        usuario = espera.until(
            EC.visibility_of_element_located(
                (By.NAME, "ineo-login-username")
            )
        )

        contrasena = espera.until(
            EC.visibility_of_element_located(
                (By.NAME, "ineo-login-password")
            )
        )

        usuario.send_keys(USERNAME)
        contrasena.send_keys(PASSWORD)

        navegador.find_element(
            By.XPATH,
            "//button[contains(., 'Iniciar Sesión')]",
        ).click()

        WebDriverWait(navegador, 90).until(
            lambda driver:
            "/login" not in driver.current_url
        )

        url_base = URL_LOGIN.split("/login")[0]
        navegador.get(f"{url_base}{RUTA_VALORACION}")

        WebDriverWait(navegador, 30).until(
            lambda driver:
            driver.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        titulo = WebDriverWait(navegador, 30).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//h1[contains(., 'Valoración') "
                    "or contains(., 'Assessment')]",
                )
            )
        )

        assert titulo.is_displayed(), (
            "La pantalla de valoración no se mostró"
        )

        boton_guardar = WebDriverWait(
            navegador,
            30,
        ).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[contains(., 'Guardar') "
                    "or contains(., 'Save')]",
                )
            )
        )

        navegador.save_screenshot(
            str(
                SCREENSHOTS
                / "ui-04-valoracion-sin-paciente.png"
            )
        )

        assert not boton_guardar.is_enabled(), (
            "El botón Guardar debería permanecer "
            "deshabilitado cuando no existe un paciente "
            "seleccionado"
        )

        contenido = navegador.page_source.lower()

        paciente_no_seleccionado = (
            "atención: n/a" in contenido
            or "atencion: n/a" in contenido
            or "attention: n/a" in contenido
            or "exp: n/a" in contenido
        )

        assert paciente_no_seleccionado, (
            "La pantalla no indicó que falta el expediente "
            "o la atención del paciente"
        )

    finally:
        navegador.quit()