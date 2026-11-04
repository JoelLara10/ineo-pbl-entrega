import os

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages import LoginPage


@pytest.mark.ui
def test_cp_s10_ui_01_login_y_logout(driver, base_url, credentials):
    page = LoginPage(driver, base_url).open()
    page.login(*credentials)
    assert "/login" not in driver.current_url
    page.logout()
    driver.get(f"{base_url}/")
    WebDriverWait(driver, 10).until(EC.url_contains("/login"))


@pytest.mark.ui
def test_cp_s10_ui_02_rol_y_ruta_directa(driver, base_url):
    user = os.getenv("INEO_NURSE_USER")
    password = os.getenv("INEO_NURSE_PASSWORD")
    if not user or not password:
        pytest.skip("Defina INEO_NURSE_USER e INEO_NURSE_PASSWORD")
    LoginPage(driver, base_url).open().login(user, password)
    driver.get(f"{base_url}/config/usuarios")
    WebDriverWait(driver, 10).until(lambda d: "/config/usuarios" not in d.current_url or "acceso" in d.page_source.lower())
    assert "/config/usuarios" not in driver.current_url or "acceso" in driver.page_source.lower()


@pytest.mark.ui
def test_cp_s10_ui_03_campos_requeridos(driver, base_url, credentials):
    LoginPage(driver, base_url).open().login(*credentials)
    driver.get(f"{base_url}/enfermeria/valoracion")
    submit = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
    submit.click()
    assert "requer" in driver.page_source.lower() or not submit.is_enabled()


@pytest.mark.ui
def test_cp_s10_ui_04_idioma_persistente(driver, base_url, credentials):
    LoginPage(driver, base_url).open().login(*credentials)
    language = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='language-selector'], select[aria-label*='idioma' i]")))
    language.click()
    option = driver.find_element(By.XPATH, "//*[self::option or @role='option'][contains(., 'English') or contains(., 'EN')]")
    option.click()
    driver.refresh()
    assert "en" in (driver.execute_script("return localStorage.getItem('i18nextLng')") or "").lower()
    assert "common." not in driver.page_source

