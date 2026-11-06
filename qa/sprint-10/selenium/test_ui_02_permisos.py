import os
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL_LOGIN = os.getenv(
    "QA_URL",
    "https://ineo-web-qa.vercel.app/login",
)

RUTA_ADMINISTRATIVA = os.getenv(
    "ADMIN_ROUTE",
    "/configuracion",
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


def test_ui_02_restriccion_por_rol():
    if not USERNAME or not PASSWORD:
        pytest.skip(
            "No se configuraron las credenciales "
            "ENFERMERIA_LOGIN_USR y ENFERMERIA_LOGIN_PSW"
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

        contrasena = navegador.find_element(
            By.NAME,
            "ineo-login-password",
        )

        usuario.send_keys(USERNAME)
        contrasena.send_keys(PASSWORD)

        navegador.find_element(
            By.XPATH,
            "//button[contains(., 'Iniciar Sesión')]",
        ).click()

        espera.until(
            lambda driver: "/login" not in driver.current_url
        )

        url_base = URL_LOGIN.split("/login")[0]
        navegador.get(f"{url_base}{RUTA_ADMINISTRATIVA}")

        espera.until(
            lambda driver: driver.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        navegador.save_screenshot(
            str(SCREENSHOTS / "ui-02-restriccion-rol.png")
        )

        contenido = navegador.page_source.lower()
        url_actual = navegador.current_url.lower()

        mensajes_denegados = (
            "acceso denegado",
            "no autorizado",
            "sin permisos",
            "no tiene permisos",
            "forbidden",
            "unauthorized",
        )

        acceso_restringido = (
            "/login" in url_actual
            or RUTA_ADMINISTRATIVA.lower() not in url_actual
            or any(
                mensaje in contenido
                for mensaje in mensajes_denegados
            )
        )

        assert acceso_restringido, (
            "El usuario de enfermería pudo abrir la sección "
            f"administrativa: {navegador.current_url}"
        )

    finally:
        navegador.quit()