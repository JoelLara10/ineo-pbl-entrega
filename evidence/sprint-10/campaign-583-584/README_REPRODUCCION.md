# Evidencia de mis tareas 583 y 584

Alcance: CP-S10-IAC-01 a 04, CP-S10-PERF-01 a 03 y CP-S10-SIT-04.
Ejecutor: Marcelino Zahid Galicia Bonifacio. Sprint académico 4 / Azure 10.
Se conserva un SHA probado por herramienta en cases.json y en los reportes.

## Archivos

- iac/: salidas reales fmt, validate, negativos, plan JSON, apply, segundo plan sin cambios, destroy y estado vacío.
- perf/: JTL, HTML JMeter, ejecución y métricas de smoke, baseline y control negativo separado.
- sit/CP-S10-SIT-04.json y sit-assigned.xml: CORS y credenciales sobre HTTP/MongoDB reales. El XML es un extracto del testcase original; no representa una ejecución nueva.
- screenshots/: dos capturas reales del visor por cada caso. Las capturas muestran extractos identificados; los archivos completos son la fuente.
- SHA256.json: integridad de los archivos documentales y reportes de esta entrega. No incluye archivos del manifiesto mismo.

## Reproducción desde la raíz del repositorio

Requisitos: Python 3.13 con Flask, Flask-Cors, Flask-SocketIO, PyMongo, pytest, requests, jsonschema y las dependencias de la API; Terraform 1.16.4, Docker Engine disponible, Java 17 y Apache JMeter 5.6.3. Versiones registradas en versiones.txt.
Las variables TF_EXE y JAVA_EXE permiten indicar ejecutables si no están en PATH. No se requieren credenciales cloud; se trabaja en Docker QA local.

```text
terraform -chdir=infra/terraform init -input=false
python qa/sprint-10/iac/verify.py --out evidence/sprint-10/campaign-583-584/iac
python qa/sprint-10/sit/server.py
```

El servidor permanece en una terminal; en otra, desde la raíz:

```text
python -m pytest qa/sprint-10/sit/test_real_contracts.py -k sit_04 -v --tb=short --junitxml=evidence/sprint-10/cors.xml
python qa/sprint-10/jmeter/run.py --home RUTA_APACHE_JMETER_5_6_3 --out evidence/sprint-10/nueva-campana-perf
```

Usar un directorio nuevo para cada campaña JMeter. El runner ejecuta 1 usuario/60 s, 5 usuarios/210 s (30 s de rampa más 180 s de carga) y un negativo separado. El evaluador exige p95 <=2000 ms y errores <=1%; el negativo debe retornar 1. Umbrales ratificados por el ejecutor antes de la ejecución documentada.

Detener el servidor local con Ctrl+C; luego:

```text
python qa/sprint-10/iac/verify.py --phase cleanup --out evidence/sprint-10/campaign-583-584/iac
```

La limpieza elimina exclusivamente recursos del estado Terraform de este ambiente. No se utiliza producción ni la suscripción Azure. La revisión cruzada y el cierre en Azure permanecen sujetos a una decisión humana verificable.
