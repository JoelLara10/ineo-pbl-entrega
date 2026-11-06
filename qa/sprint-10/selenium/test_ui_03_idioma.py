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


def buscar_elemento_por_textos(navegador, textos):
    elementos = navegador.find_elements(
        By.XPATH,
        "//button | //a | //*[@role='button']",
    )

    for elemento in elementos:
        texto = elemento.text.strip().lower()

        if any(opcion in texto for opcion in textos):
            return elemento

    return None


def test_ui_03_persistencia_del_idioma():
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

        selector_idioma = buscar_elemento_por_textos(
            navegador,
            ["idioma", "language", "español"],
        )

        assert selector_idioma is not None, (
            "No se encontró el selector de idioma"
        )

        selector_idioma.click()

        opcion_ingles = espera.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//*[self::button or self::a or "
                    "@role='option' or @role='menuitem']"
                    "[contains(translate(normalize-space(.), "
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    "'abcdefghijklmnopqrstuvwxyz'), 'english') "
                    "or normalize-space(.)='EN' "
                    "or contains(translate(normalize-space(.), "
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    "'abcdefghijklmnopqrstuvwxyz'), 'inglés')]",
                )
            )
        )

        opcion_ingles.click()

        espera.until(
            lambda driver:
            "login" in driver.page_source.lower()
            or "logout" in driver.page_source.lower()
            or "language" in driver.page_source.lower()
            or "patients" in driver.page_source.lower()
        )

        navegador.save_screenshot(
            str(SCREENSHOTS / "ui-03-idioma-ingles.png")
        )

        navegador.refresh()

        espera.until(
            lambda driver: driver.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        navegador.save_screenshot(
            str(
                SCREENSHOTS
                / "ui-03-idioma-ingles-persistente.png"
            )
        )

        pagina = navegador.page_source.lower()

        textos_ingles = (
            "logout",
            "language",
            "patients",
            "settings",
            "dashboard",
            "nursing",
        )

        assert any(texto in pagina for texto in textos_ingles), (
            "El idioma inglés no permaneció después de recargar"
        )

    finally:
        navegador.quit()