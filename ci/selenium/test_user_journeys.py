"""User-facing checks executed in Chrome, not mocked DOM/component assertions."""
from uuid import uuid4
import os
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def wait(browser):
    return WebDriverWait(browser, 25)


def login(browser, password='Prueba-Sprint7!'):
    browser.get(browser.demo_url + '/login')
    wait(browser).until(EC.visibility_of_element_located((By.NAME, 'ineo-login-username'))).send_keys('enfermeria.test')
    browser.find_element(By.CSS_SELECTOR, 'input[type=password]').send_keys(password)
    browser.find_element(By.CSS_SELECTOR, 'button.login-btn').click()
    if password == 'Prueba-Sprint7!':
        wait(browser).until(lambda b: '/login' not in b.current_url)


def assessment(browser):
    login(browser)
    browser.get(browser.demo_url + '/enfermeria/paciente/1/1')
    button = wait(browser).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Valoración')]")))
    button.click()
    wait(browser).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'form input')))


def fill(browser, pain='2'):
    fields = browser.find_elements(By.CSS_SELECTOR, 'form input')
    assert len(fields) == 5
    for field, value in zip(fields, ['Estable', pain, 'Independiente', 'Bajo', 'Bajo']):
        field.clear()
        field.send_keys(value)
    note = 'SELENIUM-' + uuid4().hex[:10]
    browser.find_element(By.CSS_SELECTOR, 'form textarea').send_keys(note)
    return note


def save(browser):
    browser.find_element(By.CSS_SELECTOR, 'form button[type=submit]').click()


def capture(browser, name):
    folder = Path(os.getenv('INEO_SCREENSHOT_DIR', 'reports/selenium-local/screenshots'))
    folder.mkdir(parents=True, exist_ok=True)
    assert browser.save_screenshot(str(folder / (name + '.png')))


def test_sel_01_private_route_requires_login(browser):
    browser.get(browser.demo_url + '/enfermeria/valoracion')
    wait(browser).until(EC.visibility_of_element_located((By.NAME, 'ineo-login-username')))
    assert '/login' in browser.current_url


def test_sel_02_wrong_password_is_rejected(browser):
    login(browser, password='Wrong-synthetic-password')
    wait(browser).until(lambda b: b.find_elements(By.CSS_SELECTOR, '.error-text'))
    assert '/login' in browser.current_url
    assert 'credenciales' in browser.find_element(By.CSS_SELECTOR, '.error-text').text.lower()


def test_sel_03_login_and_assessment_navigation(browser):
    assessment(browser)
    assert '/enfermeria/valoracion' in browser.current_url
    assert browser.find_element(By.CSS_SELECTOR, 'h1').text
    assert browser.find_element(By.CSS_SELECTOR, 'form input').is_enabled()


def test_sel_04_save_and_revisit_persisted_assessment(browser):
    assessment(browser)
    note = fill(browser)
    save(browser)
    alert = wait(browser).until(EC.alert_is_present())
    assert 'guard' in alert.text.lower()
    alert.accept()
    wait(browser).until(EC.presence_of_element_located((By.XPATH, f"//article[contains(.,'{note}')]")))
    # A fresh HTTP page load reads the persisted API result again.
    browser.refresh()
    saved = wait(browser).until(EC.presence_of_element_located((By.XPATH, f"//article[contains(.,'{note}')]")))
    assert 'Estable' in saved.text and 'Independiente' in saved.text
    browser.execute_script("arguments[0].scrollIntoView({block:'center'})", saved)


def test_sel_05_invalid_pain_is_not_saved(browser):
    assessment(browser)
    note = fill(browser, pain='11')
    save(browser)
    error = wait(browser).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[role=alert]')))
    assert error.text.strip()
    assert not browser.find_elements(By.XPATH, f"//article[contains(.,'{note}')]")


def test_sel_06_api_connection_failure_reports_error_and_retry_recovers(browser):
    assessment(browser)
    note = fill(browser)
    browser.execute_cdp_cmd('Network.enable', {})
    browser.execute_cdp_cmd('Network.setBlockedURLs', {
        'urls': ['*api/v1/appointments/*/nursing-assessment*']})
    try:
        save(browser)
        alert = wait(browser).until(EC.alert_is_present())
        message = alert.text
        alert.accept()
        assert 'no se pudo guardar' in message.lower()
        assert not browser.find_elements(By.XPATH, f"//article[contains(.,'{note}')]")
        assert browser.find_element(By.CSS_SELECTOR, 'form textarea').get_attribute('value') == note
        capture(browser, 'SEL-06-error-conexion-formulario-conservado')
    finally:
        browser.execute_cdp_cmd('Network.setBlockedURLs', {'urls': []})
    save(browser)
    wait(browser).until(EC.alert_is_present()).accept()
    wait(browser).until(EC.presence_of_element_located((By.XPATH, f"//article[contains(.,'{note}')]")))


def test_sel_07_offline_mode_blocks_clinical_writes_and_reconnects(browser):
    assessment(browser)
    note = fill(browser)
    browser.execute_cdp_cmd('Network.enable', {})
    browser.execute_cdp_cmd('Network.emulateNetworkConditions', {
        'offline': True, 'latency': 0, 'downloadThroughput': 0, 'uploadThroughput': 0})
    try:
        wait(browser).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.offline-shell')))
        assert not browser.find_elements(By.CSS_SELECTOR, 'form button[type=submit]')
        assert 'offline' in browser.find_element(By.CSS_SELECTOR, '.offline-shell h1').text.lower()
        capture(browser, 'SEL-07-operacion-clinica-bloqueada-offline')
    finally:
        browser.execute_cdp_cmd('Network.emulateNetworkConditions', {
            'offline': False, 'latency': 0, 'downloadThroughput': -1, 'uploadThroughput': -1})
    wait(browser).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'form input')))
    assert not browser.find_elements(By.XPATH, f"//article[contains(.,'{note}')]")
