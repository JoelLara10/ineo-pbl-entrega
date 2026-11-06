import os
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = os.getenv(
    "QA_URL",
    "https://ineo-web-qa.vercel.app/login",
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


def buscar_cerrar_sesion(driver):
    textos_permitidos = (
        "cerrar sesión",
        "cerrar sesion",
        "logout",
        "salir",
        "sign out",
    )

    elementos = driver.find_elements(
        By.XPATH,
        "//button | //a | //*[@role='button']",
    )

    for elemento in elementos:
        try:
            texto = elemento.text.strip().lower()

            if any(
                texto_permitido in texto
                for texto_permitido in textos_permitidos
            ):
                return elemento
        except Exception:
            continue

    return None


def test_ui_01_inicio_y_cierre_de_sesion():
    assert USERNAME, (
        "Jenkins no proporcionó ADMIN_LOGIN_USR"
    )

    assert PASSWORD, (
        "Jenkins no proporcionó ADMIN_LOGIN_PSW"
    )

    driver = crear_navegador()
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(URL)

        usuario = wait.until(
            EC.visibility_of_element_located(
                (By.NAME, "ineo-login-username")
            )
        )

        contrasena = wait.until(
            EC.visibility_of_element_located(
                (By.NAME, "ineo-login-password")
            )
        )

        usuario.clear()
        usuario.send_keys(USERNAME)

        contrasena.clear()
        contrasena.send_keys(PASSWORD)

        boton_login = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(., 'Iniciar Sesión')]",
                )
            )
        )

        boton_login.click()

        try:
            WebDriverWait(driver, 90).until(
                lambda navegador:
                "/login" not in navegador.current_url
            )
        except TimeoutException:
            driver.save_screenshot(
                str(SCREENSHOTS / "ui-01-error-login.png")
            )

            mensajes = driver.find_elements(
                By.XPATH,
                "//*[@role='alert'] | "
                "//*[contains(@class, 'error')] | "
                "//*[contains(@class, 'alert')]",
            )

            textos_error = [
                mensaje.text.strip()
                for mensaje in mensajes
                if mensaje.text.strip()
            ]

            mensaje_visible = (
                " | ".join(textos_error)
                if textos_error
                else "La aplicación no mostró un mensaje visible."
            )

            raise AssertionError(
                "El inicio de sesión no terminó dentro de "
                "90 segundos. "
                f"URL actual: {driver.current_url}. "
                f"Mensaje visible: {mensaje_visible}. "
                "Consulta la captura ui-01-error-login.png."
            )

        driver.save_screenshot(
            str(SCREENSHOTS / "ui-01-login-correcto.png")
        )

        cerrar_sesion = buscar_cerrar_sesion(driver)

        if cerrar_sesion is None:
            driver.save_screenshot(
                str(
                    SCREENSHOTS
                    / "ui-01-error-boton-cerrar-sesion.png"
                )
            )

        assert cerrar_sesion is not None, (
            "El inicio de sesión fue correcto, pero no se "
            "encontró el botón para cerrar sesión. Consulta "
            "ui-01-error-boton-cerrar-sesion.png."
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            cerrar_sesion,
        )

        driver.execute_script(
            "arguments[0].click();",
            cerrar_sesion,
        )

        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located(
                (By.NAME, "ineo-login-username")
            )
        )

        driver.save_screenshot(
            str(SCREENSHOTS / "ui-01-logout-correcto.png")
        )

        assert "/login" in driver.current_url, (
            "El usuario cerró sesión, pero la URL no regresó "
            f"al login. URL actual: {driver.current_url}"
        )

    finally:
        driver.quit()