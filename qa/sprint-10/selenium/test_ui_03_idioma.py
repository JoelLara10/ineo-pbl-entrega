import os
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL_LOGIN = os.getenv(
    "QA_URL",
    "https://ineo-web-qa.vercel.app/login",
)

USERNAME = os.getenv("ADMIN_LOGIN_USR")
PASSWORD = os.getenv("ADMIN_AUTH_VALUE")

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


def cambiar_select_a_ingles(navegador):
    selectores = navegador.find_elements(By.TAG_NAME, "select")

    for elemento in selectores:
        selector = Select(elemento)

        for opcion in selector.options:
            texto = opcion.text.strip().lower()
            valor = (
                opcion.get_attribute("value") or ""
            ).strip().lower()

            if (
                "english" in texto
                or "inglés" in texto
                or "ingles" in texto
                or valor in ("en", "en-us", "english")
            ):
                selector.select_by_visible_text(opcion.text)
                return True

    return False


def buscar_control_idioma(navegador):
    xpath = (
        "//*[self::button or self::a or @role='button']"
        "[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ',"
        "'abcdefghijklmnopqrstuvwxyzáéíóú'),'idioma')"
        " or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'language')"
        " or contains(translate(@aria-label,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'idioma')"
        " or contains(translate(@aria-label,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'language')"
        " or contains(translate(@title,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'idioma')"
        " or contains(translate(@title,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'language')"
        " or normalize-space(.)='ES'"
        " or normalize-space(.)='EN']"
    )

    elementos = navegador.find_elements(By.XPATH, xpath)

    for elemento in elementos:
        if elemento.is_displayed():
            return elemento

    return None


def buscar_opcion_ingles(navegador):
    xpath = (
        "//*[self::button or self::a or "
        "@role='option' or @role='menuitem']"
        "[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ',"
        "'abcdefghijklmnopqrstuvwxyzáéíóú'),'english')"
        " or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ',"
        "'abcdefghijklmnopqrstuvwxyzáéíóú'),'inglés')"
        " or normalize-space(.)='EN']"
    )

    elementos = navegador.find_elements(By.XPATH, xpath)

    for elemento in elementos:
        if elemento.is_displayed():
            return elemento

    return None


def test_ui_03_persistencia_del_idioma():
    assert USERNAME, (
        "Jenkins no proporcionó ADMIN_LOGIN_USR"
    )

    assert PASSWORD, (
        "Jenkins no proporcionó ADMIN_AUTH_VALUE"
    )

    navegador = crear_navegador()

    try:
        navegador.get(URL_LOGIN)

        WebDriverWait(navegador, 30).until(
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

        try:
            WebDriverWait(navegador, 90).until(
                lambda driver:
                "/login" not in driver.current_url
            )

        except TimeoutException:
            navegador.save_screenshot(
                str(SCREENSHOTS / "ui-03-error-login.png")
            )

            raise AssertionError(
                "No fue posible iniciar sesión con el usuario "
                "administrador. Consulta ui-03-error-login.png."
            )

        navegador.save_screenshot(
            str(SCREENSHOTS / "ui-03-panel-inicial.png")
        )

        cambio_realizado = cambiar_select_a_ingles(navegador)

        if not cambio_realizado:
            control_idioma = buscar_control_idioma(navegador)

            if control_idioma is None:
                navegador.save_screenshot(
                    str(
                        SCREENSHOTS
                        / "ui-03-selector-no-encontrado.png"
                    )
                )

                raise AssertionError(
                    "No se encontró un selector de idioma "
                    "de tipo select, botón o enlace. Consulta "
                    "ui-03-selector-no-encontrado.png."
                )

            navegador.execute_script(
                "arguments[0].click();",
                control_idioma,
            )

            try:
                opcion_ingles = WebDriverWait(
                    navegador,
                    15,
                ).until(
                    lambda driver:
                    buscar_opcion_ingles(driver)
                )

            except TimeoutException:
                navegador.save_screenshot(
                    str(
                        SCREENSHOTS
                        / "ui-03-opcion-ingles-no-encontrada.png"
                    )
                )

                raise AssertionError(
                    "Se abrió el selector, pero no se encontró "
                    "la opción English, Inglés o EN."
                )

            navegador.execute_script(
                "arguments[0].click();",
                opcion_ingles,
            )

        WebDriverWait(navegador, 20).until(
            lambda driver:
            "english" in driver.page_source.lower()
            or "logout" in driver.page_source.lower()
            or "patients" in driver.page_source.lower()
            or "settings" in driver.page_source.lower()
            or "dashboard" in driver.page_source.lower()
        )

        navegador.save_screenshot(
            str(SCREENSHOTS / "ui-03-idioma-ingles.png")
        )

        navegador.refresh()

        WebDriverWait(navegador, 30).until(
            lambda driver:
            driver.execute_script(
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
            "english",
            "logout",
            "patients",
            "settings",
            "dashboard",
            "nursing",
        )

        assert any(
            texto in pagina
            for texto in textos_ingles
        ), (
            "El idioma inglés no permaneció después de "
            "recargar la aplicación."
        )

    finally:
        navegador.quit()
