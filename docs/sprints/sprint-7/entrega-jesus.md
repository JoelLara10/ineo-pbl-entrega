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

## Casos de prueba y resultados observados

Las pruebas se ejecutaron el **24 de septiembre de 2026**. Para las pruebas
locales se utilizó Flask con una base Mongo simulada y datos sintéticos. En
Render no se utilizó ninguna cuenta ni se envió información clínica.

| ID | Tarea | Escenario y dato de entrada | Resultado esperado | Resultado observado | Estado |
|---|---|---|---|---|---|
| CP-01 | PBL-01-T3 | Abrir directamente `/admin/spark` y sus cuatro páginas con sesión `admin` sintética | Permanecer en la URL solicitada y mostrar el módulo | Las cinco páginas cargaron sin redirigir al inicio | Aprobado local |
| CP-02 | PBL-01-T3 | Abrir `/admin/spark/clinical` sin sesión | Redirigir a `/login` | Redirigió a `/login` | Aprobado local |
| CP-03 | PBL-01-T3 | Abrir `/admin/spark/clinical` con rol `medico` | Impedir la ruta de administrador | Redirigió a `/` | Aprobado local |
| CP-04 | PBL-02-T5 / PBL-13-T5 | Consultar overview, resultados, status y run con token `admin` sintético | Respuestas JSON conformes a los esquemas y sin 404 | `test_spark_contract.py` validó estados, resultados, códigos y esquema v1 | Aprobado local |
| CP-05 | PBL-03-T5 | Iniciar análisis, consultar estado y completar con ocho registros sintéticos | `idle → pending → running → completed`, resultado disponible | Estado completado y `summary.total=8` | Aprobado local |
| CP-06 | PBL-03-T5 / PBL-04-T3 | Producir excepción, resultado vacío y reintento | Error controlado, `available=false` para vacío y reintento posible | Se verificaron `failed`, vacío y nuevo trabajo en las pruebas de contrato | Aprobado local; visual pendiente |
| CP-07 | PBL-05-T4 | Comparar `spark.*` en español e inglés y mostrar datos dinámicos | Claves equivalentes, etiquetas traducidas y sin claves técnicas | Se renderizaron «Promedio/Frecuencia cardíaca» y «Mean/Heart rate» | Aprobado local |
| CP-08 | PBL-26-T3 | Login de `admin`, `medico`, `enfermeria` y `estudios` sintéticos | Identidad del rol correcto; Spark solo para `admin` | Cuatro logins y `/auth/me` válidos; Spark: 200 para admin, 403 para otros roles | Aprobado local |
| CP-09 | PBL-26-T3 | Contraseña incorrecta y usuario inexistente | 401, sin token ni acceso a Spark | Ambas credenciales devolvieron 401 sin token | Aprobado local |
| CP-10 | PBL-26-T3 | Alterar colecciones durante una prueba | Restablecer usuarios, pacientes y trabajos en la siguiente prueba | Se recuperaron 4 usuarios, 8 pacientes y 0 trabajos | Aprobado local |
| CP-11 | PBL-02-T5 / PBL-13-T5 | Solicitudes **sin token** a Render | 401 JSON `unauthorized` con versión 1.0; nunca 404 | Las diez rutas de la tabla siguiente devolvieron 401 y contrato válido | Aprobado en Render, solo sin token |

### Registro de la API publicada

**Base:** `https://api-clinica-jx4m.onrender.com`. Resultado de
`python scripts/sprint7_smoke_public.py`:

| Método y ruta bajo `/api/v1/spark` | HTTP | `code` | Contrato |
|---|---:|---|---|
| GET `/overview` | 401 | `unauthorized` | OK |
| GET `/analytics` | 401 | `unauthorized` | OK |
| GET `/status/analytics` | 401 | `unauthorized` | OK |
| GET `/met` | 401 | `unauthorized` | OK |
| GET `/status/met` | 401 | `unauthorized` | OK |
| GET `/clinical` | 401 | `unauthorized` | OK |
| GET `/status/clinical` | 401 | `unauthorized` | OK |
| GET `/unsupervised` | 401 | `unauthorized` | OK |
| GET `/status/unsupervised` | 401 | `unauthorized` | OK |
| POST `/run/analytics` | 401 | `unauthorized` | OK |

**Resumen de consola:** `75 passed` en las pruebas específicas de backend;
`86 passed, 7 skipped` en la suite backend; `42 passed` en Vitest. Los siete
casos omitidos requieren habilitar el motor Spark real y Java según la guía de
ambiente del equipo. Los 401 de Render son el resultado correcto para un cliente
sin token; **no significan que haya fallado la ruta**.

### Evidencia visual que debe agregarse al entregar en clase

Las pruebas automáticas dejan resultados reproducibles en el repositorio, pero
esta ejecución no generó capturas del navegador ni de una sesión autenticada
en Render. Si solicitan capturas, colocar aquí las siguientes imágenes reales:

1. **Figura 1.** Consola de `python -m pytest -q tests` con el resumen final.
2. **Figura 2.** Consola de `npm test` con el resumen final.
3. **Figura 3.** Consola de `python scripts/sprint7_smoke_public.py` con las diez rutas.
4. **Figura 4.** Panel Spark abierto con una cuenta de prueba administradora en
   el ambiente autorizado, sin mostrar token, contraseña ni datos de pacientes.

No se presenta una captura simulada como evidencia de ejecución.

La prueba sin credenciales confirma existencia y control de acceso en Render; no
demuestra resultados Spark, roles autenticados ni la interfaz publicada. Para esa
aceptación se necesita una cuenta de prueba autorizada y datos sintéticos en el
ambiente de integración. Las advertencias de `datetime.utcnow()` existentes no
impidieron las pruebas. Las pruebas de React montan el router y verifican rutas,
pero no sustituyen una inspección visual en un navegador real.
