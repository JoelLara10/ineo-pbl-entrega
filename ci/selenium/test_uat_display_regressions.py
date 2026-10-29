"""Regressions reported by Zahid: actual browser theme, role navigation and history."""
import re
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def wait(b):
    return WebDriverWait(b, 30)


def login(b, role='enfermeria', theme='dark'):
    b.execute_cdp_cmd('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-color-scheme', 'value': theme}]})
    b.execute_cdp_cmd('Emulation.setAutoDarkModeOverride', {'enabled': theme == 'dark'})
    b.get(b.demo_url + '/login')
    wait(b).until(EC.visibility_of_element_located((By.NAME, 'ineo-login-username'))).send_keys(role + '.test')
    b.find_element(By.CSS_SELECTOR, 'input[type=password]').send_keys('Prueba-Sprint7!')
    b.find_element(By.CSS_SELECTOR, 'button.login-btn').click()
    wait(b).until(lambda d: '/login' not in d.current_url)


def open_nursing(b, path):
    b.get(b.demo_url + '/enfermeria/paciente/1/1')
    label = {'valoracion': 'Valoración', 'balance-hidrico': 'Balance Hídrico', 'cuidados': 'Cuidados'}[path]
    button = wait(b).until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(.,'{label}')]")))
    button.click()
    wait(b).until(lambda d: '/enfermeria/' + path in d.current_url)


@pytest.mark.parametrize('theme', ['light', 'dark'])
@pytest.mark.parametrize('path', ['valoracion', 'balance-hidrico', 'cuidados'])
def test_uat_typed_fields_are_readable_in_both_browser_themes(browser, path, theme):
    login(browser, theme=theme)
    open_nursing(browser, path)
    fields = wait(browser).until(lambda b: b.find_elements(By.CSS_SELECTOR, '.nursing-form-body input, .nursing-form-body textarea'))
    visible = [f for f in fields if f.is_displayed() and f.is_enabled()]
    assert visible
    field = visible[0]
    field.clear()
    field.send_keys('125' if field.get_attribute('type') == 'number' else 'Texto visible QA')
    color = browser.execute_script('return getComputedStyle(arguments[0]).color', field)
    assert color not in ('rgb(255, 255, 255)', 'rgba(0, 0, 0, 0)')
    assert browser.execute_script('return getComputedStyle(document.documentElement).colorScheme') == 'light only'
    assert field.get_attribute('value')


@pytest.mark.parametrize('theme', ['light', 'dark'])
def test_uat_analytics_labels_and_buttons_remain_visible(browser, theme):
    login(browser, role='admin', theme=theme)
    browser.get(browser.demo_url + '/admin/spark/analytics')
    heading = wait(browser).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'main h1')))
    assert heading.text.strip()
    assert browser.execute_script('return getComputedStyle(arguments[0]).color', heading) != 'rgb(243, 244, 246)'
    buttons = [b for b in browser.find_elements(By.CSS_SELECTOR, 'main button') if b.is_displayed() and b.text.strip()]
    assert buttons
    for button in buttons:
        style = browser.execute_script('const s=getComputedStyle(arguments[0]);return [s.color,s.backgroundColor,s.backgroundImage]', button)
        assert not (style[0] == style[1] and style[2] == 'none')


@pytest.mark.parametrize('role', ['admin', 'administrativo'])
def test_uat_beds_opens_for_administration_without_expanding_edit_permissions(browser, role):
    login(browser, role=role)
    browser.get(browser.demo_url + '/admin')
    wait(browser).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Camas')] | //a[contains(.,'Camas')]"))).click()
    wait(browser).until(lambda d: '/config/camas' in d.current_url)
    wait(browser).until(EC.presence_of_element_located((By.XPATH, "//td[contains(.,'TEST-1')]")))
    form = browser.find_elements(By.CSS_SELECTOR, 'form.config-main-card')
    assert bool(form) == (role == 'admin')


@pytest.mark.parametrize('path', ['valoracion', 'balance-hidrico', 'cuidados'])
def test_uat_history_shows_mexico_time_without_six_hour_advance(browser, path):
    # Even a browser configured in UTC must display the hospital's Mexico time.
    browser.execute_cdp_cmd('Emulation.setTimezoneOverride', {'timezoneId': 'UTC'})
    login(browser)
    open_nursing(browser, path)
    record = wait(browser).until(EC.presence_of_element_located((By.XPATH, "//article[contains(.,'QA-UTC-1830')]")))
    assert re.search(r'12:30', record.text), record.text
    assert '18:30' not in record.text
    browser.execute_script("arguments[0].scrollIntoView({block:'center'})", record)
