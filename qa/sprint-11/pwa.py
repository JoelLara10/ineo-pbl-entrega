"""Real React build + Selenium + HTTP/Mongo session isolation while offline."""
import json
from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common import OUT, record

BASE='http://127.0.0.1:5111'
CASE='CP-S11-SIT-03'

def main():
    shots=OUT/'screenshots';shots.mkdir(exist_ok=True)
    options=webdriver.ChromeOptions()
    options.add_argument('--headless=new');options.add_argument('--window-size=1440,1000')
    driver=webdriver.Chrome(options=options)
    wait=WebDriverWait(driver,30);steps=[]
    def shot(label):driver.save_screenshot(str(shots/(CASE+'-'+label+'.png')))
    def login(name):
        driver.get(BASE+'/login')
        wait.until(EC.visibility_of_element_located((By.NAME,'ineo-login-username'))).send_keys(name)
        driver.find_element(By.NAME,'ineo-login-password').send_keys('Prueba-Sprint7!')
        driver.find_element(By.CSS_SELECTOR,'button.login-btn').click()
        wait.until(lambda d: d.execute_script("return !!localStorage.getItem('@ineo_token')") and '/login' not in d.current_url)
    def storage():
        return driver.execute_async_script("""const done=arguments[arguments.length-1];
        caches.keys().then(async names=>{let urls=[];for(const name of names){const c=await caches.open(name);urls.push(...(await c.keys()).map(r=>r.url));}
        done({localKeys:Object.keys(localStorage),sessionKeys:Object.keys(sessionStorage),cacheUrls:urls});});""")
    try:
        login('admin.test')
        wait.until(lambda d:d.execute_script('return !!navigator.serviceWorker.controller'))
        first=driver.execute_script("return JSON.parse(localStorage.getItem('@ineo_user')).username")
        driver.get(BASE+'/enfermeria')
        wait.until(lambda d:'SINTETICO' in d.find_element(By.TAG_NAME,'body').text)
        shot('01-online-admin')
        driver.execute_cdp_cmd('Network.enable',{})
        driver.execute_cdp_cmd('Network.emulateNetworkConditions',dict(offline=True,latency=0,downloadThroughput=0,uploadThroughput=0))
        wait.until(lambda d: d.execute_script('return !navigator.onLine'))
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'.offline-shell')))
        body=driver.find_element(By.TAG_NAME,'body').text
        assert 'SINTETICO' not in body
        cached=storage()
        assert not any('/api/' in url for url in cached['cacheUrls'])
        forbidden=['ineo_web_cache_','@ineo_admin_cache:','estudios_','examen_info_','ineo_selected_patient','@ineo_print_history']
        assert not any(any(k.startswith(p) for p in forbidden) for k in cached['localKeys'])
        shot('02-offline-no-clinical-data')
        # Use the actual application's offline logout control.
        driver.find_element(By.CSS_SELECTOR,'.offline-shell button').click()
        wait.until(lambda d:d.execute_script("return localStorage.getItem('@ineo_token')===null"))
        assert driver.execute_script("return localStorage.getItem('@ineo_user')") is None
        shot('03-offline-logout')
        driver.execute_cdp_cmd('Network.emulateNetworkConditions',dict(offline=False,latency=0,downloadThroughput=-1,uploadThroughput=-1))
        wait.until(lambda d:d.execute_script('return navigator.onLine'))
        login('enfermeria.test')
        second=driver.execute_script("return JSON.parse(localStorage.getItem('@ineo_user')).username")
        assert first=='admin.test' and second=='enfermeria.test'
        driver.get(BASE+'/enfermeria')
        wait.until(lambda d:'SINTETICO' in d.find_element(By.TAG_NAME,'body').text)
        shot('04-second-account')
        driver.execute_cdp_cmd('Network.emulateNetworkConditions',dict(offline=True,latency=0,downloadThroughput=0,uploadThroughput=0))
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'.offline-shell')))
        assert 'SINTETICO' not in driver.find_element(By.TAG_NAME,'body').text
        second_storage=storage()
        assert not any('/api/' in url for url in second_storage['cacheUrls'])
        shot('05-second-account-offline')
        steps=[['Abrir datos con cuenta A','Datos sintéticos desde API real','Lista visible con admin.test'],
            ['Desconectar la red','Ocultar datos clínicos y no cachear API','Shell offline; CacheStorage sin /api/'],
            ['Cerrar sesión sin red','Eliminar token y usuario','Ambos ausentes de localStorage'],
            ['Reconectar con cuenta B','Sesión independiente','enfermeria.test; consulta real'],
            ['Desconectar cuenta B','No mostrar datos de cuenta A','Shell seguro sin datos clínicos']]
        (OUT/'pwa-storage.json').write_text(json.dumps(dict(first=first,second=second,offline=cached,
            second_offline=second_storage,api='http://127.0.0.1:5110',database='ineo_test_s11'),indent=2),encoding='utf-8')
        record(CASE,'Desconexión PWA entre cuentas',steps)
    except Exception as exc:
        shot('failure')
        record(CASE,'Desconexión PWA entre cuentas',steps,status='Fallido',detail=str(exc));raise
    finally:driver.quit()
if __name__=='__main__':main()
