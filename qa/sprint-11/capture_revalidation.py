"""Capture actual revalidation reports and the explicitly simulated procedure."""
import hashlib
import html
import json
import re
from selenium import webdriver
from common import OUT, ROOT

def main():
    source=OUT/'revalidation';pages=OUT/'report-views';shots=OUT/'screenshots'
    pages.mkdir(exist_ok=True);shots.mkdir(exist_ok=True)
    options=webdriver.ChromeOptions();options.add_argument('--headless=new');options.add_argument('--window-size=1300,1150')
    driver=webdriver.Chrome(options=options)
    def capture(name,title,body,original):
        page=pages/(name+'.html')
        page.write_text('<!doctype html><meta charset="utf-8"><style>body{font:23px Arial;margin:28px;color:#17212b}h1{font-size:32px}td,th{padding:12px;border:1px solid #bbb;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}pre{font:19px Consolas;white-space:pre-wrap}small{font-size:17px;overflow-wrap:anywhere}</style><h1>'+html.escape(title)+'</h1><p>'+html.escape(original.relative_to(ROOT).as_posix())+'</p>'+body+'<p><small>SHA256 original: '+hashlib.sha256(original.read_bytes()).hexdigest()+'</small></p>',encoding='utf-8')
        driver.get(page.as_uri());driver.save_screenshot(str(shots/(name+'.png')))
    def table(headers,rows):
        return '<table><tr>'+''.join('<th>'+html.escape(str(h))+'</th>' for h in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table>'
    try:
        path=source/'existing-api.json';data=json.loads(path.read_text(encoding='utf-8'))
        capture('existing-api-validation','API Render existente sin redespliegue',
            '<p>Solicitudes GET reales. Despliegues ejecutados: 0.</p>'+table(['Ruta','Esperado','Obtenido','Resultado'],[
                [c['url'].split('.com')[-1]+(' · token inválido' if c.get('scenario') else ''),c['expected_status'],c['actual_status'],'Cumple' if c['passed'] else 'Falló'] for c in data['checks']]),path)
        path=source/'deployment-dry-run.json';data=json.loads(path.read_text(encoding='utf-8'))
        capture('deployment-dry-run','Simulación del procedimiento de despliegue',
            '<p>Ensayo documental y validación estática. Ningún despliegue ni rollback remoto ejecutado.</p>'+table(['Paso','Comprobación o simulación'],[[v['action'],v['mode']] for v in data['steps']])+ '<p>Se comprobó configuración local y se reutilizó la API pública existente.</p>',path)
        path=source/'web-checks.json';data=json.loads(path.read_text(encoding='utf-8'))
        capture('web-revalidation','Verificación del repositorio web',table(['Comprobación','Resultado','Segundos'],[[v['check'],v['status'],v.get('seconds','')] for v in data['checks']])+ '<p>La copia local de picomatch se revisa por diff y pruebas; npm audit no inspecciona ese código local.</p>',path)
        path=source/'technical-assessment.json';data=json.loads(path.read_text(encoding='utf-8'))
        capture('suite-summary','Resultados de las suites ejecutadas',table(['Suite','Casos','Fallos','Errores','Omitidos'],[[name,v['tests'],v['failures'],v['errors'],v['skipped']] for name,v in data['suites'].items()])+ '<p>Los casos omitidos se identifican en XML; el caso consumidor omitido en la suite aislada se ejecutó aparte con servicios reales.</p><p>Pendiente: revisión de Jesús.</p>',path)
        path=OUT/'logs/web-glob-security.txt'
        text=re.sub(r'\x1b\[[0-9;]*m','',path.read_text(encoding='utf-8'))
        capture('glob-security','Pruebas de la corrección local de seguridad','<p>Copia local protegida de picomatch 4.0.7. Se mantuvo la licencia y la versión de origen.</p><pre>'+html.escape(text)+'</pre><p>El cambio restringe extglobs repetidos con comodines. Revisión final: Jesús.</p>',path)
    finally:driver.quit()
if __name__=='__main__':main()
