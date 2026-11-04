from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 15)

    def open(self):
        self.driver.get(f"{self.base_url}/login")
        return self

    def login(self, username, password):
        user = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[type='email']")))
        secret = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        user.clear(); user.send_keys(username)
        secret.clear(); secret.send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(lambda d: "/login" not in d.current_url)

    def logout(self):
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Cerrar sesión') or contains(., 'Logout')]")))
        button.click()
        self.wait.until(EC.url_contains("/login"))

