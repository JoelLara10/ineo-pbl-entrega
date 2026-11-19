# Suite de pruebas Sprint 11

Suite asignada a Jesus Alejandro Diaz Serafin para PBL-50-T5 y PBL-50-T6. Incluye cinco pruebas UI, dos SIT y la validación del reporte SAST.

## Preparación en Windows

```bat
py -3.11 -m venv .venv-sprint11
.venv-sprint11\Scripts\python.exe -m pip install -r qa\sprint-11\requirements.txt
```

Configure en Jenkins las credenciales `ineo-admin-login` e `ineo-enfermeria-login`. Copie las variables de `.env.example` al entorno del job sin guardar contraseñas en Git.

## Ejecución

```bat
.venv-sprint11\Scripts\python.exe -m pytest qa\sprint-11 -v --junitxml=qa\sprint-11\reports\resultados.xml
```

También puede usar `qa\sprint-11\run_tests.bat`. Antes de ejecutar, complete
las rutas del ambiente tomando como guía `.env.example` y compruebe la
configuración con `validate_configuration.py`.

Las pruebas que modifican datos necesitan `S11_ENABLE_MUTATION_TESTS=true`, rutas reales y un fixture sintético aislado. Si falta un prerrequisito, el caso se omite con la causa y no se considera aprobado.

## Evidencias

Los reportes se guardan en `qa/sprint-11/reports/`, las capturas en `qa/sprint-11/screenshots/` y el Word de cada caso en `evidence/sprint-11/CP-ID/`.

