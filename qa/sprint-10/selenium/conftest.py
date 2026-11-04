import os
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("INEO_WEB_URL", "https://ineo-web-qa.vercel.app").rstrip("/")


@pytest.fixture(scope="session")
def credentials():
    user = os.getenv("INEO_QA_USER")
    password = os.getenv("INEO_QA_PASSWORD")
    if not user or not password:
        pytest.skip("Defina INEO_QA_USER e INEO_QA_PASSWORD con una cuenta sintética de QA")
    return user, password


@pytest.fixture
def driver(request):
    options = Options()
    if os.getenv("INEO_SHOW_BROWSER", "false").lower() != "true":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=options)
    yield browser
    if request.node.rep_call.failed:
        output = Path(os.getenv("INEO_SCREENSHOT_DIR", "evidence/sprint-10/screenshots"))
        output.mkdir(parents=True, exist_ok=True)
        browser.save_screenshot(str(output / f"{request.node.name}.png"))
    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)

