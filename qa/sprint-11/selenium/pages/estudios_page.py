import os
from selenium.webdriver.common.by import By
from .base_page import BasePage


class EstudiosPage(BasePage):
    def upload(self, path):
        selector = os.getenv("S11_FILE_SELECTOR", "input[type='file']")
        element = self.wait.until(lambda d: d.find_element(By.CSS_SELECTOR, selector))
        element.send_keys(str(path))
        self.click_text("Subir", "Cargar", "Guardar", "Upload")

    def download_link(self):
        selector = os.getenv("S11_DOWNLOAD_SELECTOR")
        if selector:
            return self.driver.find_element(By.CSS_SELECTOR, selector)
        return self.first_visible(["//a[@download]", "//a[contains(.,'Descargar') or contains(.,'Download')]"])

