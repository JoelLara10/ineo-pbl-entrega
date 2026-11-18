"""Derive a technical assessment from originals; never rewrite old results."""
from datetime import datetime, timezone
import json
from pathlib import Path
import xml.etree.ElementTree as E
from common import OUT

def junit(path):
    root=E.parse(path).getroot()
    cases=root.findall('.//testcase')
    return dict(tests=len(cases),failures=sum(c.find('failure') is not None for c in cases),
        errors=sum(c.find('error') is not None for c in cases),
        skipped=sum(c.find('skipped') is not None for c in cases))

def main():
    current=OUT/'revalidation'
    web=json.loads((current/'web-checks.json').read_text(encoding='utf-8'))
    assert len(web['checks'])==8 and all(c['status']=='Aprobado' for c in web['checks'])
    api=junit(current/'api-tests.xml');frontend=junit(current/'frontend-tests.xml')
    sit=junit(current/'consumer-sit.xml')
    assert all(v['failures']==v['errors']==0 for v in [api,frontend,sit])
    assert sit['tests']==1 and sit['skipped']==0
    audit=json.loads((current/'npm-audit.json').read_text(encoding='utf-8'))
    assert audit['metadata']['vulnerabilities']['total']==0
    remote=json.loads((current/'existing-api.json').read_text(encoding='utf-8'))
    rehearsal=json.loads((current/'deployment-dry-run.json').read_text(encoding='utf-8'))
    assert remote['passed'] and len(remote['checks'])==9
    assert rehearsal['passed'] and not rehearsal['remote_deployment_executed']
    assessment=[]
    for path in sorted((OUT/'cases').glob('CP-S11-*.json')):
        value=json.loads(path.read_text(encoding='utf-8'))
        if 'PERF' in value['case']:
            name={'CP-S11-PERF-01':'nominal','CP-S11-PERF-02':'peak','CP-S11-PERF-03':'writes'}[value['case']]
            measured=json.loads((OUT/'jmeter'/name/'metrics.json').read_text(encoding='utf-8'))
            assert measured['observed_threshold_result'] and measured['errors']==0
        else:assert value['status']=='Aprobado'
        assessment.append(dict(case=value['case'],technical_status='Cumple',
            original_status=value['status'],review='Pendiente de Jesús'))
    report=dict(created_utc=datetime.now(timezone.utc).isoformat(),
        scope='Entrega técnica de Zahid; API Render existente; sin nuevo despliegue por instrucción del solicitante',
        criteria=dict(p95_ms=2000,max_error_rate=.01,
            status='Criterios técnicos de evaluación; ratificación incluida en revisión de Jesús'),
        historical_results_preserved=True,cases=assessment,
        suites=dict(api=api,frontend=frontend,consumer_sit=sit),
        dependency_audit=audit['metadata']['vulnerabilities'],
        dependency_review='Copia local protegida: revisión de diff, licencia y ocho guardas; npm audit no analiza el código local',
        remote_api_checks=9,deployments_executed=0,
        rehearsal='Simulación documental comprobada; ningún despliegue o rollback remoto ejecutado',
        pending=['Revisión final de Jesús de resultados, criterios técnicos y corrección local'])
    (current/'technical-assessment.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Technical checks passed; pending: Jesús review. Remote deployments: 0')
if __name__=='__main__':main()
