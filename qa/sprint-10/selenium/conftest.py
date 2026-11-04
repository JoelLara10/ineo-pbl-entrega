"""
conftest.py — fixture browser para qa/sprint-10/selenium
Default QA: https://ineo-web-qa.vercel.app
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Falta selenium. Instala con: pip install selenium") from exc


def pytest_configure(config):
    shot = Path(os.getenv("INEO_SCREENSHOT_DIR", "evidence/sprint-10/uat/screenshots"))
    shot.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="function")
def browser():
    base_url = (os.getenv("INEO_BASE_URL") or os.getenv("INEO_WEB_URL", "https://ineo-web-qa.vercel.app")).rstrip("/")

    options = ChromeOptions()
    options.add_argument("--window-size=1366,768")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=es-MX")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if os.getenv("INEO_HEADLESS", "").strip() in ("1", "true", "yes"):
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(45)
    driver.implicitly_wait(2)
    driver.demo_url = base_url

    try:
        yield driver
    finally:
        try:
            driver.quit()
        except Exception:
            pass


@pytest.fixture(scope="session")
def base_url():
    return (os.getenv("INEO_BASE_URL") or os.getenv("INEO_WEB_URL", "https://ineo-web-qa.vercel.app")).rstrip("/")

