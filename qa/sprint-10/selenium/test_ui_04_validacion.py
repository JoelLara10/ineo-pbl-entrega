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

USERNAME = os.getenv("ADMIN_LOGIN_USR")
PASSWORD = os.getenv("ADMIN_LOGIN_PSW")

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


def buscar_boton_guardar(navegador):
    textos = (
        "guardar",
        "registrar",
        "enviar",
        "save",
        "submit",
    )

    botones = navegador.find_elements(
        By.XPATH,
        "//button | //input[@type='submit']",
    )

    for boton in botones:
        texto = (
            boton.text
            or boton.get_attribute("value")
            or ""
        ).strip().lower()

        if any(opcion in texto for opcion in textos):
            return boton

    return None


def test_ui_04_valoracion_sin_paciente():
    assert USERNAME, "Jenkins no proporcionó ADMIN_LOGIN_USR"
    assert PASSWORD, "Jenkins no proporcionó ADMIN_LOGIN_PSW"

    navegador = crear_navegador()
    espera = WebDriverWait(navegador, 30)

    try:
        navegador.get(URL_LOGIN)

        espera.until(
            EC.visibility_of_element_located(
                (By.NAME, "ineo-login-username")
            )
        ).send_keys(USERNAME)

        navegador.find_element(
            By.NAME,
            "ineo-login-password",
        ).send_keys(PASSWORD)

        navegador.find_element(
            By.XPATH,
            "//button[contains(., 'Iniciar Sesión')]",
        ).click()

        espera.until(
            lambda driver: "/login" not in driver.current_url
        )

        url_base = URL_LOGIN.split("/login")[0]
        navegador.get(f"{url_base}{RUTA_VALORACION}")

        espera.until(
            lambda driver: driver.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        boton_guardar = buscar_boton_guardar(navegador)

        assert boton_guardar is not None, (
            "No se encontró el botón Guardar o Registrar. "
            "Verifica la ruta de la pantalla de valoración."
        )

        boton_guardar.click()

        espera.until(
            lambda driver: any(
                mensaje in driver.page_source.lower()
                for mensaje in (
                    "seleccione un paciente",
                    "seleccionar paciente",
                    "paciente requerido",
                    "debe seleccionar",
                    "campo requerido",
                    "required",
                )
            )
        )

        navegador.save_screenshot(
            str(
                SCREENSHOTS
                / "ui-04-valoracion-sin-paciente.png"
            )
        )

        contenido = navegador.page_source.lower()

        mensajes_esperados = (
            "seleccione un paciente",
            "seleccionar paciente",
            "paciente requerido",
            "debe seleccionar",
            "campo requerido",
            "required",
        )

        assert any(
            mensaje in contenido
            for mensaje in mensajes_esperados
        ), (
            "La aplicación no mostró una validación al intentar "
            "guardar una valoración sin seleccionar paciente"
        )

    finally:
        navegador.quit()