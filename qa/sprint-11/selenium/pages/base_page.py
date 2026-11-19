import os
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, timeout=40):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_route(self, login_url, route):
        base = login_url.split("/login")[0].rstrip("/") + "/"
        self.driver.get(urljoin(base, route.lstrip("/")))
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def first_visible(self, xpaths):
        for xpath in xpaths:
            for element in self.driver.find_elements(By.XPATH, xpath):
                if element.is_displayed():
                    return element
        return None

    def click_text(self, *texts):
        clauses = " or ".join(f"contains(normalize-space(.), {text!r})" for text in texts)
        locator = (By.XPATH, f"//button[{clauses}] | //a[{clauses}] | //*[@role='button' and ({clauses})]")
        element = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].click();", element)
        return element

    def field(self, env_name, labels):
        configured = os.getenv(env_name)
        if configured:
            elements = self.driver.find_elements(By.CSS_SELECTOR, configured)
            return next((e for e in elements if e.is_displayed()), None)
        xpaths=[]
        for label in labels:
            xpaths.extend([
                f"//input[contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{label.lower()}')]",
                f"//textarea[contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{label.lower()}')]",
                f"//label[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{label.lower()}')]/following::input[1]",
            ])
        return self.first_visible(xpaths)

