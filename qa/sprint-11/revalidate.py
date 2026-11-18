"""Revalidate the existing delivery without initiating a Render deployment."""
import json
import argparse
import os
from pathlib import Path
import shutil
import sys
import time
from common import ROOT, OUT, run

WEB=ROOT/'frontend/clinica-web-react'
DEST=OUT/'revalidation'
DEST.mkdir(exist_ok=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--from-check');args=parser.parse_args()
    npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
    checks=[]
    actions=[
        ('web-clean-install',[npm,'ci']),
        ('web-glob-security',[npm,'run','test:glob-security']),
        ('web-i18n',[npm,'run','check:i18n']),
        ('web-lint',[npm,'run','lint']),
        ('web-tests',[npm,'test','--','--reporter=default','--reporter=junit','--outputFile='+str(DEST/'frontend-tests.xml')]),
        ('web-build',[npm,'run','build']),
        ('web-bundle',[npm,'run','check:bundle']),
        ('web-audit',[npm,'audit','--json']),
    ]
    if args.from_check:
        previous=DEST/'web-checks.json'
        if previous.exists():
            old=json.loads(previous.read_text(encoding='utf-8'))
            checks=[x for x in old['checks'] if x['status']=='Aprobado']
        labels=[label for label,_ in actions]
        actions=actions[labels.index(args.from_check):]
        checks=[x for x in checks if x['check'] not in {label for label,_ in actions}]
    for label,command in actions:
        started=time.time()
        try:
            result=run(label,command,cwd=WEB,env=dict(os.environ,VITE_API_URL='http://127.0.0.1:5110/api/v1'))
            if label=='web-audit':
                report=json.loads(result.stdout)
                assert report['metadata']['vulnerabilities']['high']==0
                assert report['metadata']['vulnerabilities']['critical']==0
                (DEST/'npm-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
            checks.append(dict(check=label,status='Aprobado',seconds=round(time.time()-started,3)))
        except Exception as exc:
            checks.append(dict(check=label,status='Fallido',detail=str(exc)))
            raise
        finally:
            (DEST/'web-checks.json').write_text(json.dumps(dict(
                scope='Verificación local; sin despliegue Render',
                dependency_note='La copia local de picomatch requiere revisión de su diff y test:glob-security; npm audit solo cubre paquetes publicados.',
                checks=checks),ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
