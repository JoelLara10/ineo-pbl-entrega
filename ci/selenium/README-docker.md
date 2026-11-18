# Selenium remoto para el Sprint 11

La ejecución en Chrome de Windows se cerraba al crear procesos de pestaña y GPU. La suite ahora se conecta a un Selenium Grid propio en Docker; no usa el contenedor `lab-ci` de la práctica, no monta carpetas del host y solo publica el endpoint en `127.0.0.1:4444`.

## Contenedor del proyecto

Imagen fijada: `selenium/standalone-chrome:4.52.0-20261101`.

```powershell
docker start oftalcore-selenium-sprint11
Invoke-RestMethod http://127.0.0.1:4444/status
docker stop oftalcore-selenium-sprint11
```

La respuesta de `/status` debe indicar `ready: true`. Para recrearlo si se elimina:

```powershell
docker run --detach --name oftalcore-selenium-sprint11 --publish 127.0.0.1:4444:4444 --shm-size=2g --restart=no selenium/standalone-chrome:4.52.0-20261101
```

## Ejecutar los casos manualmente

Desde la raíz del repositorio, con Node/dependencias y el entorno Python de pruebas instalados:

```powershell
$env:SELENIUM_REMOTE_URL = 'http://127.0.0.1:4444'
$env:SELENIUM_BROWSER_HOST = 'host.docker.internal'
$env:INEO_SCREENSHOT_DIR = (Join-Path $PWD 'reports/selenium/screenshots')
python -m pytest -q ci/selenium --junitxml=reports/selenium/selenium.xml
Remove-Item Env:\SELENIUM_REMOTE_URL, Env:\SELENIUM_BROWSER_HOST, Env:\INEO_SCREENSHOT_DIR
```

Los casos levantan Vite y una API temporal con Mongo simulado y datos sintéticos; esos servicios se cierran al terminar. Las capturas y el XML no representan UAT humana. El job `OftalCore-Joel-Sprint11` contiene una etapa para esperar el Grid, ejecutar los casos y archivar sus resultados.
