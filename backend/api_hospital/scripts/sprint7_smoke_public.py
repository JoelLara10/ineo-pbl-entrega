"""Non-destructive Sprint 7 smoke checks; never sends credentials to a live API."""
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = os.getenv('INEO_API_URL', 'https://api-clinica-jx4m.onrender.com').rstrip('/')
PATHS = ['/overview'] + [f'{prefix}/{kind}' for kind in
    ('analytics', 'met', 'clinical', 'unsupervised')
    for prefix in ('', '/status')]
PATHS += ['/run/analytics']


def main():
    failures = []
    for path in PATHS:
        method = 'POST' if path.startswith('/run/') else 'GET'
        url = BASE + '/api/v1/spark' + path
        try:
            with urlopen(Request(url, method=method), timeout=35) as response:
                code, body = response.status, response.read()
        except HTTPError as error:
            code, body = error.code, error.read()
        except (URLError, TimeoutError) as error:
            failures.append(f'{method} {path}: conexión fallida ({type(error).__name__})')
            continue
        try:
            payload = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            payload = {}
        passed = (code == 401 and payload.get('code') == 'unauthorized'
                  and payload.get('contract_version') == '1.0')
        print(f'{method} {path}: HTTP {code}, contrato: {"OK" if passed else "ERROR"}')
        if not passed:
            failures.append(f'{method} {path}: HTTP {code} o contrato inesperado')
    if failures:
        print('\n'.join(failures), file=sys.stderr)
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
