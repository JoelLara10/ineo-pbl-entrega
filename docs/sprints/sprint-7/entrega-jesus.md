# Sprint 7 — entrega de Jesús

**Responsable:** Jesús Alejandro Díaz Serafín

**Rama:** `sprints/jesus-sprint-7-validacion`

**Fecha:** 24 de septiembre de 2026

**Proyecto Azure:** INEO-Enfermeria, Sprint 7. Corresponde a «Sprint 1» en el PBL consolidado.

## Alcance y análisis

La autenticación web usa JWT; los módulos Spark son exclusivos del administrador. El
frontend contiene cinco rutas (`/admin/spark` y las cuatro variantes analytics, met,
clinical y unsupervised), servicio Axios y traducciones `spark.*` en español e inglés.
La API registra `/api/v1/spark`, con overview, resultados, ejecución y estado. El
contrato está en `contracts/v1/api.schema.json`. El entorno de pruebas existente
usa `mongomock`, `testing/seed.py`, usuarios de cuatro roles y limpieza por prueba.

Dependencias de esta entrega: rutas y estados de Joel; endpoints, contrato y semilla
de Zahid; implementación de traducciones de Joel. No se sustituye su código ni se
considera aceptación final una prueba aislada. Las pruebas usan contraseñas y datos
ficticios, sin conectar Mongo de producción. El script contra Render no envía token.

## Diseño de validación

| Capa | Entrada | Resultado comprobado | Evidencia |
|---|---|---|---|
| Rutas React | URL directa, sesión de administrador/médico/sin sesión | La ruta admin abre el módulo; los demás casos redirigen | `src/tests/sprint7-jesus-routes.test.jsx` |
| Idiomas y estados | Claves `spark.*`, resultados y estados | Equivalencia es/en; estados y acciones visibles en los componentes | `sprint7-zahid.test.jsx`, `sprint1-joel.test.js`, código de Spark |
| Contrato Flask | GET/POST con rol, token y datos sintéticos | Estados, resultado, error, schema y permisos | `tests/test_spark_contract.py` |
| Datos de prueba | Cuatro roles, pacientes, cambios durante cada prueba | Login por rol, acceso administrativo, fallos, restablecimiento | `tests/test_sprint7_jesus.py` |
| Render | Diez rutas sin credenciales | HTTP 401 con `code=unauthorized`, versión 1.0; distingue ruta existente de 404 | `scripts/sprint7_smoke_public.py` |

El flujo esperado es `idle → pending → running → completed/failed`. La UI consulta
estado, muestra progreso y recupera los resultados al terminar. `available=false`
se presenta como ausencia de datos, mientras que errores de conexión y ejecución
tienen acciones de reintento. El servidor es la autoridad de los permisos; esconder
una ruta en React no concede acceso a la API.

## Trazabilidad de mis tareas

| Tarea | Entrega o verificación | Estado de evidencia |
|---|---|---|
| PBL-01-T3 | Prueba montando el router real: cinco accesos directos, sesión y rol | Automatizada |
| PBL-02-T5 | Contrato HTTP de overview, cuatro resultados, run y status; prueba externa de rechazo 401 | Automatizada; sin ejecución autenticada en Render |
| PBL-03-T5 | Transiciones, resultado real sintético, reintento y fallo en `test_spark_contract.py` | Automatizada localmente |
| PBL-04-T3 | Revisados estados sin ejecutar, vacío, sin conexión, procesando y fallo; sus acciones están en pantalla | Pruebas de claves y revisión de código; falta E2E visual |
| PBL-05-T1 | Identificados componentes, dependencias, traducciones y casos límite en este documento | Documentada |
| PBL-05-T2 | Definidos contrato, flujo, estados, errores y estrategia de pruebas en este documento | Documentada |
| PBL-05-T4 | Verificadas claves equivalentes, render bilingüe, rutas e integración del consumidor | Automatizada localmente; sin aceptación visual en producción |
| PBL-13-T5 | Contratos versionados y pruebas de resultado, estado, error e imagen documentada | Automatizada; imágenes no generadas en este incremento |
| PBL-26-T3 | Casos válidos e inválidos, cuatro roles, permisos, semilla y aislamiento de datos | Automatizada |

PBL-02-T5 figura **Closed** en Azure al revisar el tablero; no se cambia su estado.
Las demás tarjetas solo deben cerrarse cuando el equipo revise los criterios y las
limitaciones de la columna anterior. No se modificaron tareas de otros integrantes.

## Ejecución reproducible

Desde `backend/api_hospital` en un entorno Python con `requirements.txt` y las
dependencias de prueba de `requirements-test.txt`:

```bash
python -m pytest -q tests/test_sprint7_jesus.py tests/test_spark_contract.py
python -m pytest -q tests
python scripts/sprint7_smoke_public.py
```

El script de Render acepta `INEO_API_URL` para otro ambiente y usa exclusivamente
solicitudes sin autenticación. Desde `frontend/clinica-web-react`:

```bash
npm ci
npm test
npm run lint
npm run build
```

## Resultados y límites

- Contrato y casos nuevos del backend: **75 aprobados**; Mongo simulado, sin datos reales.
- Frontend: **42 aprobadas**, incluidas las cinco rutas y dos escenarios de rechazo.
- Render: diez rutas respondieron **401** con `unauthorized` y versión `1.0` sin token.
- Suite backend completa: **86 aprobadas, 7 omitidas** (motor Spark opcional).
- Lint y compilación de producción: aprobados.

La prueba sin credenciales confirma existencia y control de acceso en Render; no
demuestra resultados Spark, roles autenticados ni la interfaz publicada. Para esa
aceptación se necesita una cuenta de prueba autorizada y datos sintéticos en el
ambiente de integración. Las advertencias de `datetime.utcnow()` existentes no
impidieron las pruebas. Las pruebas de React montan el router y verifican rutas,
pero no sustituyen una inspección visual en un navegador real.
