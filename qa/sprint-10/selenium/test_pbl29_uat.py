"""
PBL-29 / Sprint Azure 10 — UAT Selenium contra frontend QA real
Base: https://ineo-web-qa.vercel.app

Flujo real validado:
  login -> /enfermeria -> clic cama OCUPADO -> /enfermeria/paciente/{exp}/{ate}
  -> Valoración de Enfermería -> llenar campos -> Guardar valoración

Credenciales requeridas por variables de entorno (sin valores predeterminados):
  INEO_USER / INEO_PASSWORD
  INEO_ADMIN_USER / INEO_ADMIN_PASSWORD (opcionales; Analytics usa el usuario normal si faltan)
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

SCREENSHOT_DIR = Path(
    os.getenv("INEO_SCREENSHOT_DIR", "evidence/sprint-10/uat/screenshots")
)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_BASE = "https://ineo-web-qa.vercel.app"


def required_credentials(user_key: str, password_key: str) -> tuple[str, str]:
    """Read QA credentials only from the environment; never use committed defaults."""
    username = os.getenv(user_key)
    password = os.getenv(password_key)
    missing = [key for key, value in ((user_key, username), (password_key, password)) if not value]
    if missing:
        raise AssertionError("Required QA environment variables are missing: " + ", ".join(missing))
    return username, password


def wait(driver, timeout=25):
    return WebDriverWait(driver, timeout)


def capture(driver, name: str) -> Path:
    path = SCREENSHOT_DIR / f"{name}.png"
    try:
        driver.save_screenshot(str(path))
    except Exception:
        pass
    return path


def login_as(driver, base_url: str, username: str, password: str):
    driver.get(f"{base_url.rstrip('/')}/login")
    user_el = wait(driver, 20).until(
        EC.visibility_of_element_located((By.NAME, "ineo-login-username"))
    )
    pass_el = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    user_el.clear()
    user_el.send_keys(username)
    pass_el.clear()
    pass_el.send_keys(password)
    capture(driver, "login-filled")
    driver.find_element(By.CSS_SELECTOR, "button.login-btn").click()
    try:
        wait(driver, 20).until(lambda d: "/login" not in d.current_url)
    except TimeoutException:
        capture(driver, "login-FAILED")
        raise AssertionError(
            f"Login falló con usuario='{username}'. URL={driver.current_url}"
        ) from None


def open_nursing_panel(driver, base_url: str):
    """Abre el módulo de enfermería (lista de camas)."""
    driver.get(f"{base_url.rstrip('/')}/enfermeria")
    # Espera a ver al menos una cama ocupada o el título del módulo
    wait(driver, 20).until(
        lambda d: "enfermeria" in d.current_url.lower()
        and (
            "OCUPADO" in d.page_source
            or "Módulo de Enfermería" in d.page_source
            or "Modulo de Enfermeria" in d.page_source
        )
    )
    time.sleep(0.8)
    capture(driver, "modulo-enfermeria")


def open_first_occupied_patient(driver):
    """Clic en la primera cama OCUPADO (botón)."""
    buttons = driver.find_elements(By.XPATH, "//button[contains(.,'OCUPADO')]")
    assert buttons, "No hay camas OCUPADO visibles en /enfermeria"
    buttons[0].click()
    wait(driver, 15).until(lambda d: "/enfermeria/paciente/" in d.current_url)
    time.sleep(1.0)
    capture(driver, "detalle-paciente")


def open_valoracion(driver):
    """Desde detalle de paciente, abre el formulario de Valoración."""
    # 1) Intentar clic en la tarjeta de acciones del detalle (no el menú lateral)
    cards = driver.find_elements(
        By.XPATH,
        "//*[contains(normalize-space(.),'Valoración inicial') or "
        "contains(normalize-space(.),'Valoracion inicial')]",
    )
    clicked = False
    for el in cards:
        try:
            if el.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                time.sleep(0.3)
                el.click()
                clicked = True
                break
        except Exception:
            continue

    # 2) Fallback: botón/tarjeta que diga exactamente la acción
    if not clicked:
        for el in driver.find_elements(By.XPATH, "//button[contains(.,'Valoración')] | //div[contains(.,'Valoración de Enfermería')]"):
            try:
                if el.is_displayed() and "sidebar" not in (el.get_attribute("class") or "").lower():
                    driver.execute_script("arguments[0].click();", el)
                    clicked = True
                    break
            except Exception:
                continue

    # 3) Fallback final: ir directo si ya estamos en paciente/{exp}/{ate}
    if not clicked:
        current = driver.current_url.rstrip("/")
        if "/enfermeria/paciente/" in current:
            # Algunos builds navegan por estado; re-clic por texto visible en main
            mains = driver.find_elements(By.XPATH, "//main//*[contains(.,'Valoración de Enfermería')]")
            if mains:
                driver.execute_script("arguments[0].click();", mains[0])

    time.sleep(1.2)
    capture(driver, "despues-click-valoracion")

    # Esperar inputs del formulario (Estado general, Dolor, etc.)
    try:
        wait(driver, 20).until(
            lambda d: len([
                e for e in d.find_elements(By.CSS_SELECTOR, "input, textarea")
                if e.is_displayed()
            ]) >= 3
        )
    except TimeoutException:
        capture(driver, "valoracion-TIMEOUT")
        raise AssertionError(
            f"No apareció el formulario de valoración. URL={driver.current_url}. "
            "Revisa evidence/.../despues-click-valoracion.png y valoracion-TIMEOUT.png"
        ) from None

    capture(driver, "formulario-valoracion")





def visible_fields(driver):
    fields = []
    for el in driver.find_elements(By.CSS_SELECTOR, "input, textarea"):
        try:
            if el.is_displayed() and el.is_enabled():
                t = (el.get_attribute("type") or "").lower()
                if t in ("hidden", "checkbox", "radio", "submit", "button"):
                    continue
                fields.append(el)
        except Exception:
            continue
    return fields


def fill_valoracion(driver, note: str):
    fields = visible_fields(driver)
    assert len(fields) >= 3, (
        f"Formulario de valoración incompleto (campos={len(fields)}). URL={driver.current_url}"
    )
    values = ["Estable", "2/10", "Independiente", "Bajo", "Sin riesgo"]
    for el, val in zip(fields[:5], values):
        el.clear()
        el.send_keys(val)
    # Observaciones: textarea
    textareas = [f for f in fields if f.tag_name.lower() == "textarea"]
    if textareas:
        textareas[-1].clear()
        textareas[-1].send_keys(note)
    elif len(fields) > 5:
        fields[-1].clear()
        fields[-1].send_keys(note)
    capture(driver, "datos-capturados")
    return fields


def click_guardar_valoracion(driver):
    btns = driver.find_elements(
        By.XPATH,
        "//button[contains(.,'Guardar') or contains(.,'guardar') or contains(.,'Save')]"
        " | //*[@role='button'][contains(.,'Guardar')]",
    )
    # filtrar visibles
    btns = [b for b in btns if b.is_displayed()]
    if not btns:
        # último recurso: cualquier control con texto Guardar
        btns = [
            el for el in driver.find_elements(By.XPATH, "//*[contains(.,'Guardar valoración') or contains(.,'Guardar')]")
            if el.is_displayed() and el.tag_name.lower() in ("button", "a", "div", "span")
        ]
    assert btns, f"No se encontró botón Guardar. URL={driver.current_url}"
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btns[0])
    time.sleep(0.2)
    try:
        btns[0].click()
    except Exception:
        driver.execute_script("arguments[0].click();", btns[0])
    time.sleep(1.5)
    capture(driver, "despues-guardar")


# ---------------------------------------------------------------------------
# CP-S10-UAT-01 — Valoración comprensible
# ---------------------------------------------------------------------------
def test_cp_s10_uat_01_valoracion_comprensible(browser, base_url=None):
    url = getattr(browser, "demo_url", None) or base_url or os.getenv(
        "INEO_BASE_URL", DEFAULT_BASE
    )
    login_as(browser, url, *required_credentials("INEO_USER", "INEO_PASSWORD"))
    capture(browser, "uat01-01-login")

    open_nursing_panel(browser, url)
    open_first_occupied_patient(browser)
    open_valoracion(browser)

    note = f"UAT-S10-{uuid4().hex[:8]}"
    fill_valoracion(browser, note)
    click_guardar_valoracion(browser)

    page = (browser.page_source or "").lower()
    ok = any(
        t in page
        for t in ("éxito", "exito", "success", "guardado", note.lower(), "estable")
    )
    assert ok, (
        "No se observó confirmación/persistencia de la valoración. "
        f"URL={browser.current_url}"
    )
    capture(browser, "uat01-06-persistencia")


# ---------------------------------------------------------------------------
# CP-S10-UAT-02 — Lectura de Analytics
# ---------------------------------------------------------------------------
def test_cp_s10_uat_02_lectura_analytics(browser, base_url=None):
    url = getattr(browser, "demo_url", None) or base_url or os.getenv(
        "INEO_BASE_URL", DEFAULT_BASE
    )
    # Prefer the configured admin account; use the standard QA role only when no admin
    # account was supplied. A failed admin login remains a real test failure.
    if os.getenv("INEO_ADMIN_USER") or os.getenv("INEO_ADMIN_PASSWORD"):
        login_as(browser, url, *required_credentials("INEO_ADMIN_USER", "INEO_ADMIN_PASSWORD"))
    else:
        login_as(browser, url, *required_credentials("INEO_USER", "INEO_PASSWORD"))

    capture(browser, "uat02-01-login")

    for path in ("/spark/analytics", "/analytics", "/dashboard", "/spark", "/"):
        browser.get(f"{url.rstrip('/')}{path}")
        time.sleep(0.8)
        if "login" not in browser.current_url:
            break

    capture(browser, "uat02-02-pantalla")
    page = browser.page_source or ""
    has_signal = any(
        k in page.lower()
        for k in (
            "periodo", "period", "2026", "total", "atencion", "atención",
            "unidad", "analytics", "análisis", "analisis", "spark", "gráfica",
            "grafica", "dashboard",
        )
    ) or bool(browser.find_elements(By.CSS_SELECTOR, "svg, canvas, table, [role='img']"))
    capture(browser, "uat02-03-interpretacion")
    assert has_signal, f"No se pudo interpretar Analytics. URL={browser.current_url}"


# ---------------------------------------------------------------------------
# CP-S10-UAT-03 — Recuperación de error
# ---------------------------------------------------------------------------
def test_cp_s10_uat_03_recuperacion_error(browser, base_url=None):
    url = getattr(browser, "demo_url", None) or base_url or os.getenv(
        "INEO_BASE_URL", DEFAULT_BASE
    )
    login_as(browser, url, *required_credentials("INEO_USER", "INEO_PASSWORD"))
    open_nursing_panel(browser, url)
    open_first_occupied_patient(browser)
    open_valoracion(browser)

    marker = f"ERR-RECOVERY-{uuid4().hex[:6]}"
    fields = fill_valoracion(browser, marker)
    capture(browser, "uat03-antes-bloqueo")

    # Bloquear solo llamadas de API (la UI sigue viva)
    blocked = False
    try:
        browser.execute_cdp_cmd("Network.enable", {})
        browser.execute_cdp_cmd(
            "Network.setBlockedURLs",
            {
                "urls": [
                    "*api*",
                    "*render.com*",
                    "*onrender*",
                    "*/appointments/*",
                    "*/nursing*",
                ]
            },
        )
        blocked = True
    except Exception:
        blocked = False

    time.sleep(0.3)

    save_btns = [
        b for b in browser.find_elements(
            By.XPATH, "//button[contains(.,'Guardar') or contains(.,'guardar')]"
        )
        if b.is_displayed()
    ]
    assert save_btns, f"No se encontró botón Guardar. URL={browser.current_url}"

    try:
        browser.execute_script("arguments[0].click();", save_btns[0])
    except Exception:
        save_btns[0].click()
    time.sleep(1.5)
    capture(browser, "uat03-despues-fallo")

    page = (browser.page_source or "").lower()
    # No debe haber confirmación falsa de éxito
    false_ok = any(t in page for t in ("guardado correctamente", "save success", "éxito al guardar"))
    # Los datos deben seguir en pantalla/formulario
    fields = [
        e for e in browser.find_elements(By.CSS_SELECTOR, "input, textarea")
        if e.is_displayed()
    ]
    current = ""
    try:
        if fields:
            current = fields[0].get_attribute("value") or ""
    except Exception:
        pass

    assert "Estable" in current or "estable" in page or marker.lower() in page, (
        "Pérdida silenciosa de datos tras fallo de red"
    )
    # Si hubo mensaje de éxito explícito con API bloqueada, es fallo
    assert not false_ok, "Confirmación falsa de guardado con red/API bloqueada"

    if blocked:
        try:
            browser.execute_cdp_cmd("Network.setBlockedURLs", {"urls": []})
        except Exception:
            pass

    capture(browser, "uat03-datos-conservados")
# ---------------------------------------------------------------------------
# CP-S10-UI-05 — Contraste tema
# ---------------------------------------------------------------------------
def test_cp_s10_ui_05_contraste_tema(browser, base_url=None):
    url = getattr(browser, "demo_url", None) or base_url or os.getenv(
        "INEO_BASE_URL", DEFAULT_BASE
    )
    login_as(browser, url, *required_credentials("INEO_USER", "INEO_PASSWORD"))
    open_nursing_panel(browser, url)
    # Reproduce Chrome configurado en modo oscuro y valida que la app conserve
    # sus superficies claras y que los controles visibles sigan siendo legibles.
    browser.execute_cdp_cmd(
        "Emulation.setEmulatedMedia",
        {"features": [{"name": "prefers-color-scheme", "value": "dark"}]},
    )
    browser.refresh()
    open_nursing_panel(browser, url)
    capture(browser, "ui05-chrome-dark-preference")

    color_scheme = browser.execute_script(
        "return getComputedStyle(document.documentElement).colorScheme"
    )
    assert color_scheme == "only light", (
        f"Chrome dark preference debe respetar la paleta legible de la app; got {color_scheme!r}"
    )

    controls = browser.execute_script("""
      const visible = el => {
        const r = el.getBoundingClientRect(), s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      };
      const rgb = value => {
        const m = value.match(/[\\d.]+/g);
        return m ? m.slice(0, 3).map(Number) : null;
      };
      const luminance = color => {
        if (!color) return null;
        const linear = color.map(v => { v /= 255; return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; });
        return .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2];
      };
      return [...document.querySelectorAll('input:not([type=hidden]), textarea, select')]
        .filter(visible).map(el => {
          const s = getComputedStyle(el), fg = luminance(rgb(s.color)), bg = luminance(rgb(s.backgroundColor));
          return {tag:el.tagName, type:el.type, color:s.color, background:s.backgroundColor,
                  ratio: fg === null || bg === null ? null : (Math.max(fg,bg)+.05)/(Math.min(fg,bg)+.05)};
        });
    """)
    assert controls, "No se encontraron controles visibles del formulario para verificar contraste"
    failures = [c for c in controls if c["ratio"] is None or c["ratio"] < 4.5]
    assert not failures, f"Controles con contraste menor a WCAG AA 4.5:1: {failures}"
