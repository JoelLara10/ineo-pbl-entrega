import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = os.getenv(
    "QA_URL",
    "https://ineo-web-qa.vercel.app/login"
)

USERNAME = os.getenv("ADMIN_LOGIN_USR")
PASSWORD = os.getenv("ADMIN_LOGIN_PSW")

SCREENSHOTS = Path("qa/sprint-10/screenshots")
SCREENSHOTS.mkdir(parents=True, exist_ok=True)


def crear_navegador():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def test_ui_01_inicio_y_cierre_de_sesion():
    assert USERNAME, "Jenkins no proporcionó ADMIN_LOGIN_USR"
    assert PASSWORD, "Jenkins no proporcionó ADMIN_LOGIN_PSW"

    driver = crear_navegador()
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(URL)

        usuario = wait.until(
            EC.visibility_of_element_located(
                (By.NAME, "ineo-login-username")
            )
        )

        contrasena = driver.find_element(
            By.NAME,
            "ineo-login-password"
        )

        usuario.send_keys(USERNAME)
        contrasena.send_keys(PASSWORD)

        driver.find_element(
            By.XPATH,
            "//button[contains(., 'Iniciar Sesión')]"
        ).click()

        wait.until(
            lambda navegador:
            "/login" not in navegador.current_url
        )

        driver.save_screenshot(
            str(SCREENSHOTS / "ui-01-login-correcto.png")
        )

        elementos = driver.find_elements(
            By.XPATH,
            "//button | //a"
        )

        cerrar_sesion = None

        for elemento in elementos:
            texto = elemento.text.strip().lower()

            if (
                "cerrar sesión" in texto
                or "cerrar sesion" in texto
                or "logout" in texto
                or texto == "salir"
            ):
                cerrar_sesion = elemento
                break

        assert cerrar_sesion is not None, (
            "No se encontró el botón para cerrar sesión"
        )

        cerrar_sesion.click()

        wait.until(
            EC.visibility_of_element_located(
                (By.NAME, "ineo-login-username")
            )
        )

        driver.save_screenshot(
            str(SCREENSHOTS / "ui-01-logout-correcto.png")
        )

        assert "/login" in driver.current_url

    finally:
        driver.quit()