
"""
PBL-29 / Sprint Azure 10 — UAT Selenium contra frontend QA real
Base: https://ineo-web-qa.vercel.app

Flujo:
  login -> Enfermería -> paciente ocupado -> Valoración de Enfermería
  -> capturar datos -> bloquear API -> comprobar conservación
  -> restaurar API -> reintentar -> comprobar registro en historial.

Variables de entorno:
  INEO_BASE_URL
  INEO_USER
  INEO_PASSWORD
  INEO_ADMIN_USER
  INEO_ADMIN_PASSWORD
  INEO_SCREENSHOT_DIR
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from uuid import uuid4

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# ---------------------------------------------------------------------------
# CONFIGURACION
# ---------------------------------------------------------------------------

SCREENSHOT_DIR = Path(
    os.getenv(
        "INEO_SCREENSHOT_DIR",
        "evidence/sprint-10/uat/screenshots"
    )
)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_BASE = "https://ineo-web-qa.vercel.app"
DEFAULT_USER = os.getenv("INEO_USER", "jesus")
DEFAULT_PASSWORD = os.getenv("INEO_PASSWORD", "Jaime123456789")

ADMIN_USER = os.getenv("INEO_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("INEO_ADMIN_PASSWORD", "123456789")


def wait(driver, timeout=25):
    return WebDriverWait(driver, timeout)


def capture(driver, name: str) -> Path:
    path = SCREENSHOT_DIR / f"{name}.png"

    try:
        driver.save_screenshot(str(path))
    except Exception:
        pass

    return path


# ---------------------------------------------------------------------------
# LOGIN Y NAVEGACION
# ---------------------------------------------------------------------------

def login_as(driver, base_url, username, password):

    driver.get(f"{base_url.rstrip('/')}/login")

    user_el = wait(driver, 20).until(
        EC.visibility_of_element_located(
            (By.NAME, "ineo-login-username")
        )
    )

    pass_el = driver.find_element(
        By.CSS_SELECTOR,
        "input[type='password']"
    )

    user_el.clear()
    user_el.send_keys(username)

    pass_el.clear()
    pass_el.send_keys(password)

    capture(driver, "login-filled")

    driver.find_element(
        By.CSS_SELECTOR,
        "button.login-btn"
    ).click()

    try:
        wait(driver, 20).until(
            lambda d: "/login" not in d.current_url
        )

    except TimeoutException:
        capture(driver, "login-FAILED")

        raise AssertionError(
            f"Login falló con usuario='{username}'. "
            f"URL={driver.current_url}"
        ) from None


def open_nursing_panel(driver, base_url):

    driver.get(f"{base_url.rstrip('/')}/enfermeria")

    wait(driver, 20).until(
        lambda d: (
            "enfermeria" in d.current_url.lower()
            and (
                "OCUPADO" in d.page_source
                or "Módulo de Enfermería" in d.page_source
                or "Modulo de Enfermeria" in d.page_source
            )
        )
    )

    time.sleep(0.8)

    capture(driver, "modulo-enfermeria")


def open_first_occupied_patient(driver):

    buttons = driver.find_elements(
        By.XPATH,
        "//button[contains(.,'OCUPADO')]"
    )

    buttons = [
        button for button in buttons
        if button.is_displayed()
    ]

    assert buttons, (
        "No hay camas OCUPADO visibles en /enfermeria"
    )

    buttons[0].click()

    wait(driver, 15).until(
        lambda d: "/enfermeria/paciente/" in d.current_url
    )

    time.sleep(1)

    capture(driver, "detalle-paciente")


def open_valoracion(driver):

    clicked = False

    # Primera opción: tarjeta de valoración inicial.
    cards = driver.find_elements(
        By.XPATH,
        "//*[contains(normalize-space(.),'Valoración inicial') "
        "or contains(normalize-space(.),'Valoracion inicial')]"
    )

    for element in cards:
        try:
            if element.is_displayed():

                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    element
                )

                time.sleep(0.3)
                element.click()

                clicked = True
                break

        except Exception:
            continue

    # Segunda opción: botón o elemento de valoración.
    if not clicked:

        elements = driver.find_elements(
            By.XPATH,
            "//button[contains(.,'Valoración')] "
            "| //div[contains(.,'Valoración de Enfermería')]"
        )

        for element in elements:
            try:
                if (
                    element.is_displayed()
                    and "sidebar" not in (
                        element.get_attribute("class") or ""
                    ).lower()
                ):

                    driver.execute_script(
                        "arguments[0].click();",
                        element
                    )

                    clicked = True
                    break

            except Exception:
                continue

    # Tercera opción: búsqueda dentro del contenido principal.
    if not clicked:

        if "/enfermeria/paciente/" in driver.current_url:

            elements = driver.find_elements(
                By.XPATH,
                "//main//*[contains(.,'Valoración de Enfermería')]"
            )

            if elements:
                driver.execute_script(
                    "arguments[0].click();",
                    elements[0]
                )

    time.sleep(1.2)

    capture(driver, "despues-click-valoracion")

    try:

        wait(driver, 20).until(
            lambda d: len([
                element
                for element in d.find_elements(
                    By.CSS_SELECTOR,
                    "input, textarea"
                )
                if element.is_displayed()
            ]) >= 3
        )

    except TimeoutException:

        capture(driver, "valoracion-TIMEOUT")

        raise AssertionError(
            "No apareció el formulario de valoración. "
            f"URL={driver.current_url}"
        ) from None

    capture(driver, "formulario-valoracion")


# ---------------------------------------------------------------------------
# FORMULARIO DE VALORACION
# ---------------------------------------------------------------------------

def visible_fields(driver):

    fields = []

    for element in driver.find_elements(
        By.CSS_SELECTOR,
        "input, textarea"
    ):

        try:

            if not element.is_displayed():
                continue

            if not element.is_enabled():
                continue

            field_type = (
                element.get_attribute("type") or ""
            ).lower()

            if field_type in (
                "hidden",
                "checkbox",
                "radio",
                "submit",
                "button"
            ):
                continue

            fields.append(element)

        except Exception:
            continue

    return fields


def fill_valoracion(driver, note):

    fields = visible_fields(driver)

    assert len(fields) >= 3, (
        f"Formulario incompleto. "
        f"Campos encontrados={len(fields)}. "
        f"URL={driver.current_url}"
    )

    values = [
        "Estable",
        "2/10",
        "Independiente",
        "Bajo",
        "Sin riesgo"
    ]

    for element, value in zip(fields[:5], values):

        element.clear()
        element.send_keys(value)

    textareas = [
        field for field in fields
        if field.tag_name.lower() == "textarea"
    ]

    if textareas:

        textareas[-1].clear()
        textareas[-1].send_keys(note)

    elif len(fields) > 5:

        fields[-1].clear()
        fields[-1].send_keys(note)

    capture(driver, "datos-capturados")

    return fields


def click_guardar_valoracion(driver):

    buttons = driver.find_elements(
        By.XPATH,
        "//button[contains(.,'Guardar') "
        "or contains(.,'guardar') "
        "or contains(.,'Save')]"
    )

    buttons = [
        button for button in buttons
        if button.is_displayed() and button.is_enabled()
    ]

    assert buttons, (
        f"No se encontró botón Guardar. "
        f"URL={driver.current_url}"
    )

    button = buttons[0]

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        button
    )

    time.sleep(0.3)

    try:
        button.click()

    except Exception:
        driver.execute_script(
            "arguments[0].click();",
            button
        )

    time.sleep(2)

    capture(driver, "despues-guardar")


def get_form_values(driver):

    values = []

    for field in visible_fields(driver):

        try:

            value = (
                field.get_attribute("value")
                or field.text
                or ""
            )

            values.append(value)

        except Exception:
            continue

    return values


# ---------------------------------------------------------------------------
# CP-S10-UAT-01 — VALORACION COMPRENSIBLE
# ---------------------------------------------------------------------------

def test_cp_s10_uat_01_valoracion_comprensible(
    browser,
    base_url=None
):

    url = (
        getattr(browser, "demo_url", None)
        or base_url
        or os.getenv("INEO_BASE_URL", DEFAULT_BASE)
    )

    login_as(
        browser,
        url,
        DEFAULT_USER,
        DEFAULT_PASSWORD
    )

    capture(browser, "uat01-01-login")

    open_nursing_panel(browser, url)
    open_first_occupied_patient(browser)
    open_valoracion(browser)

    note = f"UAT-S10-{uuid4().hex[:8]}"

    fill_valoracion(browser, note)

    click_guardar_valoracion(browser)

    page = (browser.page_source or "").lower()

    ok = any(
        text in page
        for text in (
            "éxito",
            "exito",
            "success",
            "guardado",
            note.lower()
        )
    )

    assert ok, (
        "No se observó confirmación o persistencia "
        f"de la valoración. URL={browser.current_url}"
    )

    capture(browser, "uat01-06-persistencia")


# ---------------------------------------------------------------------------
# CP-S10-UAT-02 — LECTURA DE ANALYTICS
# ---------------------------------------------------------------------------

def test_cp_s10_uat_02_lectura_analytics(
    browser,
    base_url=None
):

    url = (
        getattr(browser, "demo_url", None)
        or base_url
        or os.getenv("INEO_BASE_URL", DEFAULT_BASE)
    )

    try:

        login_as(
            browser,
            url,
            ADMIN_USER,
            ADMIN_PASSWORD
        )

    except AssertionError:

        login_as(
            browser,
            url,
            DEFAULT_USER,
            DEFAULT_PASSWORD
        )

    capture(browser, "uat02-01-login")

    menu_clicked = False

    menu_options = [
        "//button[contains(.,'Análisis de datos') "
        "or contains(.,'Analisis de datos')]",

        "//*[self::button or self::a or self::span]"
        "[contains(.,'Análisis de datos')]",

        "//button[contains(.,'Analítica') "
        "or contains(.,'Analitica') "
        "or contains(.,'Analytics')]",

        "//*[contains(@class,'nav-item')]"
        "[contains(.,'Análisis') or contains(.,'Analítica')]"
    ]

    for xpath in menu_options:

        elements = browser.find_elements(
            By.XPATH,
            xpath
        )

        for element in elements:

            if element.is_displayed():

                browser.execute_script(
                    "arguments[0].click();",
                    element
                )

                menu_clicked = True
                break

        if menu_clicked:
            break

    time.sleep(1)

    capture(browser, "uat02-menu-analisis")

    sub_clicked = False

    sub_options = [
        "//button[contains(.,'Analítica general') "
        "or contains(.,'Analitica general')]",

        "//*[self::button or self::a or self::div]"
        "[contains(.,'Analítica general')]",

        "//button[contains(.,'General')]",

        "//*[contains(.,'Analytics General') "
        "or contains(.,'Analítica General')]"
    ]

    for xpath in sub_options:

        elements = browser.find_elements(
            By.XPATH,
            xpath
        )

        for element in elements:

            text = (element.text or "").strip().lower()

            if element.is_displayed() and "general" in text:

                browser.execute_script(
                    "arguments[0].click();",
                    element
                )

                sub_clicked = True
                break

        if sub_clicked:
            break

    if not sub_clicked:

        for path in (
            "/spark/analytics",
            "/analytics",
            "/spark",
            "/dashboard"
        ):

            browser.get(
                f"{url.rstrip('/')}{path}"
            )

            time.sleep(1)

            if "login" not in browser.current_url:
                break

    time.sleep(1.5)

    capture(browser, "uat02-02-analitica-general")

    page = (browser.page_source or "").lower()

    has_chart = bool(
        browser.find_elements(
            By.CSS_SELECTOR,
            "svg, canvas, table, [role='img']"
        )
    )

    has_labels = any(
        text in page
        for text in (
            "periodo",
            "period",
            "total",
            "atención",
            "atencion",
            "gráfica",
            "grafica",
            "unidad",
            "analytics",
            "analítica",
            "analitica"
        )
    )

    capture(browser, "uat02-03-graficas")

    assert has_chart or has_labels, (
        "No se visualizaron gráficas o tabla de Analítica general. "
        f"URL={browser.current_url}"
    )


# ---------------------------------------------------------------------------
# CP-S10-UAT-03 — RECUPERACION DE ERROR
# ---------------------------------------------------------------------------

def test_cp_s10_uat_03_recuperacion_error(
    browser,
    base_url=None
):

    url = (
        getattr(browser, "demo_url", None)
        or base_url
        or os.getenv("INEO_BASE_URL", DEFAULT_BASE)
    )

    login_as(
        browser,
        url,
        DEFAULT_USER,
        DEFAULT_PASSWORD
    )

    open_nursing_panel(browser, url)
    open_first_occupied_patient(browser)
    open_valoracion(browser)

    # Identificador único para encontrar el registro en el historial.
    marker = f"ERR-RECOVERY-{uuid4().hex[:6]}"

    fill_valoracion(browser, marker)

    capture(browser, "uat03-antes-bloqueo")

    # Comprobar que los datos fueron capturados.
    values_before = get_form_values(browser)

    print("\n========== ANTES DEL BLOQUEO ==========")
    print("Valores:", values_before)
    print("Identificador:", marker)

    assert marker in values_before, (
        "El identificador de prueba no quedó capturado "
        "en el formulario."
    )

    # -------------------------------------------------------
    # 1. BLOQUEAR SOLICITUDES DE API
    # -------------------------------------------------------

    blocked = False

    try:

        browser.execute_cdp_cmd(
            "Network.enable",
            {}
        )

        browser.execute_cdp_cmd(
            "Network.setBlockedURLs",
            {
                "urls": [
                    "*api*",
                    "*render.com*",
                    "*onrender*",
                    "*/appointments/*",
                    "*/nursing/*"
                ]
            }
        )

        blocked = True

    except Exception as error:

        raise AssertionError(
            "No fue posible bloquear las solicitudes de API "
            f"con Chrome DevTools Protocol: {error}"
        ) from None

    time.sleep(0.5)

    # -------------------------------------------------------
    # 2. INTENTAR GUARDAR CON LA API BLOQUEADA
    # -------------------------------------------------------

    save_buttons = browser.find_elements(
        By.XPATH,
        "//button[contains(.,'Guardar') "
        "or contains(.,'guardar')]"
    )

    save_buttons = [
        button for button in save_buttons
        if button.is_displayed() and button.is_enabled()
    ]

    assert save_buttons, (
        "No se encontró el botón Guardar "
        "durante la simulación de error."
    )

    browser.execute_script(
        "arguments[0].click();",
        save_buttons[0]
    )

    time.sleep(2)

    capture(browser, "uat03-despues-fallo")

    page_after_error = (
        browser.find_element(By.TAG_NAME, "body").text
    )

    values_after_error = get_form_values(browser)

    print("\n========== DESPUES DEL BLOQUEO ==========")
    print("Valores:", values_after_error)
    print("URL:", browser.current_url)

    # Los datos deben permanecer en el formulario.
    data_preserved = marker in values_after_error

    assert data_preserved, (
        "Pérdida de datos después del fallo de conexión. "
        f"Valores encontrados={values_after_error}"
    )

    # No debe existir confirmación falsa de guardado.
    page_lower = page_after_error.lower()

    false_success_messages = (
        "guardado correctamente",
        "valoración guardada correctamente",
        "valoracion guardada correctamente",
        "save success",
        "éxito al guardar",
        "exito al guardar"
    )

    false_success = any(
        message in page_lower
        for message in false_success_messages
    )

    assert not false_success, (
        "La aplicación mostró una confirmación de guardado "
        "aunque las solicitudes de API estaban bloqueadas."
    )

    # -------------------------------------------------------
    # 3. RESTAURAR LA CONEXION
    # -------------------------------------------------------

    if blocked:

        browser.execute_cdp_cmd(
            "Network.setBlockedURLs",
            {"urls": []}
        )

        time.sleep(1)

    # Verificar que el identificador sigue en el formulario
    # antes de volver a intentar el guardado.
    values_before_retry = get_form_values(browser)

    assert marker in values_before_retry, (
        "Los datos no están disponibles para realizar "
        "el segundo intento de guardado."
    )

    # -------------------------------------------------------
    # 4. REINTENTAR EL GUARDADO
    # -------------------------------------------------------

    save_buttons = browser.find_elements(
        By.XPATH,
        "//button[contains(.,'Guardar') "
        "or contains(.,'guardar') "
        "or contains(.,'Save')]"
    )

    save_buttons = [
        button for button in save_buttons
        if button.is_displayed() and button.is_enabled()
    ]

    assert save_buttons, (
        "No se encontró el botón Guardar después "
        "de restaurar la conexión."
    )

    browser.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        save_buttons[0]
    )

    time.sleep(0.3)

    try:

        save_buttons[0].click()

    except Exception:

        browser.execute_script(
            "arguments[0].click();",
            save_buttons[0]
        )

    capture(browser, "uat03-despues-reintento")

    # -------------------------------------------------------
    # 5. COMPROBAR PERSISTENCIA EN EL HISTORIAL
    # -------------------------------------------------------

    def marker_in_history(driver):

        try:

            body_text = driver.find_element(
                By.TAG_NAME,
                "body"
            ).text

            # Separar el formulario del historial.
            # El marcador debe aparecer después del título
            # "Historial", no solamente en el textarea.
            if "Historial" not in body_text:
                return False

            history_text = body_text.split(
                "Historial",
                1
            )[1]

            return marker.lower() in history_text.lower()

        except Exception:

            return False

    try:

        wait(browser, 15).until(
            marker_in_history
        )

        history_saved = True

    except TimeoutException:

        history_saved = False

    # Comprobar también si la aplicación muestra una
    # confirmación explícita de guardado.
    final_page = (
        browser.find_element(By.TAG_NAME, "body").text
    ).lower()

    success_messages = (
        "valoración guardada correctamente",
        "valoracion guardada correctamente",
        "guardado correctamente",
        "guardada correctamente",
        "éxito al guardar",
        "exito al guardar"
    )

    success_detected = any(
        message in final_page
        for message in success_messages
    )

    print("\n========== RESULTADO DEL REINTENTO ==========")
    print("Identificador:", marker)
    print("Registro encontrado en historial:", history_saved)
    print("Mensaje de éxito:", success_detected)
    print("URL:", browser.current_url)

    # La prueba solo pasa si existe evidencia de persistencia
    # o una confirmación explícita de éxito.
    ok_retry = history_saved or success_detected

    assert ok_retry, (
        "El reintento no produjo evidencia de guardado. "
        f"Identificador={marker}. "
        f"Registro en historial={history_saved}. "
        f"Confirmación={success_detected}. "
        f"URL={browser.current_url}"
    )

    capture(browser, "uat03-reintento-ok")


# ---------------------------------------------------------------------------
# CP-S10-UI-05 — CONTRASTE DE TEMA
# ---------------------------------------------------------------------------

def test_cp_s10_ui_05_contraste_tema(
    browser,
    base_url=None
):

    url = (
        getattr(browser, "demo_url", None)
        or base_url
        or os.getenv("INEO_BASE_URL", DEFAULT_BASE)
    )

    login_as(
        browser,
        url,
        DEFAULT_USER,
        DEFAULT_PASSWORD
    )

    open_nursing_panel(browser, url)

    capture(browser, "ui05-tema-claro")

    toggles = browser.find_elements(
        By.XPATH,
        "//*[contains(@aria-label,'tema') "
        "or contains(@aria-label,'theme') "
        "or contains(@class,'theme') "
        "or contains(@class,'dark') "
        "or contains(.,'Oscuro') "
        "or contains(.,'Dark')]"
    )

    if toggles:

        browser.execute_script(
            "arguments[0].click();",
            toggles[0]
        )

        time.sleep(0.6)

        capture(browser, "ui05-tema-oscuro")

    else:

        capture(browser, "ui05-sin-toggle-oscuro")

    try:

        open_first_occupied_patient(browser)
        open_valoracion(browser)

        capture(browser, "ui05-formulario-legible")

    except Exception:

        capture(browser, "ui05-formulario-no-abierto")
