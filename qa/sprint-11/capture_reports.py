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
    options=webdriver.ChromeOptions();options.add_argument('--headless=new');options.add_argument('--window-size=1500,1100')
    driver=webdriver.Chrome(options=options)
    try:
        for path in sorted((OUT/'logs').glob('*.txt')):
            if path.name.startswith(('init-','validate-','docker-version','terraform-version','terraform-fmt','create-','idempotency-','introduce-','detect-','restore','isolated-','mongo-','cleanup-','jmeter-','regression')):
                raw=path.read_text(encoding='utf-8')
                # Long logs stay original on disk. The browser shows their last 70 lines,
                # explicitly labeled as an excerpt, with SHA256 of the full original.
                lines=raw.splitlines();excerpt='\n'.join(lines[-70:])
                page=pages/(path.stem+'.html')
                page.write_text('<!doctype html><meta charset="utf-8"><style>body{font:18px Arial;margin:36px;color:#17212b}pre{white-space:pre-wrap;font:15px Consolas;line-height:1.35;background:#f3f5f7;padding:22px}small{overflow-wrap:anywhere}</style>'+
                    '<h1>Registro de ejecución Sprint 11</h1><p>'+html.escape(path.relative_to(ROOT).as_posix())+'</p><small>SHA256 original: '+hashlib.sha256(path.read_bytes()).hexdigest()+'</small><p>Vista del registro original'+(' — últimas 70 líneas' if len(lines)>70 else '')+'.</p><pre>'+html.escape(excerpt)+'</pre>',encoding='utf-8')
                driver.get(page.as_uri());driver.save_screenshot(str(shots/(path.stem+'.png')))
        smoke=OUT/'render-smoke.json'
        if smoke.exists():
            page=pages/'render-smoke.html'
            page.write_text('<!doctype html><meta charset="utf-8"><style>body{font:18px Arial;margin:32px}pre{white-space:pre-wrap;font:17px Consolas}</style><h1>Smoke HTTPS Render</h1><p>Resultado original de solicitudes reales de solo lectura</p><pre>'+html.escape(smoke.read_text(encoding='utf-8'))+'</pre>',encoding='utf-8')
            driver.get(page.as_uri());driver.save_screenshot(str(shots/'render-smoke.png'))
        for report in (OUT/'jmeter').glob('*/html/index.html'):
            driver.get(report.as_uri());driver.save_screenshot(str(shots/('jmeter-dashboard-'+report.parents[1].name+'.png')))
    finally:driver.quit()
if __name__=='__main__':main()
