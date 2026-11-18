# Sprint 11 de Zahid

Se preparó PBL-39 (#503) y PBL-49 (#544), con campaña de ocho casos en
PBL-39-T4 (#591) y PBL-39-T5 (#592). Este directorio ejecuta QA local con
API y MongoDB reales. Render conserva su verificación HTTPS por separado.

## Preparación

Desde la raíz del repositorio, usar Python 3.13, Node compatible con Vite,
Docker Desktop iniciado, Terraform 1.16.4, Chrome y JMeter 5.6.3 con Java 17.
Las versiones efectivas de la ejecución están en requirements-lock.txt.
El paquete pywin32 de ese inventario corresponde a Windows y no es requisito
de las pruebas Linux. No instalar estas dependencias en el ambiente productivo.

```powershell
python -m venv .venv-s11
.venv-s11/Scripts/python -m pip install -r qa/sprint-11/requirements.txt pytest-html mongomock pytest-cov
npm ci --prefix frontend/clinica-web-react
python qa/sprint-11/infrastructure/lifecycle.py
.venv-s11/Scripts/python qa/sprint-11/server.py
```

En otra consola, desde la misma raíz:

```powershell
$env:VITE_API_URL='http://127.0.0.1:5110/api/v1'
npm run build --prefix frontend/clinica-web-react
npm run preview --prefix frontend/clinica-web-react -- --host 127.0.0.1 --port 5111
```

Los servidores y Selenium deben compartir el contexto de red del host.
No usar la base productiva. El launcher solamente restablece ineo_test_s11
en MongoDB de loopback 27111; las cuentas son las sintéticas del repositorio.
Para no conservar información entre ejecuciones, el launcher restablece
fixtures, balances y sesiones revocadas antes de comenzar la campaña.

## Ejecución

```powershell
.venv-s11/Scripts/python qa/sprint-11/pwa.py
$env:JAVA_EXE='C:\Program Files\Java\jdk-17\bin\java.exe'
.venv-s11/Scripts/python qa/sprint-11/performance.py --home 'RUTA/apache-jmeter-5.6.3' --case diagnostic
.venv-s11/Scripts/python qa/sprint-11/performance.py --home 'RUTA/apache-jmeter-5.6.3'
.venv-s11/Scripts/python qa/sprint-11/render_smoke.py
.venv-s11/Scripts/python -m pytest qa/sprint-11/test_campaign_guards.py -q
.venv-s11/Scripts/python qa/sprint-11/capture_reports.py
```

Los criterios técnicos son p95 de 2000 ms y errores máximos de 1 %.
La revisión final de Jesús incluye criterios, concurrencia, recursos y duración.
No agregar --accept-thresholds antes de esa revisión. Los registros históricos
conservan el estado pendiente de ratificación; technical-assessment.json
distingue cumplimiento técnico de aprobación humana. Fallar devuelve código no cero.
El escenario nominal dura 360 s: rampa de 60 s y cinco minutos posteriores.
El pico mantiene cinco usuarios, añade quince durante 60 s y vuelve a cinco
durante 30 s. Escrituras alterna pacientes sintéticos 1/2 y compara cada registro
aceptado, ID único y suma de balances con MongoDB real.

Los estados Terraform se guardan fuera del checkout, en el directorio hermano
tf-s11/a y tf-s11/b; los TF_DATA_DIR son exclusivos. Los contenedores son
ineo-test-s11-qa-a/b, puertos loopback 27111/27112 y volúmenes exclusivos.
La imagen MongoDB es una dependencia compartida de lectura, no un estado de QA.
Se conservan intentos anteriores en evidence/sprint-11/zahid/attempts.
Los reportes HTML/JTL no almacenan tokens ni cuerpos de solicitudes.

## Limpieza

Detener los servidores iniciados para la campaña. Desde la raíz:

```powershell
python qa/sprint-11/infrastructure/lifecycle.py --cleanup
```

Esto destruye exclusivamente los recursos registrados por los dos estados
del Sprint 11. No ejecutar terraform destroy sobre otro directorio o estado.
Conservar los archivos de estado locales hasta verificar la limpieza; nunca
subirlos a Git. Los documentos de resultados están en docs/sprints/sprint-11/zahid.

## Revalidación sobre la API existente

Por instrucción del solicitante no se realiza un nuevo despliegue en Render.
existing_deployment.py realiza comprobaciones GET contra la API desplegada
y revisa la configuración local. Los resultados del servicio se conservan en
revalidation/existing-api.json; el proceso se describe en render-runbook.md.

```powershell
.venv-s11/Scripts/python qa/sprint-11/existing_deployment.py
.venv-s11/Scripts/python qa/sprint-11/revalidate.py
.venv-s11/Scripts/python qa/sprint-11/final_assessment.py
.venv-s11/Scripts/python qa/sprint-11/capture_revalidation.py
```

La suite consumidor se ejecuta con RUN_CONTRACT_SIT=1 y
INEO_CONTRACT_API_URL=http://127.0.0.1:5110/api/v1 y los servicios locales de
arriba. Sus XML consumer-sit.xml y api-tests.xml son entradas de la evaluación.
La mitigación local de picomatch se explica en
frontend/clinica-web-react/vendor/picomatch-guarded/SECURITY.md.
El único pendiente de esta entrega técnica es la revisión de Jesús.
