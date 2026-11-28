import os
from pathlib import Path

import pytest
from selenium import webdriver


ROOT = Path("qa/sprint-11")
SCREENSHOTS = ROOT / "screenshots"
REPORTS = ROOT / "reports"
DOWNLOADS = REPORTS / "downloads"
for directory in (SCREENSHOTS, REPORTS, DOWNLOADS):
    directory.mkdir(parents=True, exist_ok=True)


def _bool_env(name: str, default: bool = True) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "si"}


def pytest_generate_tests(metafunc):
    if "browser_name" in metafunc.fixturenames:
        configured = os.getenv("BROWSERS", "chrome").split(",")
        browsers = [item.strip().lower() for item in configured if item.strip()]
        metafunc.parametrize("browser_name", browsers or ["chrome"])


@pytest.fixture
def browser(browser_name, request):
    headless = _bool_env("HEADLESS", True)

    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,1000")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option(
            "prefs", {"download.default_directory": str(DOWNLOADS.resolve())}
        )
        driver = webdriver.Chrome(options=options)
    elif browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        options.add_argument("--width=1440")
        options.add_argument("--height=1000")
        options.set_preference("browser.download.dir", str(DOWNLOADS.resolve()))
        options.set_preference("browser.download.folderList", 2)
        driver = webdriver.Firefox(options=options)
    else:
        pytest.skip(f"Navegador no soportado: {browser_name}")

    driver.set_page_load_timeout(90)
    yield driver

    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        safe_name = request.node.name.replace("/", "_").replace("::", "_")
        driver.save_screenshot(str(SCREENSHOTS / f"{safe_name}-{browser_name}.png"))
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def require_env(*names):
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        pytest.skip("Faltan variables requeridas: " + ", ".join(missing))


@pytest.fixture
def require_mutation_enabled():
    if not _bool_env("S11_ENABLE_MUTATION_TESTS", False):
        pytest.skip("Prueba bloqueada hasta habilitar S11_ENABLE_MUTATION_TESTS=true")

