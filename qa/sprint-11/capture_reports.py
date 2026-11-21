"""Browser screenshots of original output reports, never simulated terminals."""
import hashlib
import html
import json
from pathlib import Path
from selenium import webdriver
from common import OUT, ROOT

def main():
    shots=OUT/'screenshots';shots.mkdir(exist_ok=True)
    pages=OUT/'report-views';pages.mkdir(exist_ok=True)
    options=webdriver.ChromeOptions();options.add_argument('--headless=new');options.add_argument('--window-size=1300,1150')
    options.add_argument('--allow-file-access-from-files')
    driver=webdriver.Chrome(options=options)
    try:
        for path in sorted((OUT/'logs').glob('*.txt')):
            if path.name.startswith(('init-','validate-','docker-version','terraform-version','terraform-fmt','create-','idempotency-','introduce-','detect-','restore','isolated-','mongo-','cleanup-','jmeter-','regression')):
                raw=path.read_text(encoding='utf-8')
                # Long logs stay original on disk. The browser shows their last 70 lines,
                # explicitly labeled as an excerpt, with SHA256 of the full original.
                lines=raw.splitlines();excerpt='\n'.join(lines[:2]+['… extracto del registro original …']+lines[-24:])
                if len(lines)<=26:excerpt=raw
                if path.stem=='detect-drift':
                    selected=set([0,1])
                    for i,line in enumerate(lines):
                        if 'name ' in line or 'drift' in line.lower() or line.startswith('Plan:'):
                            selected.update(range(max(0,i-1),min(len(lines),i+2)))
                    excerpt='\n'.join(lines[i] for i in sorted(selected))
                page=pages/(path.stem+'.html')
                page.write_text('<!doctype html><meta charset="utf-8"><style>body{font:22px Arial;margin:32px;color:#17212b}pre{white-space:pre-wrap;font:20px Consolas;line-height:1.25;background:#f3f5f7;padding:20px}small{overflow-wrap:anywhere}</style>'+
                    '<h1>Registro de ejecución Sprint 11</h1><p>'+html.escape(path.relative_to(ROOT).as_posix())+'</p><small>SHA256 original: '+hashlib.sha256(path.read_bytes()).hexdigest()+'</small><p>Extractos del registro original; archivo completo conservado.</p><pre>'+html.escape(excerpt)+'</pre>',encoding='utf-8')
                driver.get(page.as_uri());driver.save_screenshot(str(shots/(path.stem+'.png')))
        smoke=OUT/'render-smoke.json'
        if smoke.exists():
            page=pages/'render-smoke.html'
            data=json.loads(smoke.read_text(encoding='utf-8'))
            rows=''.join('<tr><td>'+html.escape(c['url'])+'</td><td>'+str(c.get('status'))+'</td><td>'+str(c.get('seconds'))+'</td><td>'+html.escape(json.dumps(c.get('body'),ensure_ascii=False))+'</td></tr>' for c in data['checks'])
            page.write_text('<!doctype html><meta charset="utf-8"><style>body{font:20px Arial;margin:28px}td,th{border:1px solid #ccc;padding:16px;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}</style><h1>Smoke HTTPS Render</h1><p>Solicitudes reales de solo lectura. Fuente: render-smoke.json</p><table><tr><th>URL</th><th>HTTP</th><th>Segundos</th><th>Respuesta original</th></tr>'+rows+'</table><p>El SHA desplegado y un nuevo despliegue siguen sin verificarse.</p>',encoding='utf-8')
            driver.get(page.as_uri());driver.save_screenshot(str(shots/'render-smoke.png'))
        for report in (OUT/'jmeter').glob('*/html/index.html'):
            driver.get(report.as_uri());driver.save_screenshot(str(shots/('jmeter-dashboard-'+report.parents[1].name+'.png')))
        for metrics in (OUT/'jmeter').glob('*/metrics.json'):
            page=pages/('metrics-'+metrics.parent.name+'.html')
            data=json.loads(metrics.read_text(encoding='utf-8'))
            rows=''.join('<tr><td>'+html.escape(key)+'</td><td>'+html.escape(json.dumps(value,ensure_ascii=False))+'</td></tr>' for key,value in data.items())
            page.write_text('<!doctype html><meta charset="utf-8"><style>body{font:24px Arial;margin:24px}h1{font-size:32px}td{border:1px solid #bbb;padding:10px;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}td:first-child{width:35%}</style><h1>Mediciones originales JMeter '+metrics.parent.name+'</h1><p>Fuente: jmeter/'+metrics.parent.name+'/metrics.json</p><table>'+rows+'</table>',encoding='utf-8')
            driver.get(page.as_uri());driver.save_screenshot(str(shots/('metrics-'+metrics.parent.name+'.png')))
    finally:driver.quit()
if __name__=='__main__':main()
