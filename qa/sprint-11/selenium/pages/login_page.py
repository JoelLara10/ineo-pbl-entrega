from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    USERNAME = (By.NAME, "ineo-login-username")
    PASSWORD = (By.NAME, "ineo-login-password")
    SUBMIT = (By.XPATH, "//button[contains(., 'Iniciar Sesión') or contains(., 'Login')]")

    def __init__(self, driver, timeout=45):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url):
        self.driver.get(url)
        self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        return self

    def login(self, username, password):
        user = self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        secret = self.wait.until(EC.visibility_of_element_located(self.PASSWORD))
        user.clear(); user.send_keys(username)
        secret.clear(); secret.send_keys(password)
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT)).click()
        self.wait.until(lambda d: "/login" not in d.current_url)
        return self

    def logout(self):
        candidates = self.driver.find_elements(By.XPATH, "//button | //a | //*[@role='button']")
        for element in candidates:
            text = (element.text or "").strip().lower()
            if any(value in text for value in ("cerrar sesión", "cerrar sesion", "logout", "salir")):
                self.driver.execute_script("arguments[0].click();", element)
                try:
                    alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                    alert.accept()
                except Exception:
                    pass
                self.wait.until(EC.visibility_of_element_located(self.USERNAME))
                return
        raise AssertionError("No se encontró un control visible para cerrar sesión")

