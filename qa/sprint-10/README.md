# Pruebas Sprint 10 de Jesús

Casos: CP-S10-SAST-04, CP-S10-SIT-01, CP-S10-SIT-02, CP-S10-SIT-03 y CP-S10-UI-01 a CP-S10-UI-04.

## Instalación

Desde la raíz del repositorio:

```powershell
python -m venv .venv-s10
.\.venv-s10\Scripts\Activate.ps1
python -m pip install -r qa/sprint-10/requirements.txt
```

## Ejecución Selenium

Defina las variables QA sin escribir contraseñas en Git: `INEO_WEB_URL`, `INEO_QA_USER`, `INEO_QA_PASSWORD`, `INEO_NURSE_USER`, `INEO_NURSE_PASSWORD`.

```powershell
python -m pytest qa/sprint-10/selenium -m ui -v --junitxml=evidence/sprint-10/ui-junit.xml --html=evidence/sprint-10/ui-report.html --self-contained-html
```

## Ejecución SIT

Defina `INEO_API_URL`, `INEO_QA_TOKEN`, `INEO_QA_PATIENT_ID` e `INEO_SPARK_KIND`.

```powershell
python -m pytest qa/sprint-10/integration -m sit -v --junitxml=evidence/sprint-10/sit-junit.xml
```

## Seguridad

```powershell
python -m pip install pip-audit bandit
powershell -ExecutionPolicy Bypass -File qa/sprint-10/security/run_security_checks.ps1
```

Un caso omitido por variables faltantes queda Bloqueado, no Aprobado. Copie los reportes y capturas reales en `evidence/sprint-10/<CP-ID>/ejecucion-AAAA-MM-DD-build/`.




## JMeter (PERF-01 a PERF-03)

Antes de ejecutar, define las variables de entorno `INEO_QA_USERNAME` e `INEO_QA_PASSWORD`. No guardes credenciales en `api.jmx`, archivos de propiedades ni evidencias. `build_plan.py` usa `__env(...)` para leerlas. Instala JMeter 5.6.3 y ejecuta `python qa/sprint-10/jmeter/run.py`. Si faltan las credenciales, la prueba SIT autenticada queda bloqueada y no debe registrarse como aprobada.