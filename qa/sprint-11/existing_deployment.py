"""Read-only verification of the existing API and an explicit deployment dry run.

This program has no Render management client, deploy hook, POST or publish step.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import requests
from common import ROOT, OUT

BASE='https://api-clinica-jx4m.onrender.com'
DEST=OUT/'revalidation'

def rehearsal():
    blueprint=(ROOT/'render.yaml').read_text(encoding='utf-8')
    dockerfile=ROOT/'backend/api_hospital/Dockerfile'
    assert 'dockerContext: ./backend/api_hospital' in blueprint
    assert 'dockerfilePath: ./backend/api_hospital/Dockerfile' in blueprint
    assert 'healthCheckPath: /ready' in blueprint
    assert 'autoDeployTrigger: "off"' in blueprint
    assert 'sync: false' in blueprint
    source=dockerfile.read_text(encoding='utf-8')
    assert 'gunicorn' in source and '${PORT:-10000}' in source
    return dict(kind='Simulación documental y validación estática local',
        requested_scope='Por instrucción del solicitante se conserva el despliegue existente.',
        remote_deployment_executed=False,rollback_executed=False,
        management_requests_sent=0,passed=True,
        checks=['Contexto y Dockerfile existentes','Inicio gunicorn con PORT de Render',
            'Readiness /ready','Auto-deploy desactivado','Variables secretas sin valores en blueprint'],
        steps=[dict(action='Preparar candidato y configuración versionada',mode='Comprobado localmente'),
            dict(action='Seleccionar el despliegue estable actual como referencia',mode='Paso simulado; ID remoto no observado'),
            dict(action='Publicar candidato',mode='Omitido por instrucción expresa del usuario'),
            dict(action='Comprobar HTTPS, salud, readiness y rutas protegidas',mode='Ejecutado realmente sobre API existente'),
            dict(action='Ante fallo, seleccionar versión estable y repetir smoke',mode='Simulado; no se efectuó rollback remoto')])

def main():
    DEST.mkdir(exist_ok=True)
    checks=[]
    endpoints=[('/health',200),('/ready',200),('/',200),('/api/v1/patients',401),
        ('/api/v1/auth/me',401),('/api/v1/medico',401),
        ('/api/v1/appointments/1/fluid-balance',401),('/api/v1/analytics/dashboard',401)]
    for path,expected in endpoints:
        started=datetime.now(timezone.utc)
        response=requests.get(BASE+path,timeout=90,allow_redirects=False)
        body=response.json()
        valid=response.status_code==expected and isinstance(body,dict)
        if path=='/health':valid=valid and body.get('status')=='ok'
        if path=='/ready':valid=valid and body.get('status')=='ready' and body.get('database')=='available'
        if expected==401:valid=valid and isinstance(body.get('error'),str)
        checks.append(dict(url=BASE+path,method='GET',expected_status=expected,
            actual_status=response.status_code,passed=bool(valid),response=body,
            elapsed_seconds=round((datetime.now(timezone.utc)-started).total_seconds(),3),
            headers={k:response.headers.get(k) for k in ['Cache-Control','X-Content-Type-Options','X-Frame-Options']}))
    response=requests.get(BASE+'/api/v1/patients',headers={'Authorization':'Bearer invalid-synthetic-token'},timeout=30)
    checks.append(dict(url=BASE+'/api/v1/patients',method='GET',scenario='Token inválido sintético',
        expected_status=401,actual_status=response.status_code,passed=response.status_code==401,
        response=response.json()))
    value=dict(executed_utc=datetime.now(timezone.utc).isoformat(),
        source_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        existing_service=BASE,remote_sha='No observado; no se atribuye el SHA local al despliegue remoto',
        deployment_executed=False,mode='Pruebas reales de solo lectura sobre despliegue existente',
        checks=checks,passed=all(c['passed'] for c in checks))
    (DEST/'existing-api.json').write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    (DEST/'deployment-dry-run.json').write_text(json.dumps(rehearsal(),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Existing API:',len(checks),'checks;',sum(c['passed'] for c in checks),'passed; deployments: 0')
    raise SystemExit(0 if value['passed'] else 1)
if __name__=='__main__':main()
