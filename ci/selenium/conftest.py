"""Real React + Flask over HTTP; disposable synthetic Mongo, fresh Chrome per case."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

ROOT = Path(__file__).resolve().parents[2]


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def stop(process):
    if process.poll() is None:
        if os.name == 'nt':
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        else:
            process.terminate()
        process.wait(timeout=15)


@pytest.fixture(scope='session')
def demo_system(tmp_path_factory):
    folder = tmp_path_factory.mktemp('selenium-system')
    ready = folder / 'api.json'
    web_port = free_port()
    env = dict(os.environ, CORS_ORIGINS=f'http://127.0.0.1:{web_port}', PYTHONUTF8='1')
    processes, logs = [], []
    def launch(command, cwd):
        log = (folder / f'process-{len(processes)}.log').open('w', encoding='utf8')
        logs.append(log)
        p = subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT)
        processes.append(p)
        return p
    try:
        api = launch([sys.executable, str(ROOT / 'ci/demo_api.py'), '--ready-file', str(ready)], ROOT)
        deadline = time.monotonic() + 50
        while not ready.exists():
            assert api.poll() is None, 'No inició la API sintética'
            assert time.monotonic() < deadline, 'Timeout de API'
            time.sleep(.1)
        api_port = json.loads(ready.read_text())['port']
        env['VITE_API_URL'] = f'http://127.0.0.1:{api_port}/api/v1'
        web = ROOT / 'frontend/clinica-web-react'
        node = shutil.which('node')
        assert node, 'Se requiere Node 22'
        vite = launch([node, str(web / 'node_modules/vite/bin/vite.js'), '--host', '127.0.0.1',
                       '--port', str(web_port), '--strictPort'], web)
        url = f'http://127.0.0.1:{web_port}'
        deadline = time.monotonic() + 60
        while True:
            assert vite.poll() is None, 'No inició Vite; revisar npm ci'
            try:
                with urllib.request.urlopen(url, timeout=2) as response:
                    if response.status == 200:
                        break
            except OSError:
                pass
            assert time.monotonic() < deadline, 'Timeout de web'
            time.sleep(.2)
        yield url
    finally:
        for p in reversed(processes):
            stop(p)
        for log in logs:
            log.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, 'rep_' + outcome.get_result().when, outcome.get_result())


@pytest.fixture
def browser(request, demo_system):
    options = webdriver.ChromeOptions()
    if os.getenv('INEO_SHOW_BROWSER', 'false').lower() != 'true':
        options.add_argument('--headless=new')
    options.add_argument('--window-size=1366,1000')
    options.add_experimental_option('prefs', {'credentials_enable_service': False,
                                            'profile.password_manager_enabled': False})
    executable = os.getenv('CHROMEDRIVER_EXE', '').strip()
    driver = webdriver.Chrome(service=Service(executable) if executable else Service(), options=options)
    driver.set_page_load_timeout(40)
    driver.demo_url = demo_system
    try:
        yield driver
    finally:
        folder = Path(os.getenv('INEO_SCREENSHOT_DIR', str(ROOT / 'reports/selenium-local/screenshots')))
        folder.mkdir(parents=True, exist_ok=True)
        name = request.node.name
        try:
            driver.save_screenshot(str(folder / (name + '.png')))
            report = getattr(request.node, 'rep_call', None)
            (folder / (name + '.json')).write_text(json.dumps({
                'case': name, 'result': report.outcome if report else 'setup_or_teardown',
                'url': driver.current_url, 'browser': driver.capabilities.get('browserVersion'),
                'scope': 'Real web/API HTTP; synthetic in-memory Mongo; technical execution, not human UAT',
            }, indent=2), encoding='utf8')
        finally:
            driver.quit()
