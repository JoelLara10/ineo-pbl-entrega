"""Wait for the dedicated local Selenium Grid used by Sprint 11."""
import json
import os
import time
import urllib.error
import urllib.request

url = os.getenv('SELENIUM_STATUS_URL', 'http://127.0.0.1:4444/status')
deadline = time.monotonic() + 90
last_error = 'Grid no respondió'
while time.monotonic() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            payload = json.loads(response.read().decode('utf-8'))
        value = payload.get('value', {})
        if response.status == 200 and value.get('ready') is True:
            print('Selenium Grid listo:', value.get('message', 'ready'))
            raise SystemExit(0)
        last_error = value.get('message', 'Grid aún no está listo')
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        last_error = type(exc).__name__
    time.sleep(2)
raise SystemExit('Selenium Grid no está listo en 90 segundos: ' + last_error)
