"""Bounded read-only HTTPS smoke on the user-supplied deployment."""
import json
from pathlib import Path
import time
import requests
from common import OUT

BASE='https://api-clinica-jx4m.onrender.com'
def main():
    results=[]
    for path, expected in [('/health',200),('/ready',200),('/',200),('/api/v1/patients',401)]:
        start=time.monotonic()
        try:
            response=requests.get(BASE+path,timeout=90)
            # Only public health/root metadata and unauthenticated errors.
            results.append(dict(url=BASE+path,status=response.status_code,
                expected=expected,passed=response.status_code==expected,
                seconds=round(time.monotonic()-start,3),body=response.json(),
                cache_control=response.headers.get('Cache-Control'),
                content_type=response.headers.get('Content-Type')))
        except Exception as exc:
            results.append(dict(url=BASE+path,passed=False,error=type(exc).__name__))
    (OUT/'render-smoke.json').write_text(json.dumps(dict(
        environment='Render remoto proporcionado por el usuario',
        deployment_sha='No verificable sin metadatos de Render',
        scope='Smoke HTTPS de solo lectura; no acredita un nuevo despliegue',
        checks=results),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(results,ensure_ascii=True,indent=2))
    return all(x['passed'] for x in results)
if __name__=='__main__':raise SystemExit(0 if main() else 1)
